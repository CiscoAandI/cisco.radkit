#!/usr/bin/env python3
"""
Unit tests for the swagger module.

These tests validate actual functionality of the swagger module functions.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
from ansible.module_utils.basic import AnsibleModule

# Import the functions we want to test
try:
    from ansible_collections.cisco.radkit.plugins.modules.swagger import (
        _validate_http_method,
        _prepare_swagger_params,
        run_action,
    )
except ImportError:
    # Fallback for when running tests in different environments
    import sys
    import os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'plugins', 'modules'))
    from swagger import (
        _validate_http_method,
        _prepare_swagger_params,
        run_action,
    )


class TestSwaggerModule(unittest.TestCase):
    """Test cases for the swagger module."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_module = Mock(spec=AnsibleModule)
        
        # Default valid parameters
        self.default_params = {
            "path": "/api/v1/devices",
            "device_name": "test-device",
            "method": "GET",
            "parameters": None,
            "params": None,
            "headers": {"Content-Type": "application/json"},
            "cookies": None,
            "json": {"test": "data"},
            "content": None,
            "data": None,
            "files": None,
            "timeout": 30.0,
            "status_code": [200],
        }
        self.mock_module.params = self.default_params.copy()

    def test_validate_http_method_success(self):
        """Test HTTP method validation with valid methods."""
        valid_methods = ["get", "post", "put", "patch", "delete", "options", "head"]
        
        for method in valid_methods:
            try:
                _validate_http_method(method)
                _validate_http_method(method.upper())  # Test case insensitivity
            except Exception as e:
                self.fail(f"Valid method '{method}' raised exception: {e}")

    def test_prepare_swagger_params(self):
        """Test preparation of Swagger parameters."""
        test_params = {
            "path": "/api/test",
            "parameters": {"id": "123"},
            "params": None,
            "headers": {"Authorization": "Bearer token"},
            "json": {"data": "test"},
            "content": None,
            "data": None,
            "files": None,
            "cookies": None,
            "timeout": 60.0,
        }
        
        result = _prepare_swagger_params(test_params)
        
        # Verify required fields are present
        self.assertEqual(result["path"], "/api/test")
        self.assertEqual(result["parameters"], {"id": "123"})
        self.assertEqual(result["headers"], {"Authorization": "Bearer token"})
        self.assertEqual(result["json"], {"data": "test"})
        self.assertEqual(result["timeout"], 60.0)
        
        # Verify None values are removed
        self.assertNotIn("content", result)
        self.assertNotIn("data", result)
        self.assertNotIn("files", result)

    @patch('ansible_collections.cisco.radkit.plugins.modules.swagger.RadkitClientService')
    @patch('ansible_collections.cisco.radkit.plugins.modules.swagger.logger')
    def test_run_action_success(self, mock_logger, mock_radkit_service_class):
        """Test successful run_action execution."""
        # Setup mock objects
        mock_radkit_service = Mock()
        mock_radkit_service_class.return_value = mock_radkit_service
        
        # Mock inventory and device
        mock_device = Mock()
        mock_inventory = {"test-device": mock_device}
        mock_radkit_service.get_inventory_by_filter.return_value = mock_inventory
        
        # Mock device swagger operations
        mock_device.update_swagger.return_value.wait.return_value = None
        mock_device.swagger.paths = {"/api/v1/devices": True}
        
        # Mock swagger method and response
        mock_swagger_method = Mock()
        mock_device.swagger.get = mock_swagger_method
        
        mock_response = Mock()
        mock_response.result.response_code = 200
        mock_response.result.text = '{"success": true}'
        mock_response.result.headers = {"Content-Type": "application/json"}
        mock_response.result.content_type = "application/json"
        mock_response.result.json = {"success": True}
        mock_response.result.url = "http://test-device/api/v1/devices"
        mock_response.result.cookies = {}
        
        mock_swagger_method.return_value.wait.return_value = mock_response
        
        # Execute the function
        results, error = run_action(self.mock_module, mock_radkit_service)
        
        # Verify results
        self.assertFalse(error)
        self.assertEqual(results["status_code"], 200)
        self.assertEqual(results["method"], "GET")
        self.assertIn("json", results)
        self.assertEqual(results["json"], {"success": True})
        
        # Verify function calls
        mock_radkit_service.get_inventory_by_filter.assert_called_once_with("test-device", "name")
        mock_device.update_swagger.assert_called_once()
        mock_swagger_method.assert_called_once()


if __name__ == "__main__":
    unittest.main()
