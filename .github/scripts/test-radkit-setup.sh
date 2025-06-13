#!/bin/bash
# Test the RADKit certificate setup locally
# This script helps verify your certificates are working before pushing to GitHub

set -e

echo "🧪 Testing RADKit certificate setup..."

# Check if identity is provided
RADKIT_IDENTITY="${1:-scdozier@cisco.com}"
echo "📧 Testing with identity: $RADKIT_IDENTITY"

# Check local certificate directory
RADKIT_IDENTITY_DIR="$HOME/.radkit/identities/prod.radkit-cloud.cisco.com/$RADKIT_IDENTITY"

if [ ! -d "$RADKIT_IDENTITY_DIR" ]; then
    echo "❌ RADKit identity directory not found: $RADKIT_IDENTITY_DIR"
    echo "💡 Make sure you have logged into RADKit and have certificates downloaded"
    exit 1
fi

echo "✅ Found RADKit identity directory"

# Check required files
check_file() {
    local file_path="$1"
    local file_name="$2"
    
    if [ -f "$file_path" ]; then
        echo "✅ $file_name exists"
        echo "   📄 Path: $file_path"
        echo "   📊 Size: $(du -h "$file_path" | cut -f1)"
        
        # Check file permissions
        local perms
        perms=$(stat -f "%OLp" "$file_path" 2>/dev/null || stat -c "%a" "$file_path" 2>/dev/null || echo "unknown")
        echo "   🔒 Permissions: $perms"
        
        return 0
    else
        echo "❌ $file_name missing: $file_path"
        return 1
    fi
}

echo ""
echo "📋 Checking certificate files..."
check_file "$RADKIT_IDENTITY_DIR/certificate.pem" "Certificate"
check_file "$RADKIT_IDENTITY_DIR/private_key_encrypted.pem" "Private Key"
check_file "$RADKIT_IDENTITY_DIR/chain.pem" "Certificate Chain"

echo ""
echo "🔑 Testing base64 encoding (for GitHub secrets)..."

# Test encoding the certificates
if [ -f "$RADKIT_IDENTITY_DIR/certificate.pem" ]; then
    cert_size=$(base64 -i "$RADKIT_IDENTITY_DIR/certificate.pem" | wc -c | tr -d ' ')
    echo "✅ Certificate encodes to $cert_size base64 characters"
fi

if [ -f "$RADKIT_IDENTITY_DIR/private_key_encrypted.pem" ]; then
    key_size=$(base64 -i "$RADKIT_IDENTITY_DIR/private_key_encrypted.pem" | wc -c | tr -d ' ')
    echo "✅ Private key encodes to $key_size base64 characters"
fi

if [ -f "$RADKIT_IDENTITY_DIR/chain.pem" ]; then
    chain_size=$(base64 -i "$RADKIT_IDENTITY_DIR/chain.pem" | wc -c | tr -d ' ')
    echo "✅ Chain encodes to $chain_size base64 characters"
fi

echo ""
echo "🧪 Testing certificate password encoding..."
echo "💡 To test your password encoding:"
echo "   echo -n 'your-password' | base64"
echo "   # This should match your RADKIT_CLIENT_PRIVATE_KEY_PASSWORD_BASE64 secret"

echo ""
echo "📂 Expected GitHub Actions paths:"
echo "   CA Path: $RADKIT_IDENTITY_DIR/ca.pem"
echo "   Key Path: $RADKIT_IDENTITY_DIR/private_key_encrypted.pem"
echo "   Cert Path: $RADKIT_IDENTITY_DIR/certificate.pem"

echo ""
echo "✅ Certificate setup test complete!"
echo ""
echo "🚀 Next steps:"
echo "1. Run: .github/scripts/encode-radkit-certs.sh $RADKIT_IDENTITY"
echo "2. Copy the base64 values to GitHub secrets"
echo "3. Set RADKIT_IDENTITY secret to: $RADKIT_IDENTITY"
echo "4. Push changes to trigger GitHub Actions"
