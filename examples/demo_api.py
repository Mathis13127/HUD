"""Pure API Demo showing how to interact with the HUD Daemon."""

import sys
import time
import subprocess
from pathlib import Path

from hud.api.client import HudDaemonClient, DaemonConnectionError

def ensure_daemon_running() -> subprocess.Popen | None:
    """Check if daemon is reachable, otherwise spawn it in the background."""
    client = HudDaemonClient()
    try:
        client.get_registered_widgets()
        client.close()
        return None  # Already running
    except DaemonConnectionError:
        client.close()
        print("Daemon is not running. Launching it in the background...")
        daemon_script = Path(__file__).parent.parent / "scripts" / "run_daemon.py"
        process = subprocess.Popen([sys.executable, str(daemon_script)])
        
        # Wait for daemon to boot up
        for _ in range(10):
            try:
                time.sleep(0.5)
                # Create a new client to test connection
                test_client = HudDaemonClient()
                test_client.get_registered_widgets()
                test_client.close()
                print("Daemon successfully started!")
                return process
            except DaemonConnectionError:
                continue
                
        print("Failed to start daemon.")
        process.terminate()
        sys.exit(1)


def main() -> None:
    # 1. Start daemon if missing
    daemon_process = ensure_daemon_running()
    
    client = HudDaemonClient()
    
    registered = client.get_registered_widgets()
    print(f"Connected! Currently registered widgets: {registered}")

    # 2. Register widget dynamically from code string!
    source_code = (
        "from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel\n"
        "from PySide6.QtCore import Qt\n"
        "\n"
        "MANIFEST = {\n"
        "    'id': 'api.demo.widget',\n"
        "    'name': 'API Demo',\n"
        "    'version': '1.0',\n"
        "    'default_placement': {\n"
        "        'anchor': 'bottom_right',\n"
        "        'offset_y': -50,\n"
        "        'offset_x': -50\n"
        "    }\n"
        "}\n"
        "\n"
        "class Widget(QWidget):\n"
        "    def __init__(self):\n"
        "        super().__init__()\n"
        "        self.setFixedSize(300, 100)\n"
        "        layout = QVBoxLayout(self)\n"
        "        self.lbl = QLabel('Injecté IN-MEMORY !')\n"
        "        self.lbl.setStyleSheet('color: white; font-size: 20px; font-weight: bold; background: rgba(255,0,0,180); padding: 10px; border-radius: 10px;')\n"
        "        self.lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)\n"
        "        layout.addWidget(self.lbl)\n"
        "\n"
        "    def mount(self):\n"
        "        pass\n"
    )

    try:
        print("\nRegistering widget from raw Python string (In-Memory)...")
        bundle_id = client.register_widget_from_code(source_code)
        print(f"Successfully registered as: {bundle_id}")
        
        print("Mounting widget to screen (Check bottom right of your screen!)...")
        client.mount_widget(bundle_id)
        
        active = client.get_mounted_widgets()
        print(f"Active widgets: {active}")
        
        print("Waiting 3 seconds...")
        time.sleep(3)
        
        print("Sending event to change something (Conceptually, since the widget doesn't listen yet in this basic demo)...")
        client.send_event("DART_STATE_CHANGED", {"state": "listening"})
        
        print("Waiting 2 seconds...")
        time.sleep(2)
        
        print("Unmounting widget...")
        client.unmount_widget(bundle_id)
        
    finally:
        # Kill the daemon if we spawned it specifically for this script
        if daemon_process:
            print("\nShutting down temporary daemon...")
            daemon_process.terminate()
            
    print("\nDemo complete!")

if __name__ == "__main__":
    main()
