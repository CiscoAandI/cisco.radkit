#!/bin/bash
# Setup RADKit certificates for GitHub Actions
# This script creates the RADKit certificate directory structure and files from GitHub secrets

set -e

echo "🔧 Setting up RADKit certificates from GitHub secrets..."

# Get the identity from environment or config
RADKIT_IDENTITY="${RADKIT_IDENTITY:-}"
if [ -z "$RADKIT_IDENTITY" ]; then
    echo "❌ RADKIT_IDENTITY environment variable not set"
    exit 1
fi

# Create the RADKit directory structure
RADKIT_BASE_DIR="$HOME/.radkit/identities/prod.radkit-cloud.cisco.com"
RADKIT_IDENTITY_DIR="$RADKIT_BASE_DIR/$RADKIT_IDENTITY"

echo "📁 Creating RADKit directory: $RADKIT_IDENTITY_DIR"
mkdir -p "$RADKIT_IDENTITY_DIR"

# Create certificate files from base64 encoded secrets
if [ -n "$RADKIT_CERTIFICATE_BASE64" ]; then
    echo "📄 Creating certificate.pem..."
    echo "$RADKIT_CERTIFICATE_BASE64" | base64 -d > "$RADKIT_IDENTITY_DIR/certificate.pem"
    chmod 644 "$RADKIT_IDENTITY_DIR/certificate.pem"
else
    echo "⚠️  RADKIT_CERTIFICATE_BASE64 not provided"
fi

if [ -n "$RADKIT_PRIVATE_KEY_BASE64" ]; then
    echo "🔑 Creating private_key_encrypted.pem..."
    echo "$RADKIT_PRIVATE_KEY_BASE64" | base64 -d > "$RADKIT_IDENTITY_DIR/private_key_encrypted.pem"
    chmod 600 "$RADKIT_IDENTITY_DIR/private_key_encrypted.pem"
else
    echo "⚠️  RADKIT_PRIVATE_KEY_BASE64 not provided"
fi

if [ -n "$RADKIT_CHAIN_BASE64" ]; then
    echo "🔗 Creating chain.pem..."
    echo "$RADKIT_CHAIN_BASE64" | base64 -d > "$RADKIT_IDENTITY_DIR/chain.pem"
    chmod 644 "$RADKIT_IDENTITY_DIR/chain.pem"
else
    echo "⚠️  RADKIT_CHAIN_BASE64 not provided"
fi

# Set up CA file (chain.pem is typically used as CA)
if [ -f "$RADKIT_IDENTITY_DIR/chain.pem" ]; then
    cp "$RADKIT_IDENTITY_DIR/chain.pem" "$RADKIT_IDENTITY_DIR/ca.pem"
    echo "📋 Created ca.pem from chain.pem"
fi

# Verify files were created
echo "✅ RADKit certificate setup complete!"
echo "📂 Certificate directory: $RADKIT_IDENTITY_DIR"
echo "📋 Files created:"
ls -la "$RADKIT_IDENTITY_DIR/" || echo "❌ Directory not accessible"

# Export paths for use in environment variables
echo "🔗 Setting environment variables..."
export RADKIT_ANSIBLE_CLIENT_CA_PATH="$RADKIT_IDENTITY_DIR/ca.pem"
export RADKIT_ANSIBLE_CLIENT_KEY_PATH="$RADKIT_IDENTITY_DIR/private_key_encrypted.pem"
export RADKIT_ANSIBLE_CLIENT_CERT_PATH="$RADKIT_IDENTITY_DIR/certificate.pem"

echo "RADKIT_ANSIBLE_CLIENT_CA_PATH=$RADKIT_ANSIBLE_CLIENT_CA_PATH" >> "$GITHUB_ENV"
echo "RADKIT_ANSIBLE_CLIENT_KEY_PATH=$RADKIT_ANSIBLE_CLIENT_KEY_PATH" >> "$GITHUB_ENV"
echo "RADKIT_ANSIBLE_CLIENT_CERT_PATH=$RADKIT_ANSIBLE_CLIENT_CERT_PATH" >> "$GITHUB_ENV"

echo "✅ Environment variables set for GitHub Actions"
