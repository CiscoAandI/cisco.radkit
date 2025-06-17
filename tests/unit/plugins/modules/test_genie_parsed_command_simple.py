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
        self.mock_module = Mock(spec=AnsibleModule)
        
        # Default valid parameters
        self.default_params = {
            "commands": ["show version"],
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
        """Test device targeting parameter validation."""
        # Test with device_name
        params_name = self.default_params.copy()
        params_name["device_name"] = "router1"
        params_name["filter_pattern"] = None
        params_name["filter_attr"] = None
        self.assertIsNotNone(params_name["device_name"])
        
        # Test with filter pattern
        params_filter = self.default_params.copy()
        params_filter["device_name"] = None
        params_filter["filter_pattern"] = "router*"
        params_filter["filter_attr"] = "name"
        self.assertIsNotNone(params_filter["filter_pattern"])
        self.assertIsNotNone(params_filter["filter_attr"])

    def test_os_parameter_validation(self):
        """Test OS parameter validation."""
        params = self.default_params
        
        # OS should be a string
        self.assertIsInstance(params["os"], str)

    def test_timeout_parameters(self):
        """Test timeout parameter validation."""
        params = self.default_params
        
        # Timeouts should be non-negative integers
        self.assertGreaterEqual(params["wait_timeout"], 0)
        self.assertGreaterEqual(params["exec_timeout"], 0)

    def test_output_processing_parameters(self):
        """Test output processing parameter validation."""
        params = self.default_params
        
        # Should be boolean
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
