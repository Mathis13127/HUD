"""Public API Client for interacting with the background HUD Daemon."""

import socket
import json
from typing import Any

from hud.errors import HudError


class DaemonConnectionError(HudError):
    """Raised when the client cannot connect to the HUD Daemon."""
    def __init__(self, reason: str) -> None:
        super().__init__(
            code="hud.api.daemon_connection",
            message=f"Could not connect to HUD Daemon: {reason}"
        )


class HudDaemonClient:
    """Synchronous Python client for interacting with the JARVIS HUD Engine.
    Maintains a persistent connection to automatically clean up injected widgets on exit.
    """

    def __init__(self, host: str = "127.0.0.1", port: int = 48321) -> None:
        self.host = host
        self.port = port
        self._sock: socket.socket | None = None
        self._connect()

    def _connect(self) -> None:
        if self._sock is not None:
            return
            
        try:
            self._sock = socket.create_connection((self.host, self.port), timeout=2.0)
        except ConnectionRefusedError:
            raise DaemonConnectionError("Connection refused. Is the HUD Daemon running?")
        except socket.timeout:
            raise DaemonConnectionError("Connection timed out.")
        except Exception as e:
            raise DaemonConnectionError(str(e))

    def close(self) -> None:
        """Close the connection to the daemon. Registered widgets will be auto-cleaned."""
        if self._sock:
            self._sock.close()
            self._sock = None

    def _send_command(self, payload: dict) -> dict:
        """Internal method to send JSON over TCP to the Daemon and await response."""
        self._connect()
        assert self._sock is not None
        
        try:
            message = json.dumps(payload) + "\n"
            self._sock.sendall(message.encode("utf-8"))
            
            response_data = b""
            while True:
                chunk = self._sock.recv(4096)
                if not chunk:
                    self.close()
                    raise DaemonConnectionError("Connection closed by server.")
                response_data += chunk
                if b"\n" in chunk:
                    break
                    
            response = json.loads(response_data.decode("utf-8").strip())
            if response.get("status") == "error":
                raise HudError(code="hud.api.daemon_error", message=response.get("reason", "Unknown error"))
                
            return response
            
        except Exception as e:
            self.close()
            if isinstance(e, HudError):
                raise
            raise DaemonConnectionError(str(e))

    def register_widget_from_code(self, source_code: str) -> str:
        """Register a widget in the Daemon directly from raw Python code (In-Memory).
        
        Args:
            source_code: The raw string of Python code containing MANIFEST and Widget class.
            
        Returns:
            The loaded bundle_id.
        """
        res = self._send_command({"action": "register_code", "code": source_code})
        return res["bundle_id"]

    def mount_widget(self, bundle_id: str) -> None:
        """Display a registered widget on the overlay."""
        self._send_command({"action": "mount", "bundle_id": bundle_id})

    def unmount_widget(self, bundle_id: str) -> None:
        """Unmount a widget from the HUD screen."""
        self._send_command({"action": "unmount", "bundle_id": bundle_id})

    def unregister_widget(self, bundle_id: str) -> None:
        """Completely unregister and remove a widget from Daemon memory."""
        self._send_command({"action": "unregister", "bundle_id": bundle_id})

    def get_widget_code(self, bundle_id: str) -> str:
        """Retrieve the original source code injected for this widget."""
        response = self._send_command({"action": "get_code", "bundle_id": bundle_id})
        return response.get("code", "")

    def get_registered_widgets(self) -> list[str]:
        """List all widgets loaded in memory."""
        res = self._send_command({"action": "get_registered"})
        return res.get("widgets", [])

    def get_mounted_widgets(self) -> list[str]:
        """List all widgets currently visible on screen."""
        res = self._send_command({"action": "get_mounted"})
        return res.get("widgets", [])

    def send_event(self, event_name: str, payload: dict[str, Any]) -> None:
        """Broadcast an event onto the HUD Event Bus."""
        self._send_command({
            "action": "send_event",
            "event_name": event_name,
            "payload": payload
        })
