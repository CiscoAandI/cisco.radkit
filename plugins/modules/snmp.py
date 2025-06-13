#!/usr/bin/python
# -*- coding: utf-8 -*-
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""
Ansible Module for Cisco RADKit SNMP Operations

This module provides comprehensive SNMP functionality via RADKit, supporting
both GET and WALK operations with proper timeout handling, error management,
and structured response processing for network monitoring and management.
"""

from __future__ import absolute_import, division, print_function
from typing import Any, Dict, List, Optional, Tuple, Union
import logging

__metaclass__ = type

DOCUMENTATION = """
---
module: snmp
short_description: Perform SNMP operations via RADKit
version_added: "0.5.0"
description:
  - Executes SNMP GET and WALK operations through RADKit infrastructure
  - Supports both device name and host-based device identification
  - Provides configurable timeouts and comprehensive error handling
  - Returns structured SNMP response data for automation workflows
  - Ideal for network monitoring, device discovery, and configuration management
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
    oid:
        description:
            - SNMP OID
        required: True
        type: str
    action:
        description:
            - Action to run on SNMP API. Supports either get or walk
        default: get
        type: str
    request_timeout:
        description:
            - Timeout for individual SNMP requests
        default: 10
        type: float
extends_documentation_fragment: cisco.radkit.radkit_client
requirements:
    - radkit
author: Scott Dozier (@scdozier)
"""

RETURN = r"""
data:
    description: SNMP Response
    returned: success
    type: list
"""
EXAMPLES = """
    - name:  SNMP Walk device
      cisco.radkit.snmp:
        device_name: router1
        oid: 1.3.6.1.2.1.1
        action: walk
      register: snmp_output
      delegate_to: localhost
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

# Constants for SNMP operations
VALID_SNMP_ACTIONS = ["get", "walk"]
DEFAULT_REQUEST_TIMEOUT = 10.0

# Setup module logger
logger = logging.getLogger(__name__)

__metaclass__ = type


def _validate_snmp_action(action: str) -> None:
    """Validate the SNMP action parameter.

    Args:
        action: The SNMP action to validate

    Raises:
        AnsibleRadkitValidationError: If action is not valid
    """
    if action.lower() not in VALID_SNMP_ACTIONS:
        raise AnsibleRadkitValidationError(
            f"Action '{action}' is not valid. Must be one of: {', '.join(VALID_SNMP_ACTIONS)}"
        )


def _get_device_inventory(
    radkit_service: RadkitClientService,
    device_name: Optional[str],
    device_host: Optional[str],
) -> Dict[str, Any]:
    """Get device inventory using device name or host.

    Args:
        radkit_service: The RADKit service instance
        device_name: Device name to search for
        device_host: Device host to search for

    Returns:
        Device inventory dictionary

    Raises:
        AnsibleRadkitValidationError: If no device identifier provided or device not found
    """
    if not device_name and not device_host:
        raise AnsibleRadkitValidationError(
            "You must specify either a device_name or device_host"
        )

    try:
        if device_name:
            logger.info(f"Looking up device by name: {device_name}")
            inventory = radkit_service.get_inventory_by_filter(device_name, "name")
            if not inventory:
                raise AnsibleRadkitValidationError(
                    f"No devices found in RADKit inventory with name: {device_name}"
                )
        else:
            logger.info(f"Looking up device by host: {device_host}")
            inventory = radkit_service.get_inventory_by_filter(device_host, "host")
            if not inventory:
                raise AnsibleRadkitValidationError(
                    f"No devices found in RADKit inventory with host: {device_host}"
                )

        return inventory
    except Exception as e:
        logger.error(f"Failed to get device inventory: {e}")
        raise AnsibleRadkitConnectionError(f"Failed to get device inventory: {e}")


def _execute_snmp_operation(
    inventory: Dict[str, Any], action: str, oid: str, timeout: float
) -> List[Dict[str, Union[str, Any]]]:
    """Execute SNMP operation on device.

    Args:
        inventory: Device inventory dictionary
        action: SNMP action (get or walk)
        oid: SNMP OID to query
        timeout: Request timeout in seconds

    Returns:
        List of SNMP result dictionaries

    Raises:
        AnsibleRadkitOperationError: If SNMP operation fails
    """
    return_data = []

    for device_name in inventory:
        try:
            logger.info(
                f"Executing SNMP {action} on device {device_name} for OID {oid}"
            )

            # Get the appropriate SNMP function
            snmp_func = getattr(inventory[device_name].snmp, action.lower())

            # Execute SNMP operation
            snmp_results = snmp_func(oid, timeout=timeout).wait().result

            # Process results
            for row in snmp_results:
                return_data.append(
                    {
                        "oid": snmp_results[row].oid_str,
                        "value": snmp_results[row].value,
                    }
                )

            logger.info(
                f"Successfully executed SNMP {action} on {device_name}, got {len(return_data)} results"
            )

        except AttributeError as e:
            logger.error(f"Invalid SNMP action '{action}': {e}")
            raise AnsibleRadkitValidationError(f"Invalid SNMP action '{action}': {e}")
        except Exception as e:
            logger.error(f"SNMP operation failed on device {device_name}: {e}")
            raise AnsibleRadkitOperationError(
                f"SNMP operation failed on device {device_name}: {e}"
            )

    return return_data


def run_action(
    module: AnsibleModule, radkit_service: RadkitClientService
) -> Tuple[Dict[str, Any], bool]:
    """Execute SNMP operations via RADKit service.

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
        action = params["action"]
        oid = params["oid"]
        timeout = params["request_timeout"]

        # Validate inputs
        _validate_snmp_action(action)

        # Get device inventory
        inventory = _get_device_inventory(radkit_service, device_name, device_host)

        # Execute SNMP operation
        snmp_data = _execute_snmp_operation(inventory, action, oid, timeout)

        return {"data": snmp_data, "changed": False}, False

    except (
        AnsibleRadkitValidationError,
        AnsibleRadkitConnectionError,
        AnsibleRadkitOperationError,
    ) as e:
        logger.error(f"RADKit SNMP operation failed: {e}")
        return {"msg": str(e), "changed": False}, True
    except Exception as e:
        logger.error(f"Unexpected error during SNMP operation: {e}")
        return {"msg": f"Unexpected error: {e}", "changed": False}, True


def main() -> None:
    """Main function to run the SNMP module.

    Sets up the Ansible module, validates parameters, and executes SNMP operations.
    """
    # Define argument specification
    spec = radkit_client_argument_spec()
    spec.update(
        {
            "device_name": {"type": "str", "required": False},
            "device_host": {"type": "str", "required": False},
            "action": {"type": "str", "default": "get", "choices": VALID_SNMP_ACTIONS},
            "oid": {"type": "str", "required": True},
            "request_timeout": {"type": "float", "default": DEFAULT_REQUEST_TIMEOUT},
        }
    )

    # Create Ansible module
    module = AnsibleModule(
        argument_spec=spec,
        supports_check_mode=False,
        mutually_exclusive=[["device_name", "device_host"]],
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
            results, err = run_action(module, radkit_service)

        # Return results
        if err:
            module.fail_json(**results)
        else:
            module.exit_json(**results)

    except Exception as e:
        logger.error(f"Critical error in SNMP module: {e}")
        module.fail_json(msg=f"Critical error in SNMP module: {e}")


if __name__ == "__main__":
    main()
