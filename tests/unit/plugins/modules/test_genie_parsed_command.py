#!/usr/bin/env python3
"""
Unit tests for the genie_parsed_command module.

These tests validate basic functionality of the genie_parsed_command module.
"""

import unittest
from unittest.mock import Mock, patch
from ansible.module_utils.basic import AnsibleModule


class TestGenieParseCommandModule(unittest.TestCase):
    """Test cases for the genie_parsed_command module."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_module = Mock()
        self.mock_radkit_service = Mock(spec=RadkitClientService)
        
        # Default valid parameters
        self.default_params = {
            "commands": ["show version", "show ip interface brief"],
            "device_name": "test-device",
            "os": "ios",
            "filter_pattern": None,
            "filter_attr": None,
            "wait_timeout": 0,
            "exec_timeout": 0,
            "remove_cmd_and_device_keys": False,
        }
        self.mock_module.params = self.default_params.copy()

    def test_validate_module_parameters_device_name_only(self):
        """Test parameter validation with device_name only."""
        self.mock_module.params = {
            "device_name": "test-device",
            "commands": ["show version"],
            "filter_pattern": None,
            "filter_attr": None,
        }
        
        # Should not raise any exception
        _validate_module_parameters(self.mock_module)
        self.mock_module.fail_json.assert_not_called()

    def test_validate_module_parameters_filter_pattern_only(self):
        """Test parameter validation with filter pattern only."""
        self.mock_module.params = {
            "device_name": None,
            "commands": ["show version"],
            "filter_pattern": "router*",
            "filter_attr": "name",
        }
        
        # Should not raise any exception
        _validate_module_parameters(self.mock_module)
        self.mock_module.fail_json.assert_not_called()

    def test_validate_module_parameters_missing_device_target(self):
        """Test parameter validation with missing device target."""
        self.mock_module.params = {
            "device_name": None,
            "commands": ["show version"],
            "filter_pattern": None,
            "filter_attr": None,
        }
        
        _validate_module_parameters(self.mock_module)
        self.mock_module.fail_json.assert_called_once_with(
            msg="Must provide either 'device_name' or both 'filter_pattern' and 'filter_attr'"
        )

    def test_validate_module_parameters_incomplete_filter(self):
        """Test parameter validation with incomplete filter parameters."""
        self.mock_module.params = {
            "device_name": None,
            "commands": ["show version"],
            "filter_pattern": "router*",
            "filter_attr": None,
        }
        
        _validate_module_parameters(self.mock_module)
        self.mock_module.fail_json.assert_called_once_with(
            msg="Must provide either 'device_name' or both 'filter_pattern' and 'filter_attr'"
        )

    def test_run_action_single_device_success(self):
        """Test successful command parsing on single device."""
        # Mock parsed command result
        mock_parsed_result = {
            "device_name": "test-device",
            "command": "show version",
            "parsed_output": {
                "version": {
                    "version": "15.1(4)M",
                    "hostname": "Router1",
                    "uptime": "1 day, 2 hours"
                }
            }
        }
        
        self.mock_radkit_service.genie_parse_command.return_value = [mock_parsed_result]
        
        result, error = run_action(self.mock_module, self.mock_radkit_service)
        
        self.assertFalse(error)
        self.assertEqual(result["changed"], False)
        self.assertEqual(len(result["ansible_module_results"]), 1)
        self.assertEqual(result["ansible_module_results"][0]["device_name"], "test-device")
        self.assertIn("parsed_output", result["ansible_module_results"][0])

    def test_run_action_multiple_devices_success(self):
        """Test successful command parsing on multiple devices."""
        self.mock_module.params = {
            "commands": ["show version"],
            "device_name": None,
            "os": "ios",
            "filter_pattern": "router*",
            "filter_attr": "name",
            "wait_timeout": 0,
            "exec_timeout": 0,
            "remove_cmd_and_device_keys": False,
        }
        
        # Mock parsed command results
        mock_parsed_results = [
            {
                "device_name": "router1",
                "command": "show version",
                "parsed_output": {
                    "version": {
                        "version": "15.1(4)M",
                        "hostname": "Router1"
                    }
                }
            },
            {
                "device_name": "router2",
                "command": "show version",
                "parsed_output": {
                    "version": {
                        "version": "15.2(4)M",
                        "hostname": "Router2"
                    }
                }
            }
        ]
        
        self.mock_radkit_service.genie_parse_commands_on_devices.return_value = mock_parsed_results
        
        result, error = run_action(self.mock_module, self.mock_radkit_service)
        
        self.assertFalse(error)
        self.assertEqual(result["changed"], False)
        self.assertEqual(len(result["ansible_module_results"]), 2)
        self.assertEqual(result["ansible_module_results"][0]["device_name"], "router1")
        self.assertEqual(result["ansible_module_results"][1]["device_name"], "router2")

    def test_run_action_with_cmd_device_key_removal(self):
        """Test command parsing with command and device key removal."""
        self.mock_module.params = self.default_params.copy()
        self.mock_module.params["remove_cmd_and_device_keys"] = True
        
        # Mock parsed command result
        mock_parsed_result = {
            "device_name": "test-device",
            "command": "show version",
            "parsed_output": {
                "version": {
                    "version": "15.1(4)M",
                    "hostname": "Router1"
                }
            }
        }
        
        self.mock_radkit_service.genie_parse_command.return_value = [mock_parsed_result]
        
        result, error = run_action(self.mock_module, self.mock_radkit_service)
        
        self.assertFalse(error)
        self.assertEqual(result["changed"], False)
        # Should have processed the key removal
        self.assertEqual(len(result["ansible_module_results"]), 1)

    def test_run_action_parsing_failure(self):
        """Test handling of parsing failure."""
        # Mock parsing failure
        mock_parsed_result = {
            "device_name": "test-device",
            "command": "show version",
            "parsed_output": None,
            "error": "Failed to parse command output"
        }
        
        self.mock_radkit_service.genie_parse_command.return_value = [mock_parsed_result]
        
        result, error = run_action(self.mock_module, self.mock_radkit_service)
        
        self.assertFalse(error)  # Parsing failure is not a module error
        self.assertEqual(result["changed"], False)
        self.assertEqual(len(result["ansible_module_results"]), 1)
        self.assertIn("error", result["ansible_module_results"][0])

    def test_run_action_connection_error(self):
        """Test run_action with connection error."""
        self.mock_radkit_service.genie_parse_command.side_effect = AnsibleRadkitConnectionError("Device unreachable")
        
        result, error = run_action(self.mock_module, self.mock_radkit_service)
        
        self.assertTrue(error)
        self.assertEqual(result["changed"], False)
        self.assertIn("Device unreachable", result["msg"])

    def test_run_action_validation_error(self):
        """Test run_action with validation error."""
        self.mock_radkit_service.genie_parse_command.side_effect = AnsibleRadkitValidationError("Invalid command")
        
        result, error = run_action(self.mock_module, self.mock_radkit_service)
        
        self.assertTrue(error)
        self.assertEqual(result["changed"], False)
        self.assertIn("Invalid command", result["msg"])

    def test_run_action_operation_error(self):
        """Test run_action with operation error."""
        self.mock_radkit_service.genie_parse_command.side_effect = AnsibleRadkitOperationError("Parsing failed")
        
        result, error = run_action(self.mock_module, self.mock_radkit_service)
        
        self.assertTrue(error)
        self.assertEqual(result["changed"], False)
        self.assertIn("Parsing failed", result["msg"])

    def test_run_action_unexpected_error(self):
        """Test run_action with unexpected error."""
        self.mock_radkit_service.genie_parse_command.side_effect = Exception("Unexpected error")
        
        result, error = run_action(self.mock_module, self.mock_radkit_service)
        
        self.assertTrue(error)
        self.assertEqual(result["changed"], False)
        self.assertIn("Unexpected error", result["msg"])

    @patch(f"{MODULE_PATH}.AnsibleModule")
    @patch(f"{MODULE_PATH}.Client")
    @patch(f"{MODULE_PATH}.RadkitClientService")
    @patch(f"{MODULE_PATH}.HAS_RADKIT", True)
    @patch(f"{MODULE_PATH}.HAS_RADKIT_GENIE", True)
    def test_main_success(self, mock_radkit_service_class, mock_client_class, mock_ansible_module_class):
        """Test main function with successful execution."""
        # Setup mocks
        mock_module = Mock()
        mock_module.params = self.default_params
        mock_ansible_module_class.return_value = mock_module
        
        mock_client = Mock()
        mock_client_class.create.return_value.__enter__.return_value = mock_client
        
        mock_radkit_service = Mock()
        mock_radkit_service_class.return_value = mock_radkit_service
        
        mock_results = {"changed": False, "ansible_module_results": []}
        
        with patch(f"{MODULE_PATH}.run_action", return_value=(mock_results, False)):
            with patch(f"{MODULE_PATH}._validate_module_parameters"):
                main()
        
        mock_module.exit_json.assert_called_once_with(**mock_results)
        mock_module.fail_json.assert_not_called()

    @patch(f"{MODULE_PATH}.AnsibleModule")
    @patch(f"{MODULE_PATH}.HAS_RADKIT", False)
    def test_main_missing_radkit(self, mock_ansible_module_class):
        """Test main function with missing RADKit dependency."""
        mock_module = Mock()
        mock_ansible_module_class.return_value = mock_module
        
        main()
        
        mock_module.fail_json.assert_called_once()
        call_args = mock_module.fail_json.call_args[1]
        self.assertIn("cisco_radkit", call_args["msg"])

    @patch(f"{MODULE_PATH}.AnsibleModule")
    @patch(f"{MODULE_PATH}.HAS_RADKIT", True)
    @patch(f"{MODULE_PATH}.HAS_RADKIT_GENIE", False)
    def test_main_missing_radkit_genie(self, mock_ansible_module_class):
        """Test main function with missing RADKit Genie dependency."""
        mock_module = Mock()
        mock_ansible_module_class.return_value = mock_module
        
        main()
        
        mock_module.fail_json.assert_called_once()
        call_args = mock_module.fail_json.call_args[1]
        self.assertIn("radkit_genie", call_args["msg"])


if __name__ == "__main__":
    unittest.main()
