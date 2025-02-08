from PyQt5.QtWidgets import QPushButton
from PyQt5.QtCore import Qt

class KeyButton(QPushButton):
    def __init__(self, key, parent=None):
        super().__init__(key, parent)
        self._setup_ui()
    
    def _setup_ui(self):
        self.setFixedSize(50, 50)
        self.setStyleSheet("""
            QPushButton {
                background-color: #FFB6C1;
                border: 2px solid #4682B4;
                border-radius: 5px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:checked {
                background-color: #4682B4;
                color: white;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
        """)
        self.setCheckable(True)