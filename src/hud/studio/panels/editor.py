"""Code editor panel for HUD Studio."""

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QTabWidget,
    QPlainTextEdit,
    QLabel,
    QHBoxLayout,
)
from PySide6.QtGui import QFont


class WorkspaceEditor(QWidget):
    """Central panel containing text editor for the .py widget file."""

    def __init__(self) -> None:
        super().__init__()
        self._current_file_path: str | None = None
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Header for current file
        header_layout = QHBoxLayout()
        self.lbl_current_file = QLabel("No file selected")
        self.lbl_current_file.setStyleSheet("color: #888; font-style: italic;")
        header_layout.addWidget(self.lbl_current_file)
        header_layout.addStretch()
        layout.addLayout(header_layout)

        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        # Code Editor Tab
        self.code_editor = QPlainTextEdit()
        font = QFont("Consolas", 10)
        font.setStyleHint(QFont.StyleHint.Monospace)
        self.code_editor.setFont(font)

        self.tabs.addTab(self.code_editor, "Code Editor")

    def load_file_content(self, file_path: str, content: str) -> None:
        """Load text into the editor."""
        self._current_file_path = file_path
        self.lbl_current_file.setText(f"Editing: {file_path}")
        self.lbl_current_file.setStyleSheet("color: #FFF; font-weight: bold;")
        self.code_editor.setPlainText(content)

    def get_current_code(self) -> str:
        return self.code_editor.toPlainText()
