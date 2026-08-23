"""Core background daemon process for the HUD Engine."""

import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication, QSystemTrayIcon, QMenu, QStyle
from PySide6.QtGui import QAction, QIcon

from hud.bundle.loader import HudBundleLoader
from hud.events.bus import HudEventBus
from hud.overlay.engine import HudOverlayWindow
from hud.overlay.manager import HudOverlayManager


class HudDaemon:
    """Headless background runner for the HUD Overlay."""

    def __init__(self) -> None:
        self._setup_architecture()
        self._setup_tray_icon()

    def _setup_architecture(self) -> None:
        """Initialize the Overlay, Manager, and Event Bus."""
        self.event_bus = HudEventBus()
        self.loader = HudBundleLoader()
        
        self.overlay = HudOverlayWindow()
        self.overlay.maximize_to_screen()
        self.overlay.show()
        
        self.manager = HudOverlayManager(
            overlay=self.overlay, 
            bundle_loader=self.loader, 
            event_bus=self.event_bus
        )
        
        # Start IPC Server
        from hud.daemon.server import HudTcpServer
        self.server = HudTcpServer(self.manager, self.event_bus)

    def _setup_tray_icon(self) -> None:
        """Configure the Windows System Tray Icon."""
        self.tray_icon = QSystemTrayIcon()
        
        # Fallback to standard computer icon if custom icon is missing
        app = QApplication.instance()
        icon = app.style().standardIcon(QStyle.StandardPixmap.SP_ComputerIcon)
        self.tray_icon.setIcon(icon)
        self.tray_icon.setToolTip("JARVIS HUD Engine")

        # Context Menu
        menu = QMenu()
        quit_action = QAction("Quitter JARVIS HUD", menu)
        quit_action.triggered.connect(self.quit)
        menu.addAction(quit_action)

        self.tray_icon.setContextMenu(menu)
        self.tray_icon.show()

    def quit(self) -> None:
        """Exit the daemon gracefully."""
        self.tray_icon.hide()
        QApplication.quit()
