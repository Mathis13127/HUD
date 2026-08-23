"""Main application window for HUD Studio."""

from pathlib import Path

from PySide6.QtWidgets import QMainWindow, QSplitter, QWidget, QHBoxLayout
from PySide6.QtCore import Qt
from PySide6.QtGui import QKeySequence, QShortcut

from hud.overlay.manager import HudOverlayManager
from hud.studio.controller import StudioController
from hud.studio.panels.editor import WorkspaceEditor
from hud.studio.panels.explorer import BundleExplorer
from hud.studio.panels.preview_control import ControlPanel


class HudStudioWindow(QMainWindow):
    """The main IDE window for editing HUD bundles."""

    def __init__(self, overlay_manager: HudOverlayManager, bundles_dir: Path) -> None:
        super().__init__()
        self.setWindowTitle("JARVIS HUD Studio")
        self.resize(1200, 800)

        # Apply dark theme stylesheet for the editor
        self.setStyleSheet("""
            QMainWindow, QWidget { background-color: #2D2D30; color: #CCCCCC; }
            QTreeView { background-color: #1E1E1E; border: none; }
            QPlainTextEdit { background-color: #1E1E1E; color: #D4D4D4; border: 1px solid #3F3F46; }
            QTabWidget::pane { border: 1px solid #3F3F46; }
            QTabBar::tab { background: #2D2D30; border: 1px solid #3F3F46; padding: 5px; }
            QTabBar::tab:selected { background: #1E1E1E; }
        """)

        self._setup_ui(bundles_dir)
        
        # Initialize Controller
        self.controller = StudioController(
            overlay_manager=overlay_manager,
            explorer=self.explorer,
            editor=self.editor,
            control=self.control,
            bundles_dir=bundles_dir,
        )

        # Setup Ctrl+S Shortcut
        self.shortcut_save = QShortcut(QKeySequence("Ctrl+S"), self)
        self.shortcut_save.activated.connect(self.controller.deploy_active_bundle)

    def _setup_ui(self, bundles_dir: Path) -> None:
        central = QWidget()
        self.setCentralWidget(central)
        layout = QHBoxLayout(central)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        layout.addWidget(splitter)

        # Instantiate Panels
        self.explorer = BundleExplorer(bundles_dir)
        self.editor = WorkspaceEditor()
        self.control = ControlPanel()

        splitter.addWidget(self.explorer)
        splitter.addWidget(self.editor)
        splitter.addWidget(self.control)

        # Set stretch factors (e.g. 20% explorer, 60% editor, 20% control)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 4)
        splitter.setStretchFactor(2, 1)
