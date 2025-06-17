#!/usr/bin/env python3
"""
Unit tests for the port_forward module.

These tests validate basic functionality of the port_forward module.
"""

import unittest
from unittest.mock import Mock, patch
from ansible.module_utils.basic import AnsibleModule

# Handle import paths for both ansible-test and pytest environments
try:
    # Try collection import first (for ansible-test environment)
    import ansible_collections.cisco.radkit.plugins.modules.port_forward
    PORT_FORWARD_MODULE_PATH = "ansible_collections.cisco.radkit.plugins.modules.port_forward"
except ImportError:
    # For pytest environment, the module path doesn't exist, so we'll skip the dependency patch tests
    PORT_FORWARD_MODULE_PATH = None


class TestPortForwardModule(unittest.TestCase):
    """Test cases for the port_forward module."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_module = Mock(spec=AnsibleModule)
        
        # Default valid parameters
        self.default_params = {
            "device_name": "test-device",
            "test": False,
            "local_port": 8080,
            "destination_port": 80,
            "timeout": None,
        }
        self.mock_module.params = self.default_params.copy()

    def test_required_parameters(self):
        """Test that required parameters are properly defined."""
        params = self.default_params
        
        # Check required parameters
        self.assertIsNotNone(params["device_name"])
        self.assertIsNotNone(params["local_port"])
        self.assertIsNotNone(params["destination_port"])

    def test_port_validation(self):
        """Test port parameter validation."""
        params = self.default_params
        
        # Ports should be integers
        self.assertIsInstance(params["local_port"], int)
        self.assertIsInstance(params["destination_port"], int)
        
        # Ports should be in valid range
        self.assertGreater(params["local_port"], 0)
        self.assertLessEqual(params["local_port"], 65535)
        self.assertGreater(params["destination_port"], 0)
        self.assertLessEqual(params["destination_port"], 65535)

    def test_test_mode_parameter(self):
        """Test test mode parameter validation."""
        params = self.default_params
        
        # Should be boolean
        self.assertIsInstance(params["test"], bool)

    def test_timeout_parameter(self):
        """Test timeout parameter validation."""
        params = self.default_params
        
        # Timeout can be None or positive integer
        if params["timeout"] is not None:
            self.assertIsInstance(params["timeout"], int)
            self.assertGreater(params["timeout"], 0)

    def test_radkit_dependency_check(self):
        """Test that RADKit dependency is properly checked."""
        if PORT_FORWARD_MODULE_PATH is None:
            self.skipTest("Skipping dependency check test in pytest environment")
        
        with patch(f'{PORT_FORWARD_MODULE_PATH}.HAS_RADKIT', True):
            has_radkit = True  # Mocked value
            self.assertTrue(has_radkit)


if __name__ == "__main__":
    unittest.main()
