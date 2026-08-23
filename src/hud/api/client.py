"""Public API Client for interacting with the background HUD Daemon."""

import socket
import json
from pathlib import Path
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
    """Synchronous Python client for interacting with the JARVIS HUD Engine."""

    def __init__(self, host: str = "127.0.0.1", port: int = 48321) -> None:
        self.host = host
        self.port = port

    def _send_command(self, payload: dict) -> dict:
        """Internal method to send JSON over TCP to the Daemon and await response."""
        try:
            with socket.create_connection((self.host, self.port), timeout=2.0) as sock:
                # Send
                message = json.dumps(payload) + "\n"
                sock.sendall(message.encode("utf-8"))
                
                # Receive
                # In a robust implementation we'd read until \n, but for local IPC a small buffer is usually enough
                response_data = b""
                while True:
                    chunk = sock.recv(4096)
                    response_data += chunk
                    if b"\n" in chunk or not chunk:
                        break
                        
                if not response_data:
                    raise DaemonConnectionError("Empty response from Daemon.")
                    
                response = json.loads(response_data.decode("utf-8").strip())
                if response.get("status") == "error":
                    raise HudError(code="hud.api.daemon_error", message=response.get("reason", "Unknown error"))
                    
                return response
                
        except ConnectionRefusedError:
            raise DaemonConnectionError("Connection refused. Is the HUD Daemon running?")
        except socket.timeout:
            raise DaemonConnectionError("Connection timed out.")
        except Exception as e:
            if isinstance(e, HudError):
                raise
            raise DaemonConnectionError(str(e))

    def register_widget(self, file_path: str | Path) -> str:
        """Register a widget in the Daemon's memory without displaying it.
        
        Args:
            file_path: Absolute path to the .py widget file.
            
        Returns:
            The loaded bundle_id.
        """
        res = self._send_command({"action": "register", "path": str(Path(file_path).absolute())})
        return res["bundle_id"]

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
        """Display a registered widget on the overlay.
        
        Args:
            bundle_id: The ID of the widget.
        """
        self._send_command({"action": "mount", "bundle_id": bundle_id})

    def unmount_widget(self, bundle_id: str) -> None:
        """Hide a widget from the overlay.
        
        Args:
            bundle_id: The ID of the widget.
        """
        self._send_command({"action": "unmount", "bundle_id": bundle_id})

    def get_registered_widgets(self) -> list[str]:
        """List all widgets loaded in memory."""
        res = self._send_command({"action": "get_registered"})
        return res.get("widgets", [])

    def get_mounted_widgets(self) -> list[str]:
        """List all widgets currently visible on screen."""
        res = self._send_command({"action": "get_mounted"})
        return res.get("widgets", [])

    def send_event(self, event_name: str, payload: dict[str, Any]) -> None:
        """Broadcast an event onto the HUD Event Bus.
        
        Args:
            event_name: The internal name of the event (e.g., 'DART_STATE_CHANGED').
            payload: Arbitrary JSON-serializable dictionary.
        """
        self._send_command({
            "action": "send_event",
            "event_name": event_name,
            "payload": payload
        })
