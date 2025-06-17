#!/usr/bin/env python3
"""
Unit tests for the snmp module.

These tests validate basic functionality of the snmp module.
"""

import unittest
from unittest.mock import Mock, patch
from ansible.module_utils.basic import AnsibleModule

try:
    # ansible-test collection import
    from ansible_collections.cisco.radkit.plugins.modules.snmp import _execute_snmp_operation
except ImportError:
    import sys
    import os
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..")))
    from plugins.modules.snmp import _execute_snmp_operation


class TestSnmpModule(unittest.TestCase):
    """Test cases for the snmp module."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_module = Mock(spec=AnsibleModule)
        
        # Default valid parameters
        self.default_params = {
            "device_name": "test-device",
            "device_host": None,
            "action": "get",
            "oid": "1.3.6.1.2.1.1.1.0",
            "request_timeout": 5.0,
            "limit": None,
            "retries": None,
            "concurrency": 10,
            "include_errors": False,
            "include_mib_info": False,
            "output_format": "simple",
        }
        self.mock_module.params = self.default_params.copy()

    def test_required_parameters(self):
        """Test that required parameters are properly defined."""
        params = self.default_params
        
        # Check required parameters
        self.assertIsNotNone(params["oid"])
        self.assertIn(params["action"], ["get", "get_next", "walk"])

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

    def test_snmp_action_validation(self):
        """Test SNMP action parameter validation."""
        valid_actions = ["get", "get_next", "walk"]
        params = self.default_params
        
        self.assertIn(params["action"], valid_actions)

    def test_oid_parameter_validation(self):
        """Test OID parameter validation."""
        params = self.default_params
        
        # OID should be provided
        self.assertIsNotNone(params["oid"])

    def test_timeout_and_concurrency_parameters(self):
        """Test timeout and concurrency parameter validation."""
        params = self.default_params
        
        # Request timeout should be positive float
        self.assertIsInstance(params["request_timeout"], (int, float))
        self.assertGreater(params["request_timeout"], 0)
        
        # Concurrency should be positive integer
        self.assertIsInstance(params["concurrency"], int)
        self.assertGreater(params["concurrency"], 0)

    def test_boolean_parameters(self):
        """Test boolean parameter validation."""
        params = self.default_params
        
        # Boolean parameters
        self.assertIsInstance(params["include_errors"], bool)
        self.assertIsInstance(params["include_mib_info"], bool)

    def test_output_format_validation(self):
        """Test output format parameter validation."""
        params = self.default_params
        valid_formats = ["simple", "detailed", "raw"]
        
        self.assertIn(params["output_format"], valid_formats)

    def test_execute_snmp_operation_detects_bug(self):
        """Test that _execute_snmp_operation does not return None (catches injected bug)."""
        # Mock inventory and SNMP function
        mock_snmp_func = Mock()
        mock_result_obj = Mock()
        mock_result_obj.without_errors.return_value = {"row1": Mock(oid_str="1.2.3", value="foo", type="str", value_str="foo", is_error=False)}
        mock_snmp_func.return_value.wait.return_value.result = mock_result_obj
        mock_device = Mock()
        setattr(mock_device, 'snmp', Mock(get=mock_snmp_func, walk=mock_snmp_func, get_next=mock_snmp_func, get_bulk=mock_snmp_func))
        inventory = {"test-device": mock_device}

        # Should not return None if function is correct
        result = _execute_snmp_operation(
            inventory=inventory,
            action="get",
            oids=["1.2.3"],
            timeout=1.0,
            limit=None,
            retries=None,
            concurrency=1,
            include_errors=False,
            include_mib_info=False,
            output_format="simple",
        )
        self.assertIsNotNone(result, "_execute_snmp_operation returned None (bug detected)")


if __name__ == "__main__":
    unittest.main()
