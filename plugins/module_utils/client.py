"""
RADKit Client Module for Ansible Collections.

This module provides client utilities for interacting with Cisco RADKit services
through Ansible modules and plugins.
"""

from __future__ import absolute_import, division, print_function

import base64
import logging
from typing import Any, Dict, Optional, Union

try:
    from packaging import version

    HAS_PACKAGING = True
except ImportError:
    HAS_PACKAGING = False

try:
    import radkit_client
    from radkit_client.sync import Client

    HAS_RADKIT = True
except ImportError:
    HAS_RADKIT = False

from ansible.module_utils.common.warnings import warn
from ansible.module_utils.basic import env_fallback
from ansible.module_utils._text import to_text

try:
    from ansible_collections.cisco.radkit.plugins.module_utils.exceptions import (
        AnsibleRadkitError,
        AnsibleRadkitConnectionError,
        AnsibleRadkitValidationError,
        AnsibleRadkitOperationError,
    )
except ImportError:
    # For standalone testing, use relative import
    from exceptions import (
        AnsibleRadkitError,
        AnsibleRadkitConnectionError,
        AnsibleRadkitValidationError,
        AnsibleRadkitOperationError,
    )

__metaclass__ = type

# Constants
SUPPORTED_VERSION_MIN = "1.8.0b"
SUPPORTED_VERSION_MAX = "1.9.0b"
DEFAULT_TIMEOUT = 0

# Environment variable names
ENV_VARS = {
    "IDENTITY": "RADKIT_ANSIBLE_IDENTITY",
    "CLIENT_KEY_PASSWORD_B64": "RADKIT_ANSIBLE_CLIENT_PRIVATE_KEY_PASSWORD_BASE64",
    "SERVICE_SERIAL": "RADKIT_ANSIBLE_SERVICE_SERIAL",
    "CLIENT_KEY_PATH": "RADKIT_ANSIBLE_CLIENT_KEY_PATH",
    "CLIENT_CERT_PATH": "RADKIT_ANSIBLE_CLIENT_CERT_PATH",
    "CLIENT_CA_PATH": "RADKIT_ANSIBLE_CLIENT_CA_PATH",
}

# Logger setup
logger = logging.getLogger(__name__)


def check_if_radkit_version_supported() -> None:
    """
    Check if the installed RADKit version is supported.

    Raises:
        AnsibleRadkitError: If RADKit client is not installed or version is unsupported.
    """
    if not HAS_PACKAGING:
        logger.warning("packaging library not available, skipping version check")
        return

    if not HAS_RADKIT:
        raise AnsibleRadkitError("RADKit Client is not installed!")

    try:
        # These imports are guarded by HAS_PACKAGING and HAS_RADKIT checks above
        if HAS_PACKAGING and HAS_RADKIT:
            radkit_version = version.parse(radkit_client.version.version_str)  # type: ignore
            next_major = version.parse(SUPPORTED_VERSION_MAX)  # type: ignore
            current_major = version.parse(SUPPORTED_VERSION_MIN)  # type: ignore

            if radkit_version >= next_major or radkit_version < current_major:
                warn(
                    f"This version of the RADKit Ansible collection is only verified "
                    f"in the RADKit 1.8.x release. Installed RADKit version: {radkit_version}"
                )
    except Exception as e:
        logger.warning(f"Could not parse RADKit version: {e}")
        raise AnsibleRadkitError(f"Unable to verify RADKit version: {to_text(e)}")


def radkit_client_argument_spec() -> Dict[str, Dict[str, Any]]:
    """
    Base argument specification for RADKit-related modules.

    Returns:
        Dict containing the common arguments for all RADKit modules.
    """
    return {
        "identity": {
            "type": "str",
            "aliases": ["radkit_identity"],
            "required": True,
            "fallback": (env_fallback, [ENV_VARS["IDENTITY"]]),
        },
        "client_key_password_b64": {
            "type": "str",
            "required": True,
            "no_log": True,
            "aliases": ["radkit_client_private_key_password_base64"],
            "fallback": (env_fallback, [ENV_VARS["CLIENT_KEY_PASSWORD_B64"]]),
        },
        "service_serial": {
            "type": "str",
            "aliases": ["radkit_serial", "radkit_service_serial"],
            "required": True,
            "fallback": (env_fallback, [ENV_VARS["SERVICE_SERIAL"]]),
        },
        "client_key_path": {
            "type": "str",
            "required": False,
            "no_log": True,
            "fallback": (env_fallback, [ENV_VARS["CLIENT_KEY_PATH"]]),
        },
        "client_cert_path": {
            "type": "str",
            "required": False,
            "fallback": (env_fallback, [ENV_VARS["CLIENT_CERT_PATH"]]),
        },
        "client_ca_path": {
            "type": "str",
            "required": False,
            "fallback": (env_fallback, [ENV_VARS["CLIENT_CA_PATH"]]),
        },
    }


class RadkitClientService:
    """
    Service class for managing RADKit client connections and operations.

    This class handles authentication, service connections, and provides
    methods for inventory management and command execution.
    """

    def __init__(self, radkit_sync_client: Any, module_params: Dict[str, Any]) -> None:
        """
        Initialize RADKit client service.

        Args:
            radkit_sync_client: The RADKit synchronous client instance
            module_params: Dictionary of module parameters

        Raises:
            AnsibleRadkitError: If connection to RADKit service fails
        """
        check_if_radkit_version_supported()

        # Store client reference
        self.radkit_client: Any = None
        self.radkit_service: Any = None

        # Extract and validate required parameters
        self.identity = module_params.get("identity")
        self.client_key_password_b64 = module_params.get("client_key_password_b64")
        self.service_serial = module_params.get("service_serial")
        self.client_ca_path = module_params.get("client_ca_path")
        self.client_key_path = module_params.get("client_key_path")
        self.client_cert_path = module_params.get("client_cert_path")
        self.exec_timeout = module_params.get("exec_timeout", DEFAULT_TIMEOUT)
        self.wait_timeout = module_params.get("wait_timeout", DEFAULT_TIMEOUT)

        # Validate required parameters
        if not self.identity:
            raise AnsibleRadkitValidationError("Identity parameter is required")
        if not self.client_key_password_b64:
            raise AnsibleRadkitValidationError(
                "Client key password (base64) is required"
            )
        if not self.service_serial:
            raise AnsibleRadkitValidationError("Service serial is required")

        self._establish_connection(radkit_sync_client)

    def _establish_connection(self, radkit_sync_client: Any) -> None:
        """
        Establish connection to RADKit service.

        Args:
            radkit_sync_client: The RADKit synchronous client instance

        Raises:
            AnsibleRadkitError: If connection fails
        """
        try:
            # Decode and validate base64 password
            private_key_password = self._decode_base64_password()

            # Perform certificate login
            radkit_sync_client.certificate_login(
                identity=self.identity,
                ca_path=self.client_ca_path,
                key_path=self.client_key_path,
                cert_path=self.client_cert_path,
                private_key_password=private_key_password,
            )

            self.radkit_client = radkit_sync_client

            # Connect to service
            service = radkit_sync_client.service(self.service_serial).wait()
            self.radkit_service = service

            logger.info(
                f"Successfully connected to RADKit service: {self.service_serial}"
            )

        except AnsibleRadkitValidationError:
            # Re-raise validation errors as-is
            raise
        except (ValueError, TypeError) as e:
            raise AnsibleRadkitValidationError(
                f"Invalid parameter format: {to_text(e)}"
            )
        except Exception as e:
            raise AnsibleRadkitConnectionError(
                f"Unable to connect to RADKit Service: {to_text(e)}"
            )

    def _decode_base64_password(self) -> str:
        """
        Safely decode base64 encoded password.

        Returns:
            Decoded password string

        Raises:
            AnsibleRadkitError: If decoding fails
        """
        if not self.client_key_password_b64:
            raise AnsibleRadkitValidationError("Client key password cannot be None")

        try:
            return base64.b64decode(self.client_key_password_b64).decode("utf-8")
        except Exception as e:
            raise AnsibleRadkitValidationError(
                f"Failed to decode client key password: {to_text(e)}"
            )

    def get_inventory_by_filter(self, pattern: str, attr: str) -> Any:
        """
        Get inventory from RADKit by pattern and attribute filter.

        Args:
            pattern: The pattern to match against
            attr: The attribute to filter by

        Returns:
            Filtered inventory object

        Raises:
            AnsibleRadkitError: If no devices found or service not available
        """
        if not self.radkit_service:
            raise AnsibleRadkitConnectionError(
                "RADKit service connection not established"
            )

        try:
            inventory = self.radkit_service.inventory.filter(attr, pattern)
            if inventory:
                logger.debug(
                    f"Found inventory with attr: {attr} and pattern: {pattern}"
                )
                return inventory
            else:
                raise AnsibleRadkitOperationError(
                    f"No devices found in RADKit inventory with attr: {attr} and pattern: {pattern}!"
                )
        except Exception as e:
            if isinstance(e, AnsibleRadkitError):
                raise
            raise AnsibleRadkitOperationError(
                f"Failed to filter inventory: {to_text(e)}"
            )

    def exec_command(
        self, cmd: str, inventory: Any, return_full_response: bool = False
    ) -> Any:
        """
        Execute a command on devices via RADKit.

        Args:
            cmd: The command to execute
            inventory: The inventory object to execute command on
            return_full_response: Whether to return full response or just result

        Returns:
            Command execution result or full response

        Raises:
            AnsibleRadkitError: If command execution fails
        """
        if not inventory:
            raise AnsibleRadkitValidationError("Inventory cannot be None")
        if not cmd:
            raise AnsibleRadkitValidationError("Command cannot be empty")

        try:
            exec_timeout = int(self.exec_timeout)
            wait_timeout = int(self.wait_timeout)

            logger.debug(f"Executing command: {cmd} with timeout: {exec_timeout}")

            if wait_timeout == 0:
                response = inventory.exec(cmd, timeout=exec_timeout).wait()
            else:
                response = inventory.exec(cmd, timeout=exec_timeout).wait(wait_timeout)

            return response if return_full_response else response.result

        except (ValueError, TypeError) as e:
            raise AnsibleRadkitValidationError(f"Invalid timeout values: {to_text(e)}")
        except Exception as e:
            raise AnsibleRadkitOperationError(f"Command execution failed: {to_text(e)}")

    def __enter__(self) -> "RadkitClientService":
        """Context manager entry."""
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Context manager exit with cleanup."""
        self.close()

    def close(self) -> None:
        """
        Clean up resources and close connections.

        This method should be called when the service is no longer needed
        to ensure proper cleanup of resources.
        """
        try:
            if self.radkit_client:
                # Attempt to close client connection if method exists
                if hasattr(self.radkit_client, "close"):
                    self.radkit_client.close()
                logger.debug("RADKit client connection closed")
        except Exception as e:
            logger.warning(f"Error during cleanup: {to_text(e)}")
        finally:
            self.radkit_client = None
            self.radkit_service = None

    def is_connected(self) -> bool:
        """
        Check if the service is connected and ready.

        Returns:
            True if connected and service is available, False otherwise
        """
        return self.radkit_client is not None and self.radkit_service is not None

    def validate_connection(self) -> None:
        """
        Validate that the connection is established and ready.

        Raises:
            AnsibleRadkitError: If connection is not established
        """
        if not self.is_connected():
            raise AnsibleRadkitConnectionError(
                "RADKit service connection not established"
            )


def create_radkit_client_service(
    radkit_sync_client: Any, module_params: Dict[str, Any]
) -> RadkitClientService:
    """
    Factory function to create a RadkitClientService instance.

    Args:
        radkit_sync_client: The RADKit synchronous client instance
        module_params: Dictionary of module parameters

    Returns:
        Configured RadkitClientService instance

    Raises:
        AnsibleRadkitError: If service creation fails
    """
    try:
        return RadkitClientService(radkit_sync_client, module_params)
    except Exception as e:
        raise AnsibleRadkitConnectionError(
            f"Failed to create RADKit client service: {to_text(e)}"
        )


# Backward compatibility aliases
RadkitClient = RadkitClientService  # For any existing code that might use this name
