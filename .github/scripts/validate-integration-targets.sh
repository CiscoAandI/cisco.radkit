#!/bin/bash

# Integration Test Targets Validation Script
# Validates the structure and readiness of all integration test targets

set -e

echo "🧪 Validating integration test targets..."
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Counters
target_count=0
valid_targets=0
issues_found=0

# Check if integration directory exists
if [ ! -d "tests/integration/targets" ]; then
    echo -e "${RED}❌ Integration targets directory not found: tests/integration/targets${NC}"
    exit 1
fi

echo -e "${BLUE}📁 Scanning integration test targets...${NC}"
echo ""

# Iterate through all target directories
for target_dir in tests/integration/targets/*/; do
    if [ -d "$target_dir" ]; then
        target_name=$(basename "$target_dir")
        echo -e "  → Found target: ${BLUE}$target_name${NC}"
        
        target_valid=true
        
        # Check if target has tasks/main.yml
        if [ -f "$target_dir/tasks/main.yml" ]; then
            echo -e "    ${GREEN}✅ Has tasks/main.yml${NC}"
        elif [ -f "$target_dir/tasks/main.yaml" ]; then
            echo -e "    ${GREEN}✅ Has tasks/main.yaml${NC}"
        else
            echo -e "    ${RED}❌ Missing tasks/main.yml${NC}"
            target_valid=false
            ((issues_found++))
        fi
        
        # Check if tasks file is valid YAML
        if [ -f "$target_dir/tasks/main.yml" ]; then
            if command -v python3 &> /dev/null; then
                if python3 -c "import yaml; yaml.safe_load(open('$target_dir/tasks/main.yml'))" 2>/dev/null; then
                    echo -e "    ${GREEN}✅ Valid YAML syntax${NC}"
                else
                    echo -e "    ${RED}❌ Invalid YAML syntax in tasks/main.yml${NC}"
                    target_valid=false
                    ((issues_found++))
                fi
            fi
        fi
        
        # Check for meta directory (optional but recommended)
        if [ -d "$target_dir/meta" ]; then
            echo -e "    ${GREEN}✅ Has meta directory${NC}"
        else
            echo -e "    ${YELLOW}⚠️  No meta directory (optional)${NC}"
        fi
        
        # Check for vars directory (optional)
        if [ -d "$target_dir/vars" ]; then
            echo -e "    ${GREEN}✅ Has vars directory${NC}"
        fi
        
        # Check for defaults directory (optional)
        if [ -d "$target_dir/defaults" ]; then
            echo -e "    ${GREEN}✅ Has defaults directory${NC}"
        fi
        
        # Check for README (optional but helpful)
        if [ -f "$target_dir/README.md" ] || [ -f "$target_dir/README.rst" ]; then
            echo -e "    ${GREEN}✅ Has README${NC}"
        fi
        
        # Count valid targets
        if [ "$target_valid" = true ]; then
            ((valid_targets++))
        fi
        
        ((target_count++))
        echo ""
    fi
done

echo -e "${BLUE}📊 Integration Test Summary${NC}"
echo "────────────────────────────────────"
echo -e "Total targets found: ${BLUE}$target_count${NC}"
echo -e "Valid targets: ${GREEN}$valid_targets${NC}"
echo -e "Issues found: ${RED}$issues_found${NC}"
echo ""

# Check for integration config template
if [ -f "tests/integration/integration_config.yml.template" ]; then
    echo -e "${GREEN}✅ Integration config template exists${NC}"
else
    echo -e "${YELLOW}⚠️  No integration config template found${NC}"
fi

# Check for integration requirements
if [ -f "tests/integration/requirements.txt" ]; then
    echo -e "${GREEN}✅ Integration requirements.txt exists${NC}"
else
    echo -e "${YELLOW}⚠️  No integration requirements.txt found${NC}"
fi

echo ""

# Final status
if [ $target_count -eq 0 ]; then
    echo -e "${RED}❌ No integration test targets found${NC}"
    exit 1
elif [ $issues_found -gt 0 ]; then
    echo -e "${YELLOW}⚠️  Integration tests have issues that should be addressed${NC}"
    echo -e "${YELLOW}   Consider fixing the issues above before running integration tests${NC}"
    exit 1
else
    echo -e "${GREEN}🎉 All integration test targets are valid and ready!${NC}"
fi

echo ""
echo -e "${BLUE}📋 Next steps:${NC}"
echo "  1. Configure integration_config.yml with your test environment"
echo "  2. Set up required GitHub secrets for CI/CD"
echo "  3. Run integration tests: make test-integration"
echo ""
