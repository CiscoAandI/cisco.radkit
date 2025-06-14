"""
RADKit Dynamic Inventory Plugin for Ansible.

This inventory plugin integrates with RADKit to dynamically discover and 
manage network devices in Ansible inventories.
"""

from __future__ import absolute_import, division, print_function

# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

__metaclass__ = type

DOCUMENTATION = """
name: radkit
author:
    - Scott Dozier (@scdozier)
short_description: Ansible dynamic inventory plugin for RADKIT.
requirements:
    - radkit-client
extends_documentation_fragment:
    - constructed
description:
    - Reads inventories from the RADKit service and creates dynamic Ansible inventory.
    - Supports SSH proxy configurations and host/port overrides for network devices.
options:
    plugin:
        description: The name of this plugin, it should always be set to 'cisco.radkit.radkit' for this plugin to recognize it as it's own.
        type: str
        required: true
        choices:
            - cisco.radkit.radkit
    radkit_service_serial:
        description:
            - The serial of the RADKit service you wish to connect through
        env:
            - name: RADKIT_ANSIBLE_SERVICE_SERIAL
        required: True
    radkit_identity:
        description:
            - The Client ID (owner email address) present in the RADKit client certificate.
        env:
            - name: RADKIT_ANSIBLE_IDENTITY
        required: True
    radkit_client_private_key_password_base64:
        description:
            - The private key password in base64 for radkit client
        env:
            - name: RADKIT_ANSIBLE_CLIENT_PRIVATE_KEY_PASSWORD_BASE64
        required: True
    radkit_client_ca_path:
        description:
            - The path to the issuer chain for the identity certificate
        env:
            - name: RADKIT_ANSIBLE_CLIENT_CA_PATH
        required: False
    radkit_client_cert_path:
        description:
            - The path to the identity certificate
        env:
            - name: RADKIT_ANSIBLE_CLIENT_CERT_PATH
        required: False
    radkit_client_key_path:
        description:
            - The path to the private key for the identity certificate
        env:
            - name: RADKIT_ANSIBLE_CLIENT_KEY_PATH
        required: False
    filter_attr:
        description:
            - Filter RADKit inventory by this attribute (ex name)
        env:
            - name: RADKIT_ANSIBLE_DEVICE_FILTER_ATTR
        required: False
    filter_pattern:
        description:
            - Filter RADKit inventory by this pattern combined with filter_attr
        env:
            - name: RADKIT_ANSIBLE_DEVICE_FILTER_PATTERN
        required: False
    ssh_proxy_mode:
        description:
            - Enable SSH proxy mode - sets ansible_host to 127.0.0.1 for all devices
            - When enabled, devices will connect through SSH proxy instead of direct connections
        type: bool
        default: False
    ssh_proxy_port:
        description:
            - Default SSH proxy port to use when ssh_proxy_mode is enabled
            - Can be overridden per device using ssh_proxy_port_overrides
        type: int
        default: 2222
    ssh_proxy_port_overrides:
        description:
            - Dictionary mapping device names to specific SSH proxy ports
            - Example- device1- 2223, device2- 2224
        type: dict
        default: {}
    ansible_host_overrides:
        description:
            - Dictionary mapping device names to specific ansible_host values
            - Useful for SSH proxy configurations where devices connect to localhost
        type: dict
        default: {}
    ansible_port_overrides:
        description:
            - Dictionary mapping device names to specific ansible_port values
            - Useful for SSH proxy or port forwarding configurations
        type: dict
        default: {}

"""

EXAMPLES = """
# Basic radkit_devices.yml
plugin: cisco.radkit.radkit

# Enhanced configuration with SSH proxy support
plugin: cisco.radkit.radkit
strict: False

# Enable SSH proxy mode - all devices will use 127.0.0.1 as ansible_host
ssh_proxy_mode: True
ssh_proxy_port: 2222

# Override specific devices with different ports/hosts
ansible_host_overrides:
  special_device: "192.168.1.100"
  
ansible_port_overrides:
  router1: 2223
  router2: 2224
  
ssh_proxy_port_overrides:
  router1: 2223
  router2: 2224

# Group devices based on attributes
keyed_groups:
  # group devices based on device type (ex radkit_device_type_IOS)
  - prefix: radkit_device_type
    key: 'device_type'
  # group devices based on description
  - prefix: radkit_description
    key: 'description'
  # group devices for SSH proxy usage
  - prefix: radkit_ssh_proxy
    key: 'device_type'
    separator: '_'

# Compose additional variables for SSH proxy
compose:
  # Set ansible_user for SSH proxy format: device@service_serial
  ansible_user: inventory_hostname + '@' + radkit_service_serial
  # Set SSH connection args for proxy
  ansible_ssh_common_args: "'-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null'"
  
# Filter devices if needed
# filter_attr: 'device_type'
# filter_pattern: 'IOS'

"""

from ansible.errors import AnsibleError, AnsibleParserError
from ansible.module_utils.common.text.converters import to_native
from ansible.plugins.inventory import BaseInventoryPlugin, Constructable
from ansible.utils.display import Display

import base64
import traceback
import os

try:
    import radkit_client
    from radkit_client.sync import Client

    HAS_RADKIT = True
except ImportError:
    HAS_RADKIT = False

display = Display()


class InventoryModule(BaseInventoryPlugin, Constructable):
    """Host inventory parser for ansible using RADKit as source."""

    NAME = "cisco.radkit.radkit"

    def _populate(self):
        """Populate inventory from RADKit service."""
        if not self.inventory:
            return
            
        self.inventory.add_group("radkit_devices")
        
        try:
            # Get configuration options with defaults
            ssh_proxy_mode = self.get_option("ssh_proxy_mode") or False
            ssh_proxy_port = self.get_option("ssh_proxy_port") or 2222
            ssh_proxy_port_overrides = self.get_option("ssh_proxy_port_overrides") or {}
            ansible_host_overrides = self.get_option("ansible_host_overrides") or {}
            ansible_port_overrides = self.get_option("ansible_port_overrides") or {}
            
            # Validate required authentication parameters
            private_key_password_b64 = self.get_option("radkit_client_private_key_password_base64")
            if not private_key_password_b64:
                raise AnsibleError("RADKit private key password is required")
                
            identity = self.get_option("radkit_identity")
            if not identity:
                raise AnsibleError("RADKit identity is required")
                
            service_serial = self.get_option("radkit_service_serial")
            if not service_serial:
                raise AnsibleError("RADKit service serial is required")

            # Use the RADKit client in a context manager (like other modules do)
            with Client.create() as radkit_sync_client:
                display.v(f"Making a RADKIT certificate_login ... identity={identity}")
                
                # Perform certificate login
                radkit_sync_client.certificate_login(
                    identity=identity,
                    ca_path=self.get_option("radkit_client_ca_path"),
                    key_path=self.get_option("radkit_client_key_path"),
                    cert_path=self.get_option("radkit_client_cert_path"),
                    private_key_password=base64.b64decode(private_key_password_b64).decode("utf8"),
                )
                
                display.vvv(f"RADKIT connection successful, connecting to service {service_serial}")
                service = radkit_sync_client.service(service_serial).wait()
                display.vvv(f"Successfully connected to serial {service_serial}, getting inventory...")

                # Get filtered or full inventory
                if self.get_option("filter_attr") and self.get_option("filter_pattern"):
                    inventory = service.inventory.filter(
                        self.get_option("filter_attr"),
                        self.get_option("filter_pattern"),
                    )
                else:
                    inventory = service.inventory
                    
                # Process each device
                for item in inventory:
                    device = inventory[item]
                    device_name = device.name
                    
                    # Add host to inventory
                    self.inventory.add_host(device_name, group="radkit_devices")
                    
                    # Set ansible_host - check overrides first, then SSH proxy mode, then device host
                    if device_name in ansible_host_overrides:
                        ansible_host = ansible_host_overrides[device_name]
                    elif ssh_proxy_mode:
                        ansible_host = "127.0.0.1"
                    else:
                        ansible_host = device.host
                        
                    self.inventory.set_variable(device_name, "ansible_host", ansible_host)
                    
                    # Set ansible_port if specified in overrides or SSH proxy mode
                    if device_name in ansible_port_overrides:
                        ansible_port = ansible_port_overrides[device_name]
                        self.inventory.set_variable(device_name, "ansible_port", ansible_port)
                    elif ssh_proxy_mode:
                        # Use device-specific SSH proxy port or default
                        proxy_port = ssh_proxy_port_overrides.get(device_name, ssh_proxy_port)
                        self.inventory.set_variable(device_name, "ansible_port", proxy_port)
                    
                    # Set RADKit-specific variables
                    self.inventory.set_variable(device_name, "radkit_device_type", device.device_type)
                    self.inventory.set_variable(device_name, "radkit_forwarded_tcp_ports", device.forwarded_tcp_ports)
                    self.inventory.set_variable(device_name, "radkit_service_serial", service_serial)
                    self.inventory.set_variable(
                        device_name,
                        "radkit_proxy_dn",
                        f'{device_name}.{service_serial}.proxy',
                    )
                    
                    # Set SSH proxy specific variables if in SSH proxy mode
                    if ssh_proxy_mode:
                        self.inventory.set_variable(
                            device_name, 
                            "ansible_user", 
                            f"{device_name}@{service_serial}"
                        )
                        self.inventory.set_variable(
                            device_name,
                            "ansible_ssh_common_args",
                            "-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null"
                        )

                    # Use constructed features for grouping
                    strict = self.get_option("strict") or False
                    
                    # Create groups based on variable values
                    host_attr = dict(inventory[item].attributes.internal) if hasattr(inventory[item], 'attributes') else {}
                    # Add device_type to attributes for keyed groups
                    host_attr['device_type'] = device.device_type
                    
                    # Only call if keyed_groups is defined
                    keyed_groups = self.get_option("keyed_groups")
                    if keyed_groups:
                        self._add_host_to_keyed_groups(
                            keyed_groups,
                            host_attr,
                            device_name,
                            strict=strict,
                        )
            
        except Exception as e:
            display.warning(f"Error populating RADKit inventory: {str(e)}")
            display.vvv(traceback.format_exc())
            raise AnsibleParserError(f'Unable to get hosts from RADKIT: {to_native(e)}')

    def verify_file(self, path):
        """Return the possibly of a file being consumable by this plugin."""
        return super(InventoryModule, self).verify_file(path) and path.endswith(
            ("radkit_devices.yaml", "radkit_devices.yml")
        )

    def parse(self, inventory, loader, path, cache=True):
        if not HAS_RADKIT:
            raise AnsibleError(
                "RADkit python library missing. Please install client. For help go to https://radkit.cisco.com"
            )
        super(InventoryModule, self).parse(inventory, loader, path, cache)
        self._read_config_data(path)
        self._populate()
