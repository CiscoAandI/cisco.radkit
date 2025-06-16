#!/usr/bin/python
# -*- coding: utf-8 -*-
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""
Ansible Module for Cisco RADKit HTTP Proxy Operations

This module provides comprehensive HTTP and SOCKS proxy functionality via RADKit,
enabling secure proxied connections to network devices through RADKit infrastructure.
Supports both testing and persistent proxy modes with proper authentication
and connection management for network automation workflows.
"""

from __future__ import absolute_import, division, print_function
from typing import Any, Dict, List, Optional, Tuple, Union
import asyncio
import logging

__metaclass__ = type

DOCUMENTATION = """
---
module: http_proxy
short_description: Starts a local HTTP (and SOCKS) proxy through RADKIT for use with modules that can utilize a proxy
version_added: "0.3.0"
description:
  - This modules starts a local HTTP (and SOCKS) proxy through RADKIT for use with modules that can utilize a proxy.
  - RADKIT can natively create a SOCKS proxy, but most Ansible modules only support HTTP proxy if at all, so this module starts both.
  - Note that the proxy will ONLY forward connections to devices that have a forwarded port in RADKIT AND to hosts in format of <hostname>.<serial>.proxy.
options:
    http_proxy_port:
        description:
            - HTTP proxy port opened by module
        default: '4001'
        type: str
    socks_proxy_port:
        description:
            - SOCKS proxy port opened by RADKIT client
        default: '4000'
        type: str
    proxy_username:
        description:
            - Username for use with both http and socks proxy.
            - If the value is not specified in the task, the value of environment variable RADKIT_ANSIBLE_PROXY_USERNAME will be used instead.
        type: str
        required: True
    proxy_password:
        description:
            - Password for use with both http and socks proxy
            - If the value is not specified in the task, the value of environment variable RADKIT_ANSIBLE_PROXY_PASSWORD will be used instead.
        type: str
        required: True
    test:
        description:
            - Tests your proxy configuration before trying to run in async
        type: bool
        default: False
extends_documentation_fragment: cisco.radkit.radkit_client
requirements:
    - radkit
    - python-proxy
author: Scott Dozier (@scdozier)
"""

EXAMPLES = """
# The idea of this module is to start the module once and run on localhost for duration of the play.
# Any other module running on the localhost can utilize it to connect to devices over HTTPS.
#
# Note that connecting through the proxy in radkit is of format <device name>.<serial>.proxy
---
- hosts: all
  gather_facts: no
  vars:
    radkit_service_serial: xxxx-xxxx-xxxx
    http_proxy_username: radkit
    http_proxy_password: Radkit999
    http_proxy_port: 4001
    socks_proxy_port: 4000
  environment:
    http_proxy: "http://{{ http_proxy_username }}:{{ http_proxy_password }}@127.0.0.1:{{ http_proxy_port }}"
    https_proxy: "http://{{ http_proxy_username }}:{{ http_proxy_password }}@127.0.0.1:{{ http_proxy_port }}"
  pre_tasks:

    - name: Test HTTP Proxy RADKIT To Find Potential Config Errors (optional)
      cisco.radkit.http_proxy:
        http_proxy_port: "{{ http_proxy_port }}"
        socks_proxy_port: "{{ socks_proxy_port }}"
        proxy_username: "{{ http_proxy_username }}"
        proxy_password: "{{ http_proxy_password }}"
        test: True
      delegate_to: localhost
      run_once: true

    - name: Start HTTP Proxy Through RADKIT And Leave Running for 300 Seconds (adjust time based on playbook exec time)
      cisco.radkit.http_proxy:
        http_proxy_port: "{{ http_proxy_port }}"
        socks_proxy_port: "{{ socks_proxy_port }}"
        proxy_username: "{{ http_proxy_username }}"
        proxy_password: "{{ http_proxy_password }}"
      async: 300
      poll: 0
      delegate_to: localhost
      run_once: true

    - name: Wait for http proxy port to become open (it takes a little bit for proxy to start)
      ansible.builtin.wait_for:
        port: "{{ http_proxy_port }}"
        delay: 1
      delegate_to: localhost
      run_once: true

  tasks:

    - name: Example ACI Task that goes through http proxy
      cisco.aci.aci_system:
        hostname:  "{{ inventory_hostname }}.{{ radkit_service_serial }}.proxy"
        username: admin
        password: "password"
        state: query
        use_proxy: yes
        validate_certs: no
      delegate_to: localhost
      failed_when: False


"""
RETURN = r"""
"""

try:
    import pproxy

    HAS_PPROXY = True
except ImportError:
    HAS_PPROXY = False
    pproxy = None

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

# Setup module logger
logger = logging.getLogger(__name__)

__metaclass__ = type

# Constants for HTTP proxy operations
DEFAULT_HTTP_PROXY_PORT = "4001"
DEFAULT_SOCKS_PROXY_PORT = "4000"


def _validate_proxy_ports(http_port: str, socks_port: str) -> None:
    """Validate proxy port configurations.

    Args:
        http_port: HTTP proxy port
        socks_port: SOCKS proxy port

    Raises:
        AnsibleRadkitValidationError: If ports are invalid or the same
    """
    if http_port == socks_port:
        raise AnsibleRadkitValidationError(
            "http_proxy_port and socks_proxy_port cannot be the same"
        )

    # Validate port numbers are numeric and in valid range
    try:
        http_port_num = int(http_port)
        socks_port_num = int(socks_port)

        for port_name, port_num in [
            ("http_proxy_port", http_port_num),
            ("socks_proxy_port", socks_port_num),
        ]:
            if not (1 <= port_num <= 65535):
                raise AnsibleRadkitValidationError(
                    f"{port_name} must be between 1 and 65535, got {port_num}"
                )
    except ValueError as e:
        raise AnsibleRadkitValidationError(f"Port numbers must be numeric: {e}")


def _start_socks_proxy(
    radkit_service: RadkitClientService, socks_port: str, username: str, password: str
) -> None:
    """Start SOCKS proxy via RADKit.

    Args:
        radkit_service: RADKit service instance
        socks_port: SOCKS proxy port
        username: Proxy username
        password: Proxy password

    Raises:
        AnsibleRadkitOperationError: If SOCKS proxy startup fails
    """
    try:
        logger.info(f"Starting SOCKS proxy on port {socks_port}")
        radkit_service.radkit_client.start_socks_proxy(
            socks_port, username=username, password=password
        )
        logger.info("SOCKS proxy started successfully")
    except Exception as e:
        logger.error(f"Failed to start SOCKS proxy: {e}")
        raise AnsibleRadkitOperationError(f"Failed to start SOCKS proxy: {e}")


def _setup_http_proxy(
    http_port: str, socks_port: str, username: str, password: str
) -> Tuple[Any, Any, Any]:
    """Set up HTTP proxy server.

    Args:
        http_port: HTTP proxy port
        socks_port: SOCKS proxy port for forwarding
        username: Proxy username
        password: Proxy password

    Returns:
        Tuple of (server, remote, event_loop)

    Raises:
        AnsibleRadkitOperationError: If HTTP proxy setup fails
    """
    if not pproxy:
        raise ImportError("pproxy module is required for HTTP proxy functionality")

    try:
        logger.info(f"Setting up HTTP proxy on port {http_port}")

        # Create HTTP proxy server
        server = pproxy.Server(f"http://0.0.0.0:{http_port}#{username}:{password}")

        # Create connection to SOCKS proxy
        remote = pproxy.Connection(
            f"socks5://127.0.0.1:{socks_port}#{username}:{password}"
        )

        # Set up event loop
        loop = asyncio.get_event_loop()

        logger.info("HTTP proxy server configured successfully")
        return server, remote, loop

    except Exception as e:
        logger.error(f"Failed to setup HTTP proxy: {e}")
        raise AnsibleRadkitOperationError(f"Failed to setup HTTP proxy: {e}")


def _run_proxy_servers(
    server: Any,
    remote: Any,
    loop: Any,
    test_mode: bool,
    radkit_service: RadkitClientService,
) -> Dict[str, Any]:
    """Run HTTP and SOCKS proxy servers.

    Args:
        server: HTTP proxy server instance
        remote: SOCKS proxy connection
        loop: Event loop
        test_mode: Whether to run in test mode
        radkit_service: RADKit service for cleanup

    Returns:
        Results dictionary

    Raises:
        AnsibleRadkitOperationError: If proxy servers fail
    """
    try:
        args = dict(rserver=[remote], verbose=print)
        handler = loop.run_until_complete(server.start_server(args))

        if test_mode:
            logger.info("Test mode: stopping proxy servers immediately")
            handler.close()
            loop.run_until_complete(handler.wait_closed())
            loop.run_until_complete(loop.shutdown_asyncgens())
            loop.close()
            radkit_service.radkit_client.stop_socks_proxy()
            return {"changed": False, "test_mode": True}
        else:
            logger.info("Production mode: keeping proxy servers active")
            try:
                loop.run_forever()
            except KeyboardInterrupt:
                logger.info("Received KeyboardInterrupt, shutting down proxies")
            finally:
                handler.close()
                loop.run_until_complete(handler.wait_closed())
                loop.run_until_complete(loop.shutdown_asyncgens())
                loop.close()
            return {"changed": True, "test_mode": False}

    except Exception as e:
        logger.error(f"Failed to run proxy servers: {e}")
        raise AnsibleRadkitOperationError(f"Failed to run proxy servers: {e}")


def run_action(
    module: AnsibleModule, radkit_service: RadkitClientService
) -> Tuple[Dict[str, Any], bool]:
    """Execute HTTP proxy operations via RADKit service.

    Args:
        module: Ansible module instance
        radkit_service: RADKit service client

    Returns:
        Tuple of (results dictionary, error boolean)
    """
    try:
        params = module.params
        http_port = params["http_proxy_port"]
        socks_port = params["socks_proxy_port"]
        username = params["proxy_username"]
        password = params["proxy_password"]
        test_mode = params["test"]

        # Validate proxy configuration
        _validate_proxy_ports(http_port, socks_port)

        # Start SOCKS proxy
        _start_socks_proxy(radkit_service, socks_port, username, password)

        # Set up HTTP proxy
        server, remote, loop = _setup_http_proxy(
            http_port, socks_port, username, password
        )

        # Run proxy servers
        results = _run_proxy_servers(server, remote, loop, test_mode, radkit_service)
        results["ansible_module_results"] = {}

        logger.info("HTTP proxy operation completed successfully")
        return results, False

    except (
        AnsibleRadkitValidationError,
        AnsibleRadkitConnectionError,
        AnsibleRadkitOperationError,
    ) as e:
        logger.error(f"RADKit HTTP proxy operation failed: {e}")
        return {"msg": str(e), "changed": False}, True
    except ImportError as e:
        logger.error(f"Missing required dependency: {e}")
        return {"msg": f"Missing required dependency: {e}", "changed": False}, True
    except Exception as e:
        logger.error(f"Unexpected error during HTTP proxy operation: {e}")
        return {"msg": str(e), "changed": False}, True


def main() -> None:
    """Main function to run the HTTP proxy module.

    Sets up the Ansible module and executes HTTP proxy operations.
    """
    # Define argument specification
    spec = radkit_client_argument_spec()
    spec.update(
        {
            "test": {"type": "bool", "default": False},
            "http_proxy_port": {"type": "str", "default": DEFAULT_HTTP_PROXY_PORT},
            "socks_proxy_port": {"type": "str", "default": DEFAULT_SOCKS_PROXY_PORT},
            "proxy_username": {
                "type": "str",
                "required": True,
                "fallback": (env_fallback, ["RADKIT_ANSIBLE_PROXY_USERNAME"]),
            },
            "proxy_password": {
                "type": "str",
                "required": True,
                "no_log": True,
                "fallback": (env_fallback, ["RADKIT_ANSIBLE_PROXY_PASSWORD"]),
            },
        }
    )

    # Create Ansible module
    module = AnsibleModule(argument_spec=spec, supports_check_mode=False)

    # Check for required libraries
    if not HAS_PPROXY:
        module.fail_json(msg="Python module pproxy is required for this module!")

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
        logger.error(f"Critical error in HTTP proxy module: {e}")
        module.fail_json(msg=f"Critical error in HTTP proxy module: {e}")


if __name__ == "__main__":
    main()
