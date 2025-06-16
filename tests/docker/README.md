# Docker SSH Proxy Testing

This directory contains Docker-based testing infrastructure for the cisco.radkit SSH proxy functionality.

## Quick Start

1. **Set required environment variables:**
   ```bash
   export RADKIT_ANSIBLE_SERVICE_SERIAL="your-service-serial"
   export RADKIT_ANSIBLE_IDENTITY="your-identity"
   export RADKIT_ANSIBLE_CLIENT_PRIVATE_KEY_PASSWORD_BASE64="your-key-password-base64"
   ```

2. **Run the SSH proxy test:**
   ```bash
   ./tests/docker/run-ssh-proxy-test.sh
   ```

## Usage Examples

### Basic SSH Proxy Test
```bash
# Run integration test with default device
./tests/docker/run-ssh-proxy-test.sh

# Run with specific device
./tests/docker/run-ssh-proxy-test.sh -d your-device-name

# Run with verbose output
./tests/docker/run-ssh-proxy-test.sh -v
```

### Local Playbook Test
```bash
# Run the local playbook version
./tests/docker/run-ssh-proxy-test.sh test-local
```

### Interactive Testing
```bash
# Get interactive shell in container
./tests/docker/run-ssh-proxy-test.sh shell

# Run test interactively (see output in real-time)
./tests/docker/run-ssh-proxy-test.sh --interactive
```

### Docker Compose Alternative
```bash
# Using docker-compose
cd tests/docker
docker-compose up -d
docker-compose exec ssh-proxy-test /bin/bash

# Inside container:
cd /root/.ansible/collections/ansible_collections/cisco/radkit
ansible-test integration ssh_proxy --color -v
```

## Available Commands

- `test-ssh-proxy` (default) - Run the official integration test
- `test-local` - Run the local playbook version  
- `shell` - Start interactive shell
- `clean` - Clean up Docker resources

## Environment Variables

### Required
- `RADKIT_ANSIBLE_SERVICE_SERIAL` - Your RADKit service serial
- `RADKIT_ANSIBLE_IDENTITY` - Your RADKit identity
- `RADKIT_ANSIBLE_CLIENT_PRIVATE_KEY_PASSWORD_BASE64` - Client key password (base64)

### Optional
- `TEST_DEVICE` - Device name to test (default: test-device)
- `IOS_DEVICE_NAME_2` - Alternative device name variable

## Debugging

### Enable Verbose Output
```bash
./tests/docker/run-ssh-proxy-test.sh -v
```

### Manual Testing Inside Container
```bash
# Get shell access
./tests/docker/run-ssh-proxy-test.sh shell

# Inside container, you'll be in the collection directory by default:
# /root/.ansible/collections/ansible_collections/cisco/radkit

# Test just the SSH proxy module
ansible-test integration ssh_proxy --color -vvv

# Test local playbook (from workspace directory)
cd /workspace
ansible-playbook -i tmp/inventory tmp/ssh_proxy_integration_test.yml -vvv
```

### Compare with GitHub Actions Environment

This Docker environment closely mirrors the GitHub Actions environment by:
- Using the same Python version (3.11)
- Installing the same dependencies
- Using the same Ansible collection structure
- Including ansible-pylibssh

## Troubleshooting

### Container Won't Start
```bash
# Check if required env vars are set
echo $RADKIT_ANSIBLE_SERVICE_SERIAL
echo $RADKIT_ANSIBLE_IDENTITY

# Rebuild image
./tests/docker/run-ssh-proxy-test.sh --build
```

### SSH Proxy Connection Issues
```bash
# Test with maximum verbosity
./tests/docker/run-ssh-proxy-test.sh -v

# Check if device exists in RADKit inventory
# (this should be done outside the container)
```

### Clean Up
```bash
# Remove containers and images
./tests/docker/run-ssh-proxy-test.sh --clean
```

## Files

- `Dockerfile` - Container definition with all dependencies
- `run-ssh-proxy-test.sh` - Main test runner script
- `docker-compose.yml` - Alternative docker-compose setup
- `README.md` - This documentation
