"""Live IDE and Manager for HUD Thin Client Architecture."""

from PySide6.QtWidgets import (
    QMainWindow, QSplitter, QWidget, QHBoxLayout, QVBoxLayout, 
    QListWidget, QPushButton, QPlainTextEdit, QLabel, QMessageBox, QListWidgetItem
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont, QKeySequence, QShortcut

from hud.api.client import HudDaemonClient, DaemonConnectionError

DEFAULT_PLACEHOLDER = '''from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout
from PySide6.QtCore import Qt

MANIFEST = {
    'id': 'my.live.widget',
    'name': 'Live Widget',
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
        
        self.lbl = QLabel('Live Injected Widget!')
        self.lbl.setStyleSheet(
            'color: white; font-size: 20px; font-weight: bold; '
            'background: rgba(0,255,0,100); padding: 10px; border-radius: 10px;'
        )
        self.lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        layout.addWidget(self.lbl)
        
    def mount(self):
        pass
'''

class HudStudioWindow(QMainWindow):
    """The main Live IDE window for editing and managing in-memory HUD widgets."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("JARVIS HUD Studio (Live Thin Client)")
        self.resize(1200, 800)

        # Apply dark theme
        self.setStyleSheet("""
            QMainWindow, QWidget { background-color: #2D2D30; color: #CCCCCC; }
            QListWidget { background-color: #1E1E1E; border: none; font-size: 14px; }
            QListWidget::item { padding: 8px; }
            QListWidget::item:selected { background-color: #007ACC; }
            QPlainTextEdit { background-color: #1E1E1E; color: #D4D4D4; border: 1px solid #3F3F46; }
            QPushButton { background-color: #3F3F46; border: none; padding: 8px; border-radius: 4px; }
            QPushButton:hover { background-color: #555555; }
            QPushButton:pressed { background-color: #007ACC; }
            QPushButton#deployBtn { background-color: #007ACC; font-weight: bold; }
            QPushButton#deployBtn:hover { background-color: #0098FF; }
        """)

        self.client = HudDaemonClient()
        self.current_bundle_id: str | None = None

        self._setup_ui()
        
        # Shortcut for quick deploy
        self.shortcut_save = QShortcut(QKeySequence("Ctrl+S"), self)
        self.shortcut_save.activated.connect(self.deploy_current_code)

        # Auto-refresh timer
        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self.refresh_widgets_list)
        self.refresh_timer.start(2000)
        
        self.refresh_widgets_list()

    def _setup_ui(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)
        layout = QHBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        
        splitter = QSplitter(Qt.Orientation.Horizontal)
        layout.addWidget(splitter)

        # --- LEFT PANEL (Live Manager) ---
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        
        left_layout.addWidget(QLabel("<b>Running Widgets (Daemon Memory)</b>"))
        
        self.list_widget = QListWidget()
        self.list_widget.itemClicked.connect(self.on_widget_selected)
        left_layout.addWidget(self.list_widget)
        
        btn_refresh = QPushButton("🔄 Refresh Status")
        btn_refresh.clicked.connect(self.refresh_widgets_list)
        left_layout.addWidget(btn_refresh)
        
        btn_new = QPushButton("✨ New Placeholder")
        btn_new.clicked.connect(self.create_placeholder)
        left_layout.addWidget(btn_new)
        
        splitter.addWidget(left_widget)

        # --- RIGHT PANEL (Code Editor) ---
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        
        header_layout = QHBoxLayout()
        self.lbl_editing = QLabel("<b>Editor:</b> No widget selected")
        header_layout.addWidget(self.lbl_editing)
        header_layout.addStretch()
        
        btn_deploy = QPushButton("🚀 Deploy & Mount (Ctrl+S)")
        btn_deploy.setObjectName("deployBtn")
        btn_deploy.clicked.connect(self.deploy_current_code)
        header_layout.addWidget(btn_deploy)
        
        btn_unmount = QPushButton("🚫 Unmount")
        btn_unmount.clicked.connect(self.unmount_current)
        header_layout.addWidget(btn_unmount)
        
        btn_unregister = QPushButton("🗑️ Unregister")
        btn_unregister.clicked.connect(self.unregister_current)
        header_layout.addWidget(btn_unregister)
        
        right_layout.addLayout(header_layout)
        
        self.editor = QPlainTextEdit()
        font = QFont("Consolas", 12)
        self.editor.setFont(font)
        # Use 4-space hard tabs for python code
        self.editor.setTabStopDistance(self.editor.fontMetrics().horizontalAdvance(" ") * 4)
        right_layout.addWidget(self.editor)
        
        splitter.addWidget(right_widget)
        
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 3)

    def refresh_widgets_list(self) -> None:
        """Poll the Daemon for registered and mounted widgets."""
        try:
            registered = self.client.get_registered_widgets()
            mounted = self.client.get_mounted_widgets()
        except DaemonConnectionError:
            self.list_widget.clear()
            self.list_widget.addItem("Daemon offline or unreachable.")
            return

        self.list_widget.blockSignals(True)
        self.list_widget.clear()
        
        for b_id in registered:
            is_mounted = b_id in mounted
            display_text = f"🟢 {b_id}" if is_mounted else f"⚪ {b_id}"
            item = QListWidgetItem(display_text)
            item.setData(Qt.ItemDataRole.UserRole, b_id)
            self.list_widget.addItem(item)
            if b_id == self.current_bundle_id:
                item.setSelected(True)
                
        self.list_widget.blockSignals(False)

    def on_widget_selected(self, item: QListWidgetItem) -> None:
        bundle_id = item.data(Qt.ItemDataRole.UserRole)
        if not bundle_id:
            return
            
        self.current_bundle_id = bundle_id
        self.lbl_editing.setText(f"<b>Editor:</b> {bundle_id}")
        
        try:
            code = self.client.get_widget_code(bundle_id)
            self.editor.setPlainText(code)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not fetch code:\n{e}")

    def create_placeholder(self) -> None:
        self.current_bundle_id = "my.live.widget"
        self.lbl_editing.setText(f"<b>Editor:</b> {self.current_bundle_id} (Unsaved)")
        self.editor.setPlainText(DEFAULT_PLACEHOLDER)
        # Clear list selection visually
        self.list_widget.blockSignals(True)
        self.list_widget.clearSelection()
        self.list_widget.blockSignals(False)

    def deploy_current_code(self) -> None:
        code = self.editor.toPlainText().strip()
        if not code:
            return
            
        try:
            # 1. Register Code
            bundle_id = self.client.register_widget_from_code(code)
            
            # 2. Unregister if it was previously there, although manager.register_code does it.
            # But the manager overwriting might just drop it, let's just mount it.
            self.client.mount_widget(bundle_id)
            
            self.current_bundle_id = bundle_id
            self.lbl_editing.setText(f"<b>Editor:</b> {bundle_id}")
            self.refresh_widgets_list()
            
        except Exception as e:
            QMessageBox.critical(self, "Deployment Failed", str(e))

    def unmount_current(self) -> None:
        if not self.current_bundle_id:
            return
        try:
            self.client.unmount_widget(self.current_bundle_id)
            self.refresh_widgets_list()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def unregister_current(self) -> None:
        if not self.current_bundle_id:
            return
        try:
            self.client.unregister_widget(self.current_bundle_id)
            self.editor.clear()
            self.current_bundle_id = None
            self.lbl_editing.setText("<b>Editor:</b> No widget selected")
            self.refresh_widgets_list()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
