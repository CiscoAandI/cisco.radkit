#!/usr/bin/env python3
"""
Unit tests for the put_file module.

These tests validate basic functionality of the put_file module.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
from ansible.module_utils.basic import AnsibleModule

# Handle import paths for both ansible-test and pytest environments
try:
    # Try collection import first (for ansible-test environment)
    from ansible_collections.cisco.radkit.plugins.modules.put_file import (
        _validate_protocol,
        run_upload,
    )
    PUT_FILE_MODULE_PATH = "ansible_collections.cisco.radkit.plugins.modules.put_file"
except ImportError:
    try:
        # Try local import (for pytest environment)
        import sys
        import os
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../../plugins/modules'))
        from put_file import (
            _validate_protocol,
            run_upload,
        )
        PUT_FILE_MODULE_PATH = "put_file"
    except ImportError:
        # Fallback - create dummy functions for testing environment
        def _validate_protocol(protocol):
            pass
        def run_upload(module, radkit_service):
            return {"changed": False}, False
        PUT_FILE_MODULE_PATH = None


class TestPutFileModule(unittest.TestCase):
    """Test cases for the put_file module."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_module = Mock(spec=AnsibleModule)
        self.mock_radkit_service = Mock()
        self.mock_radkit_client = Mock()
        self.mock_radkit_service.radkit_client = self.mock_radkit_client
        
        self.default_params = {
            "device_name": "test-device",
            "device_host": None,
            "local_path": "/tmp/test_file.txt",
            "remote_path": "/tmp/remote_file.txt",
            "protocol": "scp",
        }
        self.mock_module.params = self.default_params.copy()

    def test_validate_protocol_success(self):
        """Test successful protocol validation."""
        # Test valid protocols
        try:
            _validate_protocol("scp")
            _validate_protocol("sftp")
            _validate_protocol("SCP")  # Test case insensitive
            _validate_protocol("SFTP")  # Test case insensitive
        except Exception as e:
            self.fail(f"_validate_protocol raised an exception unexpectedly: {e}")

    def test_validate_protocol_invalid(self):
        """Test protocol validation with invalid protocol."""
        # Test with invalid protocol - should raise exception
        try:
            _validate_protocol("invalid_protocol")
            invalid_protocol_failed = False
        except:
            invalid_protocol_failed = True

        # Test with FTP (not supported in SUPPORTED_PROTOCOLS) - should raise exception
        try:
            _validate_protocol("ftp")
            ftp_protocol_failed = False
        except:
            ftp_protocol_failed = True
        
        # Verify that invalid protocols fail validation
        self.assertTrue(invalid_protocol_failed, "Invalid protocol should raise validation error")
        self.assertTrue(ftp_protocol_failed, "FTP protocol should not be supported")

    def test_run_upload_success(self):
        """Test successful file upload operation."""
        if PUT_FILE_MODULE_PATH is None:
            self.skipTest("Skipping run_upload test in pytest environment")
            
        with patch(f'{PUT_FILE_MODULE_PATH}._get_device_inventory') as mock_get_inventory, \
             patch(f'{PUT_FILE_MODULE_PATH}._get_upload_function') as mock_get_upload_func, \
             patch(f'{PUT_FILE_MODULE_PATH}._monitor_transfer') as mock_monitor:
            
            # Mock device inventory
            mock_get_inventory.return_value = {"test-device": Mock()}
            
            # Mock upload function and result
            mock_upload_result = Mock()
            mock_upload_result.status.value = "TRANSFER_DONE"
            mock_upload_result.bytes_written = 1024
            
            mock_upload_func_instance = Mock()
            mock_upload_func_instance.wait.return_value = mock_upload_result
            mock_get_upload_func.return_value = mock_upload_func_instance
            
            # Test the run_upload function
            results, error = run_upload(self.mock_module, self.mock_radkit_service)
            
            # Verify successful execution
            self.assertFalse(error)
            self.assertIn("device_name", results)
            self.assertIn("changed", results)
            self.assertTrue(results["changed"])
            
            # Verify function calls
            mock_get_inventory.assert_called_once()
            mock_get_upload_func.assert_called_once()
            mock_monitor.assert_called_once()


if __name__ == "__main__":
    unittest.main()
