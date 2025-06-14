#!/usr/bin/python
# -*- coding: utf-8 -*-
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""
Ansible Module for Cisco RADKit Control API Device Management

This module provides comprehensive device lifecycle management for RADKit
inventory using the Control API. It supports adding, updating, and removing
devices with full configuration validation and error handling.
"""

from __future__ import absolute_import, division, print_function
from typing import Any, Dict, List, Optional, Tuple, Union
import logging

__metaclass__ = type

DOCUMENTATION = """
---
module: controlapi_device
short_description: Manage devices in RADKit inventory via Control API
version_added: "1.8.0"
description:
  - Adds, updates, or removes devices in the RADKit inventory using RADKit's Control API
  - Provides comprehensive device configuration management with validation
  - Supports credential management and device state enforcement
  - Includes detailed error reporting and status tracking
options:
    radkit_service_name:
        description:
            - Name of the RADKit service to connect to.
        required: True
        type: str
    data:
        description:
            - Dictionary containing device information.
        required: True
        type: dict
        suboptions:
            name:
                description:
                    - Name of the device in the RADKit inventory.
                required: True
                type: str
            host:
                description:
                    - Hostname or IP address of the device. Required if state is 'present' or 'updated'.
                required: False
                type: str
            device_type:
                description:
                    - Type of the device in the RADKit inventory.
                required: False
                type: str
                choices: [AIRE_OS, APIC, ASA, BROADWORKS, CATALYST_CENTER, CEDGE, CIMC, CISCO_AP_OS, CML, CMS, CPS, CROSSWORK, CSPC, CUCM, CVOS, CVP, ESA, EXPRESSWAY, FDM, FMC, FTD, GENERIC, HYPERFLEX, INTERSIGHT, IOS_XE, IOS_XR, ISE, LINUX, NCS_2000, NEXUS_DASHBOARD, NSO, NX_OS, RADKIT_SERVICE, ROUTED_PON, SMA, SPLUNK, STAR_OS, UCCE, UCS_MANAGER, ULTRA_CORE_5G_AMF, ULTRA_CORE_5G_PCF, ULTRA_CORE_5G_SMF, WAS, WLC, VMANAGE]
            enabled:
                description:
                    - Boolean to enable or disable the device.
                type: bool
                default: True
            description:
                description:
                    - Description of the device.
                type: str
                default: ''
            labels:
                description:
                    - Labels to be assigned to the device.
                type: list
                elements: str
                default: []
            forwarded_tcp_ports:
                description:
                    - TCP ports to be forwarded.
                type: str
            terminal:
                description:
                    - Terminal access information.
                type: dict
                suboptions:
                    port:
                        description:
                            - Port for terminal access.
                        type: int
                        required: True
                    username:
                        description:
                            - Username for terminal access.
                        type: str
                        required: True
                    password:
                        description:
                            - Password for terminal access.
                        type: str
                        required: True
                        no_log: true
                    private_key_password:
                        description:
                            - Private key password for terminal access.
                        type: str
                        required: False
                    private_key:
                        description:
                            - Private key for terminal access.
                        type: str
                        required: False
                    enable_set:
                        description:
                            - Enable set for terminal access.
                        type: str
                        required: False
                    enable:
                        description:
                            - Enable command for terminal access.
                        type: str
                        required: False
    state:
        description:
            - Desired state of the device. Use 'present' to ensure device is present, 'updated' to update device, or 'absent' to remove device.
        required: True
        type: str
        choices: [present, absent, updated]
extends_documentation_fragment: cisco.radkit.radkit_client
requirements:
    - radkit
author: Scott Dozier (@scdozier)
"""

RETURN = r"""
device:
    description: Information about the device operation result.
    returned: success
    type: dict
"""

EXAMPLES = """
    - name: Add a device to RADKit inventory
      cisco.radkit.controlapi_device:
        radkit_service_name: radkit
        data:
          name: Test12345
          host: 12345
          device_type: IOS_XE
          enabled: True
          description: my test device
          forwarded_tcp_ports: '22'
          terminal:
            port: 22
            username: test
            password: mypassword
            private_key_password: my_private_key_password
            private_key: my_private_key
            enable_set: my_enable_set
            enable: my_enable_command
        state: present
      register: device_output
      delegate_to: localhost

    - name: Remove device from RADKit inventory with only name
      cisco.radkit.controlapi_device:
        radkit_service_name: radkit
        data:
          name: test123
        state: absent
      delegate_to: localhost
"""

import json

try:
    from radkit_client import Client
    from radkit_service.control_api import ControlAPI, StoredDeviceWithMetadata
    from radkit_service.webserver.models.devices import (
        NewDevice,
        NewTerminal,
        DeviceType,
    )

    HAS_RADKIT = True
except ImportError:
    HAS_RADKIT = False

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.cisco.radkit.plugins.module_utils.client import (
    radkit_client_argument_spec,
    RadkitClientService,
)
from ansible_collections.cisco.radkit.plugins.module_utils.exceptions import (
    AnsibleRadkitError,
    AnsibleRadkitConnectionError,
    AnsibleRadkitValidationError,
    AnsibleRadkitOperationError,
)

# Constants for device management
DEVICE_STATE_PRESENT = "present"
DEVICE_STATE_ABSENT = "absent"
DEVICE_STATE_UPDATED = "updated"

VALID_DEVICE_STATES = [DEVICE_STATE_PRESENT, DEVICE_STATE_ABSENT, DEVICE_STATE_UPDATED]

# Setup module logger
logger = logging.getLogger(__name__)


__metaclass__ = type


def run_action(module: AnsibleModule, control_api: ControlAPI):
    """
    Runs actions to create or delete devices via RADKit ControlAPI
    """
    results = {}
    err = False
    try:
        data = module.params["data"]
        state = module.params["state"]

        if state == "updated":
            devices = control_api.list_devices()
            device_list = devices.result

            for device in device_list:
                if device.name == data["name"]:
                    # If state is 'update' or device already exists, delete it first
                    apiresult = control_api.delete_devices([str(device.uuid)])
                    if apiresult.results[0].status.value != "SUCCESS":
                        results[
                            "msg"
                        ] = f"Failed to delete existing device {data['name']}"
                        err = True
                        return results, err
                    break
        if state in ["present", "updated"]:
            terminal_data = data.get("terminal", {})
            terminal_kwargs = {}

            if terminal_data:
                if terminal_data.get("port") is not None:
                    terminal_kwargs["port"] = terminal_data.get("port")
                if terminal_data.get("username") is not None:
                    terminal_kwargs["username"] = terminal_data.get("username")
                if terminal_data.get("password") is not None:
                    terminal_kwargs["password"] = terminal_data.get("password")
                if terminal_data.get("private_key_password") is not None:
                    terminal_kwargs["privateKeyPassword"] = terminal_data.get(
                        "private_key_password"
                    )
                if terminal_data.get("private_key") is not None:
                    terminal_kwargs["privateKey"] = terminal_data.get("private_key")
                if terminal_data.get("enable_set") is not None:
                    terminal_kwargs["enableSet"] = terminal_data.get("enable_set")
                if terminal_data.get("enable") is not None:
                    terminal_kwargs["enable"] = terminal_data.get("enable")

            new_terminal = NewTerminal(**terminal_kwargs) if terminal_kwargs else None

            new_device = NewDevice(
                name=data["name"],
                host=data["host"],
                deviceType=DeviceType[data["device_type"]],
                enabled=data.get("enabled", True),
                labels=data.get("labels", []),
                description=data.get("description", ""),
                forwardedTcpPorts=data.get("forwarded_tcp_ports", ""),
                terminal=new_terminal,
            )
            dev_create = control_api.create_device(new_device)
            if isinstance(dev_create, bytes):
                err = True
                results["msg"] = str(dev_create)
                return results, err

            result = dev_create.result

            if dev_create.status.value == "SUCCESS":
                results["msg"] = str(result)
                results["changed"] = True
            elif (
                dev_create.status.value != "SUCCESS"
                and result.detail[0]["type"] != "DeviceAlreadyExists"
            ):
                raise AnsibleRadkitError(f"Failed to create device: {str(result)}")
            elif result.detail[0]["type"] == "DeviceAlreadyExists":
                results["msg"] = str(result.message)
                results["changed"] = False
            else:
                results["msg"] = str(result.message)
                results["changed"] = False
                err = True

        elif state == "absent":
            devices = control_api.list_devices()
            # Access the result list from the APIResult object
            device_list = devices.result  # Extract the list of devices

            device_names = []  # Initialize an empty list to store device names
            uuids = []  # Initialize an empty list to store device UUIDs
            # Iterate over each device in the extracted list
            for device in device_list:
                if device.name == data["name"]:
                    apiresult = control_api.delete_devices([str(device.uuid)])
                    if apiresult.results[0].status.value == "SUCCESS":
                        results["msg"] = f"Device {data['name']} deleted successfully"
                        results["changed"] = True
                    else:
                        results["msg"] = f"Failed to delete device {data['name']}"
                        err = True
                    return results, err

            results["msg"] = f'Device {data["name"]} not found in inventory'
            results["changed"] = False  # Placeholder for future implementation

    except Exception as e:
        err = True
        results["msg"] = str(e)
        results["changed"] = False

    return results, err


def main():
    spec = radkit_client_argument_spec()
    spec.update(
        dict(
            radkit_service_name=dict(type="str", required=True),
            data=dict(
                type="dict",
                required=True,
                options=dict(
                    name=dict(type="str", required=True),
                    host=dict(type="str", required=False),
                    device_type=dict(
                        type="str",
                        required=False,
                        choices=[
                            "AIRE_OS",
                            "APIC",
                            "ASA",
                            "BROADWORKS",
                            "CATALYST_CENTER",
                            "CEDGE",
                            "CIMC",
                            "CISCO_AP_OS",
                            "CML",
                            "CMS",
                            "CPS",
                            "CROSSWORK",
                            "CSPC",
                            "CUCM",
                            "CVOS",
                            "CVP",
                            "ESA",
                            "EXPRESSWAY",
                            "FDM",
                            "FMC",
                            "FTD",
                            "GENERIC",
                            "HYPERFLEX",
                            "INTERSIGHT",
                            "IOS_XE",
                            "IOS_XR",
                            "ISE",
                            "LINUX",
                            "NCS_2000",
                            "NEXUS_DASHBOARD",
                            "NSO",
                            "NX_OS",
                            "RADKIT_SERVICE",
                            "ROUTED_PON",
                            "SMA",
                            "SPLUNK",
                            "STAR_OS",
                            "UCCE",
                            "UCS_MANAGER",
                            "ULTRA_CORE_5G_AMF",
                            "ULTRA_CORE_5G_PCF",
                            "ULTRA_CORE_5G_SMF",
                            "WAS",
                            "WLC",
                            "VMANAGE",
                        ],
                    ),
                    enabled=dict(type="bool", default=True),
                    labels=dict(type="list", elements="str", default=[]),
                    description=dict(type="str", default=""),
                    forwarded_tcp_ports=dict(type="str", default="", required=False),
                    terminal=dict(
                        type="dict",
                        required=False,
                        options=dict(
                            port=dict(type="int", required=True),
                            username=dict(type="str", required=True),
                            password=dict(type="str", required=True, no_log=True),
                            private_key_password=dict(type="str", required=False),
                            private_key=dict(type="str", required=False),
                            enable_set=dict(type="str", required=False),
                            enable=dict(type="str", required=False),
                        ),
                    ),
                ),
            ),
            state=dict(
                type="str", required=True, choices=["present", "absent", "updated"]
            ),
        )
    )
    module = AnsibleModule(argument_spec=spec, supports_check_mode=False)

    if module.params["state"].lower() != "absent" and not module.params["data"].get(
        "host", None
    ):
        # If the state is not 'absent', host is required
        module.fail_json(msg="Host param is required if state=present or state=updated")

    # if state is not absent then device_type is required
    if module.params["state"].lower() != "absent" and not module.params["data"].get(
        "device_type", None
    ):
        # If the state is not 'absent', device_type is required
        module.fail_json(
            msg="device_type param is required if state=present or state=updated"
        )

    if not HAS_RADKIT:
        module.fail_json(
            msg="Python module cisco_radkit_service and cisco_radkit_client 1.8.0+ is required for this module!"
        )

    with Client.create() as client:
        radkit_service_name = module.params["radkit_service_name"]
        service = RadkitClientService(client, module.params).radkit_service
        if radkit_service_name not in service.inventory:
            module.fail_json(
                msg=f"Service {radkit_service_name} not found in inventory"
            )
        control_api = ControlAPI.from_radkit_client_device(
            service.inventory[radkit_service_name]
        )

        results, err = run_action(module, control_api)

    if err:
        module.fail_json(**results)

    module.exit_json(**results)


if __name__ == "__main__":
    main()
