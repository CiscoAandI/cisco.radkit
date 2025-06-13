# RADKit SSH Proxy vs Port Forwarding

This document explains the differences bet## Comparison Table

| Feature | Port Forward | SSH Proxy |
|---------|--------------|-------------|
| **Setup Complexity** | One module per device/port | One module for all devices |
| **Device Selection** | Static (configured per task) | Dynamic (via SSH username) |
| **Protocol Support** | Any TCP protocol | SSH-based protocols |
| **Authentication** | Original service auth | SSH proxy auth + original auth |
| **Credential Location** | **Local (Ansible client)** | **Remote (RADKit service)** |
| **Security Model** | Credentials must be local | Credentials stay on service |
| **Tooling** | Protocol-specific tools | Standard SSH tools |
| **Resource Usage** | One process per forward | One SSH server for all |
| **Port Management** | Need unique ports per device | Single port for all devices |

## Key Security Advantage: Credential Location

### SSH Proxy (Recommended for Security)
- **Device credentials remain on the RADKit service**
- No need to store/manage device credentials locally
- RADKit service handles authentication to devices
- Only SSH proxy password needed locally (optional)
- Reduces credential exposure and management overhead

### Port Forwarding
- **Requires device credentials on the Ansible client**
- Must manage device usernames/passwords locally
- Credentials transmitted over the tunnel
- Higher security risk if client is compromisedo forwarding modules in the RADKit Ansible collection.

## Port Forwarding Module (`port_forward.py`)

**Purpose**: Forwards a specific TCP port from a remote device to a local port.

**Use Cases**:
- Accessing web interfaces (HTTP/HTTPS)
- Database connections
- Any TCP-based service on a specific port
- Direct protocol access (like NETCONF, RESTCONF)

**Configuration**:
```yaml
- name: Forward device HTTPS port to local port 8443
  cisco.radkit.port_forward:
    device_name: "router1"
    local_port: 8443
    destination_port: 443
  async: 300
  poll: 0
```

**Connection Method**: 
- Direct TCP connection to `localhost:8443`
- No authentication at the forwarding layer
- Original service authentication required

**Example Usage**:
```bash
# Access device web interface
curl -k https://localhost:8443

# Connect to NETCONF
ssh -p 830 localhost  # If forwarding port 830
```

## SSH Proxy Module (`ssh_proxy.py`)

**Purpose**: Creates an SSH server that proxies connections to any device in the RADKit inventory.

**Use Cases**:
- Interactive shell access to devices
- Running commands on multiple devices
- File transfers via SCP/SFTP
- Dynamic access to any device without pre-configuring ports
- Standard SSH tooling compatibility

**Configuration**:
```yaml
- name: Start SSH proxy server
  cisco.radkit.ssh_proxy:
    local_port: 2222
    password: "secure_password"
  async: 300
  poll: 0
```

**Connection Method**:
- SSH to `device_name@service_id@localhost -p 2222`
- SSH authentication required (password provided to module)
- Dynamic device selection via SSH username

**Example Usage**:
```bash
# Interactive shell
ssh router1@my-service@localhost -p 2222

# Execute command
ssh -t router1@my-service@localhost -p 2222 "show version"

# File transfer
scp -P 2222 config.txt router1@my-service@localhost:/tmp/

# Multiple devices without reconfiguration
ssh switch1@my-service@localhost -p 2222
ssh firewall1@my-service@localhost -p 2222
```

## Comparison Table

| Feature | Port Forward | SSH Proxy |
|---------|--------------|-----------|
| **Setup Complexity** | One module per device/port | One module for all devices |
| **Device Selection** | Static (configured per task) | Dynamic (via SSH username) |
| **Protocol Support** | Any TCP protocol | SSH-based protocols |
| **Authentication** | Original service auth | SSH proxy auth + original auth |
| **Tooling** | Protocol-specific tools | Standard SSH tools |
| **Resource Usage** | One process per forward | One SSH server for all |
| **Port Management** | Need unique ports per device | Single port for all devices |

## When to Use Which

### Use Port Forwarding When:
- You need access to a specific service (web UI, database, API)
- You want direct protocol access without SSH overhead
- You're working with non-SSH protocols
- You need to maintain existing connection code
- You have a small number of specific ports to forward

### Use SSH Proxy When:
- You need interactive access to devices
- You want to use standard SSH tools (ssh, scp, sftp)
- You need to access multiple devices dynamically
- You prefer SSH-based workflows
- You want file transfer capabilities
- You need to run commands across multiple devices

## Security Considerations

### Port Forwarding:
- Raw TCP tunnels (no additional encryption beyond original service)
- No authentication at forwarding layer
- Exposed ports are unprotected
- Should bind to localhost only

### SSH Proxy:
- SSH encryption for all traffic
- Authentication required at proxy level
- Additional security layer
- Standard SSH security practices apply

## Example Playbook Patterns

### Port Forwarding Pattern:
```yaml
# Start forwarding for each device
- name: Forward web ports for all devices
  cisco.radkit.port_forward:
    device_name: "{{ inventory_hostname }}"
    local_port: "{{ 8000 + ansible_play_hosts.index(inventory_hostname) }}"
    destination_port: 443
  async: 300
  poll: 0
  delegate_to: localhost

# Use the forwarded ports
- name: Check device status via HTTP
  uri:
    url: "https://localhost:{{ 8000 + ansible_play_hosts.index(inventory_hostname) }}/api/status"
  delegate_to: localhost
```

### SSH Proxy Pattern:
```yaml
# Start single SSH proxy
- name: Start SSH proxy
  cisco.radkit.ssh_proxy:
    local_port: 2222
    password: "proxy_password"
  async: 300
  poll: 0
  run_once: true

# Use SSH to access any device
- name: Get device info via SSH
  shell: |
    sshpass -p "{{ ssh_password }}" ssh -o StrictHostKeyChecking=no \
    {{ inventory_hostname }}@{{ service_id }}@localhost -p 2222 "show version"
  delegate_to: localhost
```

Both modules complement each other and can be used together in complex automation scenarios where you need both direct protocol access and SSH-based device management.
