# cisco.radkit

The cisco.radkit Ansible collection provides plugins and modules for network automation through Cisco RADKit, enabling secure, scalable remote access to network devices and infrastructure.

## What is Cisco RADKit?

Cisco RADKit (Remote Access Development Kit) is a secure, cloud-based platform that enables remote access to customer network devices for troubleshooting, monitoring, and automation. RADKit consists of three main components:

## Requirements

* **RADKit Client**: Install from [PyPI](https://pypi.org/project/cisco-radkit-client/) - `pip install cisco-radkit-client`
* **Version**: RADKit 1.8.5+ 
* **Authentication**: [Certificate-based login](https://radkit.cisco.com/docs/pages/client_advanced.html) required
* **python-proxy**: Only required for `http_proxy` module

## Installation

### Install RADKit Client
```bash
pip install cisco-radkit-client
```

### Install Ansible Collection

**From Ansible Galaxy:**
```bash
ansible-galaxy collection install cisco.radkit
```

**From Git (Development):**
```bash
ansible-galaxy collection install git+https://github.com/CiscoAandI/cisco.radkit.git
```

**From Local Archive:**
```bash
ansible-galaxy collection install cisco-radkit-<version>.tar.gz
```

## Authentication Setup

All modules and plugins require authentication credentials for RADKit. Environment variables are the recommended approach:

```bash
export RADKIT_ANSIBLE_CLIENT_PRIVATE_KEY_PASSWORD_BASE64=$(echo -n 'mypassword' | base64)
export RADKIT_ANSIBLE_IDENTITY="myuserid@cisco.com"
export RADKIT_ANSIBLE_SERVICE_SERIAL="xxxx-xxx-xxxx"
```




## Quick Start Guide

### 1. Setup Authentication
```bash
# Set RADKit credentials
export RADKIT_ANSIBLE_CLIENT_PRIVATE_KEY_PASSWORD_BASE64=$(echo -n 'your_key_password' | base64)
export RADKIT_ANSIBLE_IDENTITY="your_email@company.com"
export RADKIT_ANSIBLE_SERVICE_SERIAL="your-service-serial"
```

### 2. Setup Inventory

**For SSH Proxy Approach (Recommended):**
```ini
[cisco_devices]
router1
router2
router3

[cisco_devices:vars]
ansible_ssh_common_args='-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null'
```

**For Legacy Connection Plugins (DEPRECATED):**
```ini
# Device hostnames and IPs must match what is configured in RADKit inventory
router1 ansible_host=10.1.1.1
router2 ansible_host=10.1.2.1
router3 ansible_host=10.1.3.1
```

**Important**: 
- **SSH Proxy**: Device hostnames in inventory must match device names in your RADKit service. Use `127.0.0.1` as `ansible_host` since connections go through the local proxy.
- **Legacy Plugins**: Both hostname and IP address must match exactly what is configured in your RADKit service inventory.

### 3. Network Device Example (Recommended: SSH Proxy)

*Inventory file (inventory.ini):*
```ini
[cisco_devices]
router1
router2
router3

[cisco_devices:vars]
ansible_ssh_common_args='-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null'
```

*Playbook:*
```yaml
---
- name: Setup RADKit SSH Proxy
  hosts: localhost
  become: no
  gather_facts: no
  vars:
    ssh_proxy_port: 2225
  tasks:
    - name: Start RADKit SSH Proxy Server
      cisco.radkit.ssh_proxy:
        local_port: "{{ ssh_proxy_port }}"
      async: 300  # Keep running for 5 minutes
      poll: 0
      register: ssh_proxy_job
      failed_when: false
    
    - name: Wait for SSH proxy to become available
      ansible.builtin.wait_for:
        port: "{{ ssh_proxy_port }}"
        host: 127.0.0.1
        delay: 3
        timeout: 30

    - name: Display connection information
      debug:
        msg: |
          SSH Proxy is now running on port {{ ssh_proxy_port }}
          Connect to devices using: ssh <device_hostname>@{{ lookup('env', 'RADKIT_ANSIBLE_SERVICE_SERIAL') }}@localhost -p {{ ssh_proxy_port }}
          Device credentials are handled automatically by RADKit service

- name: Execute commands on network devices
  hosts: cisco_devices  # Define your devices in inventory
  become: no
  gather_facts: no
  connection: ansible.netcommon.network_cli
  vars:
    ansible_network_os: ios
    ansible_host: 127.0.0.1  # All connections go through local proxy
    ansible_port: 2225
    ansible_user: "{{ inventory_hostname }}@{{ lookup('env', 'RADKIT_ANSIBLE_SERVICE_SERIAL') }}"
    ansible_host_key_checking: false
  tasks:
    - name: Get device version information
      cisco.ios.ios_command:
        commands: show version
      register: version_info
```

### 4. Legacy Configuration Example (DEPRECATED)

*Inventory Setup (hostnames and IPs must match RADKit service inventory):*
```ini
[cisco_devices]
router1 ansible_host=10.1.1.100  # IP must match RADKit inventory
router2 ansible_host=10.1.2.100  # IP must match RADKit inventory
```

*Playbook:*
```yaml
---
- hosts: router1  # Hostname must match RADKit service
  connection: cisco.radkit.network_cli
  vars:
    radkit_identity: user@cisco.com
    ansible_network_os: ios
  become: yes
  gather_facts: no
  tasks:
    - name: Run show ip interface brief
      cisco.ios.ios_command:
        commands: show ip interface brief
      register: version_output
```
```yaml
- hosts: localhost
  vars:
    target_server: "linux-server-01"
    remote_port: 22
  tasks:
    - name: Start port forward
      cisco.radkit.port_forward:
        device_name: "{{ target_server }}"
        remote_port: "{{ remote_port }}"
        local_port: 2223
      register: port_forward_result

    - name: Wait for port forward to be ready
      ansible.builtin.wait_for:
        port: 2223
        delay: 3
      delegate_to: localhost

    - name: Connect to Linux server via port forward
      vars:
        ansible_host: localhost
        ansible_port: 2223
        ansible_host_key_checking: false
      delegate_to: localhost
      block:
        - name: Get system information
          ansible.builtin.setup:
          register: system_facts

        - name: Display system information
          debug:
            msg: "Server {{ target_server }} running {{ system_facts.ansible_facts.ansible_distribution }} {{ system_facts.ansible_facts.ansible_distribution_version }}"

        - name: Close port forward when done
          cisco.radkit.port_forward:
            device_name: "{{ target_server }}"
            remote_port: "{{ remote_port }}"
            local_port: 2223
            state: absent

```

### 5. Linux Server Example
```yaml
- hosts: localhost
  vars:
    target_server: "linux-server-01"
    remote_port: 22
  tasks:
    - name: Start port forward
      cisco.radkit.port_forward:
        device_name: "{{ target_server }}"
        remote_port: "{{ remote_port }}"
        local_port: 2223
      register: port_forward_result

    - name: Wait for port forward to be ready
      ansible.builtin.wait_for:
        port: 2223
        delay: 3
      delegate_to: localhost

    - name: Connect to Linux server via port forward
      vars:
        ansible_host: localhost
        ansible_port: 2223
        ansible_host_key_checking: false
      delegate_to: localhost
      block:
        - name: Get system information
          ansible.builtin.setup:
          register: system_facts

        - name: Display system information
          debug:
            msg: "Server {{ target_server }} running {{ system_facts.ansible_facts.ansible_distribution }} {{ system_facts.ansible_facts.ansible_distribution_version }}"

        - name: Close port forward when done
          cisco.radkit.port_forward:
            device_name: "{{ target_server }}"
            remote_port: "{{ remote_port }}"
            local_port: 2223
            state: absent

```

### 6. Using RADKit Command Module (Alternative)
```yaml
- hosts: localhost
  tasks:
    - name: Execute commands directly on network device
      cisco.radkit.command:
        device_name: router-01
        commands:
          - show version
          - show ip interface brief
          - show running-config | include hostname
      register: command_output

    - name: Display command results
      debug:
        var: command_output.results
```

## Key SSH Proxy Concepts

### How SSH Proxy Works
1. **Single Proxy Server**: One `ssh_proxy` instance handles connections to all devices
2. **Username Format**: Connect using `<device_hostname>@<service_serial>` as the username
3. **Device Authentication**: RADKit service handles device credentials automatically
4. **Long-Running Process**: Use `async` and `poll: 0` to keep proxy running during playbook execution

📖 **Learn More**: [SSH Forwarding Documentation](https://radkit.cisco.com/docs/features/feature_ssh_forwarding.html)

### SSH Proxy vs Port Forward
- **SSH Proxy**: Best for network devices (routers, switches) - one proxy for multiple devices
- **Port Forward**: Best for Linux servers - one port forward per device, supports file transfers

📖 **Learn More**: [Port Forwarding Documentation](https://radkit.cisco.com/docs/features/feature_port_forwarding.html)

### Important Notes
- Device hostnames in inventory **must match** device names in RADKit service
- SSH host key checking should be disabled (keys change between sessions)
- Use `ansible_host: localhost` to connect through the proxy
- Set `ansible_port` to match your SSH proxy port

## Troubleshooting & Known Issues
### Network Device Issues

**wait_for_connection not supported**: Use `cisco.radkit.exec_and_wait` instead:

```yaml
- name: Reload device and wait for recovery
  cisco.radkit.exec_and_wait:
    device_name: "{{ inventory_hostname }}"
    commands: ["reload"]
    prompts: [".*yes/no].*", ".*confirm].*"]
    answers: ["yes\r", "\r"]
    seconds_to_wait: 300
    delay_before_check: 10
  register: reload_result

- name: Reset connection after reload
  meta: reset_connection
```

**High fork errors**: When using many concurrent connections:
- Increase timeouts in `ansible.cfg`
- Reduce fork count: `ansible-playbook -f 10 playbook.yml`
- Use `port_forward` module if device credentials are available

**"RADKIT failure:" with empty error message**: This usually indicates:
1. **Missing RADKit Client**: Install with `pip install cisco-radkit-client`
2. **Invalid Credentials**: Check your environment variables:
   ```bash
   echo $RADKIT_ANSIBLE_IDENTITY
   echo $RADKIT_ANSIBLE_SERVICE_SERIAL
   echo $RADKIT_ANSIBLE_CLIENT_PRIVATE_KEY_PASSWORD_BASE64 | base64 -d
   ```
3. **Certificate Issues**: Verify radkit certificate paths, expiration, and permissions
4. **Network Connectivity**: Ensure access to RADKit cloud services
5. **Service Serial**: Confirm the service serial is correct and active

Run with `-vvv` for detailed debugging information.

### Platform-Specific Issues

**macOS "Dead Worker" Error**:
```bash
export no_proxy='*'
export OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES
```
*Note: Incompatible with HTTP Proxy module*

**Linux Requirements**:
- Terminal connection plugin requires passwordless sudo
- Add to `/etc/sudoers`: `username ALL=(ALL:ALL) NOPASSWD:ALL`

## Component Types

**Connection Plugins (DEPRECATED)**: Enable Ansible modules to connect through RADKit instead of direct SSH. Device credentials stored on RADKit service. Update your playbooks to use the new `ssh_proxy` and `port_forward` modules for better reliability and security.

**Modules**: Specific tasks using RADKit functions. Includes specialized modules for network automation, device management, and proxy functionality.

**Inventory Plugins**: Dynamically pull device inventory from RADKit service into Ansible without manual configuration.

## Feature Comparison Matrix

| Component | Network CLI | Linux SSH | File Transfer | Device Creds | Security | Status |
|-----------|-------------|-----------|---------------|--------------|----------|--------|
| **ssh_proxy + network_cli** | ✅ Excellent | ❌ No | ❌ No SCP | 🔒 Remote | 🛡️ High | ✅ **Recommended** |
| **port_forward** | ✅ Good | ✅ Excellent | ✅ Full SCP/SFTP | 📍 Local | 🛡️ Medium | ✅ **Recommended** |
| **terminal** (deprecated) | ❌ No | ✅ Basic | ✅ Limited | 🔒 Remote | 🛡️ High | ❌ **Deprecated** |
| **network_cli** (deprecated) | ✅ Good | ❌ No | ❌ No | 🔒 Remote | 🛡️ High | ❌ **Deprecated** |
| **http_proxy** | ❌ No | ❌ No | ❌ No | 📍 Local | 🛡️ Medium | ✅ Active |
| **Command/Genie modules** | ✅ Specialized | ❌ No | ❌ No | 🔒 Remote | 🛡️ High | ✅ Active |

### Links & Resources
- **RADKit Documentation**: [radkit.cisco.com](https://radkit.cisco.com)
- **PyPI Package**: [cisco-radkit-client](https://pypi.org/project/cisco-radkit-client/)
- **Certificate Setup**: [Authentication Guide](https://radkit.cisco.com/docs/pages/client_advanced.html)
- **SSH Forwarding**: [Feature Documentation](https://radkit.cisco.com/docs/features/feature_ssh_forwarding.html)
- **Port Forwarding**: [Feature Documentation](https://radkit.cisco.com/docs/features/feature_port_forwarding.html)
- **Collection Documentation**: Available in `docs/` directory

For detailed examples and advanced configurations, see the `playbooks/` directory in this collection.
