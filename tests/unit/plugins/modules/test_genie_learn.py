#!/usr/bin/env python3
"""
Unit tests for the genie_learn module.

These tests validate the core functionality of the genie_learn module
by importing and testing the actual module functions.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock

# Handle import paths for both ansible-test and pytest environments
try:
    # Try collection import first (for ansible-test environment)
    from ansible_collections.cisco.radkit.plugins.modules.genie_learn import (
        run_action,
        _process_genie_results,
        _validate_device_parameters,
    )
    GENIE_LEARN_MODULE_PATH = "ansible_collections.cisco.radkit.plugins.modules.genie_learn"
except ImportError:
    # Fallback for local development
    import sys
    import os
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..")))
    from plugins.modules.genie_learn import (
        run_action,
        _process_genie_results,
        _validate_device_parameters,
    )
    GENIE_LEARN_MODULE_PATH = None


class TestGenieLearnModule(unittest.TestCase):
    """Test cases for the genie_learn module."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_module = Mock()
        self.mock_radkit_service = Mock()
        
        # Default valid parameters for learn operation
        self.default_params = {
            "models": ["ospf", "bgp"],
            "device_name": "test-device",
            "os": "iosxe",
            "filter_pattern": None,
            "filter_attr": None,
            "wait_timeout": 0,
            "exec_timeout": 0,
            "remove_model_and_device_keys": False,
        }
        self.mock_module.params = self.default_params.copy()

    def test_process_genie_results_single_device_model(self):
        """Test _process_genie_results function with single device and model."""
        # Mock genie results object
        mock_genie_results = Mock()
        mock_results_dict = {
            "test-device": {
                "ospf": {"process_id": 1, "router_id": "1.1.1.1"}
            }
        }
        mock_genie_results.to_dict.return_value = mock_results_dict
        
        # Call the function with remove_keys=True
        result = _process_genie_results(
            genie_results=mock_genie_results,
            device_name="test-device", 
            models=["ospf"],
            remove_keys=True
        )
        
        # Should return just the model data when remove_keys=True
        expected = {"process_id": 1, "router_id": "1.1.1.1"}
        self.assertEqual(result, expected)

    @patch(f'{GENIE_LEARN_MODULE_PATH or "plugins.modules.genie_learn"}._get_device_inventory')
    @patch(f'{GENIE_LEARN_MODULE_PATH or "plugins.modules.genie_learn"}._execute_genie_learn')
    def test_run_action_successful_learn(self, mock_execute_learn, mock_get_inventory):
        """Test run_action function with successful learn operation."""
        # Mock inventory
        mock_inventory = {"test-device": Mock()}
        mock_get_inventory.return_value = mock_inventory
        
        # Mock genie learn results
        mock_genie_results = Mock()
        mock_results_dict = {
            "test-device": {
                "ospf": {"process_id": 1},
                "bgp": {"as_number": 65000}
            }
        }
        mock_genie_results.to_dict.return_value = mock_results_dict
        mock_execute_learn.return_value = mock_genie_results
        
        # Call the function
        results, err = run_action(self.mock_module, self.mock_radkit_service)
        
        # Verify results
        self.assertFalse(err)
        self.assertIn("genie_learn_result", results)
        self.assertEqual(results["genie_learn_result"], mock_results_dict)
        self.assertFalse(results["changed"])
        
        # Verify function calls
        mock_get_inventory.assert_called_once()
        mock_execute_learn.assert_called_once_with(mock_inventory, ["ospf", "bgp"], "iosxe")


if __name__ == "__main__":
    unittest.main()
