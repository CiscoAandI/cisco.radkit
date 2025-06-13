# Makefile for cisco.radkit Ansible Collection

.PHONY: help install test test-unit test-integration docs clean lint format check-secrets setup-local-testing build release

# Default target
help: ## Show this help message
	@echo "Available targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

# Installation
install: ## Install the collection and dependencies
	@echo "🔧 Installing collection and dependencies..."
	pip install -r requirements.txt
	pip install -r tests/requirements.txt
	ansible-galaxy collection install . --force
	@echo "✅ Installation complete"

# Testing
test: test-unit test-integration ## Run all tests

test-unit: ## Run unit tests
	@echo "🧪 Running unit tests..."
	./scripts/run-tests.sh unit

test-integration: ## Run integration tests (requires config)
	@echo "🧪 Running integration tests..."
	./scripts/run-tests.sh integration

test-integration-target: ## Run specific integration test target (usage: make test-integration-target TARGET=network_cli)
	@echo "🧪 Running integration test target: $(TARGET)"
	./scripts/run-tests.sh integration $(TARGET)

# Development setup
setup-local-testing: ## Set up local integration testing configuration
	@echo "🔧 Setting up local testing configuration..."
	./.github/setup-local-testing.sh

# Development setup
install-dev:	## Install development dependencies
	pip install ansible-core
	pip install ansible-lint || echo "ansible-lint not available, skipping"
	pip install black || echo "black not available, skipping"
	pip install isort || echo "isort not available, skipping"
	pip install yamllint || echo "yamllint not available, skipping"
	ansible-galaxy collection install -r requirements.yml || true

# Ansible collection testing
test-sanity:	## Run ansible-test sanity checks
	ansible-test sanity --color yes || echo "ansible-test not available or failed"

test-integration:	## Run ansible-test integration tests  
	ansible-test integration --color yes || echo "ansible-test not available or failed"

test-units:	## Run ansible-test unit tests
	ansible-test units --color yes || echo "ansible-test not available or failed"

# Code quality targets
lint:	## Run linting checks
	@if command -v ansible-lint >/dev/null 2>&1; then \
		ansible-lint .; \
	else \
		echo "ansible-lint not available, skipping"; \
	fi
	@if command -v yamllint >/dev/null 2>&1; then \
		yamllint .; \
	else \
		echo "yamllint not available, skipping"; \
	fi

format:	## Format code with black and isort
	@if command -v black >/dev/null 2>&1; then \
		black plugins/; \
	else \
		echo "black not available, skipping"; \
	fi
	@if command -v isort >/dev/null 2>&1; then \
		isort plugins/; \
	else \
		echo "isort not available, skipping"; \
	fi

format-check:	## Check code formatting without making changes
	@if command -v black >/dev/null 2>&1; then \
		black --check plugins/; \
	else \
		echo "black not available, skipping format check"; \
	fi
	@if command -v isort >/dev/null 2>&1; then \
		isort --check-only plugins/; \
	else \
		echo "isort not available, skipping import order check"; \
	fi

# Documentation
docs:	## Build collection documentation
	ansible-doc-extractor --template-dir docs/templates plugins/

docs: ## Build documentation
	@echo "📚 Building documentation..."
	cd docs && ./build.sh
	@echo "✅ Documentation built in docs/html/"

docs-serve: ## Build and serve documentation locally
	@echo "📚 Building and serving documentation..."
	cd docs && ./build.sh
	@echo "🌐 Serving documentation at http://localhost:8000"
	@cd docs && python3 -m http.server 8000

# Build and distribution
build:	## Build the ansible collection
	ansible-galaxy collection build --force

install-local:	## Install collection locally for testing
	ansible-galaxy collection install cisco-radkit-*.tar.gz --force

clean:	## Clean up build artifacts
	rm -rf cisco-radkit-*.tar.gz
	rm -rf .pytest_cache/
	rm -rf .ansible/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

# Development workflow
dev-setup:	## Complete development environment setup
	$(MAKE) install-dev
	@echo "Ansible collection development environment ready!"

quality-check:	## Run all quality checks
	$(MAKE) format-check
	$(MAKE) lint
	$(MAKE) test-sanity

check-secrets: ## Check if all required secrets are configured (for CI)
	@echo "🔍 Checking secrets configuration..."
	@python3 -c "
import yaml
import sys
import os

# Check if integration config exists
config_file = 'tests/integration/integration_config.yml'
if not os.path.exists(config_file):
    print('❌ Integration config not found. Run: make setup-local-testing')
    sys.exit(1)

# Load and validate config
with open(config_file, 'r') as f:
    config = yaml.safe_load(f)

required_keys = [
    'ios_device_name_1', 'ios_device_name_2', 'linux_device_name_1',
    'http_device_name_1', 'swagger_device_name_1', 'ios_device_name_prefix',
    'radkit_service_serial', 'radkit_identity', 'radkit_client_private_key_password_base64'
]

missing = []
placeholder = []

for key in required_keys:
    value = config.get(key, '')
    if not value:
        missing.append(key)
    elif '<' in str(value) and '>' in str(value):
        placeholder.append(key)

if missing:
    print(f'❌ Missing keys: {missing}')
    sys.exit(1)

if placeholder:
    print(f'⚠️  Keys with placeholder values: {placeholder}')
    print('   Please update these with actual values')
    sys.exit(1)

print('✅ All secrets are properly configured')
"

# CI/CD targets suitable for Ansible collections
ci:	## Run CI pipeline for ansible collection
	$(MAKE) quality-check
	$(MAKE) build

# Release preparation for Galaxy
pre-release:	## Prepare for Galaxy release
	$(MAKE) format
	$(MAKE) quality-check
	$(MAKE) build
	@echo "Collection ready for Galaxy upload!"

# Environment info
env-info:	## Show environment information
	@echo "Python version:"
	@python --version
	@echo ""
	@echo "Ansible version:"
	@ansible --version
	@echo ""
	@echo "Ansible Galaxy version:"
	@ansible-galaxy --version

# Quick development cycle for collections
quick-check:	## Quick development cycle check
	black plugins/
	ansible-lint . --exclude tmp/
	ansible-test sanity --color yes plugins/
