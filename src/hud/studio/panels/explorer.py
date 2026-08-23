"""File explorer panel for HUD Studio."""

from pathlib import Path
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QFileSystemModel,
    QTreeView,
    QPushButton
)
from PySide6.QtCore import QDir


class BundleExplorer(QWidget):
    """Left panel displaying available HUD bundle files."""

    def __init__(self, bundles_path: Path) -> None:
        super().__init__()
        self.bundles_path = bundles_path
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # New Widget Button
        self.btn_new_widget = QPushButton("+ Nouveau Widget (.py)")
        self.btn_new_widget.setStyleSheet(
            "background-color: #2D2D30; color: #00FFCC; font-weight: bold; padding: 5px; border: 1px solid #3F3F46;"
        )
        layout.addWidget(self.btn_new_widget)

        self.model = QFileSystemModel()
        self.model.setRootPath(str(self.bundles_path))
        # Only show .py and image files to keep it clean
        self.model.setNameFilters(["*.py", "*.png", "*.jpg", "*.svg"])
        self.model.setNameFilterDisables(False)

        self.tree = QTreeView()
        self.tree.setModel(self.model)
        self.tree.setRootIndex(self.model.index(str(self.bundles_path)))
        
        # Hide size, type, date modified columns for a cleaner look
        self.tree.setColumnHidden(1, True)
        self.tree.setColumnHidden(2, True)
        self.tree.setColumnHidden(3, True)
        self.tree.setHeaderHidden(True)

        layout.addWidget(self.tree)
