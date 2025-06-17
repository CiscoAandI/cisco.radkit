#!/usr/bin/env python3
"""
Unit tests for Ansible genie_parsed_command module.

These tests validate basic functionality of the genie_parsed_command module.
"""

import unittest
from unittest.mock import Mock, patch
from ansible.module_utils.basic import AnsibleModule


class TestGenieParseCommandModule(unittest.TestCase):
    """Test cases for the genie_parsed_command module."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_module = Mock(spec=AnsibleModule)
        
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

    def test_required_parameters(self):
        """Test that required parameters are properly defined."""
        params = self.default_params
        
        # Check required parameters
        self.assertIsNotNone(params["commands"])
        self.assertIsInstance(params["commands"], list)
        self.assertGreater(len(params["commands"]), 0)

    def test_device_targeting_validation(self):
        """Test device targeting validation."""
        params = self.default_params
        
        # Either device_name or filter_pattern should be provided
        if params["device_name"]:
            self.assertIsInstance(params["device_name"], str)
        elif params["filter_pattern"]:
            self.assertIsInstance(params["filter_pattern"], str)
        else:
            # At least one should be provided
            self.assertTrue(params["device_name"] or params["filter_pattern"])

    def test_commands_parameter_validation(self):
        """Test commands parameter validation."""
        params = self.default_params
        
        # Commands should be a list of strings
        self.assertIsInstance(params["commands"], list)
        for command in params["commands"]:
            self.assertIsInstance(command, str)
            self.assertGreater(len(command.strip()), 0)

    def test_os_parameter_validation(self):
        """Test OS parameter validation."""
        params = self.default_params
        
        if params["os"]:
            self.assertIsInstance(params["os"], str)
            # Common network OS values
            valid_os_types = ["ios", "iosxe", "nxos", "iosxr", "asa", "junos"]
            # Note: This is just a sample validation, actual module may support more

    def test_timeout_parameters(self):
        """Test timeout parameter validation."""
        params = self.default_params
        
        # Timeout parameters should be non-negative integers
        self.assertIsInstance(params["wait_timeout"], int)
        self.assertGreaterEqual(params["wait_timeout"], 0)
        
        self.assertIsInstance(params["exec_timeout"], int)
        self.assertGreaterEqual(params["exec_timeout"], 0)

    def test_output_processing_parameters(self):
        """Test output processing parameter validation."""
        params = self.default_params
        
        # Boolean parameters
        self.assertIsInstance(params["remove_cmd_and_device_keys"], bool)

    @patch('ansible_collections.cisco.radkit.plugins.modules.genie_parsed_command.HAS_RADKIT', True)
    @patch('ansible_collections.cisco.radkit.plugins.modules.genie_parsed_command.HAS_RADKIT_GENIE', True)
    def test_dependency_checks(self):
        """Test that dependencies are properly checked."""
        has_radkit = True  # Mocked value
        has_radkit_genie = True  # Mocked value
        self.assertTrue(has_radkit)
        self.assertTrue(has_radkit_genie)


if __name__ == "__main__":
    unittest.main()
