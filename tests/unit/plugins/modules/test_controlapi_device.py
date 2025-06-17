#!/usr/bin/env python3
"""
Unit tests for Ansible controlapi_device module.

These tests validate the core functionality of the controlapi_device module
by importing and testing the actual module functions.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock

# Mock the radkit dependencies before importing the module
with patch.dict('sys.modules', {
    'radkit_client': MagicMock(),
    'radkit_service.control_api': MagicMock(),
    'radkit_service.webserver.models.devices': MagicMock(),
}):
    try:
        from ansible_collections.cisco.radkit.plugins.modules.controlapi_device import run_action
    except ImportError:
        # Fallback for direct import
        import sys
        import os
        sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..")))
        from plugins.modules.controlapi_device import run_action


class TestControlAPIDeviceModule(unittest.TestCase):
    """Test cases for the controlapi_device module."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_module = Mock()
        self.mock_control_api = Mock()
        
        # Create a mock device object for list_devices response
        mock_device = Mock()
        mock_device.name = "test-device"
        mock_device.uuid = "test-uuid-123"
        
        # Mock the API result structure
        mock_api_result = Mock()
        mock_api_result.result = [mock_device]
        
        self.mock_control_api.list_devices.return_value = mock_api_result

    def test_run_action_device_not_found_for_deletion(self):
        """Test run_action function when device is not found for deletion."""
        # Set up module parameters for absent state
        self.mock_module.params = {
            "data": {"name": "nonexistent-device"},
            "state": "absent"
        }
        
        # Mock empty device list (device not found)
        mock_api_result = Mock()
        mock_api_result.result = []
        self.mock_control_api.list_devices.return_value = mock_api_result
        
        # Call the function
        results, err = run_action(self.mock_module, self.mock_control_api)
        
        # Verify results
        self.assertFalse(err)
        self.assertFalse(results.get("changed"))
        self.assertIn("not found in inventory", results.get("msg", ""))

    def test_run_action_delete_device_success(self):
        """Test run_action function for successfully deleting a device."""
        # Set up module parameters for absent state
        self.mock_module.params = {
            "data": {"name": "test-device"},
            "state": "absent"
        }
        
        # Create a mock device object for list_devices response
        mock_device = Mock()
        mock_device.name = "test-device"
        mock_device.uuid = "test-uuid-123"
        
        # Mock the API result structure
        mock_api_result = Mock()
        mock_api_result.result = [mock_device]
        self.mock_control_api.list_devices.return_value = mock_api_result
        
        # Mock successful delete response
        mock_delete_result = Mock()
        mock_delete_result.status.value = "SUCCESS"
        
        mock_api_response = Mock()
        mock_api_response.results = [mock_delete_result]
        
        self.mock_control_api.delete_devices.return_value = mock_api_response
        
        # Call the function
        results, err = run_action(self.mock_module, self.mock_control_api)
        
        # Verify results
        self.assertFalse(err)
        self.assertTrue(results.get("changed"))
        self.assertIn("deleted successfully", results.get("msg", ""))
        
        # Verify the control API was called with correct UUID
        self.mock_control_api.delete_devices.assert_called_once_with(["test-uuid-123"])


if __name__ == "__main__":
    unittest.main()
