from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                           QComboBox, QGroupBox, QScrollArea)
from PyQt5.QtCore import Qt
from ..components.KeyButton import KeyButton

class ConfigPage(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self._setup_ui()
        
    def _setup_ui(self):
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_area.setWidget(scroll_content)
        
        self.layout_configurar = QVBoxLayout(scroll_content)
        self.layout_configurar.setAlignment(Qt.AlignTop)
        self.layout_configurar.setSpacing(20)
        
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(scroll_area)
        
        self._setup_title()
        self._setup_general_config()
        self._setup_battle_keys_config()
        self._setup_capture_config()
        
    def _setup_title(self):
        title_label = QLabel("Configurações")
        title_label.setStyleSheet("""
            font-size: 28px;
            font-weight: bold;
            color: #4682B4;
            margin: 20px 0;
        """)
        title_label.setAlignment(Qt.AlignCenter)
        self.layout_configurar.addWidget(title_label)
        
    def _setup_general_config(self):
        general_group = QGroupBox("Configurações Gerais")
        general_group.setStyleSheet("""
            QGroupBox {
                background-color: white;
                border-radius: 10px;
                padding: 20px;
                color: #4682B4;
            }
        """)
        general_layout = QVBoxLayout()
        general_group.setLayout(general_layout)
        
        self._setup_resolution_config(general_layout)
        self._setup_digievolution_config(general_layout)
        self.layout_configurar.addWidget(general_group)
        
    def _setup_resolution_config(self, layout):
        config_layout = QHBoxLayout()
        layout.addLayout(config_layout)

        label_resolucao = QLabel("Resolução do Jogo:")
        label_resolucao.setFixedWidth(150)
        config_layout.addWidget(label_resolucao)

        self.resolucao_combobox = QComboBox()
        self.resolucao_combobox.addItems(["800x600", "1024x768"])
        self.resolucao_combobox.setFixedWidth(120)
        config_layout.addWidget(self.resolucao_combobox)
        config_layout.addStretch()
        
    def _setup_digievolution_config(self, layout):
        digievolucao_layout = QHBoxLayout()
        layout.addLayout(digievolucao_layout)

        label_digievolucao = QLabel("Digievolução:")
        label_digievolucao.setFixedWidth(150)
        digievolucao_layout.addWidget(label_digievolucao)

        self.digievolucao_combobox = QComboBox()
        self.digievolucao_combobox.addItems(["mega", "ultimate", "champion", "rookie"])
        self.digievolucao_combobox.setFixedWidth(120)
        digievolucao_layout.addWidget(self.digievolucao_combobox)
        digievolucao_layout.addStretch()