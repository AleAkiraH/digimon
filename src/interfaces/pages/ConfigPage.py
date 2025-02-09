from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                           QComboBox, QGroupBox, QScrollArea, QLineEdit,
                           QSpinBox, QPushButton)
from PyQt5.QtCore import Qt
from ..components.KeyButton import KeyButton
from ...core.entities.Config import Config

class ConfigPage(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.config = Config.load()
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
        
        # Adiciona os botões de ação no topo
        self._setup_action_buttons()
        self._setup_title()
        self._setup_general_config()
        self._setup_telegram_config()
        self._setup_battle_keys_config()
        
    def _setup_action_buttons(self):
        buttons_container = QWidget()
        buttons_layout = QHBoxLayout(buttons_container)
        buttons_layout.setAlignment(Qt.AlignRight)
        
        # Botão Carregar
        load_button = QPushButton("Carregar Configurações")
        load_button.setStyleSheet(self._get_button_style("#1E90FF"))
        load_button.clicked.connect(self._load_config)
        buttons_layout.addWidget(load_button)
        
        # Botão Salvar
        save_button = QPushButton("Salvar Configurações")
        save_button.setStyleSheet(self._get_button_style("#4CAF50"))
        save_button.clicked.connect(self._save_config)
        buttons_layout.addWidget(save_button)
        
        self.layout_configurar.addWidget(buttons_container)
        
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
        general_group.setStyleSheet(self._get_group_style())
        general_layout = QVBoxLayout()
        general_group.setLayout(general_layout)
        
        # Resolução
        resolution_layout = QHBoxLayout()
        label_resolucao = QLabel("Resolução do Jogo:")
        label_resolucao.setFixedWidth(150)
        self.resolucao_combobox = QComboBox()
        self.resolucao_combobox.addItems(["800x600", "1024x768"])
        self.resolucao_combobox.setFixedWidth(120)
        self.resolucao_combobox.setCurrentText(self.config.resolution)
        resolution_layout.addWidget(label_resolucao)
        resolution_layout.addWidget(self.resolucao_combobox)
        resolution_layout.addStretch()
        general_layout.addLayout(resolution_layout)
        
        # Digievolução
        digievolucao_layout = QHBoxLayout()
        label_digievolucao = QLabel("Digievolução:")
        label_digievolucao.setFixedWidth(150)
        self.digievolucao_combobox = QComboBox()
        self.digievolucao_combobox.addItems(["mega", "ultimate", "champion", "rookie"])
        self.digievolucao_combobox.setFixedWidth(120)
        self.digievolucao_combobox.setCurrentText(self.config.digivolution_type)
        digievolucao_layout.addWidget(label_digievolucao)
        digievolucao_layout.addWidget(self.digievolucao_combobox)
        digievolucao_layout.addStretch()
        general_layout.addLayout(digievolucao_layout)
        
        self.layout_configurar.addWidget(general_group)
        
    def _setup_telegram_config(self):
        telegram_group = QGroupBox("Configurações do Telegram")
        telegram_group.setStyleSheet(self._get_group_style())
        telegram_layout = QVBoxLayout()
        
        # Intervalo
        interval_layout = QHBoxLayout()
        label_interval = QLabel("Intervalo de mensagens (minutos):")
        label_interval.setFixedWidth(200)
        self.interval_spinbox = QSpinBox()
        self.interval_spinbox.setRange(1, 120)
        self.interval_spinbox.setValue(self.config.telegram_interval)
        interval_layout.addWidget(label_interval)
        interval_layout.addWidget(self.interval_spinbox)
        interval_layout.addStretch()
        telegram_layout.addLayout(interval_layout)
        
        # Bot Token
        token_layout = QHBoxLayout()
        label_token = QLabel("Bot Token:")
        label_token.setFixedWidth(200)
        self.token_input = QLineEdit()
        self.token_input.setText(self.config.bot_token)
        token_layout.addWidget(label_token)
        token_layout.addWidget(self.token_input)
        telegram_layout.addLayout(token_layout)
        
        # Chat ID
        chat_layout = QHBoxLayout()
        label_chat = QLabel("Chat ID:")
        label_chat.setFixedWidth(200)
        self.chat_input = QLineEdit()
        self.chat_input.setText(self.config.chat_id)
        chat_layout.addWidget(label_chat)
        chat_layout.addWidget(self.chat_input)
        telegram_layout.addLayout(chat_layout)
        
        telegram_group.setLayout(telegram_layout)
        self.layout_configurar.addWidget(telegram_group)
    
    def _setup_battle_keys_config(self):
        battle_keys_group = QGroupBox("Configuração de Teclas")
        battle_keys_group.setStyleSheet(self._get_group_style())
        battle_keys_layout = QVBoxLayout()
        
        key_groups = [
            ('group1', ['Q', 'W', 'E']),
            ('group2', ['A', 'S', 'D']),
            ('group3', ['Z', 'X', 'C'])
        ]
        
        for i, (group_name, keys) in enumerate(key_groups, 1):
            group_layout = QHBoxLayout()
            label = QLabel(f"Tecla {i}:")  # Alterado de "Grupo" para "Tecla"
            label.setFixedWidth(100)
            group_layout.addWidget(label)
            
            button_group = QHBoxLayout()
            for key in keys:
                button = KeyButton(key)
                button.setProperty('group', group_name)
                if self.config.battle_keys[group_name] == key:
                    button.setChecked(True)
                button.clicked.connect(lambda checked, k=key, g=group_name: self._update_battle_key(k, g))
                button_group.addWidget(button)
            
            group_layout.addLayout(button_group)
            battle_keys_layout.addLayout(group_layout)
        
        battle_keys_group.setLayout(battle_keys_layout)
        self.layout_configurar.addWidget(battle_keys_group)
    
    def _update_battle_key(self, key: str, group: str):
        button = self.sender()
        is_checked = button.isChecked()
        
        if not is_checked:
            self.config.battle_keys[group] = ''
            return
        
        self.config.battle_keys[group] = key
        
        parent = button.parent()
        for other_button in parent.findChildren(KeyButton):
            if other_button != button and other_button.property('group') == group:
                other_button.setChecked(False)
    
    def _save_config(self):
        self.config.resolution = self.resolucao_combobox.currentText()
        self.config.telegram_interval = self.interval_spinbox.value()
        self.config.bot_token = self.token_input.text()
        self.config.chat_id = self.chat_input.text()
        self.config.digivolution_type = self.digievolucao_combobox.currentText()
        
        self.config.save()
        self.main_window.update_config(self.config)
    
    def _load_config(self):
        self.config = Config.load()
        
        # Atualiza a interface com as configurações carregadas
        self.resolucao_combobox.setCurrentText(self.config.resolution)
        self.interval_spinbox.setValue(self.config.telegram_interval)
        self.token_input.setText(self.config.bot_token)
        self.chat_input.setText(self.config.chat_id)
        self.digievolucao_combobox.setCurrentText(self.config.digivolution_type)
        
        # Atualiza os botões de teclas
        for button in self.findChildren(KeyButton):
            group = button.property('group')
            if group and self.config.battle_keys[group] == button.text():
                button.setChecked(True)
            else:
                button.setChecked(False)
    
    def _get_group_style(self):
        return """
            QGroupBox {
                background-color: white;
                border-radius: 10px;
                padding: 20px;
                color: #4682B4;
            }
        """
    
    def _get_button_style(self, background_color):
        return f"""
            QPushButton {{
                background-color: {background_color};
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 16px;
                font-size: 14px;
                font-weight: bold;
                margin: 5px;
            }}
            QPushButton:hover {{
                background-color: {background_color}dd;
            }}
        """