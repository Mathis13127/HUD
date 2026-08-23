from pathlib import Path
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Qt

from hud.api.models import WidgetPlacement

MANIFEST = {
    "id": "jarvis.hud.new_widget",
    "name": "Nouveau Widget",
    "version": "1.0",
    "default_placement": WidgetPlacement(anchor="center")
}

class Widget(QWidget):
    def __init__(self):
        super().__init__()
        self.setFixedSize(300, 150)
        
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Exemple de label
        lbl = QLabel("Hello World!")
        lbl.setStyleSheet("color: white; font-size: 24px; font-weight: bold; background: rgba(0, 0, 0, 180); padding: 15px; border-radius: 10px;")
        layout.addWidget(lbl)
        
        # Pour charger une image qui se trouverait à côté de ce fichier :
        # from PySide6.QtGui import QPixmap
        # img_path = Path(__file__).parent / "logo.png"
        # pixmap = QPixmap(str(img_path))
        
    def mount(self):
        """Appelé juste après que le widget ait été ajouté à l'overlay."""
        pass
