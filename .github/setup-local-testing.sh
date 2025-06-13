#!/bin/bash
# Script to set up local integration testing configuration
# This helps developers set up their local environment securely

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
INTEGRATION_DIR="$PROJECT_ROOT/tests/integration"
CONFIG_FILE="$INTEGRATION_DIR/integration_config.yml"
TEMPLATE_FILE="$INTEGRATION_DIR/integration_config.yml.template"

echo "🔧 Setting up local integration test configuration..."

# Check if config already exists
if [ -f "$CONFIG_FILE" ]; then
    echo "⚠️  integration_config.yml already exists."
    read -p "Do you want to overwrite it? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "❌ Setup cancelled."
        exit 0
    fi
fi

# Create config from template
if [ ! -f "$TEMPLATE_FILE" ]; then
    echo "❌ Template file not found: $TEMPLATE_FILE"
    exit 1
fi

cp "$TEMPLATE_FILE" "$CONFIG_FILE"
echo "✅ Created integration_config.yml from template"

# Make sure it's in .gitignore
GITIGNORE_FILE="$PROJECT_ROOT/.gitignore"
if ! grep -q "integration_config.yml" "$GITIGNORE_FILE" 2>/dev/null; then
    echo "" >> "$GITIGNORE_FILE"
    echo "# Integration test secrets (local only)" >> "$GITIGNORE_FILE"
    echo "tests/integration/integration_config.yml" >> "$GITIGNORE_FILE"
    echo "✅ Added integration_config.yml to .gitignore"
fi

echo ""
echo "📝 Next steps:"
echo "1. Edit $CONFIG_FILE"
echo "2. Replace all '<...>' placeholders with your actual values"
echo "3. For base64 password encoding, use: echo -n 'your-password' | base64"
echo ""
echo "🔒 Certificate setup:"
echo "- Your RADKit certificates should be in: ~/.radkit/identities/prod.radkit-cloud.cisco.com/[your-email]"
echo "- Test certificate setup: .github/scripts/test-radkit-setup.sh"
echo "- Encode for GitHub: .github/scripts/encode-radkit-certs.sh"
echo ""
echo "🔒 Security reminders:"
echo "- NEVER commit integration_config.yml with real values"
echo "- The file is now in .gitignore to prevent accidental commits"
echo "- For CI/CD, set these values as GitHub repository secrets"
echo ""
echo "🧪 To run integration tests locally:"
echo "cd tests/integration && ansible-test integration"
