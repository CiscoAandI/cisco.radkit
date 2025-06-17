import unittest
from unittest.mock import MagicMock

try:
    # ansible-test collection import
    from ansible_collections.cisco.radkit.plugins.modules.snmp import (
        _execute_snmp_operation,
        AnsibleRadkitValidationError,
        AnsibleRadkitOperationError,
    )
except ImportError:
    import sys
    import os
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..")))
    from plugins.modules.snmp import (
        _execute_snmp_operation,
        AnsibleRadkitValidationError,
        AnsibleRadkitOperationError,
    )

class TestExecuteSnmpOperation(unittest.TestCase):
    def setUp(self):
        # Mock device and inventory
        self.device_name = "router1"
        self.mock_snmp_func = MagicMock()
        self.mock_device = MagicMock()
        self.mock_device.snmp.get = self.mock_snmp_func
        self.mock_device.snmp.walk = self.mock_snmp_func
        self.mock_device.snmp.get_next = self.mock_snmp_func
        self.mock_device.snmp.get_bulk = self.mock_snmp_func
        self.inventory = {self.device_name: self.mock_device}

        # Mock SNMP result row
        self.mock_result_row = MagicMock()
        self.mock_result_row.oid_str = "1.3.6.1.2.1.1.1.0"
        self.mock_result_row.value = "Cisco IOS"
        self.mock_result_row.type = "OctetString"
        self.mock_result_row.value_str = "Cisco IOS"
        self.mock_result_row.is_error = False
        self.mock_result_row.error_code = 0
        self.mock_result_row.error_str = ""
        self.mock_result_row.label_str = "iso.org.dod.internet.mgmt.mib-2.system.sysDescr"
        self.mock_result_row.mib_module = "SNMPv2-MIB"
        self.mock_result_row.mib_variable = "sysDescr"
        self.mock_result_row.mib_str = "SNMPv2-MIB::sysDescr.0"

        # Mock SNMP results object
        self.mock_results_obj = MagicMock()
        self.mock_results_obj.__iter__.return_value = ["row1"]
        self.mock_results_obj.__getitem__.return_value = self.mock_result_row
        self.mock_results_obj.without_errors.return_value = self.mock_results_obj

        # Mock wait().result chain
        self.mock_wait = MagicMock()
        self.mock_wait.result = self.mock_results_obj
        self.mock_snmp_func.return_value.wait.return_value = self.mock_wait

    def test_execute_snmp_operation_single_oid_simple(self):
        result = _execute_snmp_operation(
            inventory=self.inventory,
            action="get",
            oids=["1.3.6.1.2.1.1.1.0"],
            timeout=5.0,
            limit=None,
            retries=None,
            concurrency=10,
            include_errors=False,
            include_mib_info=False,
            output_format="simple",
        )
        self.assertIsInstance(result, list)
        self.assertEqual(result[0]["device_name"], self.device_name)
        self.assertEqual(result[0]["oid"], "1.3.6.1.2.1.1.1.0")
        self.assertEqual(result[0]["value"], "Cisco IOS")
        self.assertNotIn("type", result[0])

    def test_execute_snmp_operation_multiple_oids_detailed(self):
        # Simulate multiple OIDs by changing __iter__ and __getitem__
        self.mock_results_obj.__iter__.return_value = ["row1", "row2"]
        row2 = MagicMock()
        row2.oid_str = "1.3.6.1.2.1.1.2.0"
        row2.value = "sysObjectID"
        row2.type = "ObjectIdentifier"
        row2.value_str = "sysObjectID"
        row2.is_error = False
        row2.error_code = 0
        row2.error_str = ""
        row2.label_str = "iso.org.dod.internet.mgmt.mib-2.system.sysObjectID"
        row2.mib_module = "SNMPv2-MIB"
        row2.mib_variable = "sysObjectID"
        row2.mib_str = "SNMPv2-MIB::sysObjectID.0"
        self.mock_results_obj.__getitem__.side_effect = lambda k: self.mock_result_row if k == "row1" else row2

        result = _execute_snmp_operation(
            inventory=self.inventory,
            action="get",
            oids=["1.3.6.1.2.1.1.1.0", "1.3.6.1.2.1.1.2.0"],
            timeout=5.0,
            limit=None,
            retries=None,
            concurrency=10,
            include_errors=False,
            include_mib_info=True,
            output_format="detailed",
        )
        self.assertEqual(len(result), 2)
        for entry in result:
            self.assertIn("type", entry)
            self.assertIn("value_str", entry)
            self.assertIn("is_error", entry)
            self.assertIn("label", entry)
            self.assertIn("mib_module", entry)
            self.assertIn("mib_variable", entry)
            self.assertIn("mib_str", entry)

    def test_execute_snmp_operation_include_errors(self):
        # Simulate an error row
        self.mock_result_row.is_error = True
        self.mock_result_row.error_code = 2
        self.mock_result_row.error_str = "noSuchName"
        result = _execute_snmp_operation(
            inventory=self.inventory,
            action="get",
            oids=["1.3.6.1.2.1.1.1.0"],
            timeout=5.0,
            limit=None,
            retries=None,
            concurrency=10,
            include_errors=True,
            include_mib_info=False,
            output_format="detailed",
        )
        self.assertTrue(result[0]["is_error"])
        self.assertEqual(result[0]["error_code"], 2)
        self.assertEqual(result[0]["error_str"], "noSuchName")

    def test_execute_snmp_operation_invalid_action(self):
        # No mocking needed, just call with invalid action
        with self.assertRaises(AnsibleRadkitValidationError):
            _execute_snmp_operation(
                inventory=self.inventory,
                action="invalid_action",
                oids=["1.3.6.1.2.1.1.1.0"],
                timeout=5.0,
                limit=None,
                retries=None,
                concurrency=10,
                include_errors=False,
                include_mib_info=False,
                output_format="simple",
            )

    def test_execute_snmp_operation_snmp_func_exception(self):
        # The SNMP function should raise when called, not when accessed
        self.mock_device.snmp.get.side_effect = Exception("SNMP failure")
        with self.assertRaises(AnsibleRadkitOperationError):
            _execute_snmp_operation(
                inventory=self.inventory,
                action="get",
                oids=["1.3.6.1.2.1.1.1.0"],
                timeout=5.0,
                limit=None,
                retries=None,
                concurrency=10,
                include_errors=False,
                include_mib_info=False,
                output_format="simple",
            )

if __name__ == "__main__":
    unittest.main()
