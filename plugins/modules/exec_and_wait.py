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
  - Enhanced with retry logic, progress monitoring, and better error handling.
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
    command_retries:
        description:
            - Maximum number of retries for command execution failures.
        required: False
        default: 1
        type: int
    recovery_test_command:
        description:
            - Custom command to test device responsiveness during recovery.
        required: False
        default: "show clock"
        type: str
    continue_on_device_failure:
        description:
            - Continue processing other devices if one device fails.
        required: False
        default: false
        type: bool
extends_documentation_fragment: cisco.radkit.radkit_client
requirements:
    - radkit
    - pexpect
author: Scott Dozier (@scdozier)
"""
RETURN = r"""
device_name:
    description: Device name (for single device compatibility)
    returned: success
    type: str
executed_commands:
    description: Commands executed (for single device compatibility)
    returned: success
    type: list
stdout:
    description: Output of commands (for single device compatibility)
    returned: success
    type: str
devices:
    description: Results for each device processed
    returned: always
    type: dict
    contains:
        device_name:
            description: Name of the device
            type: str
        executed_commands:
            description: List of commands executed
            type: list
        stdout:
            description: Command output
            type: str
        status:
            description: Execution status (SUCCESS/FAILED)
            type: str
        recovery_time:
            description: Time taken for device recovery
            type: float
        attempt_count:
            description: Number of recovery attempts
            type: int
summary:
    description: Summary of execution across all devices
    returned: always
    type: dict
    contains:
        total_devices:
            description: Total number of devices processed
            type: int
        successful_devices:
            description: Number of devices that succeeded
            type: int
        failed_devices:
            description: Number of devices that failed
            type: int
"""
EXAMPLES = """
    - name: Test network connectivity (execution test, not success test)
      cisco.radkit.exec_and_wait:
        device_name: "{{ inventory_hostname }}"
        commands:
          - "ping 8.8.8.8 repeat 2"
        prompts: []
        answers: []
        seconds_to_wait: 60
        delay_before_check: 5
      register: ping_test
      # Note: This tests command execution, ping may fail due to network policies

    - name: Execute show commands safely
      cisco.radkit.exec_and_wait:
        device_name: "{{ inventory_hostname }}"
        commands:
          - "show version"
          - "show clock"
          - "show ip interface brief"
        prompts: []
        answers: []
        seconds_to_wait: 30
        delay_before_check: 2
        command_retries: 2
      register: show_commands

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
        recovery_test_command: "show clock"
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
        command_retries: 1
        continue_on_device_failure: false
      register: reload_result

    - name: Configuration change with confirmation
      cisco.radkit.exec_and_wait:
        device_name: "{{ inventory_hostname }}"
        commands:
          - "configure terminal"
          - "interface loopback 999"
          - "description Test interface"
          - "exit"
          - "exit"
        prompts: []
        answers: []
        seconds_to_wait: 30
        delay_before_check: 2
        recovery_test_command: "show running-config interface loopback 999"
      register: config_result

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
import logging
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
DEFAULT_COMMAND_RETRIES = 1


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
    max_retries: int = DEFAULT_COMMAND_RETRIES,
) -> Tuple[List[str], str]:
    """Execute interactive commands on device with retry logic.

    Args:
        device: Device name
        inventory: Device inventory
        commands: List of commands to execute
        prompts: List of expected prompts
        answers: List of answers to prompts
        command_timeout: Timeout for commands
        max_retries: Maximum number of retries for command execution

    Returns:
        Tuple of (executed_commands, full_output)

    Raises:
        AnsibleRadkitOperationError: If command execution fails
    """
    if not pexpect:
        raise ImportError(
            "pexpect module is required for interactive command execution"
        )

    for attempt in range(max_retries + 1):
        try:
            return _execute_commands_once(
                device, inventory, commands, prompts, answers, command_timeout
            )
        except (pexpect.exceptions.EOF, pexpect.exceptions.TIMEOUT) as e:
            if attempt < max_retries:
                logger.warning(
                    f"Command execution failed on attempt {attempt + 1}, retrying: {e}"
                )
                time.sleep(2)  # Brief pause before retry
                continue
            else:
                raise AnsibleRadkitOperationError(
                    f"Command execution failed after {max_retries + 1} attempts: {e}"
                )


def _execute_commands_once(
    device: str,
    inventory: Dict[str, Any],
    commands: List[str],
    prompts: List[str],
    answers: List[str],
    command_timeout: int,
) -> Tuple[List[str], str]:
    """Execute interactive commands once."""

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
                    if prompts:
                        # We have prompts to handle
                        index = child.expect(
                            [re.compile(p) for p in prompts]
                            + [pexpect.TIMEOUT, pexpect.EOF],
                            timeout=command_timeout,
                        )
                        
                        output = child.before.decode("utf-8", errors="replace").strip()
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
                            full_output += f"\n{child.before.decode('utf-8', errors='replace').strip()}"
                        else:
                            # Hit timeout or EOF, exit loop
                            break
                    else:
                        # No prompts expected, just wait for command completion
                        try:
                            # Wait for timeout - this means command completed normally
                            index = child.expect([pexpect.TIMEOUT], timeout=command_timeout)
                        except pexpect.exceptions.TIMEOUT:
                            # Expected timeout - command completed
                            pass
                        
                        # Capture any output that was generated
                        output = child.before.decode("utf-8", errors="replace").strip()
                        if output:
                            full_output += f"\n{output}"
                        
                        # Command completed, exit loop
                        break

        except (pexpect.exceptions.EOF, pexpect.exceptions.TIMEOUT, OSError) as e:
            logger.warning(f"Interactive session interrupted: {e}")
            if child.before:
                full_output += (
                    f"\n{child.before.decode('utf-8', errors='replace').strip()}"
                )

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
    recovery_test_command: str = "show clock",
) -> Dict[str, Any]:
    """Wait for device to recover after commands with progress info.

    Args:
        device: Device name
        inventory: Device inventory
        seconds_to_wait: Maximum time to wait
        delay_before_check: Initial delay before checking
        recovery_test_command: Command to test device responsiveness

    Returns:
        Dictionary with recovery information

    Raises:
        AnsibleRadkitOperationError: If device doesn't recover in time
    """
    logger.info(f"Waiting {delay_before_check} seconds before checking device {device}")
    time.sleep(delay_before_check)

    start_time = time.time()
    attempt_count = 0
    last_progress_log = start_time

    while True:
        elapsed = time.time() - start_time

        if elapsed > seconds_to_wait:
            raise AnsibleRadkitOperationError(
                f"Device {device} did not respond within {seconds_to_wait} seconds after {attempt_count} attempts"
            )

        # Log progress every 30 seconds
        if elapsed - (last_progress_log - start_time) >= 30:
            remaining = seconds_to_wait - elapsed
            logger.info(
                f"Device {device} recovery: {elapsed:.0f}s elapsed, {remaining:.0f}s remaining"
            )
            last_progress_log = time.time()

        try:
            attempt_count += 1

            # Check terminal connection
            _wait_for_terminal_connection(device, inventory, max_attempts=3)

            # Test with the specified recovery command
            response = inventory[device].exec(recovery_test_command).wait()

            if response and not any(
                err in response.lower() for err in ["error", "invalid", "failed"]
            ):
                logger.info(
                    f"Device {device} recovered after {elapsed:.1f}s and {attempt_count} attempts"
                )
                return {
                    "recovery_time": elapsed,
                    "attempt_count": attempt_count,
                    "status": "recovered",
                }

        except Exception as e:
            logger.debug(
                f"Device {device} not ready yet (attempt {attempt_count}): {e}"
            )
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
        command_timeout = params.get("command_timeout", DEFAULT_COMMAND_TIMEOUT)
        seconds_to_wait = params.get("seconds_to_wait")
        delay_before_check = params.get(
            "delay_before_check", DEFAULT_DELAY_BEFORE_CHECK
        )

        # Validate parameters
        _validate_interactive_parameters(commands, prompts, answers)

        # Get device inventory
        inventory = _get_device_inventory(radkit_service, device_name, device_host)

        results = {
            "devices": {},
            "summary": {
                "total_devices": 0,
                "successful_devices": 0,
                "failed_devices": 0,
            },
            "changed": False,
        }

        for device in inventory:
            logger.info(f"Starting interactive command execution on device {device}")
            results["summary"]["total_devices"] += 1

            try:
                # Execute interactive commands with retry
                executed_commands, full_output = _execute_interactive_commands(
                    device,
                    inventory,
                    commands,
                    prompts,
                    answers,
                    command_timeout,
                    params.get("command_retries", DEFAULT_COMMAND_RETRIES),
                )

                # Wait for device recovery with progress
                recovery_info = _wait_for_device_recovery(
                    device,
                    inventory,
                    seconds_to_wait,
                    delay_before_check,
                    params.get("recovery_test_command", "show clock"),
                )

                results["devices"][device] = {
                    "device_name": device,
                    "executed_commands": executed_commands,
                    "stdout": full_output,
                    "status": "SUCCESS",
                    "recovery_time": recovery_info.get("recovery_time", 0),
                    "attempt_count": recovery_info.get("attempt_count", 0),
                    "changed": True,
                }
                results["summary"]["successful_devices"] += 1
                results["changed"] = True

            except Exception as e:
                logger.error(f"Failed on device {device}: {e}")
                results["devices"][device] = {
                    "device_name": device,
                    "status": "FAILED",
                    "error": str(e),
                    "changed": False,
                }
                results["summary"]["failed_devices"] += 1

                if not params.get("continue_on_device_failure", False):
                    raise

        # For single device compatibility, also include top-level fields
        if len(inventory) == 1:
            device_name = list(inventory.keys())[0]
            device_result = results["devices"][device_name]
            results.update(
                {
                    "device_name": device_result["device_name"],
                    "executed_commands": device_result.get("executed_commands", []),
                    "stdout": device_result.get("stdout", ""),
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
            # Basic enhancements
            "command_retries": {"type": "int", "default": DEFAULT_COMMAND_RETRIES},
            "recovery_test_command": {"type": "str", "default": "show clock"},
            "continue_on_device_failure": {"type": "bool", "default": False},
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
