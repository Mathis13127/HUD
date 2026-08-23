"""Launcher for the HUD Live Studio."""

import sys
import time
import subprocess
from pathlib import Path

from PySide6.QtWidgets import QApplication, QMessageBox

from hud.api.client import HudDaemonClient, DaemonConnectionError
from hud.studio.app import HudStudioWindow

def ensure_daemon_running() -> subprocess.Popen | None:
    """Check if daemon is reachable, otherwise spawn it in the background."""
    try:
        client = HudDaemonClient()
        client.get_registered_widgets()
        client.close()
        return None  # Already running
    except DaemonConnectionError:
        print("Daemon is not running. Launching it in the background...")
        daemon_script = Path(__file__).parent / "run_daemon.py"
        process = subprocess.Popen([sys.executable, str(daemon_script)])
        
        # Wait for daemon to boot up
        for _ in range(20):
            try:
                time.sleep(0.5)
                test_client = HudDaemonClient()
                test_client.get_registered_widgets()
                test_client.close()
                print("Daemon successfully started!")
                return process
            except DaemonConnectionError:
                continue
                
        print("Failed to start daemon.")
        return process

def main() -> None:
    app = QApplication(sys.argv)
    
    # 1. Start daemon if missing
    daemon_process = ensure_daemon_running()
    
    # 2. Check connection before launching
    try:
        client = HudDaemonClient()
        client.get_registered_widgets()
    except DaemonConnectionError:
        QMessageBox.critical(None, "Error", "Could not connect to HUD Daemon. Start it manually with run_daemon.py")
        sys.exit(1)
    finally:
        if 'client' in locals() and hasattr(client, 'close'):
            client.close()
        
    # 3. Start the Studio Window
    studio = HudStudioWindow()
    studio.show()
    
    exit_code = app.exec()
    
    # If we started it automatically, kill it when studio closes
    if daemon_process:
        daemon_process.terminate()
        
    sys.exit(exit_code)

if __name__ == "__main__":
    main()
