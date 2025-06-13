
.. _docsite_root_index:

RADKit Ansible Collection
==============================================

This cisco.radkit Ansible collection is built to provide a collection of
plugins and modules allows users to build or reuse playbooks while connecting through RADKIT.

This project is currently in a beta, use at your own risk.

Requirements
################
-  `RADKIT <https://radkit.cisco.com>`__ 1.7.5 or higher
- Python >= 3.9

Installation
################
Install directly from a downloaded tar file (available in `RADKIT downloads area <https://radkit.cisco.com/downloads/release/>`__ ):

.. code-block:: bash

  ansible-galaxy collection install cisco-radkit-1.7.5.tar.gz --force

Or install directly via git:

.. code-block:: bash

  ansible-galaxy collection install git+https://wwwin-github.cisco.com/scdozier/cisco.radkit-ansible.git --force

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
   examples/swagger_example.rst

Using this collection
################################

* Connection plugins can be used by adding 'connection: cisco.radkit.network_cli' or 'connection: cisco.radkit.terminal' to your playbook
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
          service_serial: "{ radkit_service_serial }"
          client_key_password_b64: "{ radkit_client_private_key_password_base64 }"
          identity: "{ radkit_identity }"
          device_name: router1
          command: show version
        register: cmd_output
        delegate_to: localhost


Limitations
################################
- Linux modules combined with the Terminal connection plugin must have passwordless sudo (add 'your_username ALL=(ALL:ALL) NOPASSWD:ALL' to /etc/sudoers)
- Network_cli plugin is faster than using terminal due to how Ansible network plugins can do persistent plugins locally.

Connection Plugins vs Modules vs Inventory Plugins
################################################################

Connection Plugins allow you to utilize existing Ansible modules but connect through RADKIT instead of directly via SSH.  With connection plugins,
credentials to devices are stored on the remote RADKit service.

* :ref:`cisco.radkit.network_cli <ansible_collections.cisco.radkit.network_cli_connection>` -- Network_cli plugin is used for network devices with existing Ansible modules. Tested with ios, nxos.
* :ref:`cisco.radkit.terminal <ansible_collections.cisco.radkit.terminal_connection>` -- Terminal plugin is used for non networking devices (LINUX) to SSH based modules.

Modules are specific tasks built upon RADKit functions.  Some modules, such as http will require local credentials.  The HTTP Proxy and Port Forward
modules allow you to utilize nearly any existing ansible module with the caveat that you must send credentials to the device.

Inventory plugins allow you pull devices from the remote RADKIT service into your local Ansible inventory without manually building an inventory file.

This chart shows some of the differences:


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
