#!/usr/bin/env python3
"""
Unit tests for the exec_and_wait module.

These tests validate the core functionality of the exec_and_wait module,
specifically testing the run_action and helper functions.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
from ansible.module_utils.basic import AnsibleModule

# Handle import paths for both ansible-test and pytest environments
try:
    # Try collection import first (for ansible-test environment)
    from ansible_collections.cisco.radkit.plugins.modules.exec_and_wait import (
        run_action,
        _validate_interactive_parameters,
    )
    from ansible_collections.cisco.radkit.plugins.module_utils.exceptions import (
        AnsibleRadkitValidationError,
        AnsibleRadkitOperationError,
    )
    EXEC_AND_WAIT_MODULE_PATH = "ansible_collections.cisco.radkit.plugins.modules.exec_and_wait"
except ImportError:
    # Fallback for local development
    import sys
    import os
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..")))
    from plugins.modules.exec_and_wait import (
        run_action,
        _validate_interactive_parameters,
    )
    from plugins.module_utils.exceptions import (
        AnsibleRadkitValidationError,
        AnsibleRadkitOperationError,
    )
    EXEC_AND_WAIT_MODULE_PATH = None


class TestExecAndWaitModule(unittest.TestCase):
    """Test cases for the exec_and_wait module."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_module = Mock(spec=AnsibleModule)
        self.mock_radkit_service = Mock()
        
        # Default valid parameters
        self.default_params = {
            "device_name": "test-device",
            "device_host": None,
            "seconds_to_wait": 60,
            "delay_before_check": 10,
            "command_timeout": 30,
            "commands": ["reload"],
            "answers": ["y"],
            "prompts": ["Save configuration"],
            "command_retries": 1,
            "recovery_test_command": "\r",
        }
        self.mock_module.params = self.default_params.copy()

    def test_parameter_validation_with_mismatched_prompts_answers(self):
        """Test parameter validation with mismatched prompts and answers."""
        commands = ["reload"]
        prompts = ["Save configuration?", "Confirm reload?"]
        answers = ["y"]  # Only one answer for two prompts
        
        # Should raise validation error
        with self.assertRaises(AnsibleRadkitValidationError):
            _validate_interactive_parameters(commands, prompts, answers)

    def test_validate_interactive_parameters_success(self):
        """Test parameter validation with valid interactive parameters."""
        commands = ["reload"]
        prompts = ["Save configuration"]
        answers = ["y"]
        
        # Should not raise any exception
        _validate_interactive_parameters(commands, prompts, answers)


if __name__ == "__main__":
    unittest.main()
