#!/usr/bin/env python3
"""
Test suite for the RadkitClientService class.

This test file demonstrates the improved functionality and can be used
to validate the client service behavior.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import base64
from typing import Any, Dict

# Import the modules we're testing
try:
    # Try collection import first (for ansible-test environment)
    from ansible_collections.cisco.radkit.plugins.module_utils.client import (
        RadkitClientService,
        radkit_client_argument_spec,
        create_radkit_client_service,
        check_if_radkit_version_supported,
    )
    from ansible_collections.cisco.radkit.plugins.module_utils.exceptions import (
        AnsibleRadkitError,
        AnsibleRadkitConnectionError,
        AnsibleRadkitValidationError,
        AnsibleRadkitOperationError,
    )

    # Set the module path for patches when in collection environment
    CLIENT_MODULE_PATH = "ansible_collections.cisco.radkit.plugins.module_utils.client"
except ImportError:
    # Fallback to direct import for local development
    import sys
    import os

    # Add the correct path for module_utils
    sys.path.insert(
        0,
        os.path.join(os.path.dirname(__file__), "..", "..", "plugins", "module_utils"),
    )

    from client import (
        RadkitClientService,
        radkit_client_argument_spec,
        create_radkit_client_service,
        check_if_radkit_version_supported,
    )
    from exceptions import (
        AnsibleRadkitError,
        AnsibleRadkitConnectionError,
        AnsibleRadkitValidationError,
        AnsibleRadkitOperationError,
    )

    # Set the module path for patches when in local environment
    CLIENT_MODULE_PATH = "client"


class TestRadkitClientService(unittest.TestCase):
    """Test cases for RadkitClientService class."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        self.mock_client = Mock()
        self.mock_service = Mock()
        self.mock_client.service.return_value.wait.return_value = self.mock_service

        # Valid test parameters
        self.valid_params = {
            "identity": "test-identity",
            "client_key_password_b64": base64.b64encode(b"test-password").decode(
                "utf-8"
            ),
            "service_serial": "test-serial-123",
            "client_ca_path": "/path/to/ca.pem",
            "client_key_path": "/path/to/key.pem",
            "client_cert_path": "/path/to/cert.pem",
            "exec_timeout": 30,
            "wait_timeout": 60,
        }

    @patch(f"{CLIENT_MODULE_PATH}.check_if_radkit_version_supported")
    def test_init_with_valid_params(self, mock_version_check: Mock) -> None:
        """Test successful initialization with valid parameters."""
        service = RadkitClientService(self.mock_client, self.valid_params)

        # Verify initialization
        self.assertEqual(service.identity, "test-identity")
        self.assertEqual(service.service_serial, "test-serial-123")
        self.assertEqual(service.exec_timeout, 30)
        self.assertEqual(service.wait_timeout, 60)

        # Verify client methods were called
        self.mock_client.certificate_login.assert_called_once()
        self.mock_client.service.assert_called_once_with("test-serial-123")
        mock_version_check.assert_called_once()

    def test_init_missing_identity(self) -> None:
        """Test initialization fails with missing identity."""
        params = self.valid_params.copy()
        del params["identity"]

        with self.assertRaises(AnsibleRadkitValidationError) as cm:
            RadkitClientService(self.mock_client, params)

        self.assertIn("Identity parameter is required", str(cm.exception))

    def test_init_missing_password(self) -> None:
        """Test initialization fails with missing password."""
        params = self.valid_params.copy()
        del params["client_key_password_b64"]

        with self.assertRaises(AnsibleRadkitValidationError) as cm:
            RadkitClientService(self.mock_client, params)

        self.assertIn("Client key password", str(cm.exception))

    def test_init_missing_service_serial(self) -> None:
        """Test initialization fails with missing service serial."""
        params = self.valid_params.copy()
        del params["service_serial"]

        with self.assertRaises(AnsibleRadkitValidationError) as cm:
            RadkitClientService(self.mock_client, params)

        self.assertIn("Service serial is required", str(cm.exception))

    def test_decode_base64_password_invalid(self) -> None:
        """Test base64 password decoding with invalid data."""
        params = self.valid_params.copy()
        params["client_key_password_b64"] = "invalid-base64!"

        with self.assertRaises(AnsibleRadkitValidationError) as cm:
            RadkitClientService(self.mock_client, params)

        self.assertIn("Failed to decode client key password", str(cm.exception))

    @patch(f"{CLIENT_MODULE_PATH}.check_if_radkit_version_supported")
    def test_get_inventory_by_filter_success(self, mock_version_check: Mock) -> None:
        """Test successful inventory filtering."""
        service = RadkitClientService(self.mock_client, self.valid_params)

        # Mock inventory
        mock_inventory = Mock()
        service.radkit_service.inventory.filter.return_value = mock_inventory

        result = service.get_inventory_by_filter("pattern", "attr")

        self.assertEqual(result, mock_inventory)
        service.radkit_service.inventory.filter.assert_called_once_with(
            "attr", "pattern"
        )

    @patch(f"{CLIENT_MODULE_PATH}.check_if_radkit_version_supported")
    def test_get_inventory_by_filter_no_results(self, mock_version_check: Mock) -> None:
        """Test inventory filtering with no results."""
        service = RadkitClientService(self.mock_client, self.valid_params)

        # Mock empty inventory
        service.radkit_service.inventory.filter.return_value = None

        with self.assertRaises(AnsibleRadkitOperationError) as cm:
            service.get_inventory_by_filter("pattern", "attr")

        self.assertIn("No devices found", str(cm.exception))

    @patch(f"{CLIENT_MODULE_PATH}.check_if_radkit_version_supported")
    def test_exec_command_success(self, mock_version_check: Mock) -> None:
        """Test successful command execution."""
        service = RadkitClientService(self.mock_client, self.valid_params)

        # Mock inventory and response
        mock_inventory = Mock()
        mock_response = Mock()
        mock_response.result = "command output"
        mock_inventory.exec.return_value.wait.return_value = mock_response

        result = service.exec_command("show version", mock_inventory)

        self.assertEqual(result, "command output")
        mock_inventory.exec.assert_called_once_with("show version", timeout=30)

    @patch(f"{CLIENT_MODULE_PATH}.check_if_radkit_version_supported")
    def test_exec_command_with_wait_timeout(self, mock_version_check: Mock) -> None:
        """Test command execution with wait timeout."""
        service = RadkitClientService(self.mock_client, self.valid_params)

        # Mock inventory and response
        mock_inventory = Mock()
        mock_response = Mock()
        mock_response.result = "command output"
        mock_inventory.exec.return_value.wait.return_value = mock_response

        service.exec_command("show version", mock_inventory)

        # Should call wait with timeout since wait_timeout > 0
        mock_inventory.exec.return_value.wait.assert_called_once_with(60)

    @patch(f"{CLIENT_MODULE_PATH}.check_if_radkit_version_supported")
    def test_exec_command_return_full_response(self, mock_version_check: Mock) -> None:
        """Test command execution returning full response."""
        service = RadkitClientService(self.mock_client, self.valid_params)

        # Mock inventory and response
        mock_inventory = Mock()
        mock_response = Mock()
        mock_response.result = "command output"
        mock_inventory.exec.return_value.wait.return_value = mock_response

        result = service.exec_command(
            "show version", mock_inventory, return_full_response=True
        )

        self.assertEqual(result, mock_response)

    @patch(f"{CLIENT_MODULE_PATH}.check_if_radkit_version_supported")
    def test_exec_command_empty_command(self, mock_version_check: Mock) -> None:
        """Test command execution with empty command."""
        service = RadkitClientService(self.mock_client, self.valid_params)
        mock_inventory = Mock()

        with self.assertRaises(AnsibleRadkitValidationError) as cm:
            service.exec_command("", mock_inventory)

        self.assertIn("Command cannot be empty", str(cm.exception))

    @patch(f"{CLIENT_MODULE_PATH}.check_if_radkit_version_supported")
    def test_exec_command_none_inventory(self, mock_version_check: Mock) -> None:
        """Test command execution with None inventory."""
        service = RadkitClientService(self.mock_client, self.valid_params)

        with self.assertRaises(AnsibleRadkitValidationError) as cm:
            service.exec_command("show version", None)

        self.assertIn("Inventory cannot be None", str(cm.exception))

    @patch(f"{CLIENT_MODULE_PATH}.check_if_radkit_version_supported")
    def test_context_manager(self, mock_version_check: Mock) -> None:
        """Test context manager functionality."""
        with RadkitClientService(self.mock_client, self.valid_params) as service:
            self.assertTrue(service.is_connected())

        # After context manager, connection should be cleaned up
        # Note: In real implementation, this would check if close() was called

    @patch(f"{CLIENT_MODULE_PATH}.check_if_radkit_version_supported")
    def test_is_connected(self, mock_version_check: Mock) -> None:
        """Test connection status checking."""
        service = RadkitClientService(self.mock_client, self.valid_params)

        self.assertTrue(service.is_connected())

        # Clear connections
        service.radkit_client = None
        service.radkit_service = None

        self.assertFalse(service.is_connected())

    @patch(f"{CLIENT_MODULE_PATH}.check_if_radkit_version_supported")
    def test_validate_connection_success(self, mock_version_check: Mock) -> None:
        """Test connection validation when connected."""
        service = RadkitClientService(self.mock_client, self.valid_params)

        # Should not raise exception
        service.validate_connection()

    @patch(f"{CLIENT_MODULE_PATH}.check_if_radkit_version_supported")
    def test_validate_connection_failure(self, mock_version_check: Mock) -> None:
        """Test connection validation when not connected."""
        service = RadkitClientService(self.mock_client, self.valid_params)

        # Clear connections
        service.radkit_client = None
        service.radkit_service = None

        with self.assertRaises(AnsibleRadkitConnectionError):
            service.validate_connection()


class TestUtilityFunctions(unittest.TestCase):
    """Test cases for utility functions."""

    def test_radkit_client_argument_spec(self) -> None:
        """Test argument specification generation."""
        spec = radkit_client_argument_spec()

        # Check that all required fields are present
        required_fields = ["identity", "client_key_password_b64", "service_serial"]
        for field in required_fields:
            self.assertIn(field, spec)
            self.assertTrue(spec[field]["required"])

        # Check optional fields
        optional_fields = ["client_key_path", "client_cert_path", "client_ca_path"]
        for field in optional_fields:
            self.assertIn(field, spec)
            self.assertFalse(spec[field]["required"])

    @patch(f"{CLIENT_MODULE_PATH}.check_if_radkit_version_supported")
    def test_create_radkit_client_service(self, mock_version_check: Mock) -> None:
        """Test factory function for creating service."""
        mock_client = Mock()
        mock_service = Mock()
        mock_client.service.return_value.wait.return_value = mock_service

        params = {
            "identity": "test-identity",
            "client_key_password_b64": base64.b64encode(b"test-password").decode(
                "utf-8"
            ),
            "service_serial": "test-serial-123",
        }

        service = create_radkit_client_service(mock_client, params)

        self.assertIsInstance(service, RadkitClientService)
        self.assertEqual(service.identity, "test-identity")


if __name__ == "__main__":
    # Run the tests
    unittest.main(verbosity=2)
