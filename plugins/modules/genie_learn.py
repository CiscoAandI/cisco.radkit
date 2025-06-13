#!/usr/bin/python
# -*- coding: utf-8 -*-
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""
Ansible Module for Cisco RADKit Genie Learn Operations

This module provides comprehensive Genie learning functionality for automated
network device model extraction and structured data collection. Supports
both single device and multi-device operations with advanced filtering,
OS detection, and model processing capabilities for network automation workflows.
"""

from __future__ import absolute_import, division, print_function
from typing import Any, Dict, List, Optional, Tuple, Union
import logging

__metaclass__ = type

DOCUMENTATION = """
---
module: genie_learn
short_description: Runs a command via RADKit, then through genie parser, returning a parsed result
version_added: "0.2.0"
description:
  - Runs a command via RADKit, then through genie parser, returning a parsed result
options:
    device_name:
        description:
            - Name of device as it shows in RADKit inventory
        required: False
        type: str
    filter_pattern:
        description:
            - Pattern to match RADKit inventory, which can select multiple devices at once. (use instead of device_name)
        required: False
        type: str
    filter_attr:
        description:
            - Attrbute to match RADKit inventory, which can select multiple devices at once. (use with filter_pattern, ex 'name')
        required: False
        type: str
    models:
        description:
            - models to execute on device
        required: True
        type: list
        elements: str
    os:
        description:
            -  The device OS (if omitted, the OS found by fingerprint)
        default: fingerprint
        type: str
    wait_timeout:
        description:
            - Specifies how many seconds RADKit will wait before failing task.
            - Note that the request is not affected, and it will still eventually complete (successfully or unsuccessfully)
            - Can optionally set via environemnt variable RADKIT_ANSIBLE_WAIT_TIMEOUT
        required: False
        default: 0
        type: int
    exec_timeout:
        description:
            - Specifies how many seconds RADKit will for command to complete
            - Can optionally set via environemnt variable RADKIT_ANSIBLE_EXEC_TIMEOUT
        required: False
        default: 0
        type: int
    remove_model_and_device_keys:
        description:
            - Removes the model and device keys from the returned value when running a single model against a single device.
            - NOTE; This does not work with diff
        default: False
        required: False
        type: bool
extends_documentation_fragment: cisco.radkit.radkit_client
requirements:
    - radkit
author: Scott Dozier (@scdozier)
"""

RETURN = r"""
device_name:
    description: Device in Radkit
    returned: success
    type: str
command:
    description: Command
    returned: success
    type: str
exec_status:
    description: Status of exec from RADKit
    returned: success
    type: str
exec_status_message:
    description: Status message from RADKit
    returned: success
    type: str
ansible_module_results:
    description: Dictionary of results is returned if running command on multiple devices or with multiple models
    returned: success
    type: dict
genie_learn_result:
    description: Dictionary of parsed results
    returned: success
    type: dict
"""
EXAMPLES = """
- name: Get parsed output from rtr-csr1 with removed return keys
  cisco.radkit.genie_learn:
    device_name: rtr-csr1
    models: platform
    os: iosxe
    remove_model_and_device_keys: yes
  register: cmd_output
  delegate_to: localhost

- name: Show Chassis Serial Number
  debug:
    msg: "{{ cmd_output['genie_learn_result']['chassis_sn'] }}"


"""
try:
    from radkit_client.sync import Client

    HAS_RADKIT = True
except ImportError:
    HAS_RADKIT = False
    Client = None

from ansible.module_utils.basic import AnsibleModule, env_fallback
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

try:
    import radkit_genie

    HAS_RADKIT_GENIE = True
except ImportError:
    HAS_RADKIT_GENIE = False
    radkit_genie = None

# Setup module logger
logger = logging.getLogger(__name__)

__metaclass__ = type

# Constants for Genie operations
DEFAULT_OS_FINGERPRINT = "fingerprint"
DEFAULT_TIMEOUT = 0


def _validate_device_parameters(
    device_name: Optional[str],
    filter_pattern: Optional[str],
    filter_attr: Optional[str],
) -> None:
    """Validate device identification parameters.

    Args:
        device_name: Device name for single device operations
        filter_pattern: Pattern for multi-device filtering
        filter_attr: Attribute for multi-device filtering

    Raises:
        AnsibleRadkitValidationError: If parameters are invalid
    """
    if not device_name and not (filter_pattern and filter_attr):
        raise AnsibleRadkitValidationError(
            "You must provide either device_name or both filter_pattern and filter_attr"
        )

    if not device_name and filter_pattern and not filter_attr:
        raise AnsibleRadkitValidationError(
            "You must provide both filter_pattern and filter_attr when using multi-device filtering"
        )


def _get_device_inventory(
    radkit_service: RadkitClientService,
    device_name: Optional[str],
    filter_pattern: Optional[str],
    filter_attr: Optional[str],
) -> Dict[str, Any]:
    """Get device inventory for Genie operations.

    Args:
        radkit_service: RADKit service instance
        device_name: Single device name
        filter_pattern: Multi-device filter pattern
        filter_attr: Multi-device filter attribute

    Returns:
        Device inventory dictionary

    Raises:
        AnsibleRadkitValidationError: If no devices found
    """
    try:
        if device_name:
            logger.info(f"Getting inventory for single device: {device_name}")
            inventory = radkit_service.get_inventory_by_filter(device_name, "name")
            if not inventory:
                raise AnsibleRadkitValidationError(
                    f"No devices found in RADKit inventory with name: {device_name}"
                )
        else:
            logger.info(
                f"Getting inventory for multiple devices with pattern: {filter_pattern}, attr: {filter_attr}"
            )
            inventory = radkit_service.get_inventory_by_filter(
                filter_pattern, filter_attr
            )
            if not inventory:
                raise AnsibleRadkitValidationError(
                    f"No devices found in RADKit inventory with attr: {filter_attr} and pattern: {filter_pattern}"
                )

        return inventory
    except Exception as e:
        logger.error(f"Failed to get device inventory: {e}")
        raise AnsibleRadkitConnectionError(f"Failed to get device inventory: {e}")


def _execute_genie_learn(inventory: Dict[str, Any], models: List[str], os: str) -> Any:
    """Execute Genie learn operation on device inventory.

    Args:
        inventory: Device inventory
        models: List of models to learn
        os: Operating system or 'fingerprint'

    Returns:
        Genie learn results

    Raises:
        AnsibleRadkitOperationError: If learn operation fails
    """
    if not radkit_genie:
        raise ImportError("radkit_genie module is required for learn operations")

    try:
        if os == DEFAULT_OS_FINGERPRINT:
            logger.info("Performing OS fingerprinting before learning")
            radkit_genie.fingerprint(inventory)
            genie_results = radkit_genie.learn(inventory, models, skip_unknown_os=True)
        else:
            logger.info(f"Using specified OS: {os}")
            genie_results = radkit_genie.learn(inventory, models, os=os)

        logger.info(
            f"Successfully learned {len(models)} models from {len(inventory)} devices"
        )
        return genie_results
    except Exception as e:
        logger.error(f"Genie learn operation failed: {e}")
        raise AnsibleRadkitOperationError(f"Genie learn operation failed: {e}")


def _process_genie_results(
    genie_results: Any, device_name: Optional[str], models: List[str], remove_keys: bool
) -> Dict[str, Any]:
    """Process Genie learn results into the appropriate format.

    Args:
        genie_results: Raw Genie learn results
        device_name: Device name for single device operations
        models: List of models that were learned
        remove_keys: Whether to remove model and device keys

    Returns:
        Processed results dictionary
    """
    results_dict = genie_results.to_dict()

    if remove_keys and len(results_dict.keys()) == 1 and len(models) == 1:
        if device_name:
            # Single device, single model
            return results_dict[device_name][models[0]]
        else:
            # Multi-device but only one device found, single model
            device_key = list(results_dict.keys())[0]
            return results_dict[device_key][models[0]]

    return results_dict


def run_action(
    module: AnsibleModule, radkit_service: RadkitClientService
) -> Tuple[Dict[str, Any], bool]:
    """Execute Genie learn operations via RADKit service.

    Args:
        module: Ansible module instance
        radkit_service: RADKit service client

    Returns:
        Tuple of (results dictionary, error boolean)
    """
    try:
        params = module.params
        device_name = params.get("device_name")
        filter_pattern = params.get("filter_pattern")
        filter_attr = params.get("filter_attr")
        models = params["models"]
        os = params["os"]
        remove_keys = params["remove_model_and_device_keys"]

        # Validate parameters
        _validate_device_parameters(device_name, filter_pattern, filter_attr)

        # Get device inventory
        inventory = _get_device_inventory(
            radkit_service, device_name, filter_pattern, filter_attr
        )

        # Execute Genie learn
        genie_results = _execute_genie_learn(inventory, models, os)

        # Process results
        processed_results = _process_genie_results(
            genie_results, device_name, models, remove_keys
        )

        results = {
            "genie_learn_result": processed_results,
            "ansible_module_results": {},
            "changed": False,
        }

        logger.info("Genie learn operation completed successfully")
        return results, False

    except (
        AnsibleRadkitValidationError,
        AnsibleRadkitConnectionError,
        AnsibleRadkitOperationError,
    ) as e:
        logger.error(f"RADKit Genie learn operation failed: {e}")
        return {"msg": str(e), "changed": False}, True
    except ImportError as e:
        logger.error(f"Missing required dependency: {e}")
        return {"msg": f"Missing required dependency: {e}", "changed": False}, True
    except Exception as e:
        logger.error(f"Unexpected error during Genie learn operation: {e}")
        return {"msg": f"Unexpected error: {e}", "changed": False}, True


def main() -> None:
    """Main function to run the Genie learn module.

    Sets up the Ansible module, validates parameters, and executes Genie learn operations.
    """
    # Define argument specification
    spec = radkit_client_argument_spec()
    spec.update(
        {
            "models": {"type": "list", "elements": "str", "required": True},
            "device_name": {"type": "str", "required": False},
            "os": {"type": "str", "default": DEFAULT_OS_FINGERPRINT},
            "filter_pattern": {"type": "str", "required": False},
            "filter_attr": {"type": "str", "required": False},
            "wait_timeout": {
                "type": "int",
                "default": DEFAULT_TIMEOUT,
                "fallback": (env_fallback, ["RADKIT_ANSIBLE_WAIT_TIMEOUT"]),
            },
            "exec_timeout": {
                "type": "int",
                "default": DEFAULT_TIMEOUT,
                "fallback": (env_fallback, ["RADKIT_ANSIBLE_EXEC_TIMEOUT"]),
            },
            "remove_model_and_device_keys": {"type": "bool", "default": False},
        }
    )

    # Create Ansible module
    module = AnsibleModule(argument_spec=spec, supports_check_mode=False)

    # Check for required libraries
    if not HAS_RADKIT:
        module.fail_json(msg="Python module cisco_radkit is required for this module!")

    if not HAS_RADKIT_GENIE:
        module.fail_json(msg="Python module radkit_genie is required for this module!")

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
        logger.error(f"Critical error in Genie learn module: {e}")
        module.fail_json(msg=f"Critical error in Genie learn module: {e}")


if __name__ == "__main__":
    main()
