from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                           QPushButton, QGroupBox)
from PyQt5.QtCore import Qt, QTimer
from ..threads.AutomationThread import AutomationThread

class PlayPage(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.automation_thread = None
        self._setup_ui()
        
    def _setup_ui(self):
        container = QWidget()
        container.setFixedWidth(400)
        container_layout = QVBoxLayout(container)
        container_layout.setAlignment(Qt.AlignCenter)
        container_layout.setSpacing(20)
        
        main_layout = QHBoxLayout(self)
        main_layout.addWidget(container)
        
        self._setup_title(container_layout)
        self._setup_content(container_layout)
        
    def _setup_title(self, layout):
        title_label = QLabel("Digimon Automation")
        title_label.setStyleSheet("""
            font-size: 28px;
            font-weight: bold;
            color: #4682B4;
            margin: 20px 0;
        """)
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
    def _setup_content(self, layout):
        content_group = QGroupBox()
        content_group.setStyleSheet("""
            QGroupBox {
                background-color: white;
                border-radius: 10px;
                padding: 20px;
            }
        """)
        content_layout = QVBoxLayout(content_group)
        content_layout.setSpacing(15)
        
        self._setup_description(content_layout)
        self._setup_status_labels(content_layout)
        self._setup_buttons(content_layout)
        
        layout.addWidget(content_group)
        layout.addStretch()
        
    def _setup_description(self, layout):
        description = QLabel("Prepare-se para uma aventura emocionante no mundo dos Digimons!")
        description.setStyleSheet("""
            font-size: 16px;
            color: #666;
            margin-bottom: 20px;
        """)
        description.setAlignment(Qt.AlignCenter)
        description.setWordWrap(True)
        layout.addWidget(description)
        
    def _setup_status_labels(self, layout):
        self.status_label = QLabel("Status: Parado")
        self.time_label = QLabel("Tempo decorrido: 00:00:00")
        self.battles_label = QLabel("Batalhas realizadas: 0")
        self.battles_per_minute_label = QLabel("Batalhas por minuto: 0.00")
        self.license_info_label = QLabel("Informações da licença não disponíveis")
        
        labels = [self.status_label, self.time_label, self.battles_label, 
                 self.battles_per_minute_label, self.license_info_label]
                 
        for label in labels:
            label.setStyleSheet("""
                font-size: 14px;
                color: #666;
                margin: 5px 0;
            """)
            label.setAlignment(Qt.AlignCenter)
            layout.addWidget(label)
            
    def _setup_buttons(self, layout):
        buttons_container = QWidget()
        buttons_layout = QHBoxLayout(buttons_container)
        
        self.start_stop_button = QPushButton("Iniciar Automação")
        self.start_stop_button.setStyleSheet(self._get_start_button_style())
        self.start_stop_button.clicked.connect(self.toggle_automation)
        buttons_layout.addWidget(self.start_stop_button)
        
        layout.addWidget(buttons_container)
        
    def _get_start_button_style(self):
        return """
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 12px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """