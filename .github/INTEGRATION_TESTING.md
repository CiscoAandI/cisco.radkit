# Integration Tests Setup Guide

This guide explains how to set up and run integration tests for the cisco.radkit Ansible collection, including secure secret management for both local development and CI/CD.

## 🔐 Security Overview

**NEVER commit secrets to the repository!** This setup ensures:
- Local secrets stay on your machine
- CI/CD secrets are stored securely in GitHub
- Certificate files are properly ignored
- Configuration templates help team members set up quickly

## 🚀 Quick Setup

### For Local Development

1. **Run the setup script:**
   ```bash
   .github/setup-local-testing.sh
   ```

2. **Edit the configuration file:**
   ```bash
   vim tests/integration/integration_config.yml
   ```

3. **Replace all placeholders with your actual values:**
   ```yaml
   ios_device_name_1: 'your-actual-device-name'
   radkit_service_serial: 'your-actual-serial'
   radkit_identity: 'your-email@cisco.com'
   # etc.
   ```

4. **Encode your certificate password:**
   ```bash
   echo -n "your-password" | base64
   ```

### For GitHub Actions CI/CD

1. **Go to your repository Settings → Secrets and variables → Actions**

2. **Add these repository secrets:**
   - `IOS_DEVICE_NAME_1`
   - `IOS_DEVICE_NAME_2` 
   - `LINUX_DEVICE_NAME_1`
   - `HTTP_DEVICE_NAME_1`
   - `SWAGGER_DEVICE_NAME_1`
   - `IOS_DEVICE_NAME_PREFIX`
   - `RADKIT_SERVICE_SERIAL`
   - `RADKIT_IDENTITY`
   - `RADKIT_CLIENT_PRIVATE_KEY_PASSWORD_BASE64`

## 🧪 Running Tests

### Local Integration Tests
```bash
# Run all integration tests
cd tests/integration
ansible-test integration

# Run specific test target
ansible-test integration network_cli

# Run with more verbosity
ansible-test integration -vvv
```

### GitHub Actions
- **Automatic**: Tests run on every PR and push to main
- **Manual**: Use "Run workflow" in Actions tab
- **Specific target**: Use workflow dispatch with target parameter

## 📁 Project Structure

```
tests/
├── integration/
│   ├── integration_config.yml          # Your local secrets (git-ignored)
│   ├── integration_config.yml.template # Template for team members
│   └── targets/                        # Test scenarios
│       ├── network_cli/
│       ├── terminal/
│       ├── command/
│       └── ...
├── unit/                               # Unit tests
└── requirements.txt                    # Test dependencies
```

## 🛠️ GitHub Actions Workflows

### 1. `integration-tests.yml`
- **Triggers**: PR/push to main, manual dispatch
- **Matrix**: Python 3.9, 3.11 × Multiple Ansible versions
- **Features**:
  - Secure secret injection from GitHub secrets
  - Multiple test execution strategies
  - Artifact upload for debugging
  - Fallback testing methods

### 2. `unit-tests.yml`
- **Triggers**: PR/push when code changes
- **Matrix**: Python 3.9-3.12 × Multiple Ansible versions
- **Features**:
  - Code coverage reporting
  - Pytest and ansible-test support
  - Codecov integration

## 🔧 Configuration Details

### Required Secrets

| Secret Name | Description | Example |
|-------------|-------------|---------|
| `IOS_DEVICE_NAME_1` | Primary IOS device | `xxx-csr2` |
| `IOS_DEVICE_NAME_2` | Secondary IOS device | `xxx-csr1` |
| `LINUX_DEVICE_NAME_1` | Linux device for SSH tests | `dxx` |
| `HTTP_DEVICE_NAME_1` | HTTP API device | `sandboxdnac` |
| `SWAGGER_DEVICE_NAME_1` | Swagger API device | `sandbox-sdwan-2` |
| `RADKIT_SERVICE_SERIAL` | RADKit service serial | `xxx-xxxx-xxxx` |
| `RADKIT_IDENTITY` | Your RADKit identity | `you@cisco.com` |
| `RADKIT_CLIENT_PRIVATE_KEY_PASSWORD_BASE64` | Base64 encoded cert password | `xxxxxxxxx` |

### Certificate Files
If you need certificate files in CI/CD:
1. Base64 encode them: `base64 -w 0 cert.pem`
2. Store as secrets: `RADKIT_CLIENT_CERT_BASE64`
3. Decode in workflow: `echo "${{ secrets.RADKIT_CLIENT_CERT_BASE64 }}" | base64 -d > cert.pem`

## 🐛 Troubleshooting

### Local Issues
```bash
# Check configuration
cat tests/integration/integration_config.yml

# Verify Ansible can see the collection
ansible-galaxy collection list cisco.radkit

# Test individual targets
ansible-test integration network_cli -v
```

### GitHub Actions Issues
1. **Missing secrets**: Check repository secrets are set
2. **Connection failures**: Verify device names and credentials
3. **Test failures**: Check uploaded artifacts for detailed logs

### Common Problems

| Problem | Solution |
|---------|----------|
| "integration_config.yml not found" | Run `.github/setup-local-testing.sh` |
| "Certificate authentication failed" | Check base64 encoding of password |
| "Device not found" | Verify device names in RADKit portal |
| "Permission denied" | Check certificate file permissions |

## 📊 Test Coverage

The workflows test:
- ✅ Network CLI connections
- ✅ Terminal connections  
- ✅ Command execution
- ✅ File operations
- ✅ HTTP/API connections
- ✅ SNMP operations
- ✅ Port forwarding
- ✅ Multiple Python/Ansible versions

## 🚨 Security Checklist

- [ ] `integration_config.yml` is in `.gitignore`
- [ ] No secrets in code or commits
- [ ] GitHub secrets are properly set
- [ ] Certificate files are not in repository
- [ ] Local config file has proper permissions (600)
- [ ] Team members have access to secrets template

## 🔄 Workflow Features

### Advanced Options
- **Manual dispatch**: Run specific tests on demand
- **Verbosity control**: Adjust logging level (0-3)
- **Target selection**: Run individual test suites
- **Fallback execution**: Multiple test execution strategies
- **Artifact collection**: Logs and results for debugging

### Matrix Testing
Tests run across combinations of:
- Python versions: 3.9, 3.11
- Ansible versions: 6.x, 7.x, 8.x
- This ensures compatibility across environments

## 📞 Getting Help

1. **Check the logs**: GitHub Actions → Failed run → View logs
2. **Download artifacts**: Failed runs upload debug information
3. **Run locally**: Reproduce issues on your development machine
4. **Check secrets**: Verify all required secrets are set correctly

---

**Remember**: Keep your secrets secret! 🔐
