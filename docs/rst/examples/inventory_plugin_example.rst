:orphan:


Inventory Plugin
==============================
You can utilize the inventory plugin to connect to devices within the remote RADKIT service inventory without having
to build your own local inventory file.

Reference: https://docs.ansible.com/ansible/latest/plugins/inventory.html

Instructions
*********************************
1.  First create a yaml file radkit_devices.yml with the same below

.. code-block:: yaml

    ---
    plugin: cisco.radkit.radkit
    strict: False
    keyed_groups:
      # group devices based on device type (ex radkit_device_type_IOS)
      - prefix: radkit_device_type
        key: 'device_type'
      # group devices based on description
      - prefix: radkit_description
        key: 'description'

or

.. code-block:: bash

    cat > radkit_devices.yml << EOF
    ---
    plugin: cisco.radkit.radkit
    strict: False
    keyed_groups:
      # group devices based on device type (ex radkit_device_type_IOS)
      - prefix: radkit_device_type
        key: 'device_type'
      # group devices based on description
      - prefix: radkit_description
        key: 'description'
    EOF


2.  The keyed_groups section can be removed or modified.  The 'key' is key from the RADKIT inventory and 'prefix' is the
    the prefix given to the group created. For example, based on the above config, if a deivce is IOS in the RADKIT
    inventory, then it will be in the group radkit_device_type_IOS. This allows you to limit jobs to certain groups based on
    keys in the RADKIT inventory

3. Expose necessary RADKIT environment variables

.. code-block:: bash

    export RADKIT_ANSIBLE_CLIENT_PRIVATE_KEY_PASSWORD_BASE64=$(echo -n 'mypassword' | base64)
    export RADKIT_ANSIBLE_IDENTITY="myuserid@cisco.com"
    export RADKIT_ANSIBLE_SERVICE_SERIAL="xxxx-xxx-xxxx"

4.  Reference the inventory with '-i radkit_devices.yaml ' with any ansible command (ansible, ansible-playbook, ansible-inventory)

Examples
*********************************

.. code-block:: bash

    $ ansible-inventory -i radkit_devices.yml  --list --yaml
    all:
    children:
        radkit_device_type_IOS:
        hosts:
            ex-csr1:
            ansible_host: 1.3.68.61
            radkit_device_type: IOS
            radkit_forwarded_tcp_ports: 80;443
            ex-csr2:
            ansible_host: 1.3.68.62
            radkit_device_type: IOS
            radkit_forwarded_tcp_ports: ''
            ex-csr3:
            ansible_host: 1.10.30.1
            radkit_device_type: IOS
            radkit_forwarded_tcp_ports: ''
            ex-csr4:
            ansible_host: 1.10.20.2
            radkit_device_type: IOS
            radkit_forwarded_tcp_ports: ''
        radkit_device_type_LINUX:
        hosts:
            ex-bastion:
            ansible_host: 1.122.139.24
            radkit_device_type: LINUX
            radkit_forwarded_tcp_ports: ''
            ex-lin-1:
            ansible_host: 1.3.68.64
            radkit_device_type: LINUX
            radkit_forwarded_tcp_ports: ''
            ex-lin-2:
            ansible_host: 1.3.68.65
            radkit_device_type: LINUX
            radkit_forwarded_tcp_ports: ''
            ex-ubuntu:
            ansible_host: 1.3.68.69
            radkit_device_type: LINUX
            radkit_forwarded_tcp_ports: ''

        radkit_device_type_RADKitService:
        hosts:
            radkit:
            ansible_host: 127.0.0.1
            radkit_device_type: RADKitService
            radkit_forwarded_tcp_ports: ''
        radkit_devices:
        hosts:
            ex-bastion: {}
            ex-csr1: {}
            ex-csr2: {}
            ex-csr3: {}
            ex-csr4: {}
            ex-prtr-1: {}
            ex-prtr-2: {}
            ex-ubuntu: {}
            radkit: {}
            test: {}
        ungrouped: {}

    # run playbook on just IOS devices
    $ ansible-playbook -i radkit_devices.yml  myplaybook.yml --limit radkit_device_type_IOS
