# Integration Tests Configuration Template
# 
# This file shows how to configure secrets for integration tests.
# DO NOT commit the actual integration_config.yml with real values!

# For local development, copy this template to integration_config.yml
# and fill in your actual values.

# For GitHub Actions, set these as repository secrets:
# Go to Settings → Secrets and variables → Actions → New repository secret

# Device Names (use your actual RADKit device names)
IOS_DEVICE_NAME_1: 'your-ios-device-1'          # → Set as secret: IOS_DEVICE_NAME_1
IOS_DEVICE_NAME_2: 'your-ios-device-2'          # → Set as secret: IOS_DEVICE_NAME_2
LINUX_DEVICE_NAME_1: 'your-linux-device'       # → Set as secret: LINUX_DEVICE_NAME_1
HTTP_DEVICE_NAME_1: 'your-http-device'          # → Set as secret: HTTP_DEVICE_NAME_1
SWAGGER_DEVICE_NAME_1: 'your-swagger-device'    # → Set as secret: SWAGGER_DEVICE_NAME_1
IOS_DEVICE_NAME_PREFIX: 'your-device-prefix'    # → Set as secret: IOS_DEVICE_NAME_PREFIX

# RADKit Configuration
RADKIT_SERVICE_SERIAL: 'your-service-serial'    # → Set as secret: RADKIT_SERVICE_SERIAL
RADKIT_IDENTITY: 'your-email@cisco.com'         # → Set as secret: RADKIT_IDENTITY

# Certificate Password (base64 encoded)
# To encode your password: echo -n "your-password" | base64
RADKIT_CLIENT_PRIVATE_KEY_PASSWORD_BASE64: 'base64-encoded-password'  # → Set as secret: RADKIT_CLIENT_PRIVATE_KEY_PASSWORD_BASE64

# RADKit Certificate Files (base64 encoded)
# Use the script to encode your certificates: .github/scripts/encode-radkit-certs.sh
RADKIT_CERTIFICATE_BASE64: 'base64-certificate'     # → Set as secret: RADKIT_CERTIFICATE_BASE64
RADKIT_PRIVATE_KEY_BASE64: 'base64-private-key'     # → Set as secret: RADKIT_PRIVATE_KEY_BASE64
RADKIT_CHAIN_BASE64: 'base64-chain'                 # → Set as secret: RADKIT_CHAIN_BASE64

# Environment Variables for RADKit (automatically set by GitHub Actions)
# These will be set automatically based on your RADKIT_IDENTITY:
# - RADKIT_ANSIBLE_CLIENT_CA_PATH
# - RADKIT_ANSIBLE_CLIENT_KEY_PATH
# - RADKIT_ANSIBLE_CLIENT_CERT_PATH
