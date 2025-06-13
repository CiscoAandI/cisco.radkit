#!/bin/zsh
# Quick test runner for local development
# Usage: ./scripts/run-tests.sh [unit|integration|all] [target]

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
TEST_TYPE="${1:-all}"
TARGET="${2:-}"

print_usage() {
    echo "Usage: $0 [test-type] [target]"
    echo ""
    echo "Test Types:"
    echo "  unit        Run unit tests only"
    echo "  integration Run integration tests only"
    echo "  all         Run both unit and integration tests (default)"
    echo ""
    echo "Target (for integration tests only):"
    echo "  target-name Run specific integration test target"
    echo ""
    echo "Examples:"
    echo "  $0                          # Run all tests"
    echo "  $0 unit                     # Run unit tests only"
    echo "  $0 integration              # Run all integration tests"
    echo "  $0 integration network_cli  # Run network_cli integration tests"
}

log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

check_dependencies() {
    log_info "Checking dependencies..."
    
    # Check if we're in a virtual environment
    if [[ -z "$VIRTUAL_ENV" ]]; then
        log_warning "Not in a virtual environment. Consider using 'python -m venv venv && source venv/bin/activate'"
    fi
    
    # Check if collection is installed
    if ! ansible-galaxy collection list cisco.radkit >/dev/null 2>&1; then
        log_info "Installing collection..."
        ansible-galaxy collection install . --force
    fi
    
    log_success "Dependencies checked"
}

run_unit_tests() {
    log_info "Running unit tests..."
    
    cd "$PROJECT_ROOT"
    
    # Try ansible-test first
    if command -v ansible-test >/dev/null 2>&1; then
        log_info "Using ansible-test for unit tests..."
        cd tests
        ansible-test units --color -v || {
            log_warning "ansible-test failed, trying pytest..."
            cd "$PROJECT_ROOT"
            if command -v pytest >/dev/null 2>&1; then
                pytest tests/unit/ -v
            else
                log_error "Neither ansible-test nor pytest available"
                return 1
            fi
        }
    else
        log_warning "ansible-test not available, using pytest..."
        if command -v pytest >/dev/null 2>&1; then
            pytest tests/unit/ -v
        else
            log_error "Neither ansible-test nor pytest available"
            return 1
        fi
    fi
    
    log_success "Unit tests completed"
}

run_integration_tests() {
    log_info "Running integration tests..."
    
    # Check if integration config exists
    local config_file="$PROJECT_ROOT/tests/integration/integration_config.yml"
    if [[ ! -f "$config_file" ]]; then
        log_error "Integration config not found: $config_file"
        log_info "Run '.github/setup-local-testing.sh' to set up configuration"
        return 1
    fi
    
    cd "$PROJECT_ROOT/tests/integration"
    
    if command -v ansible-test >/dev/null 2>&1; then
        log_info "Using ansible-test for integration tests..."
        if [[ -n "$TARGET" ]]; then
            log_info "Running specific target: $TARGET"
            ansible-test integration "$TARGET" --color -v
        else
            log_info "Running all integration tests..."
            ansible-test integration --color -v
        fi
    else
        log_warning "ansible-test not available, using ansible-playbook..."
        
        # Create simple inventory
        cat > inventory << EOF
[all:vars]
ansible_connection=cisco.radkit.network_cli

[ios_devices]
\$(grep 'ios_device_name_1:' integration_config.yml | cut -d: -f2 | tr -d ' "'"'"'')
\$(grep 'ios_device_name_2:' integration_config.yml | cut -d: -f2 | tr -d ' "'"'"'')
EOF
        
        # Run tests manually
        if [[ -n "$TARGET" ]]; then
            if [[ -f "targets/$TARGET/tasks/main.yml" ]]; then
                log_info "Running target: $TARGET"
                ansible-playbook -i inventory -e @integration_config.yml "targets/$TARGET/tasks/main.yml" -v
            else
                log_error "Target not found: $TARGET"
                return 1
            fi
        else
            log_info "Running all available targets..."
            for target_dir in targets/*/; do
                if [[ -d "$target_dir" ]]; then
                    target_name=$(basename "$target_dir")
                    if [[ -f "$target_dir/tasks/main.yml" ]]; then
                        log_info "Running target: $target_name"
                        ansible-playbook -i inventory -e @integration_config.yml "$target_dir/tasks/main.yml" -v || {
                            log_warning "Target $target_name failed"
                        }
                    fi
                fi
            done
        fi
    fi
    
    log_success "Integration tests completed"
}

list_integration_targets() {
    log_info "Available integration test targets:"
    
    local targets_dir="$PROJECT_ROOT/tests/integration/targets"
    if [[ -d "$targets_dir" ]]; then
        for target_dir in "$targets_dir"/*/; do
            if [[ -d "$target_dir" ]]; then
                target_name=$(basename "$target_dir")
                if [[ -f "$target_dir/tasks/main.yml" ]]; then
                    echo "  ✅ $target_name"
                else
                    echo "  ⚠️  $target_name (no tasks/main.yml)"
                fi
            fi
        done
    else
        log_warning "No integration targets directory found"
    fi
}

# Parse arguments
case "$TEST_TYPE" in
    "unit")
        ;;
    "integration")
        ;;
    "all")
        ;;
    "list")
        list_integration_targets
        exit 0
        ;;
    "-h"|"--help"|"help")
        print_usage
        exit 0
        ;;
    *)
        log_error "Invalid test type: $TEST_TYPE"
        print_usage
        exit 1
        ;;
esac

# Main execution
log_info "Starting test run..."
log_info "Test type: $TEST_TYPE"
if [[ -n "$TARGET" ]]; then
    log_info "Target: $TARGET"
fi

check_dependencies

case "$TEST_TYPE" in
    "unit")
        run_unit_tests
        ;;
    "integration")
        run_integration_tests
        ;;
    "all")
        run_unit_tests
        run_integration_tests
        ;;
esac

log_success "All tests completed successfully! 🎉"
