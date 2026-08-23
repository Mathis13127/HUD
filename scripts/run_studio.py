"""Launcher for the HUD Studio and Overlay Engine."""

import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication

from hud.bundle.loader import HudBundleLoader
from hud.events.bus import HudEventBus
from hud.overlay.engine import HudOverlayWindow
from hud.overlay.manager import HudOverlayManager
from hud.studio.app import HudStudioWindow


def create_demo_widget(bundles_dir: Path) -> None:
    """Creates a default demo single-file widget so the user has something to edit."""
    bundles_dir.mkdir(parents=True, exist_ok=True)
    
    widget_file = bundles_dir / "orb_widget.py"
    if widget_file.exists():
        return
        
    widget_file.write_text(
        "from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel\n"
        "from PySide6.QtCore import Qt\n"
        "\n"
        "MANIFEST = {\n"
        "    'id': 'jarvis.hud.orb',\n"
        "    'name': 'Orb Subtitle',\n"
        "    'version': '1.0',\n"
        "    'default_placement': {\n"
        "        'anchor': 'bottom_center',\n"
        "        'offset_y': -150\n"
        "    }\n"
        "}\n"
        "\n"
        "class Widget(QWidget):\n"
        "    def __init__(self):\n"
        "        super().__init__()\n"
        "        self.setFixedSize(400, 200)\n"
        "        layout = QVBoxLayout(self)\n"
        "        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)\n"
        "        \n"
        "        self.orb = QLabel()\n"
        "        self.orb.setFixedSize(80, 80)\n"
        "        self.orb.setStyleSheet('''\n"
        "            QLabel {\n"
        "                background-color: #00FFcc;\n"
        "                border-radius: 40px;\n"
        "                border: 2px solid #ffffff;\n"
        "            }\n"
        "        ''')\n"
        "        layout.addWidget(self.orb, alignment=Qt.AlignmentFlag.AlignHCenter)\n"
        "        \n"
        "        self.text = QLabel('Waiting for input...')\n"
        "        self.text.setStyleSheet('color: white; font-size: 24px; font-weight: bold; background: rgba(0,0,0,150); border-radius: 10px; padding: 10px;')\n"
        "        self.text.setAlignment(Qt.AlignmentFlag.AlignCenter)\n"
        "        layout.addWidget(self.text, alignment=Qt.AlignmentFlag.AlignHCenter)\n"
        "        \n"
        "    def mount(self):\n"
        "        pass\n",
        encoding="utf-8"
    )


def main() -> None:
    app = QApplication(sys.argv)
    
    # 1. Setup Architecture
    event_bus = HudEventBus()
    loader = HudBundleLoader()
    
    # Start the invisible overlay
    overlay = HudOverlayWindow()
    overlay.maximize_to_screen()
    overlay.show()
    
    manager = HudOverlayManager(overlay=overlay, bundle_loader=loader, event_bus=event_bus)
    
    # 2. Setup Bundles Dir
    bundles_dir = Path(__file__).parent.parent / "bundles"
    create_demo_widget(bundles_dir)
    
    # 3. Start the Studio Window
    studio = HudStudioWindow(overlay_manager=manager, bundles_dir=bundles_dir)
    studio.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
