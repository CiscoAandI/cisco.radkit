#!/usr/bin/env python3
"""
Unit tests for the genie_diff module.

These tests validate the core functionality of the genie_diff module
by importing and testing the actual module functions.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock

# Handle import paths for both ansible-test and pytest environments
try:
    # Try collection import first (for ansible-test environment)
    from ansible_collections.cisco.radkit.plugins.modules.genie_diff import (
        run_action,
        _extract_genie_result,
        _perform_genie_diff,
    )
    GENIE_DIFF_MODULE_PATH = "ansible_collections.cisco.radkit.plugins.modules.genie_diff"
except ImportError:
    # Fallback for local development
    import sys
    import os
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..")))
    from plugins.modules.genie_diff import (
        run_action,
        _extract_genie_result,
        _perform_genie_diff,
    )
    GENIE_DIFF_MODULE_PATH = None


class TestGenieDiffModule(unittest.TestCase):
    """Test cases for the genie_diff module."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_module = Mock()
        
        # Default valid parameters for diff operation
        self.default_params = {
            "result_a": {"genie_parsed_result": {"interface": {"GigabitEthernet0/1": {"status": "up"}}}},
            "result_b": {"genie_parsed_result": {"interface": {"GigabitEthernet0/1": {"status": "down"}}}},
            "diff_snapshots": False,
        }
        self.mock_module.params = self.default_params.copy()

    def test_extract_genie_result_with_parsed_key(self):
        """Test _extract_genie_result function with genie_parsed_result key."""
        result_data = {
            "genie_parsed_result": {"interface": {"GigabitEthernet0/1": {"status": "up"}}},
            "other_data": "value"
        }
        
        extracted = _extract_genie_result(result_data)
        
        # Should return the entire dict when genie_parsed_result key exists
        self.assertEqual(extracted, result_data)
        self.assertIn("genie_parsed_result", extracted)

    @patch(f'{GENIE_DIFF_MODULE_PATH or "plugins.modules.genie_diff"}.radkit_genie')
    def test_run_action_successful_diff(self, mock_radkit_genie):
        """Test run_action function with successful diff operation."""
        # Mock the diff_dicts function
        mock_diff_result = "--- \n+++ \n@@ -1 +1 @@\n-status: up\n+status: down"
        mock_radkit_genie.diff_dicts.return_value = mock_diff_result
        
        # Call the function
        results, err = run_action(self.mock_module)
        
        # Verify results
        self.assertFalse(err)
        self.assertIn("genie_diff_result", results)
        self.assertIn("genie_diff_result_lines", results)
        self.assertEqual(results["genie_diff_result"], mock_diff_result)
        self.assertIsInstance(results["genie_diff_result_lines"], list)
        self.assertFalse(results["changed"])
        
        # Verify radkit_genie.diff_dicts was called
        mock_radkit_genie.diff_dicts.assert_called_once()


if __name__ == "__main__":
    unittest.main()
