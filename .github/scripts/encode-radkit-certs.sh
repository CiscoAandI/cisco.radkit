#!/bin/bash
# Encode RADKit certificates to base64 for GitHub secrets
# Run this script locally to prepare your certificates for GitHub Actions

set -e

# Get the identity from command line or prompt
RADKIT_IDENTITY="${1:-}"
if [ -z "$RADKIT_IDENTITY" ]; then
    echo "🔍 Enter your RADKit identity (email):"
    read -r RADKIT_IDENTITY
fi

if [ -z "$RADKIT_IDENTITY" ]; then
    echo "❌ RADKit identity is required"
    exit 1
fi

# Define the certificate directory
RADKIT_IDENTITY_DIR="$HOME/.radkit/identities/prod.radkit-cloud.cisco.com/$RADKIT_IDENTITY"

echo "🔍 Looking for certificates in: $RADKIT_IDENTITY_DIR"

if [ ! -d "$RADKIT_IDENTITY_DIR" ]; then
    echo "❌ RADKit identity directory not found: $RADKIT_IDENTITY_DIR"
    echo "💡 Make sure you have logged into RADKit and have certificates downloaded"
    exit 1
fi

echo "📋 Found RADKit identity directory"

# Function to encode file to base64
encode_file() {
    local file_path="$1"
    local secret_name="$2"
    
    if [ -f "$file_path" ]; then
        local encoded
        encoded=$(base64 -i "$file_path")
        echo ""
        echo "🔑 $secret_name:"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo "$encoded"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo ""
    else
        echo "⚠️  File not found: $file_path"
    fi
}

echo ""
echo "🔐 Encoding RADKit certificates for GitHub secrets..."
echo "📧 Identity: $RADKIT_IDENTITY"
echo ""
echo "Copy these values to your GitHub repository secrets:"
echo "Settings → Secrets and variables → Actions → New repository secret"

# Encode each certificate file
encode_file "$RADKIT_IDENTITY_DIR/certificate.pem" "RADKIT_CERTIFICATE_BASE64"
encode_file "$RADKIT_IDENTITY_DIR/private_key_encrypted.pem" "RADKIT_PRIVATE_KEY_BASE64"
encode_file "$RADKIT_IDENTITY_DIR/chain.pem" "RADKIT_CHAIN_BASE64"

# Also encode the password if provided
echo ""
echo "🔑 Certificate Password Encoding:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "To encode your certificate password:"
echo "  echo -n 'your-password' | base64"
echo ""
echo "Set this as: RADKIT_CLIENT_PRIVATE_KEY_PASSWORD_BASE64"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

echo ""
echo "📋 Required GitHub Secrets Summary:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "1. RADKIT_CERTIFICATE_BASE64         - Certificate file"
echo "2. RADKIT_PRIVATE_KEY_BASE64          - Private key file"
echo "3. RADKIT_CHAIN_BASE64                - Certificate chain file"
echo "4. RADKIT_CLIENT_PRIVATE_KEY_PASSWORD_BASE64 - Certificate password"
echo "5. RADKIT_IDENTITY                    - Your email ($RADKIT_IDENTITY)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

echo ""
echo "✅ Certificate encoding complete!"
echo "💡 After setting GitHub secrets, your workflows will automatically set up the certificate paths"
