# -*- coding: utf-8 -*-
"""
Custom exceptions for the Cisco RADKit Ansible Collection.

This module defines custom exception classes used throughout the collection
to provide clear error handling and meaningful error messages.
"""

from typing import Any, Dict, Optional
from ansible.module_utils._text import to_native


class AnsibleRadkitError(Exception):
    """
    Custom exception for RADKit-related errors in Ansible modules.

    This exception should be used for all RADKit-specific errors to provide
    consistent error handling across the collection.

    Attributes:
        message: The error message
        exception: The original exception that caused this error (if any)
        kwargs: Additional context information for the error
    """

    def __init__(
        self,
        message: Optional[str] = None,
        exception: Optional[Exception] = None,
        **kwargs: Any,
    ) -> None:
        """
        Initialize the AnsibleRadkitError.

        Args:
            message: The error message
            exception: The original exception that caused this error
            **kwargs: Additional context information
        """
        if not message and not exception:
            super().__init__()
        elif not message:
            super().__init__(str(exception))
        else:
            super().__init__(message)

        self.exception = exception
        self.message = message

        # Store additional context information that might be helpful
        # for module.fail_json or other error reporting mechanisms
        self.kwargs: Dict[str, Any] = kwargs or {}

    def __str__(self) -> str:
        """
        Return a string representation of the error.

        Returns:
            A formatted error message including both the message and exception details
        """
        if self.exception and self.message:
            return f"{self.message}: {to_native(self.exception)}"
        return super().__str__()

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the exception to a dictionary for structured error reporting.

        Returns:
            Dictionary containing error details
        """
        error_dict = {
            "error_type": self.__class__.__name__,
            "message": self.message or str(self),
        }

        if self.exception:
            error_dict["original_exception"] = {
                "type": type(self.exception).__name__,
                "message": str(self.exception),
            }

        if self.kwargs:
            error_dict["context"] = self.kwargs

        return error_dict


class AnsibleRadkitConnectionError(AnsibleRadkitError):
    """
    Exception raised when connection to RADKit service fails.

    This exception should be used specifically for connection-related issues
    such as authentication failures, network timeouts, or service unavailability.
    """

    pass


class AnsibleRadkitValidationError(AnsibleRadkitError):
    """
    Exception raised when parameter validation fails.

    This exception should be used for input validation errors,
    malformed parameters, or missing required fields.
    """

    pass


class AnsibleRadkitOperationError(AnsibleRadkitError):
    """
    Exception raised when a RADKit operation fails.

    This exception should be used for operation-specific failures
    such as command execution errors or inventory filtering issues.
    """

    pass
