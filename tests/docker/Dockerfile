# Dockerfile for testing cisco.radkit SSH proxy in a containerized environment
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    openssh-client \
    sshpass \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /workspace

# Copy requirements first for better caching
COPY requirements.txt tests/requirements.txt ./
COPY tests/requirements.txt tests/

# Install Python dependencies
RUN pip install --upgrade pip && \
    pip install -r requirements.txt && \
    pip install -r tests/requirements.txt && \
    pip install ansible-pylibssh

# Install required Ansible collections
RUN ansible-galaxy collection install cisco.ios && \
    ansible-galaxy collection install community.general && \
    ansible-galaxy collection install ansible.netcommon

# Copy the entire collection
COPY . .

# Install the collection in the proper structure
RUN mkdir -p /root/.ansible/collections/ansible_collections/cisco/radkit && \
    cp -r . /root/.ansible/collections/ansible_collections/cisco/radkit/

# Create RADKit certificates directory
RUN mkdir -p /root/.radkit/identities/prod.radkit-cloud.cisco.com/scdozier@cisco.com/

# Set up ansible.cfg
RUN echo '[defaults]\n\
host_key_checking = False\n\
timeout = 60\n\
gathering = explicit\n\
interpreter_python = auto_silent\n\
\n\
[connection]\n\
pipelining = True\n\
\n\
[inventory]\n\
host_pattern_mismatch = ignore' > /root/.ansible.cfg

# Create entrypoint script
RUN echo '#!/bin/bash\n\
set -e\n\
\n\
echo "=== Docker SSH Proxy Test Environment ==="\n\
echo "Python version: $(python --version)"\n\
echo "Ansible version: $(ansible --version | head -1)"\n\
echo "ansible-pylibssh installed: $(pip show ansible-pylibssh > /dev/null 2>&1 && echo "Yes" || echo "No")"\n\
echo ""\n\
\n\
# Check for required environment variables\n\
if [ -z "$RADKIT_ANSIBLE_SERVICE_SERIAL" ]; then\n\
    echo "ERROR: RADKIT_ANSIBLE_SERVICE_SERIAL environment variable is required"\n\
    exit 1\n\
fi\n\
\n\
if [ -z "$RADKIT_ANSIBLE_IDENTITY" ]; then\n\
    echo "ERROR: RADKIT_ANSIBLE_IDENTITY environment variable is required"\n\
    exit 1\n\
fi\n\
\n\
# Create integration config\n\
mkdir -p /root/.ansible/collections/ansible_collections/cisco/radkit/tests/integration\n\
cat > /root/.ansible/collections/ansible_collections/cisco/radkit/tests/integration/integration_config.yml << EOF\n\
ios_device_name_1: "${IOS_DEVICE_NAME_1:-daa-csr2}"\n\
ios_device_name_2: "${IOS_DEVICE_NAME_2:-daa-csr1}"\n\
linux_device_name_1: "${LINUX_DEVICE_NAME_1:-daa-bastion}"\n\
http_device_name_1: "${HTTP_DEVICE_NAME_1:-sandboxdnac}"\n\
swagger_device_name_1: "${SWAGGER_DEVICE_NAME_1:-sandbox-sdwan-2}"\n\
ios_device_name_prefix: "${IOS_DEVICE_NAME_PREFIX:-daa-csr}"\n\
radkit_service_serial: "${RADKIT_ANSIBLE_SERVICE_SERIAL}"\n\
radkit_identity: "${RADKIT_ANSIBLE_IDENTITY}"\n\
radkit_client_private_key_password_base64: "${RADKIT_ANSIBLE_CLIENT_PRIVATE_KEY_PASSWORD_BASE64}"\n\
EOF\n\
\n\
echo "Integration config created"\n\
echo "Running command: $@"\n\
\n\
# Change to the collection directory by default\n\
cd /root/.ansible/collections/ansible_collections/cisco/radkit\n\
\n\
# If no arguments provided, start bash\n\
if [ $# -eq 0 ]; then\n\
    exec /bin/bash\n\
else\n\
    # Execute the command in bash\n\
    exec /bin/bash -c "$*"\n\
fi' > /entrypoint.sh && chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
CMD ["/bin/bash"]
