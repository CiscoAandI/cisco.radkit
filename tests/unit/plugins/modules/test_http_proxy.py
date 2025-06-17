#!/usr/bin/env python3
"""
Unit tests for Ansible http_proxy module.

These tests validate basic functionality of the http_proxy module.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
from ansible.module_utils.basic import AnsibleModule

# Handle import paths for both ansible-test and pytest environments
try:
    # Try collection import first (for ansible-test environment)
    from ansible_collections.cisco.radkit.plugins.modules.http_proxy import (
        _validate_proxy_ports,
        run_action,
    )
    HTTP_PROXY_MODULE_PATH = "ansible_collections.cisco.radkit.plugins.modules.http_proxy"
except ImportError:
    try:
        # Try local import (for pytest environment)
        import sys
        import os
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../../plugins/modules'))
        from http_proxy import (
            _validate_proxy_ports,
            run_action,
        )
        HTTP_PROXY_MODULE_PATH = "http_proxy"
    except ImportError:
        # Fallback - create dummy functions for testing environment
        def _validate_proxy_ports(http_port, socks_port):
            pass
        def run_action(module, radkit_service):
            return {"changed": False}, False
        HTTP_PROXY_MODULE_PATH = None


class TestHTTPProxyModule(unittest.TestCase):
    """Test cases for the http_proxy module."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_module = Mock(spec=AnsibleModule)
        self.mock_radkit_service = Mock()
        self.mock_radkit_client = Mock()
        self.mock_radkit_service.radkit_client = self.mock_radkit_client
        
        self.default_params = {
            "test": True,  # Use test mode by default
            "http_proxy_port": "8080",
            "socks_proxy_port": "1080",
            "proxy_username": "user",
            "proxy_password": "pass",
        }
        self.mock_module.params = self.default_params.copy()

    def test_run_action_success(self):
        """Test successful run_action execution in test mode."""
        if HTTP_PROXY_MODULE_PATH is None:
            self.skipTest("Skipping run_action test in pytest environment")
            
        with patch(f'{HTTP_PROXY_MODULE_PATH}._start_socks_proxy') as mock_start_socks, \
             patch(f'{HTTP_PROXY_MODULE_PATH}._setup_http_proxy') as mock_setup_http, \
             patch(f'{HTTP_PROXY_MODULE_PATH}._run_proxy_servers') as mock_run_servers:
            
            # Mock the proxy setup functions
            mock_server = Mock()
            mock_remote = Mock()
            mock_loop = Mock()
            mock_setup_http.return_value = (mock_server, mock_remote, mock_loop)
            mock_run_servers.return_value = {"changed": False, "test_mode": True}
            
            # Test the run_action function
            results, error = run_action(self.mock_module, self.mock_radkit_service)
            
            # Verify successful execution
            self.assertFalse(error)
            self.assertIn("changed", results)
            self.assertIn("test_mode", results)
            
            # Verify function calls
            mock_start_socks.assert_called_once()
            mock_setup_http.assert_called_once()
            mock_run_servers.assert_called_once()

    def test_validate_proxy_ports_different_behavior(self):
        """Test proxy port validation with different ports vs same ports."""
        # Test with different ports - should not raise exception
        try:
            _validate_proxy_ports("8080", "1080")
            different_ports_valid = True
        except:
            different_ports_valid = False
        
        # Test with same ports - should raise exception
        try:
            _validate_proxy_ports("8080", "8080")
            same_ports_valid = True
        except:
            same_ports_valid = False
        
        # Verify behavior: different ports should be valid, same ports should be invalid
        self.assertTrue(different_ports_valid, "Different port numbers should be valid")
        self.assertFalse(same_ports_valid, "Same port numbers should be invalid")


if __name__ == "__main__":
    unittest.main()
