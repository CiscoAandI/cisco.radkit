# RadKit Module Enhancements

## Overview

Based on the comprehensive RadKit API documentation, I have enhanced both the `swagger` and `http` modules to include missing functionality that was available in the RadKit client but not exposed through the Ansible modules.

## Enhanced Features

### Swagger Module Enhancements

#### New Parameters Added:
1. **`params`** - URL query parameters (alternative to `parameters` for consistency with HTTP module)
2. **`headers`** - Custom HTTP headers for requests
3. **`cookies`** - Cookie values to include in requests
4. **`content`** - Raw request body content as string/bytes
5. **`data`** - Form-encoded data for request body
6. **`files`** - File upload support for multipart form data
7. **`timeout`** - Request timeout in seconds

#### Enhanced Response Processing:
- **`headers`** - HTTP response headers
- **`cookies`** - HTTP response cookies
- **`content_type`** - Response Content-Type header
- **`url`** - Complete requested URL
- **`method`** - HTTP method used

#### Parameter Validation:
- Added mutually exclusive parameter validation:
  - `content`, `json`, and `data` are mutually exclusive
  - `parameters` and `params` are mutually exclusive (use one or the other)

#### Enhanced Examples:
- Path parameter usage with proper dictionary format
- File upload scenarios
- Query parameter usage
- Header and cookie handling
- Raw content submission

### HTTP Module Enhancements

#### New Parameters Added:
1. **`data`** - Form-encoded data for request body
2. **`files`** - File upload support for multipart form data  
3. **`timeout`** - Request timeout in seconds

#### Enhanced Parameter Validation:
- Updated mutually exclusive validation to include `data`
- Enhanced method-specific validation for body parameters

#### Enhanced Examples:
- Form data submission scenarios
- File upload with multipart form data
- Timeout configuration examples

## Key Benefits

### 1. **Complete RadKit API Coverage**
Both modules now expose the full breadth of the RadKit Swagger and HTTP APIs, including:
- All supported HTTP request body types (`json`, `content`, `data`, `files`)
- Complete header and cookie management
- Timeout control for long-running operations
- File upload capabilities

### 2. **Enhanced Response Information**
Response processing now includes:
- Full HTTP headers and cookies
- Content-Type information
- Complete URL information
- Consistent response formatting across both modules

### 3. **Better Parameter Flexibility**
- Support for both `parameters` and `params` in swagger module for consistency
- Proper mutual exclusion of conflicting parameters
- Enhanced validation with helpful error messages

### 4. **Real-World Use Cases**
The enhanced modules now support:
- **File Uploads**: Firmware uploads, configuration file transfers
- **Form Submissions**: Login forms, configuration submissions  
- **API Authentication**: Token-based auth, session cookies
- **Long Operations**: Configurable timeouts for slow operations
- **Content Flexibility**: JSON, form data, raw content, and file uploads

### 5. **Consistent API Design**
Both modules now follow similar parameter patterns and validation rules, making them easier to use together in playbooks.

## Usage Examples

### Swagger Module Advanced Usage

```yaml
# File upload with metadata
- name: Upload configuration file
  cisco.radkit.swagger:
    device_name: device1
    path: /config/upload
    method: post
    files:
      config: "{{ config_file_path }}"
    data:
      description: "Production configuration"
      version: "2.1.0"
    headers:
      Authorization: "Bearer {{ auth_token }}"
    timeout: 120.0
  register: upload_result

# Query parameters with authentication
- name: Get filtered logs
  cisco.radkit.swagger:
    device_name: device1
    path: /logs
    method: get
    params:
      level: error
      since: "2024-01-01"
      limit: 100
    cookies:
      sessionid: "{{ session_id }}"
    timeout: 30.0
  register: log_data
```

### HTTP Module Advanced Usage

```yaml
# Form-based login
- name: Authenticate via form
  cisco.radkit.http:
    device_name: web-interface
    path: /login
    method: POST
    data:
      username: "{{ vault_username }}"
      password: "{{ vault_password }}"
      remember: true
    timeout: 10.0
  register: login_response

# Firmware upload
- name: Upload device firmware
  cisco.radkit.http:
    device_name: network-device
    path: /api/firmware/upload
    method: POST
    files:
      firmware: "/path/to/firmware.bin"
    data:
      version: "{{ firmware_version }}"
      reboot_after: false
    timeout: 600.0
  register: firmware_upload
```

## Backward Compatibility

All enhancements maintain full backward compatibility:
- Existing parameters work exactly as before
- Existing playbooks require no changes
- Default behaviors are preserved
- Error messages are enhanced but maintain the same trigger conditions

## Technical Implementation

### Parameter Processing
- Enhanced parameter preparation functions to handle new data types
- Improved response processing with comprehensive field extraction
- Better error handling and validation

### Type Safety
- Proper handling of optional parameters with None value filtering
- Consistent type conversion and validation
- Enhanced documentation with clear parameter descriptions

### Error Handling
- More specific error messages for parameter conflicts
- Better validation of parameter combinations
- Improved debugging information in responses

This enhancement brings the Ansible modules to feature parity with the underlying RadKit client library, enabling users to take full advantage of the RadKit platform's capabilities through Ansible automation.
