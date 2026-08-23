from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Qt

MANIFEST = {
    'id': 'jarvis.hud.orb',
    'name': 'Orb Subtitle',
    'version': '1.0',
    'default_placement': {
        'anchor': 'bottom_center',
        'offset_y': -150
    }
}

class Widget(QWidget):
    def __init__(self):
        super().__init__()
        self.setFixedSize(400, 200)
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.orb = QLabel()
        self.orb.setFixedSize(80, 80)
        self.orb.setStyleSheet('''
            QLabel {
                background-color: #00FFcc;
                border-radius: 40px;
                border: 2px solid #ffffff;
            }
        ''')
        layout.addWidget(self.orb, alignment=Qt.AlignmentFlag.AlignHCenter)
        
        self.text = QLabel('Waiting for input...')
        self.text.setStyleSheet('color: white; font-size: 24px; font-weight: bold; background: rgba(0,0,0,150); border-radius: 10px; padding: 10px;')
        self.text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.text, alignment=Qt.AlignmentFlag.AlignHCenter)
        
    def mount(self):
        pass
