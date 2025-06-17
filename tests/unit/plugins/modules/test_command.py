#!/usr/bin/env python3
"""
Unit tests for the command module.

These tests validate the core functionality of the command module,
specifically testing the run_action and helper functions.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
from ansible.module_utils.basic import AnsibleModule

# Handle import paths for both ansible-test and pytest environments
try:
    # Try collection import first (for ansible-test environment)
    from ansible_collections.cisco.radkit.plugins.modules.command import (
        run_action,
        _execute_on_single_device,
        _format_command_results,
    )
    from ansible_collections.cisco.radkit.plugins.module_utils.exceptions import (
        AnsibleRadkitValidationError,
        AnsibleRadkitOperationError,
    )
    COMMAND_MODULE_PATH = "ansible_collections.cisco.radkit.plugins.modules.command"
except ImportError:
    # Fallback for local development
    import sys
    import os
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..")))
    from plugins.modules.command import (
        run_action,
        _execute_on_single_device,
        _format_command_results,
    )
    from plugins.module_utils.exceptions import (
        AnsibleRadkitValidationError,
        AnsibleRadkitOperationError,
    )
    COMMAND_MODULE_PATH = None


class TestCommandModule(unittest.TestCase):
    """Test cases for the command module."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_module = Mock(spec=AnsibleModule)
        self.mock_radkit_service = Mock()
        
        # Default valid parameters
        self.default_params = {
            "device_name": "test-device",
            "commands": ["show version"],
            "wait_timeout": 0,
            "exec_timeout": 0,
            "remove_prompts": True,
            "filter_pattern": None,
            "filter_attr": None,
        }
        self.mock_module.params = self.default_params.copy()
        
        # Create properly structured mock command result
        self.mock_cmd_result = Mock()
        self.mock_cmd_result.status.value = "SUCCESS"
        self.mock_cmd_result.status_message = "Command executed successfully"
        self.mock_cmd_result.data = "Router> show version\nCisco IOS XE Software, Version 16.09.03\nRouter>"
        self.mock_cmd_result.command = "show version"
        
        # Mock device
        self.mock_device = Mock()
        self.mock_device.name = "test-device"
        self.mock_cmd_result.device = self.mock_device

    def test_execute_on_single_device_success(self):
        """Test successful command execution on a single device."""
        # Create a properly structured device result object that behaves like the radkit result
        mock_device_result = Mock()
        mock_device_result.status.value = "SUCCESS"
        mock_device_result.status_message = "Command executed successfully"
        
        # Mock the device result to be iterable for _format_command_results
        # It should behave like a dict with command keys
        mock_device_result.__iter__ = Mock(return_value=iter(["show version"]))
        mock_device_result.__getitem__ = Mock(return_value=self.mock_cmd_result)
        
        # Mock inventory and response
        mock_inventory = Mock()
        self.mock_radkit_service.get_inventory_by_filter.return_value = mock_inventory
        self.mock_radkit_service.exec_command.return_value = {"test-device": mock_device_result}
        
        params = {
            "device_name": "test-device",
            "commands": ["show version"],
            "remove_prompts": True,
        }
        
        result = _execute_on_single_device(self.mock_radkit_service, params)
        
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["device_name"], "test-device")
        self.assertEqual(result[0]["command"], "show version")
        self.assertEqual(result[0]["exec_status"], "SUCCESS")

    def test_run_action_single_device(self):
        """Test run_action with single device."""
        # Create a properly structured device result object
        mock_device_result = Mock()
        mock_device_result.status.value = "SUCCESS"
        mock_device_result.status_message = "Command executed successfully"
        
        # Mock the device result to be iterable for _format_command_results
        mock_device_result.__iter__ = Mock(return_value=iter(["show version"]))
        mock_device_result.__getitem__ = Mock(return_value=self.mock_cmd_result)
        
        # Mock inventory and response
        mock_inventory = Mock()
        self.mock_radkit_service.get_inventory_by_filter.return_value = mock_inventory
        self.mock_radkit_service.exec_command.return_value = {"test-device": mock_device_result}
        
        results, err = run_action(self.mock_module, self.mock_radkit_service)
        
        self.assertFalse(err)
        self.assertIn("device_name", results)
        self.assertIn("command", results)
        self.assertIn("exec_status", results)

if __name__ == "__main__":
    unittest.main()
