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
    - Reads inventories from the GitLab API.
    - Uses a YAML configuration file gitlab_runners.[yml|yaml].
options:
    plugin:
        description: The name of this plugin, it should always be set to 'gitlab_runners' for this plugin to recognize it as it's own.
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

"""

EXAMPLES = """
# radkit_devices.yml
plugin: cisco.radkit.radkit

# Example using constructed features
plugin: cisco.radkit.radkit
strict: False
keyed_groups:
  # group devices based on device type (ex radkit_device_type_IOS)
  - prefix: radkit_device_type
    key: 'device_type'
  # group devices based on description
  - prefix: radkit_description
    key: 'description'

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
        self.inventory.add_group("radkit_devices")
        self.inventory.add_host("test", group="radkit_devices")

        try:
            with Client.create() as radkit_sync_client:
                display.v(self.get_option("radkit_client_private_key_password_base64"))
                display.v(
                    f"Making a RADKIT certificate_login ... identity={self.get_option('radkit_identity')}"
                )
                client = radkit_sync_client.certificate_login(
                    identity=self.get_option("radkit_identity"),
                    ca_path=self.get_option("radkit_client_ca_path", None),
                    key_path=self.get_option("radkit_client_key_path", None),
                    cert_path=self.get_option("radkit_client_cert_path", None),
                    private_key_password=base64.b64decode(
                        (self.get_option("radkit_client_private_key_password_base64"))
                    ).decode("utf8"),
                )
                display.vvv(
                    f"RADKIT connection successful, connecting to service {self.get_option('radkit_service_serial')}"
                )
                service = client.service(
                    self.get_option("radkit_service_serial")
                ).wait()
                display.vvv(
                    f"Sucessfully connected to serial {self.get_option('radkit_service_serial')}, getting inventory.."
                )

                if self.get_option("filter_attr") and self.get_option("filter_pattern"):
                    inventory = service.inventory.filter(
                        self.get_option("filter_attr"),
                        self.get_option("filter_pattern"),
                    )
                else:
                    inventory = service.inventory
                for item in inventory:
                    device = inventory[item]
                    self.inventory.add_host(device.name, group="radkit_devices")
                    self.inventory.set_variable(
                        device.name, "ansible_host", device.host
                    )
                    self.inventory.set_variable(
                        device.name, "radkit_device_type", device.device_type
                    )
                    self.inventory.set_variable(
                        device.name,
                        "radkit_forwarded_tcp_ports",
                        device.forwarded_tcp_ports,
                    )
                    self.inventory.set_variable(
                        device.name,
                        "radkit_proxy_dn",
                        f'{device.name}.{self.get_option("radkit_service_serial")}.proxy',
                    )

                    # Use constructed if applicable
                    strict = self.get_option("strict")

                    # Create groups based on variable values and add the corresponding hosts to it
                    host_attr = dict(inventory[item].attributes.internal)
                    self._add_host_to_keyed_groups(
                        self.get_option("keyed_groups"),
                        host_attr,
                        device.name,
                        strict=strict,
                    )
        except Exception as e:
            print(traceback.format_exc())
            # raise AnsibleParserError('Unable to get hosts from RADKIT: %s' % to_native(e))

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
