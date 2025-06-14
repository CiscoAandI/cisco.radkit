# exec_and_wait Module Enhancements

## Summary of Enhancements

The `exec_and_wait` module has been enhanced with several key improvements for better reliability, debugging, and multi-device support.

## New Features

### 1. Command Retry Logic
- **Parameter**: `command_retries` (default: 1)
- **Description**: Automatically retries command execution if pexpect sessions fail
- **Usage**: Set to higher values for unreliable network conditions

### 2. Custom Recovery Test Commands
- **Parameter**: `recovery_test_command` (default: "show clock")
- **Description**: Customize the command used to test device responsiveness after operations
- **Usage**: Use device-specific commands that reliably indicate the device is operational

### 3. Enhanced Error Handling
- **Parameter**: `continue_on_device_failure` (default: false)
- **Description**: Continue processing other devices even if one device fails
- **Usage**: Useful for bulk operations across multiple devices

### 4. Progress Monitoring
- **Feature**: Automatic progress logging every 30 seconds during device recovery
- **Benefit**: Better visibility into long-running operations like device reloads

### 5. Multi-Device Results Structure
- **New Return Fields**:
  - `devices`: Individual results for each device
  - `summary`: Overall statistics (total, successful, failed devices)
  - `recovery_time`: Time taken for device recovery
  - `attempt_count`: Number of recovery attempts

### 6. Better UTF-8 Handling
- **Enhancement**: Improved handling of device output with UTF-8 decode error replacement
- **Benefit**: More robust handling of devices with non-standard character output

## Updated Documentation

### New Parameters

```yaml
command_retries:
  description: Maximum number of retries for command execution failures
  type: int
  default: 1

recovery_test_command:
  description: Custom command to test device responsiveness during recovery
  type: str
  default: "show clock"

continue_on_device_failure:
  description: Continue processing other devices if one device fails
  type: bool
  default: false
```

### Enhanced Return Values

```yaml
devices:
  description: Results for each device processed
  type: dict
  contains:
    device_name: str
    executed_commands: list
    stdout: str
    status: str (SUCCESS/FAILED)
    recovery_time: float
    attempt_count: int

summary:
  description: Summary of execution across all devices
  type: dict
  contains:
    total_devices: int
    successful_devices: int
    failed_devices: int
```

## Example Usage

### Basic Enhancement Usage
```yaml
- name: Execute commands with retry logic
  cisco.radkit.exec_and_wait:
    device_name: "{{ inventory_hostname }}"
    commands:
      - "show version"
    prompts: []
    answers: []
    seconds_to_wait: 30
    command_retries: 3
    recovery_test_command: "show clock"
```

### Multi-Device with Error Handling
```yaml
- name: Execute on multiple devices with error tolerance
  cisco.radkit.exec_and_wait:
    device_name: "{{ item }}"
    commands:
      - "show ip interface brief"
    prompts: []
    answers: []
    seconds_to_wait: 30
    continue_on_device_failure: true
  loop: "{{ device_list }}"
```

## Integration Test

An enhanced integration test has been created that focuses on:

1. **Command Execution Testing**: Tests that commands are executed (not network success)
2. **Non-Intrusive Operations**: Uses safe commands like `ping` and `show clock`
3. **Enhanced Parameter Testing**: Validates new retry and recovery features
4. **Error Handling**: Tests proper error reporting for invalid devices

### Running the Test

```bash
cd /path/to/cisco.radkit
ansible-playbook test_exec_and_wait_enhanced.yml
```

## Backward Compatibility

All enhancements are backward compatible:
- Existing playbooks will continue to work unchanged
- New parameters have sensible defaults
- Return structure includes original fields for single-device compatibility

## Benefits

1. **Improved Reliability**: Retry logic and better error handling
2. **Better Observability**: Progress logging and detailed return information
3. **Multi-Device Support**: Structured results for bulk operations
4. **Debugging**: Enhanced logging and session capture capabilities
5. **Robustness**: Better handling of edge cases and character encoding issues

The enhanced module provides a solid foundation for production network automation while maintaining the simplicity of the original interface.
