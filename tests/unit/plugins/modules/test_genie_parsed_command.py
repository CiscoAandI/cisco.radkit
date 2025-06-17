#!/usr/bin/env python3
"""
Unit tests for Ansible genie_parsed_command module.

These tests validate the core functionality of the genie_parsed_command module
by importing and testing the actual module functions.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock

# Handle import paths for both ansible-test and pytest environments
try:
    # Try collection import first (for ansible-test environment)
    from ansible_collections.cisco.radkit.plugins.modules.genie_parsed_command import (
        run_action,
        _parse_genie_results,
        _execute_single_device_commands,
    )
    GENIE_PARSED_COMMAND_MODULE_PATH = "ansible_collections.cisco.radkit.plugins.modules.genie_parsed_command"
except ImportError:
    # Fallback for local development
    import sys
    import os
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..")))
    from plugins.modules.genie_parsed_command import (
        run_action,
        _parse_genie_results,
        _execute_single_device_commands,
    )
    GENIE_PARSED_COMMAND_MODULE_PATH = None


class TestGenieParseCommandModule(unittest.TestCase):
    """Test cases for the genie_parsed_command module."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_module = Mock()
        self.mock_radkit_service = Mock()
        
        # Default valid parameters for parsed command operation
        self.default_params = {
            "commands": ["show version", "show ip interface brief"],
            "device_name": "test-device",
            "os": "iosxe",
            "filter_pattern": None,
            "filter_attr": None,
            "wait_timeout": 0,
            "exec_timeout": 0,
            "remove_cmd_and_device_keys": False,
        }
        self.mock_module.params = self.default_params.copy()

    @patch(f'{GENIE_PARSED_COMMAND_MODULE_PATH or "plugins.modules.genie_parsed_command"}.radkit_genie')
    def test_parse_genie_results_with_os_specified(self, mock_radkit_genie):
        """Test _parse_genie_results function with specific OS."""
        # Mock inventory and response
        mock_inventory = {"test-device": Mock()}
        mock_response = Mock()
        mock_radkit_result = {"test-device": {"show version": Mock()}}
        
        # Mock genie parsed result
        mock_genie_result = Mock()
        mock_genie_result.to_dict.return_value = {
            "test-device": {
                "show version": {"version": {"version": "16.09.03"}}
            }
        }
        mock_radkit_genie.parse.return_value = mock_genie_result
        
        params = {
            "os": "iosxe",
            "device_name": "test-device",
            "commands": ["show version"],
            "remove_cmd_and_device_keys": False
        }
        
        # Call the function
        result = _parse_genie_results(params, mock_radkit_result, mock_response, mock_inventory)
        
        # Verify results
        expected = {
            "test-device": {
                "show version": {"version": {"version": "16.09.03"}}
            }
        }
        self.assertEqual(result, expected)
        mock_radkit_genie.parse.assert_called_once_with(mock_response, os="iosxe")

    @patch(f'{GENIE_PARSED_COMMAND_MODULE_PATH or "plugins.modules.genie_parsed_command"}._execute_single_device_commands')
    @patch(f'{GENIE_PARSED_COMMAND_MODULE_PATH or "plugins.modules.genie_parsed_command"}._parse_genie_results')
    def test_run_action_single_device(self, mock_parse_genie, mock_execute_single):
        """Test run_action function for single device command execution."""
        # Mock the execution response
        mock_radkit_result = {"test-device": {"show version": Mock()}}
        mock_ansible_result = [{
            "device_name": "test-device",
            "command": "show version", 
            "exec_status": "SUCCESS",
            "exec_status_message": "Command executed successfully"
        }]
        mock_response = Mock()
        mock_execute_single.return_value = (mock_radkit_result, mock_ansible_result, mock_response)
        
        # Mock parsed results
        mock_parsed_result = {"test-device": {"show version": {"version": {"version": "16.09.03"}}}}
        mock_parse_genie.return_value = mock_parsed_result
        
        # Mock inventory
        self.mock_radkit_service.get_inventory_by_filter.return_value = {"test-device": Mock()}
        
        # Call the function
        results, err = run_action(self.mock_module, self.mock_radkit_service)
        
        # Verify results
        self.assertFalse(err)
        self.assertIn("genie_parsed_result", results)
        self.assertEqual(results["genie_parsed_result"], mock_parsed_result)
        self.assertFalse(results["changed"])
        
        # Verify function calls
        mock_execute_single.assert_called_once()
        mock_parse_genie.assert_called_once()


if __name__ == "__main__":
    unittest.main()
