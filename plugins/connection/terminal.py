# (c) 2012, Michael DeHaan <michael.dehaan@gmail.com>
# (c) 2017 Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = """
    author:
    - Ansible Core Team
    - Scott Dozier (@scdozier)
    name: terminal
    short_description: "DEPRECATED: Use port_forward module for Linux servers instead"
    description:
        - "🚨 DEPRECATED as of v2.0.0: This connection plugin is deprecated."
        - "Use port_forward module for Linux servers instead of this terminal connection."
        - "Port forwarding provides better file transfer support (SCP/SFTP) required by most Ansible modules."
        - "For network devices, use ssh_proxy module with ansible.netcommon.network_cli connection."
        - Uses RADKit to connect to devices over SSH.  Works with LINUX platforms.
    deprecated:
      why: "Replaced by port_forward module for better file transfer support"
      version: "2.0.0"
      alternative: "Use port_forward module for Linux servers"
    version_added: "0.1.0"
    options:
      device_name:
        description:
            - Device name of the remote target. This must match the device name on RADKit (not host field)
        vars:
            - name: inventory_hostname
      device_addr:
        description:
            - Hostname/Address of the remote target. This must match the host on RADKit.
            - This option will be used when ansible_host or ansible_ssh_host is specified
        vars:
            - name: ansible_host
            - name: ansible_ssh_host
      radkit_service_serial:
        description:
            - The serial of the RADKit service you wish to connect through
        vars:
            - name: radkit_service_serial
        env:
          - name: RADKIT_ANSIBLE_SERVICE_SERIAL
        required: True
      radkit_identity:
        description:
            - The Client ID (owner email address) present in the RADKit client certificate.
        vars:
            - name: radkit_identity
        env:
          - name: RADKIT_ANSIBLE_IDENTITY
        required: True
      radkit_client_private_key_password_base64:
        description:
            - The private key password in base64 for radkit client
        vars:
            - name: radkit_client_private_key_password_base64
        env:
          - name: RADKIT_ANSIBLE_CLIENT_PRIVATE_KEY_PASSWORD_BASE64
        required: True
      radkit_client_ca_path:
        description:
            - The path to the issuer chain for the identity certificate
        vars:
            - name: radkit_client_ca_path
        env:
          - name: RADKIT_ANSIBLE_CLIENT_CA_PATH
        required: False
      radkit_client_cert_path:
        description:
            - The path to the identity certificate
        vars:
            - name: radkit_client_cert_path
        env:
          - name: RADKIT_ANSIBLE_CLIENT_CERT_PATH
        required: False
      radkit_client_key_path:
        description:
            - The path to the private key for the identity certificate
        vars:
            - name: radkit_client_key_path
        env:
          - name: RADKIT_ANSIBLE_CLIENT_KEY_PATH
        required: False
      radkit_wait_timeout:
        description:
            - Specifies how many seconds RADKit will wait before failing task.
            - Note that the request is not affected, and it will still eventually complete (successfully or unsuccessfully)
        vars:
            - name: radkit_wait_timeout
        env:
          - name: RADKIT_ANSIBLE_WAIT_TIMEOUT
        required: False
        default: 0
        type: int
      radkit_exec_timeout:
        description:
            - Specifies how many seconds RADKit will for wait command to complete
        vars:
            - name: radkit_exec_timeout
        env:
          - name: RADKIT_ANSIBLE_EXEC_TIMEOUT
        required: False
        default: 3600
        type: int
      radkit_connection_timeout:
        description:
            - Timeout in seconds for RADKit connection lifecycle
            - Connection will be automatically cleaned up after this period of inactivity
        vars:
            - name: radkit_connection_timeout
        env:
          - name: RADKIT_CONNECTION_TIMEOUT
        required: False
        default: 3600
        type: int
      radkit_login_timeout:
        description:
            - Timeout in seconds for RADKit certificate login
        vars:
            - name: radkit_login_timeout  
        env:
          - name: RADKIT_LOGIN_TIMEOUT
        required: False
        default: 60
        type: int
"""
EXAMPLES = """
- hosts: all
  connection: cisco.radkit.terminal
  vars:
    ansible_remote_tmp: /tmp/.ansible/tmp
    ansible_async_dir: /tmp/.ansible_async
    radkit_service_serial: xxxx-xxxx-xxxx
    radkit_identity: user@cisco.com
  become: yes
  tasks:
    - name: Restart sshd
      ansible.builtin.service:
        name: sshd
        state: restarted

"""
import os
import base64
import time
import random
import asyncio
import threading
import traceback
from contextlib import ExitStack
from anyio import BrokenResourceError

try:
    import radkit_client
    from radkit_client.sync import Client

    HAS_RADKIT = True
except ImportError:
    HAS_RADKIT = False
    radkit_client = None
    Client = None
from ansible.errors import (
    AnsibleConnectionFailure,
    AnsibleError,
    AnsibleFileNotFound,
)
from ansible.plugins.connection import ConnectionBase
from ansible.utils.display import Display
from ansible.module_utils._text import to_bytes, to_text
from concurrent.futures import ThreadPoolExecutor, TimeoutError
from ansible_collections.cisco.radkit.plugins.module_utils.client import (
    check_if_radkit_version_supported,
)

display = Display()

# keep connection objects on a per host basis to avoid repeated attempts to reconnect
RADKIT_ANSIBLE_CONNECTION_CACHE = {}  # type: dict[str, radkit_client.device.Device]
RADKIT_ANSIBLE_SESSION_CACHE = (
    {}
)  # type: dict[str, radkit_client.InteractiveConnection]


# Import the professional RADKit context
from .radkit_context import RadkitClientContext, configure_radkit_context


class Connection(ConnectionBase):
    """CLI (shell) SSH connections via RADKit"""

    radkit_client_created = False
    radkit_client_exception = False
    transport = "radkit-terminal"
    _log_channel = None
    ssh = None
    _session = None

    def _set_log_channel(self, name):
        self._log_channel = name

    def _cache_key(self):
        return "%s__%s__" % (self.device_filter, self._play_context.remote_user)

    async def session(self):
        """Gets or opens terminal session to device

        :return: session
        """
        cache_key = self._cache_key()
        if cache_key in RADKIT_ANSIBLE_SESSION_CACHE:
            self._session = RADKIT_ANSIBLE_SESSION_CACHE[cache_key]
        else:
            if not self._connected:
                self._connect()
            self._session = RADKIT_ANSIBLE_SESSION_CACHE[
                cache_key
            ] = self.device.terminal().wait()
        if hasattr(self._session, "_lock"):
            while self._session._lock.lock.locked():
                await asyncio.sleep(0.3)
        self._session.wait()
        return self._session

    async def write_async(self, data):
        """Writes data to session"""
        session = await self.session()
        successful = False
        retries = 10
        # Retry getting lock write to session up to 10 times
        while not successful and retries > 0:
            try:
                session.wait()
                session.write(data)
                successful = True
            except RuntimeError:
                await asyncio.sleep(1)
                retries = retries - 1
                continue
        # need a slight delay before returning to prevent read issues with flood of commands
        await asyncio.sleep(0.4)

    async def read_async(self, buffer_timeout=1):
        """Reads data from session

        :return: bytes read from terminal session
        :rtype: bytes
        """
        session = await self.session()
        # send carriage return so prompt is shown
        try:
            session.write(b"\r\n")
        except BrokenResourceError as ex:
            # Handle issue where session is broken on reload, continue to read which will be a diff exception
            pass
        try:
            data = session.readuntil_timeout(timeout=buffer_timeout)
        except (ValueError, TimeoutError, asyncio.exceptions.TimeoutError):
            data = b""
        return data

    def read(self, buffer_timeout=1):
        return asyncio.run(self.read_async(buffer_timeout=buffer_timeout))

    def write(self, data):
        return asyncio.run(self.write_async(data))

    def _connect(self):
        # check radkit version
        check_if_radkit_version_supported()
        # choose whether to filter by host or name in radkit inventory
        if self.get_option("device_addr"):
            if self.get_option("device_addr") != self.get_option("device_name"):
                self.device_filter = self.get_option("device_addr")
                self.radkit_filter_inv_by_host = True
            else:
                self.device_filter = self.get_option("device_name")
                self.radkit_filter_inv_by_host = False
        else:
            self.device_filter = self.get_option("device_name")
            self.radkit_filter_inv_by_host = False
        cache_key = self._cache_key()
        if cache_key in RADKIT_ANSIBLE_CONNECTION_CACHE:
            self.device = RADKIT_ANSIBLE_CONNECTION_CACHE[cache_key]
            display.vvv("USING CACHED RADKIT CONNECTION")
        else:
            self.device = RADKIT_ANSIBLE_CONNECTION_CACHE[
                cache_key
            ] = self._connect_uncached()
        self._connected = True
        display.vvv("RADKIT CLOUD CONNECTED")
        return self

    def _connect_uncached(self):
        """Creates the radkit connection, creates the filter inventory and returns a RadkitDevice

        :return: RADKit device
        """
        if not HAS_RADKIT:
            raise AnsibleError(
                "RADKit python library missing. Please install client. "
                "For help go to https://radkit.cisco.com"
            )
        # sleep for a small bit of time to spread out connectionss
        time.sleep(round(random.uniform(0, 3), 1))
        display.vvv(
            "ESTABLISH RADKIT CONNECTION FOR USER: %s TO %s"
            % (self.get_option("radkit_identity"), self.device_filter),
            host=self.device_filter,
        )

        # Configure the professional RADKit context with configurable timeouts
        config = {
            "connection_timeout": self.get_option("radkit_connection_timeout", 3600),
            "login_timeout": self.get_option("radkit_login_timeout", 60),
        }

        self.radkit_client_context = configure_radkit_context(self, config)
        self.radkit_client_context.start()

        while not self.radkit_client_created:
            if self.radkit_client_exception:
                error_msg = self.radkit_client_exception_msg or "Unknown RADKit connection error occurred"
                raise AnsibleConnectionFailure(f"RADKIT failure: {error_msg}")
            time.sleep(0.5)
        display.vvv(
            f"RADKIT connection successful, connecting to service {self.get_option('radkit_service_serial')}"
        )
        device = None
        display.vvv("RADKIT CLIENT CREATED")
        try:
            service = self.radkit_client.service(
                self.get_option("radkit_service_serial")
            ).wait()
            display.vvv("RADKIT CLIENT SERVICE CONNECTED")

            if self.radkit_filter_inv_by_host:
                display.vvv(f"filtering by host {self.device_filter}")
                inventory = service.inventory.filter("host", self.device_filter)
            else:
                inventory = service.inventory.filter("name", self.device_filter)

            if inventory:
                for device in inventory.values():
                    if (
                        self.radkit_filter_inv_by_host
                        and self.device_filter == device.host
                    ):
                        device = inventory[device.name]
                    elif self.device_filter == device.name:
                        device = inventory[device.name]
            else:
                raise AnsibleConnectionFailure(
                    f"Device {self.device_filter} not in RADKit inventory!"
                )
            self.inventory = inventory
        except Exception as e:
            msg = to_text(e)
            self.close()
            raise AnsibleConnectionFailure(msg)

        return device

    def exec_command(self, cmd, in_data=None, sudoable=False, remove_prompts=True):
        """Runs a command on remote host via RADKit

        :returns: False, stdout, ''
        """
        if not self._connected:
            self._connect()
        display.vvv("EXEC COMMAND %s" % cmd)
        if in_data:
            raise AnsibleError(
                "Internal Error: this module does not support optimized module pipelining"
            )
        if int(self.get_option("radkit_wait_timeout")) == 0:
            response = self.device.exec(
                cmd, timeout=int(self.get_option("radkit_exec_timeout"))
            ).wait()
        else:
            response = self.device.exec(
                cmd, timeout=int(self.get_option("radkit_exec_timeout"))
            ).wait(int(self.get_option("radkit_wait_timeout")))
        display.vvv("RADKIT REQUEST STATUS:  %s" % response.status.value)
        if response.status.value == "SUCCESS":
            stdout = response.result.data
            # remove prompts
            if "\n" in stdout and remove_prompts:
                stdout = "".join(stdout.splitlines(keepends=True)[1:][:-1]).strip()
        else:
            raise AnsibleConnectionFailure(f"{response.result.status_message}")
        stderr = b""  # stderr not directly supported in radkit
        recv_exit_status = 0
        return (recv_exit_status, stdout, stderr)

    def get_prompt(self):
        """Gets the prompt of device

        :return: device prompt
        :rtype: string
        """
        if not self._connected:
            self._connect()
        response = self.device.exec("\n").wait()
        display.vvv("RADKIT REQUEST STATUS:  %s" % response.status)
        if response.status.value == "SUCCESS":
            stdout = response.result.data
            # remove prompts
            if "\n" in stdout:
                prompt = "".join(stdout.splitlines(keepends=True)[-1]).strip()
        else:
            raise AnsibleConnectionFailure(f"{response.result.status_message}")
        display.vvv("DEVICE PROMPT:  %s" % prompt)
        return prompt

    def put_file(self, in_path, out_path):
        """transfer a file from local to remote"""
        if not self._connected:
            self._connect()
        if not os.path.exists(to_bytes(in_path, errors="surrogate_or_strict")):
            raise AnsibleFileNotFound("file or module does not exist: %s" % in_path)

        input_file_size = os.path.getsize(in_path)
        display.vvv(
            "PUT %s TO %s" % (in_path, out_path),
            host=getattr(self, "device_filter", ""),
        )
        try:
            fwc = self.device.sftp_upload_from_file(
                local_path=in_path, remote_path=out_path
            ).wait()
            # HACK; I dont know why but the transfer cuts off with some Ansiball files, need to run again.
            if "AnsiballZ_" in out_path:
                while fwc.result.status.value != "TRANSFER_DONE":
                    time.sleep(0.5)
                actual_file_size = self.exec_command(
                    f"ls -l {out_path} " + "| awk '{print  $5}'"
                )[1]
                if int(actual_file_size) != int(input_file_size):
                    retry_transfer = True
                else:
                    retry_transfer = False

                while retry_transfer:
                    display.vvv(
                        f"RETRY PUSHING FILE AnsiballZ {actual_file_size} != {input_file_size}"
                    )
                    fwc = self.device.sftp_upload_from_file(
                        local_path=in_path, remote_path=out_path
                    ).wait()
                    while fwc.result.status.value != "TRANSFER_DONE":
                        time.sleep(0.5)
                    actual_file_size = self.exec_command(
                        f"ls -l {out_path} " + "| awk '{print  $5}'"
                    )[1]
                    if int(actual_file_size) != int(input_file_size):
                        retry_transfer = True
                    else:
                        retry_transfer = False
            else:
                # wait for first transfer to complete
                while fwc.result.status.value != "TRANSFER_DONE":
                    time.sleep(0.5)
                display.vvv("BYTES WRITTEN:  %s" % str(fwc.bytes_written))
                display.vvv("TRANSFER STATUS:  %s" % fwc.result.status.value)

        except Exception as e:
            msg = to_text(e)
            raise AnsibleConnectionFailure(msg)

    def fetch_file(self, in_path, out_path):
        """save a remote file to the specified path"""
        if not self._connected:
            self._connect()
        display.vvv(
            "FETCH %s TO %s" % (in_path, out_path),
            host=getattr(self, "device_filter", ""),
        )
        try:
            progress = self.device.sftp_download_to_file(
                remote_path=in_path, local_path=out_path
            ).wait()
            while progress.result.status.value != "TRANSFER_DONE":
                time.sleep(1)
        except Exception as e:
            msg = to_text(e)
            raise AnsibleConnectionFailure(msg)

    def reset(self):
        """
        Resets the connection by closing and reconnecting to RADKit
        """
        if not self._connected:
            return
        self.close()
        self._connect()

    def close(self):
        """terminate the connection"""

        cache_key = self._cache_key()
        display.vvv("CLOSING RADKIT CONNECTION")

        # Clean up the context properly with the new professional context
        if hasattr(self, "radkit_client_context") and self.radkit_client_context:
            self.radkit_client_context.close()

        RADKIT_ANSIBLE_CONNECTION_CACHE.pop(cache_key, None)
        if self._session:
            RADKIT_ANSIBLE_SESSION_CACHE.pop(cache_key, None)
            self._session.close()
        self._connected = False
