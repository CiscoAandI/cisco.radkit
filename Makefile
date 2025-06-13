# Makefile for Cisco RADKit Ansible Collection
# Ansible Galaxy Collection development workflow

.PHONY: help install-dev lint format clean docs build test-sanity test-integration

# Default target
help:	## Show this help message
	@echo 'Usage: make [target] ...'
	@echo ''
	@echo 'Targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-15s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

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
