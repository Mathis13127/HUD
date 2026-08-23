"""Control panel for triggering deployments and viewing logs."""

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QPushButton,
    QTextEdit,
    QLabel,
)


class ControlPanel(QWidget):
    """Right panel handling Hot-Reload triggering and error logs."""

    def __init__(self) -> None:
        super().__init__()
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.btn_deploy = QPushButton("🚀 Deploy / Hot-Reload (Ctrl+S)")
        self.btn_deploy.setStyleSheet(
            "background-color: #0078D7; color: white; font-weight: bold; padding: 10px;"
        )
        layout.addWidget(self.btn_deploy)

        layout.addWidget(QLabel("Logs & Dry-Run Status:"))

        self.log_console = QTextEdit()
        self.log_console.setReadOnly(True)
        self.log_console.setStyleSheet("background-color: #1E1E1E; color: #CCCCCC; font-family: Consolas;")
        layout.addWidget(self.log_console)

    def log_message(self, message: str, is_error: bool = False) -> None:
        """Append a message to the internal log console."""
        color = "#FF5555" if is_error else "#55FF55"
        self.log_console.append(f"<span style='color:{color}'>{message}</span>")
