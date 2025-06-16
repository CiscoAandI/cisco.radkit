
.. _docsite_root_index:

RADKit Ansible Collection
==============================================

This cisco.radkit Ansible collection provides plugins and modules for network automation through Cisco RADKit, enabling secure, scalable remote access to network devices and infrastructure.

⚠️ **IMPORTANT**: Connection plugins (:ref:`cisco.radkit.network_cli <ansible_collections.cisco.radkit.network_cli_connection>` and :ref:`cisco.radkit.terminal <ansible_collections.cisco.radkit.terminal_connection>`) are **DEPRECATED** as of v2.0.0. Use :ref:`ssh_proxy <ansible_collections.cisco.radkit.ssh_proxy_module>` module with ``ansible.netcommon.network_cli`` for network devices and :ref:`port_forward <ansible_collections.cisco.radkit.port_forward_module>` module for Linux servers.

Requirements
################
-  `RADKIT <https://radkit.cisco.com>`__ 1.8.5 or higher
- Python >= 3.9

Installation
################
**From Ansible Galaxy:**

.. code-block:: bash

  ansible-galaxy collection install cisco.radkit

**From Git (Development):**

.. code-block:: bash

  ansible-galaxy collection install git+https://github.com/CiscoAandI/cisco.radkit.git --force

**From Local Archive:**
Install directly from a downloaded tar file (available in `RADKIT downloads area <https://radkit.cisco.com/downloads/release/>`__ ):

.. code-block:: bash

  ansible-galaxy collection install cisco-radkit-<version>.tar.gz

.. toctree::
   :maxdepth: 2
   :caption: Collections:

   collections/index


.. toctree::
   :maxdepth: 1
   :caption: Plugin indexes:
   :glob:

   collections/index_*

.. toctree::
   :maxdepth: 2
   :caption: Examples:

   examples/terminal_connection_plugin_example.rst
   examples/network_cli_connection_plugin_example.rst
   examples/inventory_plugin_example.rst
   examples/radkit_command_example.rst
   examples/genie_parsed_command_example.rst
   examples/genie_diff_example.rst
   examples/http_proxy_example.rst
   examples/port_forward_example.rst
   examples/ssh_proxy_example.rst
   examples/swagger_example.rst

Using this collection
################################

⚠️ **MIGRATION NOTICE**: As of v2.0.0, the recommended approach has changed:

**For Network Devices (Recommended):**
- Use :ref:`ssh_proxy <ansible_collections.cisco.radkit.ssh_proxy_module>` module with standard ``ansible.netcommon.network_cli`` connection
- Device credentials remain on RADKit service (more secure)
- Better compatibility with standard Ansible network modules

**For Linux Servers (Recommended):**
- Use :ref:`port_forward <ansible_collections.cisco.radkit.port_forward_module>` module with standard SSH connection
- Full SSH functionality including SCP/SFTP file transfers

**Legacy (DEPRECATED):**
- Connection plugins :ref:`cisco.radkit.network_cli <ansible_collections.cisco.radkit.network_cli_connection>` and :ref:`cisco.radkit.terminal <ansible_collections.cisco.radkit.terminal_connection>` are deprecated
- Will be removed in version 3.0.0

* Inventory plugins can be used by specifying the radkit_devices.yml with -i or --inventory
* Modules can be specified in the playbook by name cisco.radkit.<module name>

All modules and plugins require that radkit-client be installed via pip along with `certificate based authentication <https://radkit.cisco.com/docs/pages/client_advanced.html#non-interactive-authentication>`__ .
In order for Ansible to utilize the certificate based authentication mechanism, either configure standard environment variables or vars.

Using Environment Variables
*********************************
Environment Variables are the preferred method as they work with connections plugins, inventory plugins, and modules.

.. code-block:: bash

  export RADKIT_ANSIBLE_CLIENT_PRIVATE_KEY_PASSWORD_BASE64=$(echo -n 'mypassword' | base64)
  export RADKIT_ANSIBLE_IDENTITY="myuserid@cisco.com"
  export RADKIT_ANSIBLE_SERVICE_SERIAL="xxxx-xxx-xxxx"

Using Vars Files
*********************************
If you are using modules, you can also utilize a vars_file to import the variables into your playbook.
Be sure to encrypt it with ansible-encrypt!

First, define a radkit-vars.yml (example) file where you specify your RADKIT variables:

.. code-block:: ini

  ---
  radkit_service_serial: xxxx-xxx-xxxx
  radkit_client_private_key_password_base64: bXlwYXNzd29yZA==
  radkit_identity: myuserid@cisco.com


Then link the radkit-vars.yml in your playbook under vars_files.

.. code-block:: yaml

  - hosts: all
    vars_files:
      - radkit-vars.yml
    gather_facts: no
    tasks:
      - name: Run Command on router1
        cisco.radkit.command:
          service_serial: "{{ radkit_service_serial }}"
          client_key_password_b64: "{{ radkit_client_private_key_password_base64 }}"
          identity: "{{ radkit_identity }}"
          device_name: router1
          command: show version
        register: cmd_output
        delegate_to: localhost


Quick Start Guide
################################

1. Setup Authentication
*********************************

.. code-block:: bash

  # Set RADKit credentials
  export RADKIT_ANSIBLE_CLIENT_PRIVATE_KEY_PASSWORD_BASE64=$(echo -n 'your_key_password' | base64)
  export RADKIT_ANSIBLE_IDENTITY="your_email@company.com"
  export RADKIT_ANSIBLE_SERVICE_SERIAL="your-service-serial"

2. Setup Inventory
*********************************

**For SSH Proxy Approach (Recommended):**

.. code-block:: ini

  [cisco_devices]
  router1
  router2
  router3

  [cisco_devices:vars]
  ansible_ssh_common_args='-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null'

**For Legacy Connection Plugins (DEPRECATED):**

.. code-block:: ini

  # Device hostnames and IPs must match what is configured in RADKit inventory
  router1 ansible_host=10.1.1.1
  router2 ansible_host=10.1.2.1
  router3 ansible_host=10.1.3.1

**Important**: 

- **SSH Proxy**: Device hostnames in inventory must match device names in your RADKit service. Use ``127.0.0.1`` as ``ansible_host`` since connections go through the local proxy.
- **Legacy Plugins**: Both hostname and IP address must match exactly what is configured in your RADKit service inventory.

3. Network Device Example (Recommended: SSH Proxy)
****************************************************

*Inventory file (inventory.ini):*

.. code-block:: ini

  [cisco_devices]
  router1
  router2
  router3

  [cisco_devices:vars]
  ansible_ssh_common_args='-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null'

*Playbook:*

.. code-block:: yaml

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

4. Legacy Configuration Example (DEPRECATED)
*********************************************

*Inventory Setup (hostnames and IPs must match RADKit service inventory):*

.. code-block:: ini

  [cisco_devices]
  router1 ansible_host=10.1.1.100  # IP must match RADKit inventory
  router2 ansible_host=10.1.2.100  # IP must match RADKit inventory

*Playbook:*

.. code-block:: yaml

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

5. Linux Server Example
*********************************

.. code-block:: yaml

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

6. Using RADKit Command Module (Alternative)
********************************************

.. code-block:: yaml

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

Key SSH Proxy Concepts
********************************

How SSH Proxy Works
===========================

1. **Single Proxy Server**: One ``ssh_proxy`` instance handles connections to all devices
2. **Username Format**: Connect using ``<device_hostname>@<service_serial>`` as the username
3. **Device Authentication**: RADKit service handles device credentials automatically
4. **Long-Running Process**: Use ``async`` and ``poll: 0`` to keep proxy running during playbook execution

📖 **Learn More**: `SSH Forwarding Documentation <https://radkit.cisco.com/docs/features/feature_ssh_forwarding.html>`__

SSH Proxy vs Port Forward
===========================

- **SSH Proxy**: Best for network devices (routers, switches) - one proxy for multiple devices
- **Port Forward**: Best for Linux servers - one port forward per device, supports file transfers

📖 **Learn More**: `Port Forwarding Documentation <https://radkit.cisco.com/docs/features/feature_port_forwarding.html>`__

Important Notes
===========================

- Device hostnames in inventory **must match** device names in RADKit service
- SSH host key checking should be disabled (keys change between sessions)
- Use ``ansible_host: localhost`` to connect through the proxy
- Set ``ansible_port`` to match your SSH proxy port


Troubleshooting & Known Issues
################################

Network Device Issues
**********************

**wait_for_connection not supported**: Use ``cisco.radkit.exec_and_wait`` instead:

.. code-block:: yaml

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

**High fork errors**: When using many concurrent connections:

- Increase timeouts in ``ansible.cfg``
- Reduce fork count: ``ansible-playbook -f 10 playbook.yml``
- Use ``port_forward`` module if device credentials are available

**"RADKIT failure:" with empty error message**: This usually indicates:

1. **Missing RADKit Client**: Install with ``pip install cisco-radkit-client``
2. **Invalid Credentials**: Check your environment variables:

   .. code-block:: bash

     echo $RADKIT_ANSIBLE_IDENTITY
     echo $RADKIT_ANSIBLE_SERVICE_SERIAL
     echo $RADKIT_ANSIBLE_CLIENT_PRIVATE_KEY_PASSWORD_BASE64 | base64 -d

3. **Certificate Issues**: Verify radkit certificate paths, expiration, and permissions
4. **Network Connectivity**: Ensure access to RADKit cloud services
5. **Service Serial**: Confirm the service serial is correct and active

Run with ``-vvv`` for detailed debugging information.

Platform-Specific Issues
*************************

**macOS "Dead Worker" Error**:

.. code-block:: bash

  export no_proxy='*'
  export OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES

*Note: Incompatible with HTTP Proxy module*

**Linux Requirements**:

- Terminal connection plugin requires passwordless sudo
- Add to ``/etc/sudoers``: ``username ALL=(ALL:ALL) NOPASSWD:ALL``


Limitations
################################
- Linux modules combined with the Terminal connection plugin must have passwordless sudo (add 'your_username ALL=(ALL:ALL) NOPASSWD:ALL' to /etc/sudoers)
- Network_cli plugin is faster than using terminal due to how Ansible network plugins can do persistent plugins locally.

Connection Plugins vs Modules vs Inventory Plugins
################################################################

⚠️ **IMPORTANT**: Connection plugins are **DEPRECATED as of v2.0.0**

**Recommended Architecture (v2.0.0+):**

**For Network Devices (Routers, Switches, Firewalls):**

- ✅ **Recommended**: :ref:`ssh_proxy <ansible_collections.cisco.radkit.ssh_proxy_module>` module + standard ``ansible.netcommon.network_cli``
- **Benefits**:

  - Device credentials remain on RADKit service (more secure)
  - Standard Ansible network modules work seamlessly
  - Better performance and compatibility

- **Note**: Disable SSH host key checking (host keys change between sessions)

**For Linux Servers:**

- ✅ **Recommended**: :ref:`port_forward <ansible_collections.cisco.radkit.port_forward_module>` module + standard SSH
- **Benefits**:

  - Full SSH functionality including SCP/SFTP file transfers
  - Works with all standard Ansible modules
  - More reliable than SSH proxy for Linux hosts

**Legacy Support (DEPRECATED):**

Connection Plugins allow you to utilize existing Ansible modules but connect through RADKIT instead of directly via SSH.  With connection plugins,
credentials to devices are stored on the remote RADKit service.

* :ref:`cisco.radkit.network_cli <ansible_collections.cisco.radkit.network_cli_connection>` -- **DEPRECATED**: Use ssh_proxy module instead
* :ref:`cisco.radkit.terminal <ansible_collections.cisco.radkit.terminal_connection>` -- **DEPRECATED**: Use port_forward module instead

Modules are specific tasks built upon RADKit functions.  The SSH Proxy and Port Forward
modules allow you to utilize nearly any existing ansible module with better security and compatibility.

Inventory plugins allow you pull devices from the remote RADKIT service into your local Ansible inventory without manually building an inventory file.

This chart shows the current recommendations:


 ==================================== ============================= ===================== ====================== ==================== ================= ======================= ==============
             .                         Terminal Connection Plugin    Network_CLI Plugin    Port Forward Module    HTTP Proxy Module    Swagger Module    Command/Genie Modules    HTTP Module
 ==================================== ============================= ===================== ====================== ==================== ================= ======================= ==============
  Device credentials stored locally                                                                  X                      X                                                   X
  Device credentials stored remotely                X                         X                                                               X                 X
  Supports network cli modules                                                X                      X
  Supports linux  ssh based modules                 X                                                X
  Supports http based modules                                                                        X                      X
  RADKIT Functions                                                                                                                            X                 X               X
 ==================================== ============================= ===================== ====================== ==================== ================= ======================= ==============


Component Types
################################

**Connection Plugins (DEPRECATED)**: Enable Ansible modules to connect through RADKit instead of direct SSH. Device credentials stored on RADKit service. Update your playbooks to use the new ``ssh_proxy`` and ``port_forward`` modules for better reliability and security.

**Modules**: Specific tasks using RADKit functions. Includes specialized modules for network automation, device management, and proxy functionality.

**Inventory Plugins**: Dynamically pull device inventory from RADKit service into Ansible without manual configuration.

Feature Comparison Matrix
################################

+------------------------------+-------------+-----------+---------------+--------------+---------------------+
| Component                    | Network CLI | Linux SSH | File Transfer | Device Creds | Status              |
+==============================+=============+===========+===============+==============+=====================+
| **ssh_proxy + network_cli**  | Excellent   | No        | No SCP        | Remote       | **Recommended**     |
+------------------------------+-------------+-----------+---------------+--------------+---------------------+
| **port_forward**             | Good        | Excellent | Full SCP/SFTP | Local        | **Recommended**     |
+------------------------------+-------------+-----------+---------------+--------------+---------------------+
| **terminal** (deprecated)    | No          | Basic     | Yes           | Remote       | **Deprecated**      |
+------------------------------+-------------+-----------+---------------+--------------+---------------------+
| **network_cli** (deprecated) | Good        | No        | Yes           | Remote       | **Deprecated**      |
+------------------------------+-------------+-----------+---------------+--------------+---------------------+
| **http_proxy**               | No          | No        | Yes           | Local        | Active              |
+------------------------------+-------------+-----------+---------------+--------------+---------------------+
| **Command/Genie modules**    | Specialized | No        | No            | Remote       | **Recommended**     |
+------------------------------+-------------+-----------+---------------+--------------+---------------------+

Links & Resources
################################

- **RADKit Documentation**: `radkit.cisco.com <https://radkit.cisco.com>`__
- **PyPI Package**: `cisco-radkit-client <https://pypi.org/project/cisco-radkit-client/>`__
- **Certificate Setup**: `Authentication Guide <https://radkit.cisco.com/docs/pages/client_advanced.html>`__
- **SSH Forwarding**: `Feature Documentation <https://radkit.cisco.com/docs/features/feature_ssh_forwarding.html>`__
- **Port Forwarding**: `Feature Documentation <https://radkit.cisco.com/docs/features/feature_port_forwarding.html>`__
- **Collection Documentation**: Available in ``docs/`` directory

For detailed examples and advanced configurations, see the ``playbooks/`` directory in this collection.
