#!/bin/bash
# Docker-based SSH proxy test runner

set -e

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Default values
CONTAINER_NAME="radkit-ssh-proxy-test"
IMAGE_NAME="cisco-radkit-test"
TEST_DEVICE="${TEST_DEVICE:-daa-csr1}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

usage() {
    cat << EOF
Usage: $0 [OPTIONS] [COMMAND]

Test cisco.radkit SSH proxy functionality in a Docker container.

OPTIONS:
    -h, --help              Show this help message
    -d, --device DEVICE     Device name to test (default: daa-csr1)
    -v, --verbose           Enable verbose output
    --build                 Force rebuild of Docker image
    --interactive           Run container interactively
    --clean                 Clean up containers and images

COMMANDS:
    test-ssh-proxy          Run SSH proxy integration test (default)
    test-local              Run local SSH proxy test
    shell                   Start interactive shell in container
    clean                   Clean up Docker resources

ENVIRONMENT VARIABLES (required):
    RADKIT_ANSIBLE_SERVICE_SERIAL              RADKit service serial
    RADKIT_ANSIBLE_IDENTITY                    RADKit identity
    RADKIT_ANSIBLE_CLIENT_PRIVATE_KEY_PASSWORD_BASE64  Client key password (base64)

EXAMPLES:
    # Run SSH proxy test with default device
    $0

    # Run test with specific device
    $0 -d my-device-name

    # Build image and run test interactively
    $0 --build --interactive

    # Get interactive shell
    $0 shell

EOF
}

log() {
    echo -e "${BLUE}[$(date +'%H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

check_env() {
    local missing=()
    
    if [ -z "$RADKIT_ANSIBLE_SERVICE_SERIAL" ]; then
        missing+=("RADKIT_ANSIBLE_SERVICE_SERIAL")
    fi
    
    if [ -z "$RADKIT_ANSIBLE_IDENTITY" ]; then
        missing+=("RADKIT_ANSIBLE_IDENTITY")
    fi
    
    if [ ${#missing[@]} -gt 0 ]; then
        error "Missing required environment variables:"
        for var in "${missing[@]}"; do
            echo "  - $var"
        done
        echo ""
        echo "Please set these variables and try again."
        exit 1
    fi
}

build_image() {
    log "Building Docker image: $IMAGE_NAME"
    cd "$PROJECT_ROOT"
    docker build -f tests/docker/Dockerfile -t "$IMAGE_NAME" .
    success "Docker image built successfully"
}

cleanup() {
    log "Cleaning up Docker resources..."
    
    # Stop and remove container if running
    if docker ps -q -f name="$CONTAINER_NAME" | grep -q .; then
        log "Stopping container: $CONTAINER_NAME"
        docker stop "$CONTAINER_NAME" >/dev/null 2>&1 || true
    fi
    
    if docker ps -aq -f name="$CONTAINER_NAME" | grep -q .; then
        log "Removing container: $CONTAINER_NAME"
        docker rm "$CONTAINER_NAME" >/dev/null 2>&1 || true
    fi
    
    # Optionally remove image
    if [ "$1" = "all" ]; then
        if docker images -q "$IMAGE_NAME" | grep -q .; then
            log "Removing image: $IMAGE_NAME"
            docker rmi "$IMAGE_NAME" >/dev/null 2>&1 || true
        fi
    fi
    
    success "Cleanup completed"
}

run_container() {
    local command="$1"
    local interactive_flags=""
    
    if [ "$INTERACTIVE" = "true" ]; then
        interactive_flags="-it"
    fi
    
    # Cleanup any existing container
    cleanup
    
    log "Starting container: $CONTAINER_NAME"
    
    # Check if certificates exist on host
    if [ ! -d "$HOME/.radkit/identities/prod.radkit-cloud.cisco.com" ]; then
        warn "RADKit certificates not found at $HOME/.radkit/identities/prod.radkit-cloud.cisco.com"
        warn "The SSH proxy may not work without proper certificates"
    fi
    
    docker run $interactive_flags --rm \
        --name "$CONTAINER_NAME" \
        -v "$HOME/.radkit:/root/.radkit:ro" \
        --tmpfs /root/.radkit/session_logs:rw \
        -e "RADKIT_ANSIBLE_SERVICE_SERIAL=$RADKIT_ANSIBLE_SERVICE_SERIAL" \
        -e "RADKIT_ANSIBLE_IDENTITY=$RADKIT_ANSIBLE_IDENTITY" \
        -e "RADKIT_ANSIBLE_CLIENT_PRIVATE_KEY_PASSWORD_BASE64=$RADKIT_ANSIBLE_CLIENT_PRIVATE_KEY_PASSWORD_BASE64" \
        -e "IOS_DEVICE_NAME_2=$TEST_DEVICE" \
        -e "TEST_DEVICE=$TEST_DEVICE" \
        "$IMAGE_NAME" \
        $command
}

test_ssh_proxy() {
    log "Running SSH proxy integration test for device: $TEST_DEVICE"
    
    local test_command="cd /root/.ansible/collections/ansible_collections/cisco/radkit && ansible-test integration ssh_proxy --color -v"
    
    if [ "$VERBOSE" = "true" ]; then
        test_command="$test_command -vv"
    fi
    
    run_container "$test_command"
}

test_local() {
    log "Running local SSH proxy test for device: $TEST_DEVICE"
    
    # Create inventory for container test
    local inventory_content="[radkit_devices]
$TEST_DEVICE ansible_host=127.0.0.1 ansible_password=radkit

[cisco_devices]
$TEST_DEVICE

[cisco_devices:vars]
ansible_ssh_common_args='-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null'"
    
    local test_command="cd /workspace && \
        echo '$inventory_content' > /tmp/test_inventory && \
        ansible-playbook -i /tmp/test_inventory tmp/ssh_proxy_integration_test.yml"
    
    if [ "$VERBOSE" = "true" ]; then
        test_command="$test_command -vvv"
    fi
    
    run_container "$test_command"
}

# Parse command line arguments
VERBOSE=false
INTERACTIVE=false
FORCE_BUILD=false
COMMAND="test-ssh-proxy"

while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            usage
            exit 0
            ;;
        -d|--device)
            TEST_DEVICE="$2"
            shift 2
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        --build)
            FORCE_BUILD=true
            shift
            ;;
        --interactive)
            INTERACTIVE=true
            shift
            ;;
        --clean)
            cleanup all
            exit 0
            ;;
        test-ssh-proxy|test-local|shell|clean)
            COMMAND="$1"
            shift
            ;;
        *)
            error "Unknown option: $1"
            usage
            exit 1
            ;;
    esac
done

# Main execution
log "=== Docker SSH Proxy Test Runner ==="
log "Device: $TEST_DEVICE"
log "Command: $COMMAND"

# Check environment variables
check_env

# Build image if needed
if [ "$FORCE_BUILD" = "true" ] || ! docker images -q "$IMAGE_NAME" | grep -q .; then
    build_image
fi

# Execute command
case $COMMAND in
    test-ssh-proxy)
        test_ssh_proxy
        ;;
    test-local)
        test_local
        ;;
    shell)
        INTERACTIVE=true
        run_container "/bin/bash"
        ;;
    clean)
        cleanup all
        ;;
    *)
        error "Unknown command: $COMMAND"
        exit 1
        ;;
esac

success "Operation completed"
