# JARVIS HUD Subsystem 🎯

The **HUD (Heads-Up Display) Subsystem** is a real-time, click-through desktop overlay engine built with PySide6. It allows JARVIS to project non-intrusive, dynamic widgets (like Siri-style orbs, subtitles, or system monitors) directly onto the user's desktop environment.

## 🌟 Key Features

- **True Desktop Overlay**: Uses advanced PySide6 window flags (`FramelessWindowHint`, `WindowTransparentForInput`) to render fully transparent widgets that float above all applications without blocking mouse clicks.
- **Single-File Widgets**: A widget is simply a standard `.py` file containing a `MANIFEST` dictionary and a PySide6 `QWidget` class. No complex folder structures or JSON parsing required.
- **HUD Studio (Live-Coding IDE)**: Includes a built-in WYSIWYG editor. You can code PySide6 UI components and deploy them instantly to the desktop using the **Hot-Reload** engine (`Ctrl+S`).
- **Zero Silent Failures**: Features a strict "Dry-Run" validation system. If a widget's code contains syntax errors, the Studio intercepts it and logs the error without crashing the live desktop overlay.

## 🚀 Getting Started

### 1. Launching the HUD Studio
To open the live-coding environment and the invisible desktop overlay simultaneously, run:

```powershell
python examples/run_studio.py
```

### 2. Creating a Widget
In the HUD Studio, click **[+ Nouveau Widget]**. It will automatically generate the required boilerplate. A valid HUD widget looks like this:

```python
from pathlib import Path
from PySide6.QtWidgets import QWidget, QLabel
from hud.api.models import WidgetPlacement

# The Manifest is defined directly in the code
MANIFEST = {
    "id": "jarvis.hud.my_widget",
    "name": "My Custom Widget",
    "version": "1.0",
    "default_placement": WidgetPlacement(anchor="bottom_center", offset_y=-100)
}

class Widget(QWidget):
    def __init__(self):
        super().__init__()
        self.setFixedSize(300, 100)
        
        self.lbl = QLabel("Hello Desktop!", self)
        self.lbl.setStyleSheet("color: #00FFCC; font-size: 20px; font-weight: bold;")
        
    def mount(self):
        """Called automatically after the widget is mounted on the overlay."""
        pass
```

### 3. Loading Assets (Images, Fonts)
Because widgets are pure Python files, you can load images natively relative to the script's location:
```python
img_path = Path(__file__).parent / "my_icon.png"
my_label.setPixmap(QPixmap(str(img_path)))
```

## 🏗️ Architecture

- `hud.overlay.engine.HudOverlayWindow`: The invisible, full-screen `QWidget` host.
- `hud.overlay.manager.HudOverlayManager`: Orchestrates mounting, unmounting, and dynamic placement.
- `hud.bundle.loader.HudBundleLoader`: Uses `importlib` to securely hot-swap Python modules in memory.
- `hud.studio.*`: The 3-pane PySide6 editor (Explorer, Editor, Control Panel).
- `hud.events.bus` & `hud.hooks.registry`: Strict event and hook systems for internal lifecycle management.

## 🛡️ Ecosystem Rules (AGENTS.md)
This package strictly complies with the JARVIS industrial standards:
- 100% Typed Errors (`WidgetLoadError`, `ManifestValidationError`). No `except: pass`.
- 100% Isolated tests (`pytest-qt`).
- Pure Public APIs (no cross-package leakages).
