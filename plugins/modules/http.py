#!/usr/bin/python
# -*- coding: utf-8 -*-
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""
Ansible module for HTTP/HTTPS interactions with devices via Cisco RADKit.

This module provides a professional interface for making HTTP requests to
network devices or services managed by Cisco RADKit, with comprehensive
request and response handling.
"""

from __future__ import absolute_import, division, print_function
from typing import Any, Dict, List, Optional, Union

__metaclass__ = type

DOCUMENTATION = """
---
module: http
short_description: Execute HTTP/HTTPS requests on devices via Cisco RADKit
version_added: "0.3.0"
description:
  - Executes HTTP and HTTPS requests on devices or services managed by Cisco RADKit
  - Supports all standard HTTP methods with comprehensive request configuration
  - Provides structured response data including status, headers, and content
  - Handles authentication, cookies, and custom headers professionally
options:
    device_name:
        description:
            - Name of the device or service as it appears in RADKit inventory
            - Must be a valid device accessible through RADKit
        required: true
        type: str
    path:
        description:
            - URL path for the HTTP request, must start with '/'
            - Can include query parameters or use the 'params' option separately
        required: true
        type: str
    method:
        description:
            - HTTP method to use for the request
            - Supports all standard REST API methods
        required: true
        type: str
        choices: ['GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'OPTIONS', 'HEAD', 'get', 'post', 'put', 'patch', 'delete', 'options', 'head']
    cookies:
        description:
            - Cookie values to include in the request
            - Provided as a dictionary of cookie names and values
        required: false
        type: dict
    headers:
        description:
            - Custom HTTP headers to include in the request
            - Common headers include 'Content-Type', 'Authorization', etc.
        required: false
        type: dict
    params:
        description:
            - URL parameters to append to the request
            - Will be properly URL-encoded and appended to the path
        required: false
        type: dict
    json:
        description:
            - Request body to be JSON-encoded and sent with appropriate Content-Type
            - Mutually exclusive with 'content' and 'data' parameters
        required: false
        type: dict
    content:
        description:
            - Raw request body content as string
            - Mutually exclusive with 'json' and 'data' parameters
        required: false
        type: str
    data:
        description:
            - Data to be form-encoded and sent in the request body
            - Mutually exclusive with 'json' and 'content' parameters
        required: false
        type: dict
    files:
        description:
            - Files to upload with the request (multipart form data)
            - Can be used alone or with 'data' parameter
        required: false
        type: dict
    timeout:
        description:
            - Timeout for the request on the Service side, in seconds
            - If not specified, the Service default timeout will be used
        required: false
        type: float
    status_code:
        description:
            - List of valid HTTP status codes that indicate successful requests
            - Request will be considered failed if response code is not in this list
        default: [200]
        type: list
        elements: int
extends_documentation_fragment: cisco.radkit.radkit_client
requirements:
    - cisco-radkit-client
author: Scott Dozier (@scdozier)
"""

RETURN = r"""
data:
    description: Response body content as string
    returned: success
    type: str
    sample: '{"result": "success", "message": "Operation completed"}'
json:
    description: Response body content parsed as JSON (if valid JSON)
    returned: when response contains valid JSON
    type: dict
    sample: {"result": "success", "message": "Operation completed"}
status_code:
    description: HTTP response status code
    returned: always
    type: int
    sample: 200
cookies:
    description: Response cookies as dictionary
    returned: when cookies are present in response
    type: dict
    sample: {"sessionid": "abc123", "token": "xyz789"}
headers:
    description: Response headers as dictionary
    returned: always
    type: dict
    sample: {"content-type": "application/json", "server": "nginx/1.18"}
changed:
    description: Whether any changes were made (depends on HTTP method used)
    returned: always
    type: bool
    sample: false
"""
EXAMPLES = """
# Simple GET request
- name: Execute HTTP GET request
  cisco.radkit.http:
    device_name: api-server-01
    path: /api/v1/status
    method: GET
  register: status_response
  delegate_to: localhost

# POST request with JSON payload
- name: Create new resource via POST
  cisco.radkit.http:
    device_name: api-server-01
    path: /api/v1/resources
    method: POST
    headers:
      Content-Type: application/json
      Authorization: Bearer {{ api_token }}
    json:
      name: "new-resource"
      type: "configuration"
      enabled: true
    status_code: [201, 202]
  register: create_response
  delegate_to: localhost

# GET request with query parameters
- name: Fetch filtered data
  cisco.radkit.http:
    device_name: monitoring-server
    path: /metrics
    method: GET
    params:
      start_time: "2024-01-01T00:00:00Z"
      end_time: "2024-01-02T00:00:00Z"
      format: json
    headers:
      Accept: application/json
  register: metrics_data
  delegate_to: localhost

# PUT request with authentication cookies
- name: Update configuration
  cisco.radkit.http:
    device_name: config-server
    path: /api/config/network
    method: PUT
    cookies:
      sessionid: "{{ login_session.cookies.sessionid }}"
      csrftoken: "{{ csrf_token }}"
    content: |
      interface GigabitEthernet0/1
       ip address 192.168.1.1 255.255.255.0
       no shutdown
    headers:
      Content-Type: text/plain
    status_code: [200, 204]
    timeout: 30.0
  register: config_update
  delegate_to: localhost

# POST request with form data
- name: Submit form data
  cisco.radkit.http:
    device_name: web-server
    path: /api/form-submit
    method: POST
    data:
      username: "admin"
      password: "secret"
      action: "login"
    headers:
      User-Agent: "Ansible-HTTP-Client"
  register: form_response
  delegate_to: localhost

# File upload with multipart form data
- name: Upload firmware file
  cisco.radkit.http:
    device_name: device-01
    path: /api/firmware/upload
    method: POST
    files:
      firmware: "/path/to/firmware.bin"
    data:
      version: "1.2.3"
      description: "Latest firmware"
    timeout: 300.0
  register: upload_response
  delegate_to: localhost

# Display response data
- name: Show HTTP response
  debug:
    msg: "Status: {{ status_response.status_code }}, Data: {{ status_response.json }}"

# Handle different response types
- name: Process API response
  debug:
    msg: "{{ create_response.json.id if create_response.json is defined else create_response.data }}"
"""
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
    AnsibleRadkitOperationError,
    AnsibleRadkitValidationError,
)

__metaclass__ = type


def run_action(
    module: AnsibleModule, radkit_service: RadkitClientService
) -> tuple[Dict[str, Any], bool]:
    """
    Execute HTTP request via RADKit service with comprehensive error handling.

    Args:
        module: Ansible module instance with validated parameters
        radkit_service: Configured RADKit client service

    Returns:
        Tuple of (results dictionary, error flag)

    Raises:
        AnsibleRadkitError: For RADKit-specific operational errors
    """
    results: Dict[str, Any] = {}
    err = False

    try:
        params = module.params
        device_name = params["device_name"]
        method = params["method"].upper()

        # Get device inventory
        try:
            inventory = radkit_service.get_inventory_by_filter(device_name, "name")
        except AnsibleRadkitError as e:
            raise AnsibleRadkitOperationError(
                f"Device '{device_name}' not found in RADKit inventory"
            ) from e

        # Prepare HTTP request parameters
        http_params = _prepare_http_params(params, method)

        # Execute HTTP request
        try:
            http_func = getattr(inventory[device_name].http, method.lower())
            radkit_response = http_func(**http_params).wait()

            # Process response
            results = _process_http_response(radkit_response, params)

        except Exception as e:
            raise AnsibleRadkitOperationError(
                f"HTTP {method} request failed on {device_name}: {str(e)}"
            ) from e

    except AnsibleRadkitError:
        # Re-raise RADKit specific errors
        raise
    except Exception as e:
        # Handle unexpected errors
        err = True
        results["msg"] = f"Unexpected error during HTTP request: {str(e)}"
        results["changed"] = False

    return results, err


def _prepare_http_params(params: Dict[str, Any], method: str) -> Dict[str, Any]:
    """
    Prepare HTTP request parameters based on method and input.

    Args:
        params: Module parameters
        method: HTTP method (uppercase)

    Returns:
        Dictionary of HTTP parameters for the request
    """
    http_params = {
        "path": params["path"],
        "headers": params.get("headers"),
        "cookies": params.get("cookies"),
        "params": params.get("params"),
        "timeout": params.get("timeout"),
    }

    # Only include body parameters for methods that support them
    if method not in ["GET", "HEAD", "DELETE"]:
        http_params["content"] = params.get("content")
        http_params["data"] = params.get("data")
        http_params["files"] = params.get("files")
        http_params["json"] = params.get("json")

    # Remove None values to avoid API issues
    return {k: v for k, v in http_params.items() if v is not None}


def _process_http_response(
    radkit_response: Any, params: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Process RADKit HTTP response into structured Ansible results.

    Args:
        radkit_response: RADKit HTTP response object
        params: Module parameters for validation

    Returns:
        Dictionary of processed response data

    Raises:
        AnsibleRadkitOperationError: If response status code is not acceptable
    """
    results = {}
    response = radkit_response.result
    method = params["method"].upper()

    # Extract basic response data
    results["status_code"] = response.status_code
    results["headers"] = (
        dict(response.headers)
        if hasattr(response.headers, "items")
        else str(response.headers)
    )
    results["cookies"] = response.cookies if hasattr(response, "cookies") else {}

    # Extract response content
    if hasattr(response, "content") and response.content:
        results["data"] = response.content
    elif hasattr(response, "data") and response.data:
        results["data"] = response.data

    # Try to parse JSON if content-type indicates JSON
    headers = results["headers"]
    if isinstance(headers, dict):
        content_type = headers.get("content-type", "").lower()
        if "json" in content_type and hasattr(response, "json"):
            try:
                results["json"] = response.json
            except Exception:
                # JSON parsing failed, but that's okay
                pass

    # Determine if this operation should be considered a change
    results["changed"] = method not in ["GET", "HEAD", "OPTIONS"]

    # Validate status code
    if response.status_code not in params["status_code"]:
        raise AnsibleRadkitOperationError(
            f"HTTP {method} request returned status code {response.status_code}, "
            f"expected one of {params['status_code']}"
        )

    return results


def main() -> None:
    """
    Main entry point for the Ansible HTTP module.

    Handles argument parsing, validation, and HTTP request orchestration.
    """
    # Define module argument specification
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
                "choices": [
                    "GET",
                    "POST",
                    "PUT",
                    "PATCH",
                    "DELETE",
                    "OPTIONS",
                    "HEAD",
                    "get",
                    "post",
                    "put",
                    "patch",
                    "delete",
                    "options",
                    "head",
                ],
            },
            "cookies": {
                "type": "dict",
                "required": False,
            },
            "headers": {
                "type": "dict",
                "required": False,
            },
            "params": {
                "type": "dict",
                "required": False,
            },
            "content": {
                "type": "str",
                "required": False,
            },
            "json": {
                "type": "dict",
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
                "default": [200],
            },
        }
    )

    # Create module instance
    module = AnsibleModule(
        argument_spec=spec,
        supports_check_mode=False,
        mutually_exclusive=[
            ("content", "json"),
            ("content", "data"),
            ("json", "data"),
        ],
    )

    # Validate module prerequisites
    if not HAS_RADKIT:
        module.fail_json(
            msg="Required Python package 'cisco-radkit-client' is not installed. "
            "Install it using: pip install cisco-radkit-client"
        )

    # Validate parameters
    _validate_http_parameters(module)

    # Execute HTTP request via RADKit
    try:
        if not HAS_RADKIT:
            raise ImportError("radkit_client not available")

        with Client.create() as client:
            with RadkitClientService(client, module.params) as radkit_service:
                results, err = run_action(module, radkit_service)

        if err:
            module.fail_json(**results)
        else:
            module.exit_json(**results)

    except AnsibleRadkitError as e:
        module.fail_json(
            msg=f"RADKit HTTP operation failed: {str(e)}", error_type=type(e).__name__
        )
    except Exception as e:
        module.fail_json(msg=f"Unexpected error: {str(e)}", error_type=type(e).__name__)


def _validate_http_parameters(module: AnsibleModule) -> None:
    """
    Validate HTTP-specific module parameters.

    Args:
        module: Ansible module instance

    Raises:
        AnsibleFailJson: If parameter validation fails
    """
    params = module.params

    # Validate path format
    if not params["path"].startswith("/"):
        module.fail_json(msg="Path must start with '/'")

    # Validate status codes
    for code in params["status_code"]:
        if not (100 <= code <= 599):
            module.fail_json(msg=f"Invalid HTTP status code: {code}")

    # Validate method-specific constraints
    method = params["method"].upper()
    if method in ["GET", "HEAD", "DELETE"] and (
        params.get("content") or params.get("json") or params.get("data")
    ):
        module.fail_json(
            msg=f"HTTP {method} requests cannot include request body (content, json, or data)"
        )


if __name__ == "__main__":
    main()
