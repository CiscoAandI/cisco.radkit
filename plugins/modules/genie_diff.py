#!/usr/bin/python
# -*- coding: utf-8 -*-
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""
Ansible Module for Cisco RADKit Genie Diff Operations

This module provides comprehensive Genie comparison functionality for analyzing
differences between network device configurations and operational states.
Supports both device-to-device comparisons and temporal snapshot analysis
for change tracking and network automation workflows.
"""

from __future__ import absolute_import, division, print_function
from typing import Any, Dict, List, Optional, Tuple, Union
import logging
import traceback

__metaclass__ = type

DOCUMENTATION = """
---
module: genie_diff
short_description: This module compares the results across multiple devices and outputs the differences.
version_added: "0.2.0"
description:
  - This module compares the results across multiple devices and outputs the differences between the parsed command output or the learned model output.
  - If diff_snapshots is used, compares differences in results from the same device.
options:
    result_a:
        description:
            - Result A from previous genie_parsed_command
        required: True
        type: dict
    result_b:
        description:
            - Result B from previous genie_parsed_command
        required: True
        type: dict
    diff_snapshots:
        description:
            - Set to true if comparing output from the same device.
        default: False
        type: bool
requirements:
    - radkit
author: Scott Dozier (@scdozier)
"""

RETURN = r"""
genie_diff_result:
    description: Result from Genie Diff
    returned: success
    type: str
genie_diff_result_lines:
    description: Result from Genie Diff split into a list
    returned: success
    type: str
"""
EXAMPLES = """
    - name:  Get show version parsed (initial snapshot)
      cisco.radkit.genie_parsed_command:
        commands: show version
        device_name: daa-csr1
        os: iosxe
      register: cmd_output
      delegate_to: localhost

    - name:  Get show version parsed (2nd snapshot)
      cisco.radkit.genie_parsed_command:
        commands: show version
        device_name: daa-csr1
        os: iosxe
      register: cmd_output2
      delegate_to: localhost

    - name:  Get a diff from snapshots daa-csr1
      cisco.radkit.genie_diff:
        result_a: "{{ cmd_output }}"
        result_b: "{{ cmd_output2 }}"
        diff_snapshots: yes
      delegate_to: localhost

    - name:  Get show version parsed from routerA
      cisco.radkit.genie_parsed_command:
        commands: show version
        device_name: daa-csr1
        os: iosxe
      register: cmd_output
      delegate_to: localhost

    - name: Get show version parsed from routerB
      cisco.radkit.genie_parsed_command:
        commands: show version
        device_name: daa-csr2
        os: iosxe
      register: cmd_output2
      delegate_to: localhost

    - name:  Get a diff from snapshots of routerA and routerB
      cisco.radkit.genie_diff:
        result_a: "{{ cmd_output }}"
        result_b: "{{ cmd_output2 }}"
        diff_snapshots: no
      delegate_to: localhost

"""
from ansible.module_utils.basic import AnsibleModule

try:
    import radkit_genie

    HAS_RADKIT_GENIE = True
except ImportError:
    HAS_RADKIT_GENIE = False
    radkit_genie = None

# Setup module logger
logger = logging.getLogger(__name__)

__metaclass__ = type

# Constants for Genie diff operations
GENIE_PARSED_RESULT_KEY = "genie_parsed_result"


def _extract_genie_result(result_data):
    """Extract Genie parsed result from module output."""
    if isinstance(result_data, dict) and GENIE_PARSED_RESULT_KEY in result_data:
        return result_data
    return result_data


def _perform_genie_diff(result_a, result_b, diff_snapshots):
    """Perform Genie diff operation using diff_dicts."""
    if not radkit_genie:
        raise ImportError("radkit_genie module is required for this operation")

    try:
        # Extract the actual parsed dictionaries for diff_dicts
        dict_a = result_a.get('genie_parsed_result', result_a) if isinstance(result_a, dict) else result_a
        dict_b = result_b.get('genie_parsed_result', result_b) if isinstance(result_b, dict) else result_b
        
        # Use diff_dicts for regular dictionaries
        diff_result = radkit_genie.diff_dicts(dict_a, dict_b)
        
        return str(diff_result)
    except Exception as e:
        raise Exception(f"Genie diff operation failed: {e}")


def run_action(module):
    """Execute Genie diff operations."""
    try:
        params = module.params
        
        # Extract Genie results from input parameters
        result_a = _extract_genie_result(params["result_a"])
        result_b = _extract_genie_result(params["result_b"])
        diff_snapshots = params["diff_snapshots"]

        # Perform the diff operation
        diff_result = _perform_genie_diff(result_a, result_b, diff_snapshots)

        # Process results
        results = {
            "genie_diff_result": diff_result,
            "genie_diff_result_lines": diff_result.split("\n"),
            "ansible_module_results": {},
            "changed": False,
        }

        return results, False

    except ImportError as e:
        return {"msg": f"Missing required dependency: {e}", "changed": False}, True
    except Exception as e:
        return {"msg": str(e), "changed": False}, True


def main() -> None:
    """Main function to run the Genie diff module.

    Sets up the Ansible module and executes Genie diff operations.
    """
    # Define argument specification
    spec = {
        "result_a": {"type": "dict", "required": True},
        "result_b": {"type": "dict", "required": True},
        "diff_snapshots": {"type": "bool", "default": False},
    }

    # Create Ansible module
    module = AnsibleModule(argument_spec=spec, supports_check_mode=False)

    # Check for required library
    if not HAS_RADKIT_GENIE:
        module.fail_json(msg="Python module radkit_genie is required for this module!")

    try:
        # Execute the diff operation
        results, err = run_action(module)

        # Return results
        if err:
            module.fail_json(**results)
        else:
            module.exit_json(**results)

    except Exception as e:
        logger.error(f"Critical error in Genie diff module: {e}")
        module.fail_json(msg=f"Critical error in Genie diff module: {e}")


if __name__ == "__main__":
    main()
