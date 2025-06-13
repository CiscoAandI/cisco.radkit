#!/usr/bin/python
# -*- coding: utf-8 -*-
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""
Ansible module for retrieving Cisco RADKit service information and status.

This module provides comprehensive information about RADKit services including
connectivity, capabilities, inventory status, and security features.
"""

from __future__ import absolute_import, division, print_function
from typing import Any, Dict, Tuple

__metaclass__ = type

DOCUMENTATION = """
---
module: service_info
short_description: Retrieve RADKit service information and status
version_added: "0.6.0"
description:
  - Tests connectivity to RADKit service and retrieves comprehensive service information
  - Provides service status, capabilities, inventory details, and security features
  - Useful for health checks, monitoring, and service discovery operations
  - Supports optional inventory and capability updates during information gathering
options:
    ping:
        description:
            - Send ping RPC messages to verify service connectivity and responsiveness
            - Useful as a liveness check for monitoring systems
        default: true
        type: bool
    update_inventory:
        description:
            - Refresh the device inventory for this service during information gathering
            - Also refreshes service capabilities as a side effect
            - May take additional time for services with large inventories
        default: true
        type: bool
    update_capabilities:
        description:
            - Update service capabilities information during the request
            - Capabilities may change after service upgrades or configuration changes
            - Automatically enabled when update_inventory is true
        default: true
        type: bool
extends_documentation_fragment: cisco.radkit.radkit_client
requirements:
    - cisco-radkit-client
author: Scott Dozier (@scdozier)
"""

RETURN = r"""
service_id:
    description: The service ID / serial of service
    returned: success
    type: str
version:
    description: The version of service
    returned: success
    type: str
status:
    description: Returns 'up' or 'down' depending on if the service is reachable
    returned: success
    type: str
capabilities:
    description: List of capabilities of service
    returned: success
    type: list
inventory_length:
    description: Number of devices in inventory
    returned: success
    type: int
e2ee_active:
    description: Returns True E2EE is currently in use when communicating with this Service
    returned: success
    type: bool
e2ee_supported:
    description: Returns True if this Service supports end-to-end encryption (E2EE)
    returned: success
    type: bool
"""
EXAMPLES = """
    - name:  Get RADKit service info
      cisco.radkit.service_info:
        service_serial: abc-def-ghi
      register: service_info
      delegate_to: localhost
"""
try:
    from radkit_client.sync import Client

    HAS_RADKIT = True
except ImportError:
    HAS_RADKIT = False

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

import logging

# Setup module logger
logger = logging.getLogger(__name__)

__metaclass__ = type


def run_action(module: AnsibleModule) -> Tuple[Dict[str, Any], bool]:
    """
    Retrieve information about the remote RADKit service.

    Args:
        module: Ansible module instance

    Returns:
        Tuple containing results dictionary and error flag

    Raises:
        AnsibleRadkitConnectionError: For connectivity issues
        AnsibleRadkitOperationError: For service operation failures
    """
    results: Dict[str, Any] = {"changed": False}

    try:
        params = module.params

        with Client.create() as client:
            radkit_service = RadkitClientService(client, params).radkit_service

            # Perform optional ping test
            if params["ping"]:
                logger.debug("Running service ping test")
                radkit_service.ping()

            # Update inventory if requested
            if params["update_inventory"]:
                logger.debug("Updating service inventory")
                radkit_service.update_inventory()

            # Update capabilities if requested
            if params["update_capabilities"]:
                logger.debug("Updating service capabilities")
                radkit_service.update_capabilities()

            # Gather service information
            results["inventory_length"] = len(radkit_service.inventory)

            capabilities = radkit_service.capabilities.wait()
            capabilities_list = [
                capabilities[capability].name for capability in capabilities
            ]
            results["capabilities"] = capabilities_list
            results["service_id"] = capabilities.service_id
            results["e2ee_active"] = radkit_service.e2ee_active
            results["e2ee_supported"] = radkit_service.e2ee_supported
            results["version"] = radkit_service.version
            results["status"] = "up"

        return results, False

    except (
        AnsibleRadkitConnectionError,
        AnsibleRadkitValidationError,
        AnsibleRadkitOperationError,
    ) as e:
        logger.error(f"RADKit service operation failed: {e}")
        error_results = {"msg": str(e), "changed": False, "status": "down"}
        return error_results, True
    except Exception as e:
        logger.error(f"Unexpected error in service_info: {e}")
        error_results = {
            "msg": f"Unexpected error: {str(e)}",
            "changed": False,
            "status": "down",
        }
        return error_results, True


def main() -> None:
    """Main module execution function."""
    spec = radkit_client_argument_spec()
    spec.update(
        {
            "ping": {
                "type": "bool",
                "default": True,
            },
            "update_inventory": {
                "type": "bool",
                "default": True,
            },
            "update_capabilities": {
                "type": "bool",
                "default": True,
            },
        }
    )

    module = AnsibleModule(argument_spec=spec, supports_check_mode=True)

    # Validate dependencies
    if not HAS_RADKIT:
        module.fail_json(msg="Python module cisco_radkit is required for this module!")

    try:
        results, err = run_action(module)

        if err:
            module.fail_json(**results)
        module.exit_json(**results)

    except (
        AnsibleRadkitConnectionError,
        AnsibleRadkitValidationError,
        AnsibleRadkitOperationError,
    ) as e:
        module.fail_json(msg=str(e), changed=False, status="down")
    except Exception as e:
        logger.error(f"Unexpected error in main: {e}")


if __name__ == "__main__":
    main()
