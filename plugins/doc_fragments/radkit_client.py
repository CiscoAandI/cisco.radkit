class ModuleDocFragment(object):
    DOCUMENTATION = """
options:
  identity:
    description:
    - Identity to authentiate with RADKit (xxxx@cisco.com).
        If the value is not specified in the task, the value of environment variable RADKIT_ANSIBLE_IDENTITY will be used instead.
    type: str
    required: True
    aliases: ['radkit_identity']
  client_key_password_b64:
    description:
    - Client certificate password in base64
        If the value is not specified in the task, the value of environment variable RADKIT_ANSIBLE_CLIENT_PRIVATE_KEY_PASSWORD_BASE64 will be used instead.
    type: str
    aliases: ['radkit_client_private_key_password_base64']
    required: True
  service_serial:
    description:
    - Radkit service serial
      If the value is not specified in the task, the value of environment variable RADKIT_ANSIBLE_SERVICE_SERIAL will be used instead.
    type: str
    aliases: ['radkit_serial', 'radkit_service_serial']
    required: True
  client_key_path:
    description:
    - Alternate path to client key for RADKIT
      If the value is not specified in the task, the value of environment variable RADKIT_ANSIBLE_CLIENT_KEY_PATH will be used instead.
    type: str
    required: False
  client_cert_path:
    description:
    - Alternate path to client cert for RADKIT
      If the value is not specified in the task, the value of environment variable RADKIT_ANSIBLE_CLIENT_CERT_PATH will be used instead.
    type: str
    required: False
  client_ca_path:
    description:
    - Alternate path to client ca cert for RADKIT
      If the value is not specified in the task, the value of environment variable RADKIT_ANSIBLE_CLIENT_CA_PATH will be used instead.
    type: str
    required: False
"""
