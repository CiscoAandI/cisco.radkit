"""
RADKit connection context management for Ansible connection plugins.
"""

import threading
import time
import base64
import weakref
import atexit
from contextlib import ExitStack
from concurrent.futures import ThreadPoolExecutor, TimeoutError
from typing import Dict, Any, Optional
from ansible.errors import AnsibleConnectionFailure, AnsibleError
from ansible.utils.display import Display

display = Display()

try:
    import radkit_client
    from radkit_client.sync import Client

    HAS_RADKIT = True
except ImportError:
    HAS_RADKIT = False


class RadkitConnectionRegistry:
    """
    Singleton registry for managing RADKit connections across the application.
    Uses weak references for automatic cleanup and configurable timeouts.
    """

    _instance = None
    _lock = threading.RLock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        self._connections: Dict[str, Dict[str, Any]] = {}
        self._cleanup_thread = None
        self._stop_event = threading.Event()
        self._start_cleanup_thread()
        atexit.register(self.cleanup_all)

    def _start_cleanup_thread(self):
        """Start background thread for cleaning up stale connections."""

        def cleanup_worker():
            while not self._stop_event.wait(300):  # Check every 5 minutes
                self._cleanup_stale_connections()

        self._cleanup_thread = threading.Thread(target=cleanup_worker, daemon=True)
        self._cleanup_thread.start()

    def _cleanup_stale_connections(self):
        """Remove connections that haven't been used recently."""
        current_time = time.time()
        to_remove = []

        with self._lock:
            for key, conn_info in self._connections.items():
                # Check if connection is still referenced
                if conn_info["weak_ref"]() is None:
                    to_remove.append(key)
                    continue

                # Check if connection has exceeded its timeout
                timeout = conn_info.get("timeout", 3600)
                if current_time - conn_info["last_used"] > timeout:
                    to_remove.append(key)

            for key in to_remove:
                self._remove_connection(key)

    def register_connection(
        self, key: str, context: "RadkitClientContext", timeout: int = 3600
    ):
        """Register a connection context with automatic cleanup."""
        with self._lock:
            # Remove old connection if it exists
            if key in self._connections:
                self._remove_connection(key)

            # Create weak reference with cleanup callback
            def cleanup_callback(ref):
                with self._lock:
                    if key in self._connections:
                        self._remove_connection(key)

            weak_ref = weakref.ref(context, cleanup_callback)

            self._connections[key] = {
                "weak_ref": weak_ref,
                "last_used": time.time(),
                "timeout": timeout,
                "cleanup_timer": None,
            }

            # Set up individual timer for this connection
            self._reset_connection_timer(key)

    def update_last_used(self, key: str):
        """Update the last used timestamp for a connection."""
        with self._lock:
            if key in self._connections:
                self._connections[key]["last_used"] = time.time()
                self._reset_connection_timer(key)

    def _reset_connection_timer(self, key: str):
        """Reset the cleanup timer for a specific connection."""
        if key not in self._connections:
            return

        conn_info = self._connections[key]

        # Cancel existing timer
        if conn_info["cleanup_timer"]:
            conn_info["cleanup_timer"].cancel()

        # Create new timer
        timeout = conn_info["timeout"]
        timer = threading.Timer(timeout, lambda: self._cleanup_connection_by_timer(key))
        timer.daemon = True
        timer.start()

        conn_info["cleanup_timer"] = timer

    def _cleanup_connection_by_timer(self, key: str):
        """Clean up a connection when its timer expires."""
        with self._lock:
            if key in self._connections:
                context = self._connections[key]["weak_ref"]()
                if context:
                    # Only cleanup if it hasn't been used recently
                    current_time = time.time()
                    last_used = self._connections[key]["last_used"]
                    timeout = self._connections[key]["timeout"]

                    if current_time - last_used >= timeout:
                        context._force_cleanup()
                        self._remove_connection(key)

    def _remove_connection(self, key: str):
        """Remove a connection from the registry."""
        if key in self._connections:
            conn_info = self._connections[key]
            if conn_info["cleanup_timer"]:
                conn_info["cleanup_timer"].cancel()
            del self._connections[key]

    def cleanup_all(self):
        """Clean up all connections."""
        self._stop_event.set()

        with self._lock:
            # Cancel all timers and clean up contexts
            for key in list(self._connections.keys()):
                conn_info = self._connections[key]
                if conn_info["cleanup_timer"]:
                    conn_info["cleanup_timer"].cancel()

                context = conn_info["weak_ref"]()
                if context:
                    context._force_cleanup()

            self._connections.clear()


class RadkitClientContext:
    """
    RADKit client context with proper lifecycle management.
    """

    def __init__(self, connection_obj, timeout: Optional[int] = None):
        self.obj = connection_obj
        
        # Get timeout from configuration or use default
        if timeout is None:
            # Try to get from connection options, default to 1 hour instead of 4 hours
            timeout = getattr(connection_obj, "radkit_connection_timeout", None)
            if timeout is None:
                try:
                    timeout = connection_obj.get_option("radkit_connection_timeout", 3600)
                except (AttributeError, KeyError):
                    timeout = 3600

        # Get login timeout
        login_timeout = getattr(connection_obj, "radkit_login_timeout", None)
        if login_timeout is None:
            try:
                login_timeout = connection_obj.get_option("radkit_login_timeout", 60)
            except (AttributeError, KeyError):
                login_timeout = 60
        
        self.timeout = timeout or 3600
        self.login_timeout = login_timeout or 60

        self.stack = None
        self.client = None
        self._lock = threading.RLock()
        self._cleanup_done = False

        # Set initial state for compatibility
        self.obj.radkit_client_created = False
        self.obj.radkit_client_exception = False
        self.obj.radkit_client_exception_msg = ""

        # Create unique key for this connection
        self.connection_key = self._create_connection_key()

        # Register with the global registry
        registry = RadkitConnectionRegistry()
        registry.register_connection(self.connection_key, self, self.timeout)

    def _create_connection_key(self) -> str:
        """Create a unique key for this connection."""
        identity = self.obj.get_option("radkit_identity", "")
        service_serial = self.obj.get_option("radkit_service_serial", "")
        device_filter = getattr(self.obj, "device_filter", "")
        return f"{identity}|{service_serial}|{device_filter}"

    def initialize(self):
        """Initialize the RADKit client connection."""
        with self._lock:
            if self._cleanup_done:
                raise AnsibleConnectionFailure("Connection context has been cleaned up")

            try:
                # Add debugging information
                display.vvv("RADKit context: Starting client creation")
                self._create_client()
                
                display.vvv("RADKit context: Starting certificate login")
                self._perform_login()

                # Set success flags
                self.obj.radkit_client = self.client
                self.obj.radkit_client_created = True
                self.obj.radkit_client_exception = False
                
                display.vvv("RADKit context: Initialization successful")

                # Update last used time
                registry = RadkitConnectionRegistry()
                registry.update_last_used(self.connection_key)

            except Exception as ex:
                display.vvv(f"RADKit context: Exception during initialization: {type(ex).__name__}: {ex}")
                self._handle_error(ex)
                raise

    def _create_client(self):
        """Create the RADKit client."""
        try:
            if not HAS_RADKIT:
                raise AnsibleError(
                    "RADkit python library missing. Please install client. "
                    "For help go to https://radkit.cisco.com"
                )

            self.stack = ExitStack()
            self.client = self.stack.enter_context(Client.create())

        except Exception as ex:
            if self.stack:
                self.stack.close()
                self.stack = None
            raise AnsibleConnectionFailure(f"Failed to create RADKit client: {ex}")

    def _perform_login(self):
        """Perform certificate login with timeout and retry logic."""
        # Validate required configuration parameters
        identity = self.obj.get_option("radkit_identity")
        service_serial = self.obj.get_option("radkit_service_serial")
        password_b64 = self.obj.get_option("radkit_client_private_key_password_base64")
        
        if not identity:
            raise AnsibleConnectionFailure(
                "RADKit identity not configured. Set RADKIT_ANSIBLE_IDENTITY or radkit_identity variable."
            )
        
        if not service_serial:
            raise AnsibleConnectionFailure(
                "RADKit service serial not configured. Set RADKIT_ANSIBLE_SERVICE_SERIAL or radkit_service_serial variable."
            )
            
        if not password_b64:
            raise AnsibleConnectionFailure(
                "RADKit client private key password not configured. Set RADKIT_ANSIBLE_CLIENT_PRIVATE_KEY_PASSWORD_BASE64."
            )
        
        try:
            # Decode the password
            private_key_password = base64.b64decode(password_b64).decode("utf8")
        except Exception as ex:
            raise AnsibleConnectionFailure(
                f"Error decoding radkit_client_private_key_password_base64: {ex}. "
                f"Ensure the value is proper base64 encoded."
            )

        def certificate_login():
            return self.client.certificate_login(
                identity=self.obj.get_option("radkit_identity"),
                ca_path=self.obj.get_option("radkit_client_ca_path"),
                key_path=self.obj.get_option("radkit_client_key_path"),
                cert_path=self.obj.get_option("radkit_client_cert_path"),
                private_key_password=private_key_password,
            )

        # Attempt login with timeout
        max_retries = 3
        for attempt in range(max_retries):
            try:
                with ThreadPoolExecutor(max_workers=1) as executor:
                    future = executor.submit(certificate_login)
                    future.result(timeout=self.login_timeout)
                return  # Success

            except TimeoutError:
                error_msg = (
                    f"Certificate login timed out (attempt {attempt + 1}/{max_retries})"
                )
                if attempt == max_retries - 1:
                    raise AnsibleConnectionFailure(error_msg)
                else:
                    time.sleep(2**attempt)  # Exponential backoff

            except Exception as ex:
                error_str = str(ex).lower()
                if attempt == max_retries - 1:
                    # Provide specific guidance based on error type
                    if "certificate" in error_str or "cert" in error_str:
                        detailed_msg = (
                            f"Certificate login failed: {ex}. "
                            f"Please verify certificate paths and permissions. "
                            f"Identity: {identity}"
                        )
                    elif "password" in error_str or "private key" in error_str:
                        detailed_msg = (
                            f"Private key password authentication failed: {ex}. "
                            f"Please check RADKIT_ANSIBLE_CLIENT_PRIVATE_KEY_PASSWORD_BASE64 is correct."
                        )
                    elif "service" in error_str or "serial" in error_str:
                        detailed_msg = (
                            f"Service connection failed: {ex}. "
                            f"Please verify service serial: {service_serial}"
                        )
                    elif "network" in error_str or "connection" in error_str:
                        detailed_msg = (
                            f"Network connection failed: {ex}. "
                            f"Please check internet connectivity to RADKit cloud services."
                        )
                    else:
                        detailed_msg = f"Certificate login failed: {ex}"
                    
                    raise AnsibleConnectionFailure(detailed_msg)
                else:
                    time.sleep(2**attempt)  # Exponential backoff

    def _handle_error(self, ex: Exception):
        """Handle errors and set appropriate flags on the connection object."""
        self.obj.radkit_client_exception = True
        
        # Provide more detailed error message
        error_msg = str(ex) if str(ex).strip() else f"Unknown {type(ex).__name__} error occurred"
        
        # Add more context for common error types
        if isinstance(ex, AnsibleConnectionFailure):
            error_msg = f"Connection failed: {error_msg}"
        elif isinstance(ex, TimeoutError):
            error_msg = f"Timeout after {self.login_timeout} seconds: {error_msg}"
        elif "certificate" in str(ex).lower() or "authentication" in str(ex).lower():
            error_msg = f"Authentication failed: {error_msg}"
        elif "service" in str(ex).lower() or "serial" in str(ex).lower():
            error_msg = f"Service connection failed: {error_msg}"
        
        self.obj.radkit_client_exception_msg = error_msg

        # Clean up on error
        self._force_cleanup()

    def update_usage(self):
        """Update the last used timestamp for this connection."""
        if not self._cleanup_done:
            registry = RadkitConnectionRegistry()
            registry.update_last_used(self.connection_key)

    def _force_cleanup(self):
        """Force cleanup of resources."""
        with self._lock:
            if self._cleanup_done:
                return

            self._cleanup_done = True

            if self.stack:
                try:
                    self.stack.close()
                except Exception:
                    pass  # Ignore cleanup errors
                finally:
                    self.stack = None

            self.client = None

    def __del__(self):
        """Ensure cleanup on deletion."""
        self._force_cleanup()

    def run(self):
        """
        Main method that replaces the threading approach with direct initialization.
        This maintains compatibility with the existing interface.
        """
        try:
            self.initialize()
        except Exception:
            # Errors are already handled in initialize()
            pass

    def start(self):
        """
        Compatibility method - just calls run() directly since we don't need threading.
        """
        self.run()

    def close(self):
        """
        Public method to force cleanup (maintains original interface).
        """
        self._force_cleanup()


def configure_radkit_context(
    connection_obj, config: Optional[Dict[str, Any]] = None
) -> RadkitClientContext:
    """
    Helper function to create and configure a RadkitClientContext with best practices.

    Args:
        connection_obj: The Ansible connection object
        config: Optional configuration dictionary

    Returns:
        Configured RadkitClientContext
    """
    config = config or {}

    # Set reasonable defaults
    timeout = config.get("connection_timeout", 3600)  # 1 hour default
    login_timeout = config.get("login_timeout", 60)  # 1 minute default

    context = RadkitClientContext(connection_obj, timeout=timeout)

    # Optional: Add configuration options to the connection object
    connection_obj.radkit_connection_timeout = timeout
    connection_obj.radkit_login_timeout = login_timeout

    return context
