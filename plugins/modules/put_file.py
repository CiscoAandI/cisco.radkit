#!/usr/bin/python
# -*- coding: utf-8 -*-
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""
Ansible Module for Cisco RADKit File Upload Operations

This module provides comprehensive file upload functionality via RADKit,
supporting both SCP and SFTP protocols for transferring files to network
devices. Features proper error handling, transfer status monitoring,
and support for various device identification methods.
"""

from __future__ import absolute_import, division, print_function
from typing import Any, Dict, List, Optional, Tuple, Union
import time
import logging

__metaclass__ = type

DOCUMENTATION = """
---
module: put_file
short_description: Uploads a file to a remote device using SCP or SFTP via RADKit
version_added: "1.7.5"
description:
  - Uploads a file to a remote device using SCP or SFTP via RADKit
options:
    device_name:
        description:
            - Name of device as it shows in RADKit inventory
        required: False
        type: str
    device_host:
        description:
            - Hostname or IP address of the device as it appears in the RADKit inventory. Use either device_name or device_host.
        required: False
        type: str
    local_path:
        description:
            - Path to the local file to be uploaded
        required: True
        type: str
    remote_path:
        description:
            - Path on the remote device where the file will be uploaded
        required: True
        type: str
    protocol:
        description:
            - Protocol to use for uploading, either scp or sftp
        required: True
        type: str
extends_documentation_fragment: cisco.radkit.radkit_client
requirements:
    - radkit
author: Scott Dozier (@scdozier)
"""

RETURN = r"""
message:
    description: Status message
    type: str
    returned: always
"""

EXAMPLES = """
- name: Upload file to device using SCP
  put_file:
    device_name: router1
    local_path: /path/to/local/file
    remote_path: /path/to/remote/file
    protocol: scp

- name: Upload file to device using SFTP
  put_file:
    device_name: router1
    local_path: /path/to/local/file
    remote_path: /path/to/remote/file
    protocol: sftp
"""
import json

try:
    from radkit_client.sync import Client

    HAS_RADKIT = True
except ImportError:
    HAS_RADKIT = False
    Client = None

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

# Setup module logger
logger = logging.getLogger(__name__)

__metaclass__ = type

# Constants for file upload operations
SUPPORTED_PROTOCOLS = ["scp", "sftp"]
TRANSFER_CHECK_INTERVAL = 0.5
TRANSFER_DONE_STATUS = "TRANSFER_DONE"


def _validate_protocol(protocol: str) -> None:
    """Validate the upload protocol.

    Args:
        protocol: Protocol to validate (scp or sftp)

    Raises:
        AnsibleRadkitValidationError: If protocol is not supported
    """
    if protocol.lower() not in SUPPORTED_PROTOCOLS:
        raise AnsibleRadkitValidationError(
            f"Protocol '{protocol}' is not supported. Must be one of: {', '.join(SUPPORTED_PROTOCOLS)}"
        )


def _get_device_inventory(
    radkit_service: RadkitClientService,
    device_name: Optional[str],
    device_host: Optional[str],
) -> Dict[str, Any]:
    """Get device inventory for file upload operations.

    Args:
        radkit_service: RADKit service instance
        device_name: Device name identifier
        device_host: Device host identifier

    Returns:
        Device inventory dictionary

    Raises:
        AnsibleRadkitValidationError: If no device found or invalid parameters
    """
    if not device_name and not device_host:
        raise AnsibleRadkitValidationError(
            "You must specify either a device_name or device_host"
        )

    try:
        if device_name:
            logger.info(f"Getting inventory for device name: {device_name}")
            inventory = radkit_service.get_inventory_by_filter(device_name, "name")
            if not inventory:
                raise AnsibleRadkitValidationError(
                    f"No devices found in RADKit inventory with name: {device_name}"
                )
        else:
            logger.info(f"Getting inventory for device host: {device_host}")
            inventory = radkit_service.get_inventory_by_filter(device_host, "host")
            if not inventory:
                raise AnsibleRadkitValidationError(
                    f"No devices found in RADKit inventory with host: {device_host}"
                )

        return inventory
    except Exception as e:
        logger.error(f"Failed to get device inventory: {e}")
        raise AnsibleRadkitConnectionError(f"Failed to get device inventory: {e}")


def _get_upload_function(inventory: Dict[str, Any], device: str, protocol: str) -> Any:
    """Get the appropriate upload function based on protocol.

    Args:
        inventory: Device inventory
        device: Device name
        protocol: Upload protocol (scp or sftp)

    Returns:
        Upload function

    Raises:
        AnsibleRadkitValidationError: If protocol is invalid
    """
    if protocol == "scp":
        return inventory[device].scp_upload_from_file
    elif protocol == "sftp":
        return inventory[device].sftp_upload_from_file
    else:
        raise AnsibleRadkitValidationError(f"Unsupported protocol: {protocol}")


def _monitor_transfer(result: Any) -> None:
    """Monitor file transfer until completion.

    Args:
        result: Transfer result object

    Raises:
        AnsibleRadkitOperationError: If transfer fails
    """
    try:
        while result.result.status.value != TRANSFER_DONE_STATUS:
            time.sleep(TRANSFER_CHECK_INTERVAL)

        logger.info(
            f"File transfer completed successfully, bytes written: {result.bytes_written}"
        )
    except Exception as e:
        logger.error(f"File transfer monitoring failed: {e}")
        raise AnsibleRadkitOperationError(f"File transfer monitoring failed: {e}")


def run_upload(
    module: AnsibleModule, radkit_service: RadkitClientService
) -> Tuple[Dict[str, Any], bool]:
    """Execute file upload operations via RADKit service.

    Args:
        module: Ansible module instance
        radkit_service: RADKit service client

    Returns:
        Tuple of (results dictionary, error boolean)
    """
    try:
        params = module.params
        device_name = params.get("device_name")
        device_host = params.get("device_host")
        local_path = params["local_path"]
        remote_path = params["remote_path"]
        protocol = params["protocol"].lower()

        # Validate inputs
        _validate_protocol(protocol)

        # Get device inventory
        inventory = _get_device_inventory(radkit_service, device_name, device_host)

        results = {}

        for device in inventory:
            logger.info(f"Starting {protocol.upper()} upload to device {device}")
            logger.info(f"Local path: {local_path}, Remote path: {remote_path}")

            # Get upload function
            upload_func = _get_upload_function(inventory, device, protocol)

            # Perform file upload
            result = upload_func(remote_path=remote_path, local_path=local_path).wait()

            # Monitor transfer completion
            _monitor_transfer(result)

            results.update(
                {
                    "device_name": device,
                    "message": f"status:{result.status.value} bytes_written:{str(result.bytes_written)}",
                    "changed": True,
                }
            )

        logger.info("File upload operation completed successfully")
        return results, False

    except (
        AnsibleRadkitValidationError,
        AnsibleRadkitConnectionError,
        AnsibleRadkitOperationError,
    ) as e:
        logger.error(f"RADKit file upload operation failed: {e}")
        return {"msg": str(e), "changed": False}, True
    except Exception as e:
        logger.error(f"Unexpected error during file upload operation: {e}")
        import traceback

        return {"msg": str(e) + "\n" + traceback.format_exc(), "changed": False}, True


def main() -> None:
    """Main function to run the file upload module.

    Sets up the Ansible module and executes file upload operations.
    """
    # Define argument specification
    spec = radkit_client_argument_spec()
    spec.update(
        {
            "device_name": {"type": "str", "required": False},
            "device_host": {"type": "str", "required": False},
            "local_path": {"type": "str", "required": True},
            "remote_path": {"type": "str", "required": True},
            "protocol": {
                "type": "str",
                "required": True,
                "choices": SUPPORTED_PROTOCOLS,
            },
        }
    )

    # Create Ansible module
    module = AnsibleModule(
        argument_spec=spec,
        supports_check_mode=False,
        required_one_of=[["device_name", "device_host"]],
    )

    # Check for required library
    if not HAS_RADKIT:
        module.fail_json(msg="Python module cisco_radkit is required for this module!")

    try:
        # Create RADKit client and service
        if not Client:
            module.fail_json(msg="RADKit client not available - check installation")

        with Client.create() as client:
            radkit_service = RadkitClientService(client, module.params)
            results, err = run_upload(module, radkit_service)

        # Return results
        if err:
            module.fail_json(**results)
        else:
            module.exit_json(**results)

    except Exception as e:
        logger.error(f"Critical error in file upload module: {e}")
        module.fail_json(msg=f"Critical error in file upload module: {e}")


if __name__ == "__main__":
    main()
