#!/usr/bin/python
# -*- coding: utf-8 -*-
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""
Ansible Module for Cisco RADKit Port Forwarding Operations

This module provides comprehensive TCP port forwarding functionality via RADKit,
enabling secure tunneling from localhost to remote device ports. Supports
both testing and persistent forwarding modes with proper error handling
and configuration validation for network automation workflows.
"""

from __future__ import absolute_import, division, print_function
from typing import Any, Dict, List, Optional, Tuple, Union
from threading import Event
import logging
import signal
import sys
import time

__metaclass__ = type

DOCUMENTATION = """
---
module: port_forward
short_description: Forwards a port on a device in RADKIT inventory to localhost port.
version_added: "0.3.0"
description:
  - This module forwards a port on a device in RADKIT inventory to local port so that connections can be made with other modules by changing port.
  - Exposed local ports are unprotected (there is no way to add an authentication layer, as these are raw TCP sockets).
  - In the case of port forwarding, no credentials are used from the RADKit service and must be configured locally on ansible client side.
options:
    device_name:
        description:
            - Name of device as it shows in RADKit inventory
        required: True
        type: str
    local_port:
        description:
            - Port on localhost to open
        required: True
        type: int
    destination_port:
        description:
            - Port on remote device to connect. Port must be configured to be forwarded in RADKIT inventory.
        required: True
        type: int
    test:
        description:
            - Tests your configuration before trying to run in async
        type: bool
        default: False
    timeout:
        description:
            - Maximum time in seconds to keep the port forward active. If not specified, runs indefinitely until terminated. Not needed to use with as
        type: int
        required: False
extends_documentation_fragment: cisco.radkit.radkit_client
requirements:
    - radkit
author: Scott Dozier (@scdozier)
"""

EXAMPLES = """
# The idea of this module is to start the module once and run on localhost for duration of the play.
# Any other module running on the localhost can utilize it to connect to devices over the opened port.
#
# This example utilizes port forwarding to connect to multiple hosts at a time. Each host will have ssh
# port forwarded to a port on the localhost (host 1 = 4000, host 2, 4001, etc). The port must be allowed
# for forwarding in the RADKIT inventory.
---
- hosts: all
  become: no
  gather_facts: no
  vars:
    # This is the base port, each host will be 4000 + index (4000, 4001, etc)
    local_port_base_num: 4000
    # in this example, we will forward ssh port
    destination_port: 22
    ansible_ssh_host: 127.0.0.1
  pre_tasks:
    - name: Get a host index number from ansible_hosts
      set_fact:
        host_index: "{{ lookup('ansible.utils.index_of', data=ansible_play_hosts, test='eq', value=inventory_hostname, wantlist=True)[0] }}"
      delegate_to: localhost

    - name: Create local_port var
      set_fact:
        local_port: "{{ local_port_base_num|int + host_index|int }}"
        ansible_ssh_port: "{{ local_port_base_num|int + host_index|int }}"
      delegate_to: localhost

    - name: Test RADKIT Port Forward To Find Potential Config Errors (optional)
      cisco.radkit.port_forward:
        device_name: "{{ inventory_hostname }}"
        local_port: "{{ local_port }}"
        destination_port: "{{ destination_port }}"
        test: True
      delegate_to: localhost

    - name: Start RADKIT Port Forward And Leave Running for 300 Seconds (adjust time based on playbook exec time)
      cisco.radkit.port_forward:
        device_name: "{{ inventory_hostname }}"
        local_port: "{{ local_port }}"
        destination_port: "{{ destination_port }}"
      async: 300
      poll: 0
      delegate_to: localhost

    - name: Wait for local port to become open (it takes a little bit for forward to start)
      ansible.builtin.wait_for:
        port: "{{ local_port }}"
        delay: 3
      delegate_to: localhost
  tasks:

    - name: Example linux module 1 (note; credentials are passed locally)
      service:
        name: sshd
        state: started

    - name: Example linux module 2 (note; credentials are passed locally)
      shell: echo $HOSTNAME
"""
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

# Constants for port forwarding operations
MIN_PORT_NUMBER = 1
MAX_PORT_NUMBER = 65535

RETURN = r"""
"""


def _validate_port_numbers(local_port: int, destination_port: int) -> None:
    """Validate port numbers are within valid range.

    Args:
        local_port: Local port number
        destination_port: Destination port number

    Raises:
        AnsibleRadkitValidationError: If port numbers are invalid
    """
    for port_name, port_num in [
        ("local_port", local_port),
        ("destination_port", destination_port),
    ]:
        if not (MIN_PORT_NUMBER <= port_num <= MAX_PORT_NUMBER):
            raise AnsibleRadkitValidationError(
                f"{port_name} must be between {MIN_PORT_NUMBER} and {MAX_PORT_NUMBER}, got {port_num}"
            )


def _get_device_inventory(
    radkit_service: RadkitClientService, device_name: str
) -> Dict[str, Any]:
    """Get device inventory for port forwarding operations.

    Args:
        radkit_service: RADKit service instance
        device_name: Device name identifier

    Returns:
        Device inventory dictionary

    Raises:
        AnsibleRadkitValidationError: If device not found
    """
    try:
        logger.info(f"Getting inventory for device: {device_name}")
        inventory = radkit_service.get_inventory_by_filter(device_name, "name")
        if not inventory:
            raise AnsibleRadkitValidationError(
                f"No devices found in RADKit inventory with name: {device_name}"
            )
        return inventory
    except Exception as e:
        logger.error(f"Failed to get device inventory: {e}")
        raise AnsibleRadkitConnectionError(f"Failed to get device inventory: {e}")


def _setup_port_forwarding(
    inventory: Dict[str, Any],
    device_name: str,
    local_port: int,
    destination_port: int,
    test_mode: bool,
    timeout: Optional[int] = None,
) -> Dict[str, Any]:
    """Set up TCP port forwarding for the device.

    Args:
        inventory: Device inventory
        device_name: Device name
        local_port: Local port to bind
        destination_port: Remote port to forward to
        test_mode: Whether to run in test mode
        timeout: Maximum time in seconds to keep the port forward active

    Returns:
        Results dictionary

    Raises:
        AnsibleRadkitOperationError: If port forwarding setup fails
    """
    port_forwarder = None
    try:
        logger.info(
            f"Setting up port forwarding: {local_port} -> {device_name}:{destination_port}"
        )

        # Create port forwarder
        port_forwarder = inventory[device_name].forward_tcp_port(
            local_port=local_port,
            destination_port=destination_port,
        )

        if test_mode:
            logger.info("Test mode: stopping port forwarder immediately")
            port_forwarder.stop()
            return {"changed": False, "test_mode": True}
        else:
            logger.info("Production mode: keeping port forwarder active")

            # Set up signal handlers for graceful shutdown
            def signal_handler(sig, frame):
                logger.info(f"Received signal {sig}, stopping port forwarder")
                if port_forwarder:
                    try:
                        port_forwarder.stop()
                    except Exception as e:
                        logger.error(f"Error stopping port forwarder: {e}")
                sys.exit(0)

            signal.signal(signal.SIGTERM, signal_handler)
            signal.signal(signal.SIGINT, signal_handler)

            # Use timeout if provided, otherwise wait indefinitely
            if timeout:
                logger.info(f"Running with timeout of {timeout} seconds")
                start_time = time.time()
                try:
                    while (time.time() - start_time) < timeout:
                        if (
                            hasattr(port_forwarder, "status")
                            and port_forwarder.status.value != "RUNNING"
                        ):
                            logger.warning("Port forwarder is no longer running")
                            break
                        time.sleep(1)
                except KeyboardInterrupt:
                    logger.info("Received keyboard interrupt")
                finally:
                    logger.info(
                        "Stopping port forwarder due to timeout or interruption"
                    )
                    port_forwarder.stop()
            else:
                logger.info("Running indefinitely until signal received")
                try:
                    # Keep checking the port forwarder status periodically
                    while True:
                        if (
                            hasattr(port_forwarder, "status")
                            and port_forwarder.status.value != "RUNNING"
                        ):
                            logger.warning(
                                "Port forwarder is no longer running, exiting"
                            )
                            break
                        time.sleep(5)  # Check every 5 seconds
                except KeyboardInterrupt:
                    logger.info("Received keyboard interrupt")
                finally:
                    logger.info("Stopping port forwarder")
                    port_forwarder.stop()

            return {"changed": True, "test_mode": False, "timeout": timeout}

    except Exception as e:
        if port_forwarder:
            try:
                logger.info("Cleaning up port forwarder due to exception")
                port_forwarder.stop()
            except Exception as cleanup_error:
                logger.error(f"Error during cleanup: {cleanup_error}")
        logger.error(f"Failed to setup port forwarding: {e}")
        raise AnsibleRadkitOperationError(f"Failed to setup port forwarding: {e}")


def run_action(
    module: AnsibleModule, radkit_service: RadkitClientService
) -> Tuple[Dict[str, Any], bool]:
    """Execute port forwarding operations via RADKit service.

    Args:
        module: Ansible module instance
        radkit_service: RADKit service client

    Returns:
        Tuple of (results dictionary, error boolean)
    """
    try:
        params = module.params
        device_name = params["device_name"]
        local_port = params["local_port"]
        destination_port = params["destination_port"]
        test_mode = params["test"]
        timeout = params.get("timeout")

        # Validate port numbers
        _validate_port_numbers(local_port, destination_port)

        # Get device inventory
        inventory = _get_device_inventory(radkit_service, device_name)

        # Setup port forwarding
        results = _setup_port_forwarding(
            inventory, device_name, local_port, destination_port, test_mode, timeout
        )

        logger.info("Port forwarding operation completed successfully")
        return results, False

    except (
        AnsibleRadkitValidationError,
        AnsibleRadkitConnectionError,
        AnsibleRadkitOperationError,
    ) as e:
        logger.error(f"RADKit port forwarding operation failed: {e}")
        return {"msg": str(e), "changed": False}, True
    except Exception as e:
        logger.error(f"Unexpected error during port forwarding operation: {e}")
        return {"msg": str(e), "changed": False}, True


def main() -> None:
    """Main function to run the port forwarding module.

    Sets up the Ansible module and executes port forwarding operations.
    """
    # Define argument specification
    spec = radkit_client_argument_spec()
    spec.update(
        {
            "device_name": {"type": "str", "required": True},
            "test": {"type": "bool", "default": False},
            "local_port": {"type": "int", "required": True},
            "destination_port": {"type": "int", "required": True},
            "timeout": {"type": "int", "required": False},
        }
    )

    # Create Ansible module
    module = AnsibleModule(argument_spec=spec, supports_check_mode=False)

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
        logger.error(f"Critical error in port forwarding module: {e}")
        module.fail_json(msg=f"Critical error in port forwarding module: {e}")


if __name__ == "__main__":
    main()
