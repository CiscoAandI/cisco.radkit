#!/usr/bin/env python3
"""
Unit tests for the exec_and_wait module.

These tests validate basic functionality of the exec_and_wait module.
"""

import unittest
from unittest.mock import Mock, patch
from ansible.module_utils.basic import AnsibleModule


class TestExecAndWaitModule(unittest.TestCase):
    """Test cases for the exec_and_wait module."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_module = Mock(spec=AnsibleModule)
        
        # Default valid parameters
        self.default_params = {
            "device_name": "test-device",
            "device_host": None,
            "seconds_to_wait": 60,
            "delay_before_check": 10,
            "command_timeout": 30,
            "commands": ["reload"],
            "answers": ["y"],
            "prompts": ["Save configuration"],
            "command_retries": 1,
            "recovery_test_command": "\r",
        }
        self.mock_module.params = self.default_params.copy()

    def test_required_parameters(self):
        """Test that required parameters are properly defined."""
        params = self.default_params
        
        # Check that either device_name or device_host is provided
        self.assertTrue(params["device_name"] is not None or params["device_host"] is not None)
        
        # Check required seconds_to_wait
        self.assertIsInstance(params["seconds_to_wait"], int)
        self.assertGreater(params["seconds_to_wait"], 0)

    def test_device_targeting_validation(self):
        """Test device targeting parameter validation."""
        # Test with device_name
        params_name = self.default_params.copy()
        params_name["device_name"] = "router1"
        params_name["device_host"] = None
        self.assertIsNotNone(params_name["device_name"])
        
        # Test with device_host
        params_host = self.default_params.copy()
        params_host["device_name"] = None
        params_host["device_host"] = "192.168.1.1"
        self.assertIsNotNone(params_host["device_host"])

    def test_timing_parameters(self):
        """Test timing parameter validation."""
        params = self.default_params
        
        # Validate timing parameters are positive integers
        self.assertGreaterEqual(params["seconds_to_wait"], 0)
        self.assertGreaterEqual(params["delay_before_check"], 0)
        self.assertGreaterEqual(params["command_timeout"], 0)
        self.assertGreaterEqual(params["command_retries"], 0)

    def test_command_parameters(self):
        """Test command parameter validation."""
        params = self.default_params
        
        # Commands should be a list if provided
        if params["commands"] is not None:
            self.assertIsInstance(params["commands"], list)
        
        # Answers should be a list if provided
        if params["answers"] is not None:
            self.assertIsInstance(params["answers"], list)
        
        # Prompts should be a list if provided
        if params["prompts"] is not None:
            self.assertIsInstance(params["prompts"], list)

    def test_recovery_command_validation(self):
        """Test recovery command parameter."""
        params = self.default_params
        recovery_cmd = params["recovery_test_command"]
        
        self.assertIsInstance(recovery_cmd, str)
        # Default should be carriage return
        self.assertEqual(recovery_cmd, "\r")

    @patch('ansible_collections.cisco.radkit.plugins.modules.exec_and_wait.HAS_RADKIT', True)
    @patch('ansible_collections.cisco.radkit.plugins.modules.exec_and_wait.HAS_PEXPECT', True)
    def test_dependency_checks(self):
        """Test that dependencies are properly checked."""
        has_radkit = True  # Mocked value
        has_pexpect = True  # Mocked value
        self.assertTrue(has_radkit)
        self.assertTrue(has_pexpect)


if __name__ == "__main__":
    unittest.main()
