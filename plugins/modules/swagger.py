#!/usr/bin/python
# -*- coding: utf-8 -*-
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""
Ansible Module for Cisco RADKit Swagger/OpenAPI Integration

This module provides comprehensive interaction with Swagger/OpenAPI endpoints
via RADKit, supporting all HTTP methods with proper validation, error handling,
and response processing for network automation workflows.
"""

from __future__ import absolute_import, division, print_function
from typing import Any, Dict, List, Optional, Tuple, Union
import logging

__metaclass__ = type

DOCUMENTATION = """
---
module: swagger
short_description: Interacts with Swagger/OpenAPI endpoints via RADKit
version_added: "0.3.0"
description:
  - Provides comprehensive interaction with Swagger/OpenAPI endpoints through RADKit
  - Supports all standard HTTP methods with automatic request/response handling
  - Includes proper status code validation and JSON response processing
  - Automatically updates Swagger paths before making requests
  - Designed for network device API automation and integration
options:
    device_name:
        description:
            - Name of device as it shows in RADKit inventory
        required: True
        type: str
    path:
        description:
            - url path, starting with /
        required: True
        type: str
    method:
        description:
            - HTTP method (get,post,put,patch,delete,options,head)
        required: True
        type: str
    parameters:
        description:
            - Path parameters for the Swagger path (e.g., for /users/{userId})
            - Provided as a dictionary of parameter names and values
        required: False
        type: dict
    params:
        description:
            - URL query parameters to append to the request
            - Will be properly URL-encoded and appended to the path
        required: False
        type: dict
    headers:
        description:
            - Custom HTTP headers to include in the request
            - Common headers include 'Content-Type', 'Authorization', etc.
        required: False
        type: dict
    cookies:
        description:
            - Cookie values to include in the request
            - Provided as a dictionary of cookie names and values
        required: False
        type: dict
    json:
        description:
            - Request body to be JSON-encoded and sent with appropriate Content-Type
            - Mutually exclusive with 'content' and 'data' parameters
        required: False
        type: dict
    content:
        description:
            - Raw request body content as string or bytes
            - Mutually exclusive with 'json' and 'data' parameters
        required: False
        type: str
    data:
        description:
            - Data to be form-encoded and sent in the request body
            - Mutually exclusive with 'json' and 'content' parameters
        required: False
        type: dict
    files:
        description:
            - Files to upload with the request (multipart form data)
            - Can be used alone or with 'data' parameter
        required: False
        type: dict
    timeout:
        description:
            - Timeout for the request on the Service side, in seconds
            - If not specified, the Service default timeout will be used
        required: False
        type: float
    status_code:
        description:
            - A list of valid, numeric, HTTP status codes that signifies success of the request.
        default: [ 200 ]
        type: list
        elements: int
extends_documentation_fragment: cisco.radkit.radkit_client
requirements:
    - radkit
author: Scott Dozier (@scdozier)
"""

RETURN = r"""
data:
    description: response body content as string
    returned: success
    type: str
json:
    description: response body content decoded as json
    returned: when response contains valid JSON
    type: dict
status_code:
    description: HTTP response status code
    returned: success
    type: int
headers:
    description: HTTP response headers
    returned: success
    type: dict
cookies:
    description: HTTP response cookies
    returned: when cookies are present in response
    type: dict
content_type:
    description: HTTP response Content-Type header
    returned: success
    type: str
url:
    description: The complete URL that was requested
    returned: success
    type: str
method:
    description: The HTTP method that was used
    returned: success
    type: str
"""
EXAMPLES = """
    - name: Get alarms from vManage
      cisco.radkit.swagger:
        device_name: vmanage1
        path: /alarms
        method: get
        status_code: [200]
      register: swagger_output
      delegate_to: localhost

    - name: Register a new NMS partner in vManage with path parameters
      cisco.radkit.swagger:
        device_name: vmanage1
        path: /partner/{partnerType}
        parameters: 
          partnerType: "dnac"
        method: post
        status_code: [200]
        json: 
          name: "DNAC-test"
          partnerId: "dnac-test"
          description: "dnac-test"
        headers:
          Authorization: "Bearer {{ auth_token }}"
      register: swagger_output
      delegate_to: localhost

    - name: Upload configuration file
      cisco.radkit.swagger:
        device_name: device1
        path: /config/upload
        method: post
        files:
          config: "{{ config_file_path }}"
        data:
          description: "New configuration"
        timeout: 60.0
      register: upload_result
      delegate_to: localhost

    - name: Get device status with query parameters
      cisco.radkit.swagger:
        device_name: device1
        path: /status
        method: get
        params:
          format: json
          verbose: true
        headers:
          Accept: application/json
        cookies:
          sessionid: "{{ session_id }}"
      register: status_result
      delegate_to: localhost

    - name: Send raw content data
      cisco.radkit.swagger:
        device_name: device1
        path: /config/raw
        method: put
        content: |
          interface GigabitEthernet0/1
           ip address 192.168.1.1 255.255.255.0
           no shutdown
        headers:
          Content-Type: text/plain
      register: config_result
      delegate_to: localhost
"""
import json

try:
    from radkit_client.sync import Client

    HAS_RADKIT = True
except ImportError:
    HAS_RADKIT = False

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.cisco.radkit.plugins.module_utils.client import (
    radkit_client_argument_spec,
    RadkitClientService,
)
from ansible_collections.cisco.radkit.plugins.module_utils.exceptions import (
    AnsibleRadkitError,
    AnsibleRadkitConnectionError,
    AnsibleRadkitValidationError,
    AnsibleRadkitOperationError,
)

# Constants for HTTP methods and validation
VALID_HTTP_METHODS = ["get", "post", "put", "patch", "delete", "options", "head"]
READ_ONLY_METHODS = ["get", "head", "options"]
DEFAULT_SUCCESS_STATUS = [200]

# Setup module logger
logger = logging.getLogger(__name__)

__metaclass__ = type


def _validate_http_method(method: str) -> None:
    """Validate that the HTTP method is supported."""
    if method.lower() not in VALID_HTTP_METHODS:
        raise AnsibleRadkitValidationError(
            f"HTTP method '{method}' not supported. Valid methods: {', '.join(VALID_HTTP_METHODS)}"
        )


def _prepare_swagger_params(params: Dict[str, Any]) -> Dict[str, Any]:
    """Prepare parameters for Swagger API call, removing None values."""
    swagger_params = {
        "path": params["path"],
        "parameters": params.get("parameters")
        or params.get("params"),  # Support both parameter names
        "content": params.get("content"),
        "data": params.get("data"),
        "files": params.get("files"),
        "json": params.get("json"),
        "headers": params.get("headers"),
        "cookies": params.get("cookies"),
        "timeout": params.get("timeout"),
    }

    # Remove None values to avoid API issues
    return {k: v for k, v in swagger_params.items() if v is not None}


def _process_swagger_response(response: Any, method: str) -> Dict[str, Any]:
    """Process Swagger API response and extract relevant data."""
    results = {
        "status_code": response.result.response_code,
        "data": response.result.text,
        "changed": method.lower() not in READ_ONLY_METHODS,
        "method": method.upper(),
        "url": getattr(response.result, "url", ""),
        "content_type": getattr(response.result, "content_type", ""),
    }

    # Add headers if available
    if hasattr(response.result, "headers"):
        results["headers"] = (
            dict(response.result.headers)
            if hasattr(response.result.headers, "items")
            else {}
        )
    else:
        results["headers"] = {}

    # Add cookies if available
    if hasattr(response.result, "cookies"):
        results["cookies"] = response.result.cookies if response.result.cookies else {}
    else:
        results["cookies"] = {}

    # Parse JSON response if available
    if (
        hasattr(response.result, "content_type")
        and response.result.content_type
        and "json" in response.result.content_type.lower()
    ):
        if hasattr(response.result, "json") and response.result.json is not None:
            results["json"] = response.result.json

    return results


def _validate_status_code(actual_code: int, expected_codes: List[int]) -> None:
    """Validate that the response status code is acceptable."""
    if actual_code not in expected_codes:
        raise AnsibleRadkitOperationError(
            f"Response code {actual_code} not in expected codes {expected_codes}"
        )


def _validate_swagger_path(device: Any, path: str, device_name: str) -> None:
    """Validate that the Swagger path exists in the device's API specification."""
    try:
        # Check if the path exists in the swagger paths
        if hasattr(device.swagger, "paths") and path not in device.swagger.paths:
            available_paths = (
                list(device.swagger.paths.keys())
                if hasattr(device.swagger, "paths")
                else []
            )
            raise AnsibleRadkitValidationError(
                f"Swagger path '{path}' not found in API specification for device '{device_name}'. "
                f"Available paths: {available_paths[:10]}{'...' if len(available_paths) > 10 else ''}"
            )
    except AttributeError:
        # If we can't check paths, we'll let the actual API call handle the error
        logger.debug(
            f"Could not validate Swagger path '{path}' - proceeding with API call"
        )


def run_action(
    module: AnsibleModule, radkit_service: RadkitClientService
) -> Tuple[Dict[str, Any], bool]:
    """
    Execute Swagger/OpenAPI operations via RADKit.

    Args:
        module: Ansible module instance
        radkit_service: RADKit client service instance

    Returns:
        Tuple containing results dictionary and error flag

    Raises:
        AnsibleRadkitValidationError: For parameter validation issues
        AnsibleRadkitConnectionError: For connectivity problems
        AnsibleRadkitOperationError: For API operation failures
    """
    try:
        params: Dict[str, Any] = module.params
        device_name: str = params["device_name"]
        method: str = params["method"]

        # Validate HTTP method
        _validate_http_method(method)

        # Get device from inventory
        inventory = radkit_service.get_inventory_by_filter(device_name, "name")
        if not inventory:
            raise AnsibleRadkitValidationError(
                f"No devices found in RADKit inventory with name: {device_name}"
            )

        device = inventory[device_name]

        # Update Swagger paths
        logger.debug(f"Updating Swagger paths for device {device_name}")
        device.update_swagger().wait()

        # Validate that the path exists in the Swagger specification
        path = params["path"]
        _validate_swagger_path(device, path, device_name)

        # Prepare API call parameters
        swagger_params = _prepare_swagger_params(dict(params))

        # Get the appropriate HTTP method function
        swagger_func = getattr(device.swagger, method.lower())

        # Execute the Swagger API call
        logger.debug(f"Executing {method.upper()} request to {params.get('path')}")
        radkit_response = swagger_func(**swagger_params).wait()

        # Process response
        results = _process_swagger_response(radkit_response, method)

        # Validate status code
        expected_codes: List[int] = params["status_code"]
        _validate_status_code(results["status_code"], expected_codes)

        return results, False

    except KeyError as e:
        # Handle case where Swagger path is not found in the API specification
        path = params.get("path", "unknown")
        logger.error(
            f"Swagger path '{path}' not found in API specification for device {device_name}"
        )
        raise AnsibleRadkitValidationError(
            f"Swagger path '{path}' not found in API specification for device '{device_name}'. "
            f"Please verify the path exists in the device's Swagger documentation."
        )
    except (
        AnsibleRadkitConnectionError,
        AnsibleRadkitValidationError,
        AnsibleRadkitOperationError,
    ) as e:
        logger.error(f"RADKit Swagger operation failed: {e}")
        return {"msg": str(e), "changed": False}, True
    except Exception as e:
        logger.error(f"Unexpected error in swagger module: {e}")
        # print traceback for debugging
        import traceback

        # get the traceback as a string
        tb_str = traceback.format_exc()
        return {"msg": f"Unexpected error: {str(tb_str)}", "changed": False}, True


def main() -> None:
    """Main module execution function."""
    spec = radkit_client_argument_spec()
    spec.update(
        {
            "path": {
                "type": "str",
                "required": True,
            },
            "device_name": {
                "type": "str",
                "required": True,
            },
            "method": {
                "type": "str",
                "required": True,
            },
            "parameters": {
                "type": "dict",
                "required": False,
            },
            "params": {
                "type": "dict",
                "required": False,
            },
            "headers": {
                "type": "dict",
                "required": False,
            },
            "cookies": {
                "type": "dict",
                "required": False,
            },
            "json": {
                "type": "dict",
                "required": False,
            },
            "content": {
                "type": "str",
                "required": False,
            },
            "data": {
                "type": "dict",
                "required": False,
            },
            "files": {
                "type": "dict",
                "required": False,
            },
            "timeout": {
                "type": "float",
                "required": False,
            },
            "status_code": {
                "type": "list",
                "elements": "int",
                "default": DEFAULT_SUCCESS_STATUS,
            },
        }
    )

    module = AnsibleModule(
        argument_spec=spec,
        supports_check_mode=False,
        mutually_exclusive=[
            ("content", "json"),
            ("content", "data"),
            ("json", "data"),
            ("parameters", "params"),  # Only one way to specify parameters
        ],
    )

    # Validate dependencies
    if not HAS_RADKIT:
        module.fail_json(msg="Python module cisco_radkit is required for this module!")

    try:
        # Validate HTTP method
        method = module.params["method"]
        if method.lower() not in VALID_HTTP_METHODS:
            module.fail_json(
                msg=f"HTTP method must be one of: {', '.join(VALID_HTTP_METHODS.upper())}"
            )

        # Execute with RADKit client
        with Client.create() as client:
            radkit_service = RadkitClientService(client, module.params)
            results, err = run_action(module, radkit_service)

        if err:
            module.fail_json(**results)
        module.exit_json(**results)

    except (
        AnsibleRadkitConnectionError,
        AnsibleRadkitValidationError,
        AnsibleRadkitOperationError,
    ) as e:
        module.fail_json(msg=str(e), changed=False)
    except Exception as e:
        logger.error(f"Unexpected error in main: {e}")
        module.fail_json(msg=f"Unexpected error: {str(e)}", changed=False)


if __name__ == "__main__":
    main()
