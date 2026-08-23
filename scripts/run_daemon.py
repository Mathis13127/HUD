"""Production Launcher for the JARVIS HUD Engine."""

import sys
import json
from pathlib import Path

from PySide6.QtWidgets import QApplication

from hud.daemon.core import HudDaemon


def ensure_default_config(config_path: Path) -> None:
    """Create an empty default config file if none exists."""
    if config_path.is_file():
        return
        
    config_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Démarrage 100% vide
    default_config = {
        "autostart_widgets": []
    }
    
    config_path.write_text(json.dumps(default_config, indent=4), encoding="utf-8")


def main() -> None:
    # Must use QApplication since we have a System Tray Icon and UI elements
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)  # Keep running even if overlay is hidden
    
    config_path = Path(__file__).parent.parent / "config" / "autostart.json"
    ensure_default_config(config_path)
    
    daemon = HudDaemon(config_path=config_path)
    daemon.load_autostart_widgets()
    
    print("[HUD Daemon] Running in background. Check System Tray to quit.")
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
