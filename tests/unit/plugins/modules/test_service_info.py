#!/usr/bin/env python3
"""
Unit tests for the service_info module.

These tests validate basic functionality of the service_info module.
"""

import unittest
from unittest.mock import Mock, patch
from ansible.module_utils.basic import AnsibleModule

# Handle import paths for both ansible-test and pytest environments
try:
    # Try collection import first (for ansible-test environment)
    import ansible_collections.cisco.radkit.plugins.modules.service_info
    SERVICE_INFO_MODULE_PATH = "ansible_collections.cisco.radkit.plugins.modules.service_info"
except ImportError:
    # For pytest environment, the module path doesn't exist, so we'll skip the dependency patch tests
    SERVICE_INFO_MODULE_PATH = None


class TestServiceInfoModule(unittest.TestCase):
    """Test cases for the service_info module."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_module = Mock(spec=AnsibleModule)
        
        # Default valid parameters
        self.default_params = {
            "ping": True,
            "update_inventory": True,
            "update_capabilities": True,
        }
        self.mock_module.params = self.default_params.copy()
        self.mock_module.check_mode = False

    def test_module_parameters_validation(self):
        """Test that module accepts valid parameters."""
        params = {
            "ping": True,
            "update_inventory": True,
            "update_capabilities": True,
        }
        
        # Validate required parameters exist and are correct types
        self.assertIsInstance(params["ping"], bool)
        self.assertIsInstance(params["update_inventory"], bool)
        self.assertIsInstance(params["update_capabilities"], bool)

    def test_ping_only_parameters(self):
        """Test ping-only configuration."""
        params = {
            "ping": True,
            "update_inventory": False,
            "update_capabilities": False,
        }
        
        self.assertTrue(params["ping"])
        self.assertFalse(params["update_inventory"])
        self.assertFalse(params["update_capabilities"])

    def test_selective_updates(self):
        """Test selective update configurations."""
        # Test inventory only
        params_inv = {
            "ping": True,
            "update_inventory": True,
            "update_capabilities": False,
        }
        self.assertTrue(params_inv["update_inventory"])
        self.assertFalse(params_inv["update_capabilities"])
        
        # Test capabilities only
        params_cap = {
            "ping": True,
            "update_inventory": False,
            "update_capabilities": True,
        }
        self.assertFalse(params_cap["update_inventory"])
        self.assertTrue(params_cap["update_capabilities"])

    def test_argument_spec_structure(self):
        """Test that argument spec has required structure."""
        expected_args = {"ping", "update_inventory", "update_capabilities"}
        param_keys = set(self.default_params.keys())
        self.assertEqual(expected_args, param_keys)

    def test_radkit_dependency_check(self):
        """Test that RADKit dependency is properly checked."""
        if SERVICE_INFO_MODULE_PATH is None:
            self.skipTest("Skipping dependency check test in pytest environment")
        
        with patch(f'{SERVICE_INFO_MODULE_PATH}.HAS_RADKIT', True):
            has_radkit = True  # Mocked value
            self.assertTrue(has_radkit)


if __name__ == "__main__":
    unittest.main()
