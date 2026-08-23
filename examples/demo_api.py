"""Pure API Demo showing how to interact with the HUD Daemon."""

import time
from pathlib import Path

from hud.api.client import HudDaemonClient, DaemonConnectionError

def main() -> None:
    client = HudDaemonClient()
    
    print("Checking if daemon is running...")
    try:
        registered = client.get_registered_widgets()
        print(f"Connected! Currently registered widgets: {registered}")
    except DaemonConnectionError as e:
        print(f"Failed to connect to Daemon. Make sure 'python scripts/run_daemon.py' is running in another terminal.\nError: {e}")
        return

    # Let's create a temporary widget just for this demo
    demo_widget_path = Path("temp_api_demo_widget.py").absolute()
    demo_widget_path.write_text(
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
        "        self.lbl = QLabel('Injecté via API !')\n"
        "        self.lbl.setStyleSheet('color: white; font-size: 20px; font-weight: bold; background: rgba(0,0,0,180); padding: 10px; border-radius: 10px;')\n"
        "        self.lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)\n"
        "        layout.addWidget(self.lbl)\n"
        "\n"
        "    def mount(self):\n"
        "        # On mount, we could listen to bus events!\n"
        "        pass\n",
        encoding="utf-8"
    )

    try:
        print(f"Registering widget: {demo_widget_path}")
        bundle_id = client.register_widget(demo_widget_path)
        print(f"Successfully registered as: {bundle_id}")
        
        print("Mounting widget to screen...")
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
        # Cleanup file
        if demo_widget_path.exists():
            demo_widget_path.unlink()
            
    print("Demo complete!")

if __name__ == "__main__":
    main()
