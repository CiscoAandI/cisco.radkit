SSH Proxy Example
==================

The SSH Proxy module allows you to create an SSH server that proxies connections to devices in the RADKit inventory. This is particularly useful for network devices where you want device credentials to remain on the RADKit service rather than locally.

**Key Features:**
- Device credentials remain on RADKit service (not stored locally)
- Username format: ``<device_name>@<radkit_service_serial>``
- Supports both shell and exec modes
- Recommended for network devices with Ansible network_cli connection
- Replaces deprecated network_cli and terminal connection plugins as of version 2.0.0

**Important Notes:**
- For Linux servers, use the ``port_forward`` module instead
- SCP and SFTP file transfers are not supported through SSH proxy
- Always disable SSH host key checking unless custom host keys are configured
- Password authentication may not work reliably with Ansible network_cli

Prerequisites
#############

1. RADKit service running and accessible
2. Devices configured in RADKit inventory
3. Certificate-based authentication configured
4. Required environment variables set:

.. code-block:: bash

   export RADKIT_ANSIBLE_CLIENT_PRIVATE_KEY_PASSWORD_BASE64=$(echo -n 'mypassword' | base64)
   export RADKIT_ANSIBLE_IDENTITY="myuserid@cisco.com"
   export RADKIT_ANSIBLE_SERVICE_SERIAL="xxxx-xxx-xxxx"

Basic SSH Proxy Example
########################

.. code-block:: yaml

   ---
   - hosts: localhost
     become: no
     gather_facts: no
     vars:
       ssh_proxy_port: 2222
     tasks:
       - name: Start RADKit SSH Proxy Server
         cisco.radkit.ssh_proxy:
           local_port: "{{ ssh_proxy_port }}"
           local_address: "127.0.0.1"
         async: 300  # Keep running for 5 minutes
         poll: 0
         register: ssh_proxy_job

       - name: Wait for SSH proxy to become available
         ansible.builtin.wait_for:
           port: "{{ ssh_proxy_port }}"
           host: 127.0.0.1
           delay: 3
           timeout: 30

       - name: Display connection information
         debug:
           msg: |
             SSH proxy is now running on port {{ ssh_proxy_port }}
             Connect to devices using: ssh <device_name>@{{ lookup('env', 'RADKIT_ANSIBLE_SERVICE_SERIAL') }}@localhost -p {{ ssh_proxy_port }}
             Example: ssh router1@{{ lookup('env', 'RADKIT_ANSIBLE_SERVICE_SERIAL') }}@localhost -p {{ ssh_proxy_port }}

Using SSH Proxy with Network Devices
#####################################

.. code-block:: yaml

   ---
   # Start the SSH proxy
   - hosts: localhost
     become: no
     gather_facts: no
     vars:
       ssh_proxy_port: 2222
     tasks:
       - name: Start RADKit SSH Proxy Server
         cisco.radkit.ssh_proxy:
           local_port: "{{ ssh_proxy_port }}"
         async: 300
         poll: 0
         register: ssh_proxy_job

       - name: Wait for SSH proxy to become available
         ansible.builtin.wait_for:
           port: "{{ ssh_proxy_port }}"
           host: 127.0.0.1
           delay: 3
           timeout: 30

   # Use the proxy with network devices
   - hosts: cisco_devices  # Define your devices in inventory
     become: no
     gather_facts: no
     connection: ansible.netcommon.network_cli
     vars:
       ansible_network_os: ios
       ansible_port: 2222
       ansible_user: "{{ inventory_hostname }}@{{ lookup('env', 'RADKIT_ANSIBLE_SERVICE_SERIAL') }}"
       ansible_host: localhost
       ansible_host_key_checking: false
     tasks:
       - name: Get device version information
         cisco.ios.ios_command:
           commands: show version
         register: version_info

       - name: Display version information
         debug:
           var: version_info.stdout_lines

Advanced SSH Proxy Configuration
#################################

.. code-block:: yaml

   ---
   - hosts: localhost
     become: no
     gather_facts: no
     tasks:
       - name: Start SSH Proxy with custom configuration
         cisco.radkit.ssh_proxy:
           local_port: 2222
           local_address: "0.0.0.0"  # Listen on all interfaces
           test_mode: false          # Run persistently
           timeout: 600              # 10 minutes timeout
         register: ssh_proxy_result

       - name: Display proxy information
         debug:
           msg: |
             SSH Proxy started successfully
             Local address: {{ ssh_proxy_result.local_address }}
             Local port: {{ ssh_proxy_result.local_port }}
             PID: {{ ssh_proxy_result.pid }}

SSH Proxy with Inventory Plugin
###############################

Create a ``radkit_devices.yml`` inventory file:

.. code-block:: yaml

   plugin: cisco.radkit.radkit
   strict: False
   keyed_groups:
     - prefix: radkit_device_type
       key: 'device_type'

Then use it in your playbook:

.. code-block:: yaml

   ---
   - hosts: localhost
     tasks:
       - name: Start SSH Proxy
         cisco.radkit.ssh_proxy:
           local_port: 2222
         async: 300
         poll: 0

       - name: Wait for proxy
         ansible.builtin.wait_for:
           port: 2222
           host: 127.0.0.1
           delay: 3

   - hosts: radkit_device_type_IOS_XE  # From inventory plugin
     connection: ansible.netcommon.network_cli
     vars:
       ansible_network_os: ios
       ansible_port: 2222
       ansible_user: "{{ inventory_hostname }}@{{ lookup('env', 'RADKIT_ANSIBLE_SERVICE_SERIAL') }}"
       ansible_host: localhost
       ansible_host_key_checking: false
     tasks:
       - cisco.ios.ios_facts:
           gather_subset: all

Manual SSH Connection Examples
##############################

Once the SSH proxy is running, you can connect manually:

.. code-block:: bash

   # Connect to a specific device
   ssh router1@xxxx-xxx-xxxx@localhost -p 2222

   # Run a single command
   ssh router1@xxxx-xxx-xxxx@localhost -p 2222 "show version"

   # Disable host key checking (recommended)
   ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null router1@xxxx-xxx-xxxx@localhost -p 2222

Troubleshooting
###############

**Connection Issues:**

1. Verify RADKit service is accessible
2. Check environment variables are set correctly
3. Ensure device exists in RADKit inventory
4. Confirm SSH proxy port is not in use

**Common Error Solutions:**

.. code-block:: yaml

   # Always disable host key checking
   vars:
     ansible_host_key_checking: false
     ansible_ssh_common_args: '-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null'

**Testing Connection:**

.. code-block:: yaml

   - name: Test SSH proxy connection
     cisco.radkit.ssh_proxy:
       local_port: 2222
       test_mode: true
       test_device: "router1"
     register: test_result

   - debug:
       var: test_result

Comparison with Other Methods
#############################

+------------------+----------------+------------------+-------------------+
| Method           | Credentials    | File Transfer    | Use Case          |
+==================+================+==================+===================+
| SSH Proxy        | On RADKit      | Not Supported    | Network Devices   |
+------------------+----------------+------------------+-------------------+
| Port Forward     | Local          | Supported        | Linux Servers     |
+------------------+----------------+------------------+-------------------+
| Connection       | On RADKit      | Not Supported    | Legacy            |
| Plugins          |                |                  | (deprecated)      |
+------------------+----------------+------------------+-------------------+

For more examples, see the `ssh_proxy.yml playbook <https://github.com/cisco-system-traffic-generator/radkit-ansible/blob/main/playbooks/ssh_proxy.yml>`_ in the repository.
