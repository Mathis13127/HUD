import json
import logging

from PySide6.QtNetwork import QTcpServer, QHostAddress, QTcpSocket
from PySide6.QtCore import QObject

from hud.overlay.manager import HudOverlayManager
from hud.events.bus import HudEventBus
from hud.events.types import HudEvent

logger = logging.getLogger("hud.daemon.server")


class HudTcpServer(QObject):
    """Listens for JSON commands on a local TCP port to manipulate the HUD."""

    def __init__(self, manager: HudOverlayManager, event_bus: HudEventBus, port: int = 48321) -> None:
        super().__init__()
        self._manager = manager
        self._event_bus = event_bus
        
        # Track which sockets own which widgets for auto-cleanup on disconnect
        self._socket_widgets: dict[QTcpSocket, set[str]] = {}
        
        self._server = QTcpServer(self)
        self._server.newConnection.connect(self._on_new_connection)
        
        if not self._server.listen(QHostAddress(QHostAddress.SpecialAddress.LocalHost), port):
            logger.critical("[HudTcpServer] FATAL: Could not bind to port %s", port)
        else:
            logger.info("[HudTcpServer] Listening for IPC commands on 127.0.0.1:%s", port)

    def _on_new_connection(self) -> None:
        socket = self._server.nextPendingConnection()
        self._socket_widgets[socket] = set()
        
        socket.readyRead.connect(lambda: self._on_ready_read(socket))
        socket.disconnected.connect(lambda: self._on_disconnect(socket))

    def _on_disconnect(self, socket: QTcpSocket) -> None:
        """Handle auto-cleanup when a client disconnects/crashes."""
        widgets_to_cleanup = self._socket_widgets.pop(socket, set())
        for bundle_id in widgets_to_cleanup:
            logger.info("[HudTcpServer] Auto-cleaning widget %s due to client disconnect.", bundle_id)
            try:
                self._manager.unregister(bundle_id)
            except Exception as e:
                logger.error("[HudTcpServer] Error auto-cleaning %s: %s", bundle_id, e)
                
        socket.deleteLater()

    def _on_ready_read(self, socket: QTcpSocket) -> None:
        while socket.canReadLine():
            line = socket.readLine().data().decode("utf-8").strip()
            if not line:
                continue
                
            try:
                payload = json.loads(line)
                response = self._handle_command(payload, socket)
                socket.write((json.dumps(response) + "\n").encode("utf-8"))
            except json.JSONDecodeError:
                socket.write(b'{"status": "error", "reason": "Invalid JSON"}\n')
            except Exception as e:
                socket.write((json.dumps({"status": "error", "reason": str(e)}) + "\n").encode("utf-8"))

    def _handle_command(self, payload: dict, socket: QTcpSocket) -> dict:
        action = payload.get("action")
        
        if action == "register_code":
            code = payload.get("code", "")
            bundle_id = self._manager.register_code(code)
            self._socket_widgets[socket].add(bundle_id)
            return {"status": "ok", "bundle_id": bundle_id}
            
        elif action == "mount":
            bundle_id = payload.get("bundle_id", "")
            self._manager.mount(bundle_id)
            return {"status": "ok"}
            
        elif action == "unmount":
            bundle_id = payload.get("bundle_id", "")
            self._manager.unmount(bundle_id)
            return {"status": "ok"}
            
        elif action == "unregister":
            bundle_id = payload.get("bundle_id", "")
            self._manager.unregister(bundle_id)
            return {"status": "ok"}
            
        elif action == "get_code":
            bundle_id = payload.get("bundle_id", "")
            code = self._manager.get_code(bundle_id)
            if code is None:
                return {"status": "error", "reason": "Widget not found"}
            return {"status": "ok", "code": code}
            
        elif action == "get_registered":
            return {"status": "ok", "widgets": self._manager.get_registered()}
            
        elif action == "get_mounted":
            return {"status": "ok", "widgets": self._manager.get_mounted()}
            
        elif action == "send_event":
            # Pass arbitrary event to the bus
            event_name = payload.get("event_name", "UNKNOWN_API_EVENT")
            event_payload = payload.get("payload", {})
            self._event_bus.publish(HudEvent(
                name=event_name,
                payload=event_payload,
                source="hud.api.client"
            ))
            return {"status": "ok"}
            
        return {"status": "error", "reason": f"Unknown action: {action}"}
