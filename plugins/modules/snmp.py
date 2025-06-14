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
  - Executes SNMP GET, WALK, GET_NEXT, and GET_BULK operations through RADKit infrastructure
  - Supports both device name and host-based device identification
  - Supports multiple OIDs in a single request for efficient bulk operations
  - Provides configurable timeouts, retries, limits, and concurrency settings
  - Returns structured SNMP response data with comprehensive error handling
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
            - SNMP OID or list of OIDs to query
            - Can be dot-separated strings like "1.3.6.1.2.1.1.1.0" or tuple of integers
            - Multiple OIDs can be provided for bulk operations
        required: True
        type: raw
    action:
        description:
            - Action to run on SNMP API
            - get - Get specific OID values
            - walk - Walk OID tree (GETNEXT for SNMPv1, GETBULK for SNMPv2+)
            - get_next - Get next OID values after specified OIDs
            - get_bulk - Get multiple values after each OID (SNMPv2+ only)
        default: get
        type: str
        choices: ['get', 'walk', 'get_next', 'get_bulk']
    request_timeout:
        description:
            - Timeout for individual SNMP requests in seconds
        default: 10
        type: float
    limit:
        description:
            - Maximum number of OIDs to look up in one request (get/get_next)
            - Maximum number of SNMP entries to fetch in one request (walk)
            - Number of SNMP entries to get after each OID (get_bulk)
        required: False
        type: int
    retries:
        description:
            - How many times to retry SNMP requests if they timeout
        required: False
        type: int
    concurrency:
        description:
            - Maximum number of queries to fetch at once (walk/get_bulk only)
        default: 100
        type: int
    include_errors:
        description:
            - Include error rows in the output
        default: False
        type: bool
    include_mib_info:
        description:
            - Include MIB information (labels, modules, variables) in output
        default: False
        type: bool
    output_format:
        description:
            - Format of the output data
            - simple - Basic OID and value pairs
            - detailed - Include all available SNMP row information
        default: simple
        type: str
        choices: ['simple', 'detailed']
extends_documentation_fragment: cisco.radkit.radkit_client
requirements:
    - radkit
author: Scott Dozier (@scdozier)
"""

RETURN = r"""
data:
    description: SNMP Response data containing OID values and metadata
    returned: success
    type: list
    elements: dict
    contains:
        device_name:
            description: Name of the device that responded
            type: str
            sample: "router1"
        oid:
            description: The SNMP OID as a dot-separated string
            type: str
            sample: "1.3.6.1.2.1.1.1.0"
        value:
            description: The SNMP value returned
            type: raw
            sample: "Cisco IOS Software"
        type:
            description: ASN.1 type of the SNMP value (only in detailed format)
            type: str
            sample: "OctetString"
            returned: when output_format is detailed
        value_str:
            description: String representation of the value (only in detailed format)
            type: str
            sample: "Cisco IOS Software"
            returned: when output_format is detailed
        is_error:
            description: Whether this row contains an error (only in detailed format)
            type: bool
            sample: false
            returned: when output_format is detailed
        error_code:
            description: SNMP error code if is_error is true (only in detailed format)
            type: int
            sample: 0
            returned: when output_format is detailed and is_error is true
        error_str:
            description: SNMP error string if is_error is true (only in detailed format)
            type: str
            sample: "noSuchName"
            returned: when output_format is detailed and is_error is true
        label:
            description: MIB-resolved object ID (only when include_mib_info is true)
            type: str
            sample: "iso.org.dod.internet.mgmt.mib-2.system.sysDescr"
            returned: when include_mib_info is true
        mib_module:
            description: MIB module name (only when include_mib_info is true)
            type: str
            sample: "SNMPv2-MIB"
            returned: when include_mib_info is true
        mib_variable:
            description: MIB variable name (only when include_mib_info is true)
            type: str
            sample: "sysDescr"
            returned: when include_mib_info is true
        mib_str:
            description: Full MIB string representation (only when include_mib_info is true)
            type: str
            sample: "SNMPv2-MIB::sysDescr.0"
            returned: when include_mib_info is true
"""
EXAMPLES = """
    - name: Simple SNMP Get
      cisco.radkit.snmp:
        device_name: router1
        oid: "1.3.6.1.2.1.1.1.0"
        action: get
      register: snmp_output
      delegate_to: localhost

    - name: SNMP Walk with detailed output
      cisco.radkit.snmp:
        device_name: router1
        oid: "1.3.6.1.2.1.1"
        action: walk
        output_format: detailed
        include_mib_info: true
      register: snmp_output
      delegate_to: localhost

    - name: Multiple OID Get with error handling
      cisco.radkit.snmp:
        device_host: "192.168.1.1"
        oid:
          - "1.3.6.1.2.1.1.1.0"
          - "1.3.6.1.2.1.1.2.0"
          - "1.3.6.1.2.1.1.3.0"
        action: get
        include_errors: true
        retries: 3
        request_timeout: 15
      register: snmp_output
      delegate_to: localhost

    - name: SNMP Get Next
      cisco.radkit.snmp:
        device_name: switch1
        oid: "1.3.6.1.2.1.2.2.1.1"
        action: get_next
        limit: 10
      register: snmp_output
      delegate_to: localhost

    - name: SNMP Get Bulk (SNMPv2+ only)
      cisco.radkit.snmp:
        device_name: router1
        oid: "1.3.6.1.2.1.2.2.1"
        action: get_bulk
        limit: 20
        concurrency: 50
        request_timeout: 30
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
VALID_SNMP_ACTIONS = ["get", "walk", "get_next", "get_bulk"]
DEFAULT_REQUEST_TIMEOUT = 10.0
DEFAULT_CONCURRENCY = 100
VALID_OUTPUT_FORMATS = ["simple", "detailed"]

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


def _normalize_oids(oids: Union[str, List[str]]) -> List[str]:
    """Normalize OID input to a list of strings.

    Args:
        oids: Single OID string or list of OID strings

    Returns:
        List of OID strings

    Raises:
        AnsibleRadkitValidationError: If OID format is invalid
    """
    if isinstance(oids, str):
        return [oids]
    elif isinstance(oids, list):
        return oids
    else:
        raise AnsibleRadkitValidationError(
            f"OID must be a string or list of strings, got {type(oids)}"
        )


def _validate_output_format(output_format: str) -> None:
    """Validate the output format parameter.

    Args:
        output_format: The output format to validate

    Raises:
        AnsibleRadkitValidationError: If format is not valid
    """
    if output_format.lower() not in VALID_OUTPUT_FORMATS:
        raise AnsibleRadkitValidationError(
            f"Output format '{output_format}' is not valid. Must be one of: {', '.join(VALID_OUTPUT_FORMATS)}"
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
    inventory: Dict[str, Any],
    action: str,
    oids: List[str],
    timeout: float,
    limit: Optional[int] = None,
    retries: Optional[int] = None,
    concurrency: int = DEFAULT_CONCURRENCY,
    include_errors: bool = False,
    include_mib_info: bool = False,
    output_format: str = "simple",
) -> List[Dict[str, Union[str, Any]]]:
    """Execute SNMP operation on device.

    Args:
        inventory: Device inventory dictionary
        action: SNMP action (get, walk, get_next, get_bulk)
        oids: List of SNMP OIDs to query
        timeout: Request timeout in seconds
        limit: Maximum number of entries per request
        retries: Number of retry attempts
        concurrency: Maximum concurrent queries
        include_errors: Whether to include error rows
        include_mib_info: Whether to include MIB information
        output_format: Output format ('simple' or 'detailed')

    Returns:
        List of SNMP result dictionaries

    Raises:
        AnsibleRadkitOperationError: If SNMP operation fails
    """
    return_data = []

    for device_name in inventory:
        try:
            logger.info(
                f"Executing SNMP {action} on device {device_name} for OIDs {oids}"
            )

            # Get the appropriate SNMP function
            snmp_func = getattr(inventory[device_name].snmp, action.lower())

            # Build function arguments
            kwargs = {}
            if timeout is not None:
                kwargs["timeout"] = timeout
            if limit is not None:
                kwargs["limit"] = limit
            if retries is not None:
                kwargs["retries"] = retries
            if action.lower() in ["walk", "get_bulk"] and concurrency is not None:
                kwargs["concurrency"] = concurrency

            # Execute SNMP operation
            if len(oids) == 1:
                snmp_results = snmp_func(oids[0], **kwargs).wait().result
            else:
                snmp_results = snmp_func(oids, **kwargs).wait().result

            # Process results based on output format
            if include_errors:
                results_to_process = snmp_results
            else:
                results_to_process = snmp_results.without_errors()

            for row in results_to_process:
                result_dict = {
                    "device_name": device_name,
                    "oid": results_to_process[row].oid_str,
                    "value": results_to_process[row].value,
                }

                if output_format == "detailed":
                    result_dict.update(
                        {
                            "type": results_to_process[row].type,
                            "value_str": results_to_process[row].value_str,
                            "is_error": results_to_process[row].is_error,
                        }
                    )

                    if results_to_process[row].is_error:
                        result_dict.update(
                            {
                                "error_code": results_to_process[row].error_code,
                                "error_str": results_to_process[row].error_str,
                            }
                        )

                    if include_mib_info:
                        result_dict.update(
                            {
                                "label": results_to_process[row].label_str,
                                "mib_module": results_to_process[row].mib_module,
                                "mib_variable": results_to_process[row].mib_variable,
                                "mib_str": results_to_process[row].mib_str,
                            }
                        )

                return_data.append(result_dict)

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
        action = params.get("action", "get")
        oid_input = params.get("oid")
        timeout = params.get("request_timeout", DEFAULT_REQUEST_TIMEOUT)
        limit = params.get("limit")
        retries = params.get("retries")
        concurrency = params.get("concurrency", DEFAULT_CONCURRENCY)
        include_errors = params.get("include_errors", False)
        include_mib_info = params.get("include_mib_info", False)
        output_format = params.get("output_format", "simple")

        # Validate inputs
        _validate_snmp_action(action)
        _validate_output_format(output_format)

        # Normalize OIDs to list
        oids = _normalize_oids(oid_input)

        # Get device inventory
        inventory = _get_device_inventory(radkit_service, device_name, device_host)

        # Execute SNMP operation
        snmp_data = _execute_snmp_operation(
            inventory=inventory,
            action=action,
            oids=oids,
            timeout=timeout,
            limit=limit,
            retries=retries,
            concurrency=concurrency,
            include_errors=include_errors,
            include_mib_info=include_mib_info,
            output_format=output_format,
        )

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
            "oid": {"type": "raw", "required": True},
            "request_timeout": {"type": "float", "default": DEFAULT_REQUEST_TIMEOUT},
            "limit": {"type": "int", "required": False},
            "retries": {"type": "int", "required": False},
            "concurrency": {"type": "int", "default": DEFAULT_CONCURRENCY},
            "include_errors": {"type": "bool", "default": False},
            "include_mib_info": {"type": "bool", "default": False},
            "output_format": {
                "type": "str",
                "default": "simple",
                "choices": VALID_OUTPUT_FORMATS,
            },
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
