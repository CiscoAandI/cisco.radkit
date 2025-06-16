#!/usr/bin/python
# -*- coding: utf-8 -*-
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""
Ansible Module for Cisco RADKit SSH Proxy Operations

This module provides comprehensive SSH proxy functionality via RADKit,
enabling secure SSH access to remote devices through the RADKit service.
Supports both testing and persistent proxy modes with proper error handling
and configuration validation for network automation workflows.
"""

from __future__ import absolute_import, division, print_function
from typing import Any, Dict, List, Optional, Tuple, Union
import logging
import signal
import sys
import time

__metaclass__ = type

DOCUMENTATION = """
---
module: ssh_proxy
short_description: Starts an SSH server proxy to access devices in RADKIT inventory via SSH.
version_added: "2.0.0"
description:
  - This module starts an SSH server that proxies connections to devices in RADKIT inventory.
  - SSH username format is <device_name>@<radkit_service_serial> to specify the target device.
  - Supports both shell and exec modes for device interaction.
  - Key advantage over port forwarding - device credentials remain on the RADKit service, not locally.
  - "RECOMMENDED FOR: Network devices (routers, switches, firewalls) with Ansible network_cli connection."
  - "FOR LINUX SERVERS: Use port_forward module instead - SSH proxy has limitations with SCP/file transfers."
  - "IMPORTANT: Always disable SSH host key checking unless custom host keys are configured (host keys are ephemeral by default)."
  - "Password authentication to SSH proxy may not work reliably with Ansible network_cli connection."
  - "For network devices, use without password and rely on RADKit service authentication."
  - "SCP and SFTP file transfers are not supported through SSH proxy - use port_forward for Linux servers."
  - "This module replaces the deprecated network_cli and terminal connection plugins as of version 2.0.0."
options:
    local_port:
        description:
            - Port on localhost to bind the SSH server
        required: True
        type: int
    local_address:
        description:
            - Local address to bind the SSH server to
        required: False
        type: str
        default: localhost
    password:
        description:
            - Password for SSH authentication to the proxy server (optional)
            - "WARNING: Using password may cause authentication issues with Ansible network_cli connection"
            - "RECOMMENDED: Leave empty and rely on RADKit service authentication for network devices"
            - This password protects access to the SSH proxy itself, not the device credentials
            - Device credentials remain securely on the RADKit service side
        required: False
        type: str
    host_key:
        description:
            - Custom SSH host private key in PEM format. If not provided, an ephemeral key will be generated.
        type: str
        required: False
        no_log: True
    destroy_previous:
        description:
            - Destroy any existing SSH proxy before starting a new one
        type: bool
        default: False
    test:
        description:
            - Tests your configuration before trying to run in async
        type: bool
        default: False
    timeout:
        description:
            - Maximum time in seconds to keep the SSH server active. If not specified, runs indefinitely until terminated.
        type: int
        required: False
extends_documentation_fragment: cisco.radkit.radkit_client
requirements:
    - radkit
author: Scott Dozier (@scdozier)
"""

EXAMPLES = """
# Recommended: SSH proxy for network devices without password
# This configuration works reliably with Ansible network_cli connection
---
- name: Setup RADKit SSH Proxy for Network Devices
  hosts: localhost
  become: no
  gather_facts: no
  vars:
    ssh_proxy_port: 2225
    radkit_service_serial: "{{ lookup('env', 'RADKIT_ANSIBLE_SERVICE_SERIAL') }}"
  tasks:
    - name: Test RADKIT SSH Proxy Configuration (optional)
      cisco.radkit.ssh_proxy:
        local_port: "{{ ssh_proxy_port }}"
        test: True


    - name: Start RADKIT SSH Proxy Server
      cisco.radkit.ssh_proxy:
        local_port: "{{ ssh_proxy_port }}"
      async: 300  # Keep running for 5 minutes
      poll: 0

    - name: Wait for SSH proxy to become available
      ansible.builtin.wait_for:
        port: "{{ ssh_proxy_port }}"
        host: 127.0.0.1
        delay: 3
        timeout: 30

- name: Execute commands on network devices via SSH proxy
  hosts: cisco_devices
  become: no
  gather_facts: no
  connection: ansible.netcommon.network_cli
  vars:
    ansible_network_os: ios
    ansible_port: 2225  # Port where the ssh_proxy is listening
    ansible_user: "{{ inventory_hostname }}@{{ lookup('env', 'RADKIT_ANSIBLE_SERVICE_SERIAL') }}"
    # IMPORTANT: Disable host key checking - SSH proxy host keys change between sessions
    ansible_ssh_common_args: '-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null'
  tasks:
    - name: Run show ip interface brief
      cisco.ios.ios_command:
        commands: show ip interface brief
      register: interfaces_output
      
    - name: Display interface information
      debug:
        var: interfaces_output.stdout_lines

# Inventory configuration for the above playbook:
# [cisco_devices]
# router1 ansible_host=127.0.0.1
# 
# [cisco_devices:vars]
# ansible_ssh_common_args='-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null'

# WARNING: Using password under ssh_proxy module may cause authentication issues

- name: SSH Proxy
  hosts: localhost
  become: no
  gather_facts: no
  tasks:
    - name: Start RADKIT SSH Proxy with Password
      cisco.radkit.ssh_proxy:
        local_port: 2222
      async: 300
      poll: 0
      
    # Manual SSH connection works: ssh device@service@localhost -p 2222
    # But Ansible network_cli may fail with authentication errors

# Example with custom host key for consistent fingerprints
- name: SSH Proxy with Custom Host Key
  hosts: localhost
  become: no
  gather_facts: no
  vars:
    ssh_host_key: |
      -----BEGIN OPENSSH PRIVATE KEY-----
      b3BlbnNzaC1rZXktdjEAAAAABG5vbmUAAAAEbm9uZQAAAAAAAAABAAAAFwAAAAdzc2gtcn
      ...
      -----END OPENSSH PRIVATE KEY-----
  tasks:
    - name: Start RADKIT SSH Proxy with Custom Host Key
      cisco.radkit.ssh_proxy:
        local_port: 2222
        host_key: "{{ ssh_host_key }}"
        destroy_previous: True
      async: 300
      poll: 0

# IMPORTANT USAGE NOTES:
# 
# 1. FOR NETWORK DEVICES (routers, switches, firewalls):
#    - Use ssh_proxy module (this module)
#    - Works with ansible.netcommon.network_cli connection
#    - No password on SSH proxy recommended
#    - Always disable host key checking
#
# 2. FOR LINUX SERVERS:
#    - Use port_forward module instead
#    - SSH proxy doesn't support SCP/SFTP file transfers
#    - Required for Ansible modules that transfer files
#
# 3. DEPRECATED CONNECTION PLUGINS:
#    - cisco.radkit.network_cli (deprecated as of 2.0.0)
#    - cisco.radkit.terminal (deprecated as of 2.0.0)
#    - Use standard ansible.netcommon.network_cli with ssh_proxy instead
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

# Constants for SSH proxy operations
MIN_PORT_NUMBER = 1
MAX_PORT_NUMBER = 65535

RETURN = r"""
ssh_server_info:
    description: Information about the SSH server that was started
    returned: success
    type: dict
    contains:
        status:
            description: Status of the SSH server
            type: str
            sample: "RUNNING"
        local_port:
            description: Port the SSH server is listening on
            type: int
            sample: 2222
        local_address:
            description: Address the SSH server is bound to
            type: str
            sample: "localhost"
        addresses:
            description: List of addresses the SSH server is bound to
            type: list
            sample: [["::1", 2222], ["127.0.0.1", 2222]]
        fingerprint_md5:
            description: MD5 fingerprint of the SSH host key
            type: str
            sample: "MD5:fc:68:c6:3c:b0:e7:3f:3e:6e:d4:34:ff:aa:57:ce:ef"
        fingerprint_sha256:
            description: SHA256 fingerprint of the SSH host key
            type: str
            sample: "SHA256:+HOFSDUBXhbY5SSvBzxBysw+SlrXuRYo2RP84/Lyxns"
"""


def _validate_port_number(local_port: int) -> None:
    """Validate port number is within valid range.

    Args:
        local_port: Local port number

    Raises:
        AnsibleRadkitValidationError: If port number is invalid
    """
    if not (MIN_PORT_NUMBER <= local_port <= MAX_PORT_NUMBER):
        raise AnsibleRadkitValidationError(
            f"local_port must be between {MIN_PORT_NUMBER} and {MAX_PORT_NUMBER}, got {local_port}"
        )


def _setup_ssh_forwarding(
    client,
    local_port: int,
    local_address: str,
    password: Optional[str],
    test_mode: bool,
    host_key: Optional[str] = None,
    destroy_previous: bool = False,
    timeout: Optional[int] = None,
) -> Dict[str, Any]:
    """Set up SSH forwarding server.

    Args:
        client: RADKit Client instance
        local_port: Local port to bind
        local_address: Local address to bind to
        password: SSH authentication password
        test_mode: Whether to run in test mode
        host_key: Optional custom SSH host key
        destroy_previous: Whether to destroy existing proxy
        timeout: Maximum time in seconds to keep the SSH server active

    Returns:
        Results dictionary

    Raises:
        AnsibleRadkitOperationError: If SSH forwarding setup fails
    """
    ssh_server = None
    try:
        logger.info(f"Setting up SSH proxy on {local_address}:{local_port}")

        # Prepare arguments for start_ssh_proxy
        ssh_args = {
            "local_port": local_port,
            "local_address": local_address,
            "destroy_previous": destroy_previous,
        }

        # Add password if provided
        if password:
            ssh_args["password"] = password

        # Add host key if provided
        if host_key:
            ssh_args["host_key"] = host_key.encode("utf-8")

        # Create SSH server using client method
        # Based on interactive session: client.start_ssh_proxy(2222)
        if password and host_key:
            ssh_server = client.start_ssh_proxy(
                local_port,
                local_address=local_address,
                password=password,
                host_key=host_key.encode("utf-8"),
                destroy_previous=destroy_previous,
            )
        elif password:
            ssh_server = client.start_ssh_proxy(
                local_port,
                local_address=local_address,
                password=password,
                destroy_previous=destroy_previous,
            )
        elif host_key:
            ssh_server = client.start_ssh_proxy(
                local_port,
                local_address=local_address,
                host_key=host_key.encode("utf-8"),
                destroy_previous=destroy_previous,
            )
        else:
            ssh_server = client.start_ssh_proxy(
                local_port,
                local_address=local_address,
                destroy_previous=destroy_previous,
            )

        if test_mode:
            logger.info("Test mode: stopping SSH server immediately")
            # Get server info before stopping
            server_info = {
                "status": ssh_server.status.value
                if hasattr(ssh_server, "status")
                else "UNKNOWN",
                "local_port": local_port,
                "local_address": local_address,
                "addresses": ssh_server.addresses
                if hasattr(ssh_server, "addresses")
                else [],
                "fingerprint_md5": ssh_server.host_key_pair.fingerprint_md5
                if hasattr(ssh_server, "host_key_pair")
                else "",
                "fingerprint_sha256": ssh_server.host_key_pair.fingerprint_sha256
                if hasattr(ssh_server, "host_key_pair")
                else "",
            }
            client.stop_ssh_proxy()
            return {"changed": False, "test_mode": True, "ssh_server_info": server_info}
        else:
            logger.info("Production mode: keeping SSH server active")

            # Get server info
            server_info = {
                "status": ssh_server.status.value
                if hasattr(ssh_server, "status")
                else "UNKNOWN",
                "local_port": local_port,
                "local_address": local_address,
                "addresses": ssh_server.addresses
                if hasattr(ssh_server, "addresses")
                else [],
                "fingerprint_md5": ssh_server.host_key_pair.fingerprint_md5
                if hasattr(ssh_server, "host_key_pair")
                else "",
                "fingerprint_sha256": ssh_server.host_key_pair.fingerprint_sha256
                if hasattr(ssh_server, "host_key_pair")
                else "",
            }

            # Set up signal handlers for graceful shutdown
            def signal_handler(sig, frame):
                logger.info(f"Received signal {sig}, stopping SSH server")
                try:
                    client.stop_ssh_proxy()
                except Exception as e:
                    logger.error(f"Error stopping SSH server: {e}")
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
                            hasattr(ssh_server, "status")
                            and ssh_server.status.value != "RUNNING"
                        ):
                            logger.warning("SSH server is no longer running")
                            break
                        time.sleep(1)
                except KeyboardInterrupt:
                    logger.info("Received keyboard interrupt")
                finally:
                    logger.info("Stopping SSH server due to timeout or interruption")
                    client.stop_ssh_proxy()
            else:
                logger.info("Running indefinitely until signal received")
                try:
                    # Keep checking the SSH server status periodically
                    while True:
                        if (
                            hasattr(ssh_server, "status")
                            and ssh_server.status.value != "RUNNING"
                        ):
                            logger.warning("SSH server is no longer running, exiting")
                            break
                        time.sleep(5)  # Check every 5 seconds
                except KeyboardInterrupt:
                    logger.info("Received keyboard interrupt")
                finally:
                    logger.info("Stopping SSH server")
                    client.stop_ssh_proxy()

            return {
                "changed": True,
                "test_mode": False,
                "timeout": timeout,
                "ssh_server_info": server_info,
            }

    except Exception as e:
        if ssh_server:
            try:
                logger.info("Cleaning up SSH server due to exception")
                client.stop_ssh_proxy()
            except Exception as cleanup_error:
                logger.error(f"Error during cleanup: {cleanup_error}")
        logger.error(f"Failed to setup SSH forwarding: {e}")
        raise AnsibleRadkitOperationError(f"Failed to setup SSH forwarding: {e}")


def run_action(
    module: AnsibleModule, radkit_service: RadkitClientService
) -> Tuple[Dict[str, Any], bool]:
    """Execute SSH forwarding operations via RADKit service.

    Args:
        module: Ansible module instance
        radkit_service: RADKit service client

    Returns:
        Tuple of (results dictionary, error boolean)
    """
    try:
        params = module.params
        local_port = params["local_port"]
        local_address = params.get("local_address", "localhost")
        password = params.get("password")
        test_mode = params["test"]
        host_key = params.get("host_key")
        destroy_previous = params.get("destroy_previous", False)
        timeout = params.get("timeout")

        # Validate port number
        _validate_port_number(local_port)

        # Get the client from the service
        client = radkit_service.radkit_client

        # Setup SSH forwarding
        results = _setup_ssh_forwarding(
            client,
            local_port,
            local_address,
            password,
            test_mode,
            host_key,
            destroy_previous,
            timeout,
        )

        logger.info("SSH forwarding operation completed successfully")
        return results, False

    except (
        AnsibleRadkitValidationError,
        AnsibleRadkitConnectionError,
        AnsibleRadkitOperationError,
    ) as e:
        logger.error(f"RADKit SSH forwarding operation failed: {e}")
        return {"msg": str(e), "changed": False}, True
    except Exception as e:
        logger.error(f"Unexpected error during SSH forwarding operation: {e}")
        return {"msg": str(e), "changed": False}, True


def main() -> None:
    """Main function to run the SSH forwarding module.

    Sets up the Ansible module and executes SSH forwarding operations.
    """
    # Define argument specification
    spec = radkit_client_argument_spec()
    spec.update(
        {
            "local_port": {"type": "int", "required": True},
            "local_address": {"type": "str", "required": False, "default": "localhost"},
            "password": {"type": "str", "required": False, "no_log": True},
            "host_key": {"type": "str", "required": False, "no_log": True},
            "destroy_previous": {"type": "bool", "default": False},
            "test": {"type": "bool", "default": False},
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
        logger.error(f"Critical error in SSH forwarding module: {e}")
        module.fail_json(msg=f"Critical error in SSH forwarding module: {e}")


if __name__ == "__main__":
    main()
