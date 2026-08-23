"""Production Launcher for the JARVIS HUD Engine."""

import sys
from pathlib import Path

hud_src = Path(__file__).resolve().parent.parent / "src"
if hud_src.exists() and str(hud_src) not in sys.path:
    sys.path.insert(0, str(hud_src))

from PySide6.QtWidgets import QApplication
from hud.daemon.core import HudDaemon

def main() -> None:
    # Must use QApplication since we have a System Tray Icon and UI elements
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)  # Keep running even if overlay is hidden
    
    daemon = HudDaemon()
    
    print("[HUD Daemon] Running in background. Check System Tray to quit.")
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
