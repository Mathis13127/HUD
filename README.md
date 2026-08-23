# JARVIS HUD Subsystem 🟢

> **HUD (Heads-Up Display)** is the standalone, purely in-memory visual rendering engine for the JARVIS ecosystem.

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![PySide6](https://img.shields.io/badge/PySide-6-green.svg)](https://doc.qt.io/qtforpython/)

## 🚀 The "Thin Client" Architecture

Unlike traditional UI engines, **HUD does not manage, save, or read widget files from the disk**.
It acts as a completely stateless **"Thin Client"**. 

1. **Invisible Daemon**: The HUD runs in the background as a transparent overlay covering your entire screen.
2. **In-Memory Injection**: External scripts (like JARVIS) connect via TCP (Port `48321`) and inject raw Python code as strings.
3. **AST Sandbox**: Before execution, injected code is strictly validated by an Abstract Syntax Tree (AST) sandbox. It blocks dangerous operations (`open`, `exec`, `eval`) and restricts imports to safe UI modules (like `PySide6`).
4. **Auto-Cleanup**: The engine uses persistent TCP connections. If the AI or the script that injected a widget disconnects or crashes, the HUD automatically unmounts and purges the widget from memory to keep the screen clean.

## 📦 Installation

This package is designed to be installed globally or in your virtual environment:

```bash
git clone https://github.com/Mathis13127/HUD.git
cd HUD
pip install -e .
```

## 🛠️ Usage

### 1. Start the Daemon

The Daemon runs quietly in the Windows System Tray and opens the `127.0.0.1:48321` IPC port.

```bash
python scripts/run_daemon.py
```

### 2. Injecting an Overlay (Remote Control)

Any Python script on your machine can now use the `HudDaemonClient` to dynamically spawn overlays onto the screen.

```python
from hud.api.client import HudDaemonClient

# The raw Python code of your UI widget
WIDGET_CODE = """
from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout
from PySide6.QtCore import Qt

MANIFEST = {
    'id': 'api.demo.widget',
    'name': 'API Demo',
    'version': '1.0',
    'default_placement': {
        'anchor': 'center'
    }
}

class Widget(QWidget):
    def __init__(self):
        super().__init__()
        self.setFixedSize(300, 100)
        layout = QVBoxLayout(self)
        
        self.lbl = QLabel('Hello from Memory!')
        self.lbl.setStyleSheet('color: white; font-size: 20px; font-weight: bold; background: rgba(0,0,0,180); padding: 10px; border-radius: 10px;')
        self.lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        layout.addWidget(self.lbl)
        
    def mount(self):
        pass
"""

client = HudDaemonClient()

# 1. Compile & Inject code into Daemon's memory
bundle_id = client.register_widget_from_code(WIDGET_CODE)

# 2. Display the widget on the screen
client.mount_widget(bundle_id)

# 3. Disconnect
# Note: Because of Auto-Cleanup, the widget will instantly disappear 
# from the screen when this script finishes and the socket closes!
client.close() 
```

## 🔐 Security (The AST Sandbox)

Because local IPC execution of Python strings is inherently risky, the engine features a strict `HudAstValidator`.
- Only allows specific roots like `PySide6`, `typing`, `hud`.
- Blocks Dunder introspection (`__subclasses__`) to prevent VM escapes.
- Instantly rejects malicious payloads.

## 🧪 Testing

```bash
pytest -v
```
*Built following the L1-L14 JARVIS Architectural Laws.*
