#!/usr/bin/python
# -*- coding: utf-8 -*-
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""
Ansible Module for Cisco RADKit Interactive Command Execution

This module provides comprehensive functionality for executing interactive commands
on network devices via RADKit with pexpect-based prompt handling. Supports
device reloads, configuration changes, and other operations requiring interactive
responses with proper timing and connection management.
"""

from __future__ import absolute_import, division, print_function
from typing import Any, Dict, List, Optional, Tuple, Union
import time
import re
import logging

__metaclass__ = type

DOCUMENTATION = """
---
module: exec_and_wait
short_description: Executes commands on devices using RADKit and handles interactive prompts
version_added: "1.7.61"
description:
  - This module runs commands on specified devices using RADKit, handling interactive prompts with pexpect.
options:
    device_name:
        description:
            - Name of the device as it appears in the RADKit inventory. Use either device_name or device_host.
        required: False
        type: str
    device_host:
        description:
            - Hostname or IP address of the device as it appears in the RADKit inventory. Use either device_name or device_host.
        required: False
        type: str
    commands:
        description:
            - List of commands to execute on the device.
        required: False
        type: list
        elements: str
    prompts:
        description:
            - List of expected prompts to handle interactively.
        required: False
        type: list
        elements: str
    answers:
        description:
            - List of answers corresponding to the expected prompts.
        required: False
        type: list
        elements: str
    command_timeout:
        description:
            - Time in seconds to wait for a command to complete.
        required: False
        default: 15
        type: int
    seconds_to_wait:
        description:
            - Maximum time in seconds to wait after sending the commands before checking the device state.
        required: True
        type: int
    delay_before_check:
        description:
            - Delay in seconds before performing a final check on the device state.
        required: False
        default: 10
        type: int
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
executed_commands:
    description: Command
    returned: success
    type: list
stdout:
    description: Output of commands
    returned: success
    type: str
"""
EXAMPLES = """
    - name: Reload Router and Wait Until Available by using ansible_host
      cisco.radkit.exec_and_wait:
        #device_name: "{{inventory_hostname}}"
        device_host: "{{ansible_host}}"
        commands:
          - "reload"
        prompts:
          - ".*yes/no].*"
          - ".*confirm].*"
        answers:
          - "yes\r"
          - "\r"
        seconds_to_wait: 300  # total time to wait for reload
        delay_before_check: 10  # Delay before checking terminal
      register: reload_result

    - name: Reload Router and Wait Until Available by using inventory_hostname
      cisco.radkit.exec_and_wait:
        device_name: "{{inventory_hostname}}"
        commands:
          - "reload"
        prompts:
          - ".*yes/no].*"
          - ".*confirm].*"
        answers:
          - "yes\r"
          - "\r"
        seconds_to_wait: 300  # total time to wait for reload
        delay_before_check: 10  # Delay before checking terminal
      register: reload_result

    - name: Reset the Connection
      # The connection must be reset to allow Ansible to poll the router for connectivity
      meta: reset_connection
"""
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

try:
    from radkit_client.sync import Client

    HAS_RADKIT = True
except ImportError:
    HAS_RADKIT = False
    Client = None

try:
    import pexpect
    import socket

    HAS_PEXPECT = True
except ImportError:
    HAS_PEXPECT = False
    pexpect = None
    socket = None

# Setup module logger
logger = logging.getLogger(__name__)

__metaclass__ = type

# Constants for exec and wait operations
DEFAULT_COMMAND_TIMEOUT = 15
DEFAULT_DELAY_BEFORE_CHECK = 10
DEFAULT_MAX_TERMINAL_ATTEMPTS = 30
DEFAULT_RETRY_INTERVAL = 1
DEFAULT_WAIT_BETWEEN_COMMANDS = 2
DEFAULT_WAIT_AFTER_ANSWER = 1
DEFAULT_RETRY_WAIT = 5


def _wait_for_terminal_connection(
    device: str,
    inventory: Dict[str, Any],
    max_attempts: int = DEFAULT_MAX_TERMINAL_ATTEMPTS,
    retry_interval: int = DEFAULT_RETRY_INTERVAL,
) -> Any:
    """Wait for terminal connection to become available.

    Args:
        device: Device name
        inventory: Device inventory
        max_attempts: Maximum connection attempts
        retry_interval: Seconds between attempts

    Returns:
        Connected terminal instance

    Raises:
        AnsibleRadkitConnectionError: If connection fails
    """
    logger.info(f"Waiting for terminal connection on device {device}")
    terminal = inventory[device].terminal()

    for attempt in range(max_attempts):
        if terminal.status.value == "CONNECTED":
            logger.info(f"Terminal connected to {device} on attempt {attempt + 1}")
            return terminal
        time.sleep(retry_interval)

    # Final check and cleanup
    if terminal.status.value != "CONNECTED":
        terminal.close()
        raise AnsibleRadkitConnectionError(
            f"Device {device} terminal failed to connect after {max_attempts} attempts"
        )

    return terminal


def _validate_interactive_parameters(
    commands: Optional[List[str]],
    prompts: Optional[List[str]],
    answers: Optional[List[str]],
) -> None:
    """Validate interactive command parameters.

    Args:
        commands: List of commands to execute
        prompts: List of expected prompts
        answers: List of answers to prompts

    Raises:
        AnsibleRadkitValidationError: If parameters are invalid
    """
    if commands and prompts and answers:
        if len(prompts) != len(answers):
            raise AnsibleRadkitValidationError(
                f"Number of prompts ({len(prompts)}) must match number of answers ({len(answers)})"
            )


def _get_device_inventory(
    radkit_service: RadkitClientService,
    device_name: Optional[str],
    device_host: Optional[str],
) -> Dict[str, Any]:
    """Get device inventory for exec and wait operations.

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


def _execute_interactive_commands(
    device: str,
    inventory: Dict[str, Any],
    commands: List[str],
    prompts: List[str],
    answers: List[str],
    command_timeout: int,
) -> Tuple[List[str], str]:
    """Execute interactive commands on device.

    Args:
        device: Device name
        inventory: Device inventory
        commands: List of commands to execute
        prompts: List of expected prompts
        answers: List of answers to prompts
        command_timeout: Timeout for commands

    Returns:
        Tuple of (executed_commands, full_output)

    Raises:
        AnsibleRadkitOperationError: If command execution fails
    """
    if not pexpect:
        raise ImportError(
            "pexpect module is required for interactive command execution"
        )

    executed_commands = []
    full_output = ""

    try:
        terminal = inventory[device].terminal().wait()
        forwarder = terminal.attach_socket()
        child = forwarder.spawn_pexpect()

        if not child.isalive():
            raise AnsibleRadkitOperationError(
                f"Pexpect session for {device} is not alive"
            )

        try:
            for command in commands:
                logger.info(f"Executing command on {device}: {command}")
                executed_commands.append(command)
                child.sendline(command)
                time.sleep(DEFAULT_WAIT_BETWEEN_COMMANDS)

                while True:
                    # Check for expected prompts
                    index = child.expect(
                        [re.compile(p) for p in prompts]
                        + [pexpect.TIMEOUT, pexpect.EOF],
                        timeout=command_timeout,
                    )

                    output = child.before.decode("utf-8").strip()
                    if output:
                        full_output += f"\n{output}"

                    if index < len(prompts):
                        # Found matching prompt, send answer
                        answer = answers[index]
                        logger.info(f"Responding to prompt with: {answer}")
                        executed_commands.append(answer)
                        child.sendline(answer)
                        time.sleep(DEFAULT_WAIT_AFTER_ANSWER)

                        # Capture output after answer
                        child.expect([".*"], timeout=command_timeout)
                        full_output += f"\n{child.before.decode('utf-8').strip()}"
                    else:
                        # No more prompts, exit loop
                        break

        except (pexpect.exceptions.EOF, pexpect.exceptions.TIMEOUT, OSError) as e:
            logger.warning(f"Interactive session interrupted: {e}")
            if child.before:
                full_output += f"\n{child.before.decode('utf-8').strip()}"

        finally:
            if child.isalive():
                try:
                    child.close()
                except Exception:
                    pass

        return executed_commands, full_output.strip()

    except Exception as e:
        logger.error(f"Failed to execute interactive commands on {device}: {e}")
        raise AnsibleRadkitOperationError(
            f"Failed to execute interactive commands on {device}: {e}"
        )


def _wait_for_device_recovery(
    device: str,
    inventory: Dict[str, Any],
    seconds_to_wait: int,
    delay_before_check: int,
) -> None:
    """Wait for device to recover after commands.

    Args:
        device: Device name
        inventory: Device inventory
        seconds_to_wait: Maximum time to wait
        delay_before_check: Initial delay before checking

    Raises:
        AnsibleRadkitOperationError: If device doesn't recover in time
    """
    logger.info(f"Waiting {delay_before_check} seconds before checking device {device}")
    time.sleep(delay_before_check)

    start_time = time.time()

    while True:
        if time.time() - start_time > seconds_to_wait:
            raise AnsibleRadkitOperationError(
                f"Device {device} did not respond within {seconds_to_wait} seconds"
            )

        try:
            # Check terminal connection
            _wait_for_terminal_connection(device, inventory)

            # Send a newline to ensure we have a prompt
            inventory[device].exec("\r").wait()
            logger.info(f"Device {device} has recovered successfully")
            break

        except Exception as e:
            logger.debug(f"Device {device} not ready yet: {e}")
            time.sleep(DEFAULT_RETRY_WAIT)


def run_action(
    module: AnsibleModule, radkit_service: RadkitClientService
) -> Tuple[Dict[str, Any], bool]:
    """Execute interactive commands and wait for device recovery.

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
        commands = params.get("commands", [])
        prompts = params.get("prompts", [])
        answers = params.get("answers", [])
        command_timeout = params["command_timeout"]
        seconds_to_wait = params["seconds_to_wait"]
        delay_before_check = params["delay_before_check"]

        # Validate parameters
        _validate_interactive_parameters(commands, prompts, answers)

        # Get device inventory
        inventory = _get_device_inventory(radkit_service, device_name, device_host)

        results = {}

        for device in inventory:
            logger.info(f"Starting interactive command execution on device {device}")

            # Execute interactive commands
            executed_commands, full_output = _execute_interactive_commands(
                device, inventory, commands, prompts, answers, command_timeout
            )

            # Wait for device recovery
            _wait_for_device_recovery(
                device, inventory, seconds_to_wait, delay_before_check
            )

            results.update(
                {
                    "device_name": device,
                    "executed_commands": executed_commands,
                    "stdout": full_output,
                    "changed": True,
                }
            )

        logger.info("Interactive command execution completed successfully")
        return results, False

    except (
        AnsibleRadkitValidationError,
        AnsibleRadkitConnectionError,
        AnsibleRadkitOperationError,
    ) as e:
        logger.error(f"RADKit exec and wait operation failed: {e}")
        return {"msg": str(e), "exec_status": "FAILURE", "changed": False}, True
    except ImportError as e:
        logger.error(f"Missing required dependency: {e}")
        return {"msg": f"Missing required dependency: {e}", "changed": False}, True
    except Exception as e:
        logger.error(f"Unexpected error during exec and wait operation: {e}")
        import traceback

        return {
            "msg": traceback.format_exc(),
            "exec_status": "FAILURE",
            "changed": False,
        }, True


def main() -> None:
    """Main function to run the exec and wait module.

    Sets up the Ansible module and executes interactive command operations.
    """
    # Define argument specification
    spec = radkit_client_argument_spec()
    spec.update(
        {
            "device_name": {"type": "str", "required": False},
            "device_host": {"type": "str", "required": False},
            "seconds_to_wait": {"type": "int", "required": True},
            "delay_before_check": {
                "type": "int",
                "default": DEFAULT_DELAY_BEFORE_CHECK,
            },
            "command_timeout": {"type": "int", "default": DEFAULT_COMMAND_TIMEOUT},
            "commands": {"type": "list", "elements": "str", "required": False},
            "answers": {"type": "list", "elements": "str", "required": False},
            "prompts": {"type": "list", "elements": "str", "required": False},
        }
    )

    # Create Ansible module
    module = AnsibleModule(
        argument_spec=spec,
        supports_check_mode=False,
        required_one_of=[["device_name", "device_host"]],
    )

    # Check for required libraries
    if not HAS_RADKIT:
        module.fail_json(msg="Python module cisco_radkit is required for this module!")

    if not HAS_PEXPECT:
        module.fail_json(msg="Python module pexpect is required for this module!")

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
        logger.error(f"Critical error in exec and wait module: {e}")
        module.fail_json(msg=f"Critical error in exec and wait module: {e}")


if __name__ == "__main__":
    main()
