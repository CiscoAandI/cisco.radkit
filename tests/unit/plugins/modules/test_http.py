#!/usr/bin/env python3
"""
Unit tests for the http module.

These tests validate the core functionality of the http module,
specifically testing the run_action and helper functions.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
from ansible.module_utils.basic import AnsibleModule

# Handle import paths for both ansible-test and pytest environments
try:
    # Try collection import first (for ansible-test environment)
    from ansible_collections.cisco.radkit.plugins.modules.http import (
        run_action,
        _process_http_response,
    )
    from ansible_collections.cisco.radkit.plugins.module_utils.exceptions import (
        AnsibleRadkitValidationError,
        AnsibleRadkitOperationError,
    )
    HTTP_MODULE_PATH = "ansible_collections.cisco.radkit.plugins.modules.http"
except ImportError:
    # Fallback for local development
    import sys
    import os
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..")))
    from plugins.modules.http import (
        run_action,
        _process_http_response,
    )
    from plugins.module_utils.exceptions import (
        AnsibleRadkitValidationError,
        AnsibleRadkitOperationError,
    )
    HTTP_MODULE_PATH = None


class TestHttpModule(unittest.TestCase):
    """Test cases for the http module."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_module = Mock(spec=AnsibleModule)
        self.mock_radkit_service = Mock()
        
        # Default valid parameters
        self.default_params = {
            "path": "/api/v1/status",
            "device_name": "test-device",
            "method": "GET",
            "headers": None,
            "params": None,
            "json": None,
            "data": None,
            "timeout": None,
            "status_code": [200],
        }
        self.mock_module.params = self.default_params.copy()
        
        # Mock HTTP response with proper structure
        self.mock_http_response = Mock()
        self.mock_response_result = Mock()
        self.mock_response_result.status_code = 200
        self.mock_response_result.data = {"status": "ok"}
        self.mock_response_result.content = {"status": "ok"}
        
        # Mock headers that can be converted to dict
        self.mock_response_result.headers = {"Content-Type": "application/json"}
        self.mock_response_result.cookies = {}
        
        # Set up the radkit response structure
        self.mock_http_response.result = self.mock_response_result

    def test_run_action_success(self):
        """Test successful HTTP request execution."""
        # Mock inventory and HTTP function
        mock_inventory = {"test-device": Mock()}
        mock_http_func = Mock()
        mock_http_func.return_value.wait.return_value = self.mock_http_response
        
        # Set up the HTTP method on the device mock
        mock_inventory["test-device"].http.get = mock_http_func
        
        self.mock_radkit_service.get_inventory_by_filter.return_value = mock_inventory
        
        results, err = run_action(self.mock_module, self.mock_radkit_service)
        
        self.assertFalse(err)
        self.assertIn("status_code", results)
        self.assertEqual(results["status_code"], 200)

    def test_process_http_response_success(self):
        """Test successful HTTP response processing."""
        params = {
            "status_code": [200, 201],
            "method": "GET",  # Add the required method parameter
        }
        
        result = _process_http_response(self.mock_http_response, params)
        
        self.assertIn("status_code", result)
        self.assertIn("headers", result)
        self.assertEqual(result["status_code"], 200)
        self.assertEqual(result["headers"], {"Content-Type": "application/json"})


if __name__ == "__main__":
    unittest.main()
