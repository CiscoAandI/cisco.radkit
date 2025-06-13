#!/usr/bin/python
# -*- coding: utf-8 -*-
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""
Ansible Module for Cisco RADKit Genie Parsed Command Execution

This module runs commands via RADKit and processes the output through Genie parsers
to return structured, parsed results. It provides type-safe command execution with
comprehensive error handling and validation.
"""

from __future__ import absolute_import, division, print_function
from typing import Any, Dict, List, Optional, Tuple, Union
import logging

__metaclass__ = type

DOCUMENTATION = """
---
module: genie_parsed_command
short_description: Runs a command via RADKit, then through genie parser, returning a parsed result
version_added: "0.2.0"
description:
  - Runs a command via RADKit, then through genie parser, returning a parsed result
  - Supports both single device and multiple device command execution
  - Automatically fingerprints device OS or accepts explicit OS specification
  - Returns structured data through Genie parsers for network automation
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
    commands:
        description:
            - Commands to execute on device
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
    remove_cmd_and_device_keys:
        description:
            - Removes the command and device keys from the returned value when running a single command against a single device.
            - NOTE; This does not work with diff
        default: False
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
    description: Dictionary of results is returned if running command on multiple devices or with multiple commands
    returned: success
    type: dict
genie_parsed_result:
    description: Dictionary of parsed results
    returned: success
    type: dict
"""
EXAMPLES = """
- name:  Get parsed output from all routers starting with rtr-
  cisco.radkit.genie_parsed_command:
    commands: show version
    filter_pattern: rtr-
    filter_attr: name
    os: iosxe
  register: cmd_output
  delegate_to: localhost

- name: Show output
  debug:
    msg: "{{ cmd_output }}"

- name: Get parsed output from rtr-csr1 with removed return keys
  cisco.radkit.genie_parsed_command:
    device_name: rtr-csr1
    commands: show version
    os: iosxe
    remove_cmd_and_device_keys: yes
  register: cmd_output
  delegate_to: localhost

- name: Show IOS version
  debug:
    msg: "{{ cmd_output['genie_parsed_result']['version']['version'] }}"


"""
try:
    from radkit_client.sync import Client

    HAS_RADKIT = True
except ImportError:
    HAS_RADKIT = False

try:
    import radkit_genie

    HAS_RADKIT_GENIE = True
except ImportError:
    HAS_RADKIT_GENIE = False

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

# Constants for consistent messaging
DEVICE_NOT_FOUND_MSG = (
    "No devices found in RADKit inventory with attr: '{attr}' and pattern: '{pattern}'"
)
ALL_DEVICES_FAILED_MSG = (
    "All devices failed to connect via RADKIT. Check connectivity and/or authentication"
)
MISSING_DEVICE_PARAM_MSG = (
    "You must provide either argument device_name or filter_pattern+filter_attr"
)
MISSING_FILTER_ATTR_MSG = "You must provide BOTH filter_pattern and filter_attr"

# Setup module logger
logger = logging.getLogger(__name__)


def _execute_single_device_commands(
    module: AnsibleModule, radkit_service: RadkitClientService, params: Dict[str, Any]
) -> Tuple[Dict[str, Any], List[Dict[str, Any]], Any]:
    """Execute commands on a single device and return results."""
    inventory = radkit_service.get_inventory_by_filter(params["device_name"], "name")

    if not inventory:
        raise AnsibleRadkitValidationError(
            DEVICE_NOT_FOUND_MSG.format(attr="name", pattern=params["device_name"])
        )

    response = radkit_service.exec_command(
        params["commands"], inventory, return_full_response=True
    )
    radkit_result = response.result[params["device_name"]]

    ansible_results = []
    for command in radkit_result:
        cmd_result = radkit_result[command]
        cmd_result_dict = {
            "device_name": cmd_result.device.name,
            "command": cmd_result.command,
            "exec_status": cmd_result.status.value,
            "exec_status_message": cmd_result.status_message,
        }
        ansible_results.append(cmd_result_dict)

        if cmd_result.status.value != "SUCCESS":
            raise AnsibleRadkitOperationError(f"{cmd_result.status_message}")

    return radkit_result, ansible_results, response


def _execute_multiple_device_commands(
    module: AnsibleModule, radkit_service: RadkitClientService, params: Dict[str, Any]
) -> Tuple[Dict[str, Any], List[Dict[str, Any]], Any]:
    """Execute commands on multiple devices and return results."""
    inventory = radkit_service.get_inventory_by_filter(
        params["filter_pattern"], params["filter_attr"]
    )

    if not inventory:
        raise AnsibleRadkitValidationError(
            DEVICE_NOT_FOUND_MSG.format(
                attr=params["filter_attr"], pattern=params["filter_pattern"]
            )
        )

    response = radkit_service.exec_command(
        params["commands"], inventory, return_full_response=True
    )
    radkit_result = response.result

    # Check if all devices failed
    device_statuses = {radkit_result[d].status.value for d in radkit_result}
    if len(device_statuses) == 1 and list(device_statuses)[0] == "FAILURE":
        raise AnsibleRadkitConnectionError(ALL_DEVICES_FAILED_MSG)

    ansible_results = []
    for device in radkit_result:
        for command in radkit_result[device]:
            cmd_result = radkit_result[device][command]
            cmd_result_dict = {
                "device_name": cmd_result.device.name,
                "command": cmd_result.command,
                "exec_status": cmd_result.status.value,
                "exec_status_message": cmd_result.status_message,
            }
            ansible_results.append(cmd_result_dict)

    return radkit_result, ansible_results, response


def _parse_genie_results(
    params: Dict[str, Any], radkit_result: Dict[str, Any], response: Any, inventory: Any
) -> Dict[str, Any]:
    """Parse command results using Genie parsers."""
    if not HAS_RADKIT_GENIE:
        raise AnsibleRadkitValidationError("radkit_genie is required for parsing")

    if params["os"] == "fingerprint":
        radkit_genie.fingerprint(inventory)
        if params.get("device_name"):
            genie_parsed_result = radkit_genie.parse(response)
        else:
            genie_parsed_result = radkit_genie.parse(response, skip_unknown_os=True)
    else:
        genie_parsed_result = radkit_genie.parse(response, os=params["os"])

    # Process results based on removal preferences
    if params["remove_cmd_and_device_keys"]:
        if params.get("device_name") and len(radkit_result.keys()) == 1:
            return genie_parsed_result.to_dict()[params["device_name"]][
                params["commands"][0]
            ]
        elif (
            not params.get("device_name")
            and len(genie_parsed_result.keys()) == 1
            and len(params["commands"]) == 1
        ):
            device_key = list(genie_parsed_result.keys())[0]
            return genie_parsed_result.to_dict()[device_key][params["commands"][0]]

    return genie_parsed_result.to_dict()


def run_action(
    module: AnsibleModule, radkit_service: RadkitClientService
) -> Tuple[Dict[str, Any], bool]:
    """
    Execute commands via RADKit service and parse with Genie.

    Args:
        module: Ansible module instance
        radkit_service: RADKit client service instance

    Returns:
        Tuple containing results dictionary and error flag

    Raises:
        AnsibleRadkitValidationError: For parameter validation issues
        AnsibleRadkitConnectionError: For connectivity problems
        AnsibleRadkitOperationError: For command execution failures
    """
    results: Dict[str, Any] = {"ansible_module_results": {}, "changed": False}

    try:
        params = module.params
        ansible_returned_result: Union[List[Dict[str, Any]], Dict[str, Any]] = {}

        if params["device_name"]:
            # Single device execution
            (
                radkit_result,
                ansible_returned_result,
                response,
            ) = _execute_single_device_commands(module, radkit_service, params)
            inventory = radkit_service.get_inventory_by_filter(
                params["device_name"], "name"
            )

            if len(ansible_returned_result) == 1:
                ansible_returned_result = ansible_returned_result[0]
        else:
            # Multiple device execution
            (
                radkit_result,
                ansible_returned_result,
                response,
            ) = _execute_multiple_device_commands(module, radkit_service, params)
            inventory = radkit_service.get_inventory_by_filter(
                params["filter_pattern"], params["filter_attr"]
            )

        # Parse results with Genie
        results["genie_parsed_result"] = _parse_genie_results(
            params, radkit_result, response, inventory
        )

        # Set final results
        if isinstance(ansible_returned_result, list):
            results["ansible_module_results"] = ansible_returned_result
        elif isinstance(ansible_returned_result, dict):
            results.update(ansible_returned_result)

        return results, False

    except (
        AnsibleRadkitConnectionError,
        AnsibleRadkitValidationError,
        AnsibleRadkitOperationError,
    ) as e:
        logger.error(f"RADKit operation failed: {e}")
        return {"msg": str(e), "changed": False}, True
    except Exception as e:
        logger.error(f"Unexpected error in genie_parsed_command: {e}")
        return {"msg": f"Unexpected error: {str(e)}", "changed": False}, True


def _validate_module_parameters(module: AnsibleModule) -> None:
    """Validate module parameters and fail if invalid combinations are provided."""
    params = module.params

    if (
        not params["device_name"]
        and not params["filter_pattern"]
        and not params["filter_attr"]
    ):
        raise AnsibleRadkitValidationError(MISSING_DEVICE_PARAM_MSG)

    if (
        not params["device_name"]
        and params["filter_pattern"]
        and not params["filter_attr"]
    ):
        raise AnsibleRadkitValidationError(MISSING_FILTER_ATTR_MSG)


def main() -> None:
    """Main module execution function."""
    spec = radkit_client_argument_spec()
    spec.update(
        dict(
            commands=dict(
                type="list",
                elements="str",
                required=True,
            ),
            device_name=dict(
                type="str",
                required=False,
            ),
            os=dict(
                type="str",
                default="fingerprint",
            ),
            filter_pattern=dict(
                type="str",
                required=False,
            ),
            filter_attr=dict(
                type="str",
                required=False,
            ),
            wait_timeout=dict(
                type="int",
                default=0,
                fallback=(env_fallback, ["RADKIT_ANSIBLE_WAIT_TIMEOUT"]),
            ),
            exec_timeout=dict(
                type="int",
                default=0,
                fallback=(env_fallback, ["RADKIT_ANSIBLE_EXEC_TIMEOUT"]),
            ),
            remove_cmd_and_device_keys=dict(
                type="bool",
                default=False,
            ),
        )
    )

    module = AnsibleModule(argument_spec=spec, supports_check_mode=False)

    # Validate dependencies
    if not HAS_RADKIT:
        module.fail_json(msg="Python module cisco_radkit is required for this module!")

    if not HAS_RADKIT_GENIE:
        module.fail_json(msg="Python module radkit_genie is required for this module!")

    try:
        # Validate parameters
        _validate_module_parameters(module)

        # Execute with RADKit client
        with Client.create() as client:
            radkit_service = RadkitClientService(client, module.params)
            results, err = run_action(module, radkit_service)

        if err:
            module.fail_json(**results)
        module.exit_json(**results)

    except (
        AnsibleRadkitConnectionError,
        AnsibleRadkitValidationError,
        AnsibleRadkitOperationError,
    ) as e:
        module.fail_json(msg=str(e), changed=False)
    except Exception as e:
        logger.error(f"Unexpected error in main: {e}")
        module.fail_json(msg=f"Unexpected error: {str(e)}", changed=False)


if __name__ == "__main__":
    main()
