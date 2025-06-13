#!/usr/bin/python
# -*- coding: utf-8 -*-
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""
Ansible module for executing commands on network devices through Cisco RADKit.

This module provides a professional interface for running commands on one or more
network devices managed by Cisco RADKit, with proper error handling and result formatting.
"""

from __future__ import absolute_import, division, print_function
from typing import Any, Dict, List, Optional, Tuple, Union

__metaclass__ = type

DOCUMENTATION = """
---
module: command
short_description: Execute commands on network devices via Cisco RADKit
version_added: "0.2.0"
description:
  - Executes one or more commands on network devices managed by Cisco RADKit
  - Supports execution on single devices or multiple devices using filter patterns
  - Returns structured command output with execution status and optional prompt removal
  - Provides comprehensive error handling and logging for troubleshooting
options:
    device_name:
        description:
            - Name of a specific device as it appears in RADKit inventory
            - Mutually exclusive with filter_pattern and filter_attr
        required: false
        type: str
    filter_pattern:
        description:
            - Pattern to match against RADKit inventory for multi-device operations
            - Use glob-style patterns (e.g., 'router*', 'switch-*')
            - Must be used together with filter_attr
        required: false
        type: str
    filter_attr:
        description:
            - Inventory attribute to match against the filter_pattern
            - Common values include 'name', 'hostname', 'ip_address'
            - Must be used together with filter_pattern
        required: false
        type: str
    commands:
        description:
            - List of commands to execute on the target device(s)
            - Each command will be executed sequentially
            - Commands should be valid for the target device OS
        required: true
        aliases: ['command']
        type: list
        elements: str
    wait_timeout:
        description:
            - Maximum time in seconds to wait for RADKit task completion
            - Set to 0 for no timeout (default behavior)
            - Can be set via environment variable RADKIT_ANSIBLE_WAIT_TIMEOUT
        required: false
        default: 0
        type: int
    exec_timeout:
        description:
            - Maximum time in seconds to wait for individual command execution
            - Set to 0 for no timeout (default behavior)  
            - Can be set via environment variable RADKIT_ANSIBLE_EXEC_TIMEOUT
        required: false
        default: 0
        type: int
    remove_prompts:
        description:
            - Remove first and last lines from command output (typically CLI prompts)
            - Helps clean up output for parsing and display
        required: false
        default: true
        type: bool
extends_documentation_fragment: cisco.radkit.radkit_client
requirements:
    - cisco-radkit-client
author: Scott Dozier (@scdozier)
"""

RETURN = r"""
device_name:
    description: Name of the device where the command was executed
    returned: success
    type: str
    sample: "router-01"
command:
    description: The command that was executed
    returned: success
    type: str
    sample: "show version"
stdout:
    description: Command output from the device
    returned: success
    type: str
    sample: "Cisco IOS XE Software, Version 16.09.08..."
exec_status:
    description: Execution status from RADKit
    returned: always
    type: str
    sample: "SUCCESS"
exec_status_message:
    description: Detailed status message from RADKit
    returned: always
    type: str
    sample: "Command executed successfully"
ansible_module_results:
    description: 
        - List of results when executing on multiple devices or multiple commands
        - Each item contains device_name, command, stdout, exec_status, and exec_status_message
    returned: when multiple devices or commands are involved
    type: list
    elements: dict
    sample: [
        {
            "device_name": "router-01",
            "command": "show version",
            "stdout": "Cisco IOS XE Software...",
            "exec_status": "SUCCESS",
            "exec_status_message": "Command executed successfully"
        }
    ]
changed:
    description: Whether any changes were made (always false for command execution)
    returned: always
    type: bool
    sample: false
"""
EXAMPLES = """
# Execute a single command on a specific device
- name: Get version information from router-01
  cisco.radkit.command:
    device_name: router-01
    commands: show version
  register: version_output
  delegate_to: localhost

# Execute multiple commands on a single device
- name: Get system information from router-01
  cisco.radkit.command:
    device_name: router-01
    commands:
      - show version
      - show ip interface brief
      - show running-config | include hostname
  register: system_info
  delegate_to: localhost

# Execute commands on multiple devices using filter pattern
- name: Get version from all routers
  cisco.radkit.command:
    filter_attr: name
    filter_pattern: router*
    commands: show version
  register: all_versions
  delegate_to: localhost

# Execute with custom timeouts and without prompt removal
- name: Long running command with custom settings
  cisco.radkit.command:
    device_name: core-switch-01
    commands: show tech-support
    exec_timeout: 300
    wait_timeout: 600
    remove_prompts: false
  register: tech_support
  delegate_to: localhost

# Display command output
- name: Show command results
  debug:
    msg: "{{ version_output.stdout }}"

# Process multiple device results
- name: Process results from multiple devices
  debug:
    msg: "Device {{ item.device_name }} version: {{ item.stdout | regex_search('Version ([0-9.]+)', '\\1') | first }}"
  loop: "{{ all_versions.ansible_module_results }}"
  when: all_versions.ansible_module_results is defined
"""
try:
    from radkit_client.sync import Client

    HAS_RADKIT = True
except ImportError:
    HAS_RADKIT = False

from ansible.module_utils.basic import AnsibleModule, env_fallback
from ansible_collections.cisco.radkit.plugins.module_utils.client import (
    radkit_client_argument_spec,
    RadkitClientService,
)
from ansible_collections.cisco.radkit.plugins.module_utils.exceptions import (
    AnsibleRadkitError,
    AnsibleRadkitOperationError,
    AnsibleRadkitValidationError,
)

__metaclass__ = type


def run_action(
    module: AnsibleModule, radkit_service: RadkitClientService
) -> Tuple[Dict[str, Any], bool]:
    """
    Execute commands via RADKit service with comprehensive error handling.

    Args:
        module: Ansible module instance with validated parameters
        radkit_service: Configured RADKit client service

    Returns:
        Tuple of (results dictionary, error flag)

    Raises:
        AnsibleRadkitError: For RADKit-specific operational errors
    """
    results: Dict[str, Any] = {"changed": False}
    err = False
    ansible_returned_result: List[Dict[str, Any]] = []

    try:
        params = module.params

        if params["device_name"]:
            # Execute commands on a single device
            ansible_returned_result = _execute_on_single_device(radkit_service, params)
        else:
            # Execute commands on multiple devices using filter
            ansible_returned_result = _execute_on_multiple_devices(
                radkit_service, params
            )

        # Format results based on number of results
        if len(ansible_returned_result) == 1:
            results.update(ansible_returned_result[0])
        else:
            results["ansible_module_results"] = ansible_returned_result

    except AnsibleRadkitError:
        # Re-raise RADKit specific errors
        raise
    except Exception as e:
        # Handle unexpected errors
        err = True
        results["msg"] = f"Unexpected error during command execution: {str(e)}"

    return results, err


def _execute_on_single_device(
    radkit_service: RadkitClientService, params: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """
    Execute commands on a single device identified by name.

    Args:
        radkit_service: RADKit client service instance
        params: Module parameters

    Returns:
        List of command result dictionaries

    Raises:
        AnsibleRadkitOperationError: If device not found or command execution fails
    """
    device_name = params["device_name"]
    commands = params["commands"]
    remove_prompts = params["remove_prompts"]

    # Get device inventory
    try:
        inventory = radkit_service.get_inventory_by_filter(device_name, "name")
    except AnsibleRadkitError as e:
        raise AnsibleRadkitOperationError(
            f"Device '{device_name}' not found in RADKit inventory"
        ) from e

    # Execute commands
    try:
        response = radkit_service.exec_command(commands, inventory)
        radkit_result = response[device_name]

        if radkit_result.status.value != "SUCCESS":
            raise AnsibleRadkitOperationError(
                f"Command execution failed on {device_name}: {radkit_result.status_message}"
            )

        return _format_command_results(radkit_result, remove_prompts)

    except Exception as e:
        if isinstance(e, AnsibleRadkitError):
            raise
        raise AnsibleRadkitOperationError(
            f"Failed to execute commands on {device_name}: {str(e)}"
        ) from e


def _execute_on_multiple_devices(
    radkit_service: RadkitClientService, params: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """
    Execute commands on multiple devices using filter pattern.

    Args:
        radkit_service: RADKit client service instance
        params: Module parameters

    Returns:
        List of command result dictionaries

    Raises:
        AnsibleRadkitOperationError: If no devices found or all executions fail
    """
    filter_pattern = params["filter_pattern"]
    filter_attr = params["filter_attr"]
    commands = params["commands"]
    remove_prompts = params["remove_prompts"]

    # Get filtered inventory
    try:
        inventory = radkit_service.get_inventory_by_filter(filter_pattern, filter_attr)
    except AnsibleRadkitError as e:
        raise AnsibleRadkitOperationError(
            f"No devices found with {filter_attr}='{filter_pattern}'"
        ) from e

    # Execute commands with full response
    try:
        radkit_result = radkit_service.exec_command(
            commands, inventory, return_full_response=True
        )

        # Check if all devices failed
        device_statuses = {
            radkit_result.result[d].status.value for d in radkit_result.result
        }

        if len(device_statuses) == 1 and "FAILURE" in device_statuses:
            raise AnsibleRadkitOperationError(
                "All devices failed to connect via RADKit. "
                "Check connectivity and authentication."
            )

        # Format results for all devices
        all_results = []
        for device in radkit_result.result:
            device_results = _format_command_results(
                radkit_result.result[device], remove_prompts
            )
            all_results.extend(device_results)

        return all_results

    except Exception as e:
        if isinstance(e, AnsibleRadkitError):
            raise
        raise AnsibleRadkitOperationError(
            f"Failed to execute commands on devices matching {filter_attr}='{filter_pattern}': {str(e)}"
        ) from e


def _format_command_results(
    radkit_result: Any, remove_prompts: bool
) -> List[Dict[str, Any]]:
    """
    Format RADKit command results for Ansible return.

    Args:
        radkit_result: RADKit command execution result
        remove_prompts: Whether to remove CLI prompts from output

    Returns:
        List of formatted command result dictionaries
    """
    results = []

    for command in radkit_result:
        cmd_result = radkit_result[command]

        # Extract command output
        stdout = getattr(cmd_result, "data", "")

        # Remove prompts if requested and output has multiple lines
        if remove_prompts and "\n" in stdout:
            lines = stdout.splitlines(keepends=True)
            if len(lines) > 2:  # Need at least 3 lines to remove first and last
                stdout = "".join(lines[1:-1]).strip()

        result_dict = {
            "device_name": getattr(cmd_result.device, "name", ""),
            "command": getattr(cmd_result, "command", ""),
            "exec_status": getattr(cmd_result.status, "value", ""),
            "exec_status_message": getattr(cmd_result, "status_message", ""),
            "stdout": stdout,
        }

        results.append(result_dict)

    return results


def main() -> None:
    """
    Main entry point for the Ansible module.

    Handles argument parsing, validation, and command execution orchestration.
    """
    # Define module argument specification
    spec = radkit_client_argument_spec()
    spec.update(
        {
            "commands": {
                "type": "list",
                "required": True,
                "elements": "str",
                "aliases": ["command"],
            },
            "device_name": {
                "type": "str",
                "required": False,
            },
            "filter_pattern": {
                "type": "str",
                "required": False,
            },
            "filter_attr": {
                "type": "str",
                "required": False,
            },
            "wait_timeout": {
                "type": "int",
                "default": 0,
                "fallback": (env_fallback, ["RADKIT_ANSIBLE_WAIT_TIMEOUT"]),
            },
            "exec_timeout": {
                "type": "int",
                "default": 0,
                "fallback": (env_fallback, ["RADKIT_ANSIBLE_EXEC_TIMEOUT"]),
            },
            "remove_prompts": {
                "type": "bool",
                "default": True,
            },
        }
    )

    # Create module instance
    module = AnsibleModule(
        argument_spec=spec,
        supports_check_mode=False,
        mutually_exclusive=[
            ("device_name", "filter_pattern"),
            ("device_name", "filter_attr"),
        ],
        required_together=[
            ("filter_pattern", "filter_attr"),
        ],
    )

    # Validate module prerequisites
    if not HAS_RADKIT:
        module.fail_json(
            msg="Required Python package 'cisco-radkit-client' is not installed. "
            "Install it using: pip install cisco-radkit-client"
        )

    # Validate parameter combinations
    _validate_parameters(module)

    # Execute commands via RADKit
    try:
        if not HAS_RADKIT:
            raise ImportError("radkit_client not available")

        with Client.create() as client:
            with RadkitClientService(client, module.params) as radkit_service:
                results, err = run_action(module, radkit_service)

        if err:
            module.fail_json(**results)
        else:
            module.exit_json(**results)

    except AnsibleRadkitError as e:
        module.fail_json(
            msg=f"RADKit operation failed: {str(e)}", error_type=type(e).__name__
        )
    except Exception as e:
        module.fail_json(msg=f"Unexpected error: {str(e)}", error_type=type(e).__name__)


def _validate_parameters(module: AnsibleModule) -> None:
    """
    Validate module parameter combinations and requirements.

    Args:
        module: Ansible module instance

    Raises:
        AnsibleFailJson: If parameter validation fails
    """
    params = module.params

    # Check that either device_name or filter pattern is provided
    if not params["device_name"] and not (
        params["filter_pattern"] and params["filter_attr"]
    ):
        module.fail_json(
            msg="Must provide either 'device_name' or both 'filter_pattern' and 'filter_attr'"
        )

    # Validate commands parameter
    if not params["commands"]:
        module.fail_json(msg="At least one command must be specified")

    # Validate timeout values
    if params["wait_timeout"] < 0:
        module.fail_json(msg="wait_timeout must be non-negative")

    if params["exec_timeout"] < 0:
        module.fail_json(msg="exec_timeout must be non-negative")


if __name__ == "__main__":
    main()
