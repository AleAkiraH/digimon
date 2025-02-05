import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QVBoxLayout, QHBoxLayout, QWidget, QLabel, QPushButton, QComboBox, QGroupBox, QTabWidget, QLineEdit, QScrollArea, QFrame
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QPixmap, QImage

import pyautogui
import time
import keyboard
import win32gui
import win32con
import os
from PIL import ImageGrab
import io

# Importe as funções e variáveis necessárias dos outros arquivos
from variables import WINDOW_NAME, RESOLUCAO_PADRAO, SCREENSHOTS_DIR, IMAGE_PATHS, APP_STATES
from functions import log, is_image_on_screen, dividir_e_desenhar_contornos, initiate_battle, battle_actions, refill_digimons

class AutomationThread(QThread):
    status_update = pyqtSignal(str)
    
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.is_running = True
        self.is_paused = False
        
    def run(self):
        start_time = time.time()
        while self.is_running:
            if self.is_paused:
                time.sleep(0.1)
                continue

            try:
                if is_image_on_screen(IMAGE_PATHS['captcha_exists']):
                    dividir_e_desenhar_contornos()
                
                elapsed_time = time.time() - start_time
                elapsed_hours = int(elapsed_time // 3600)
                elapsed_minutes = int((elapsed_time % 3600) // 60)
                elapsed_seconds = int(elapsed_time % 60)
                elapsed_time_str = f"{elapsed_hours:02}:{elapsed_minutes:02}:{elapsed_seconds:02}"

                self.status_update.emit("Automação principal em execução...")
                
                for _ in range(3):
                    if is_image_on_screen(IMAGE_PATHS['captcha_exists']):
                        dividir_e_desenhar_contornos()
                
                time.sleep(1)
                for _ in range(4):
                    pyautogui.press('g')
                pyautogui.press('v')
                time.sleep(1)

                if is_image_on_screen(IMAGE_PATHS['captcha_exists']):
                    dividir_e_desenhar_contornos()
                
                self.status_update.emit("Tela de digimons aberta...")
                if is_image_on_screen(IMAGE_PATHS['evp_terminado']):
                    location = pyautogui.locateCenterOnScreen(IMAGE_PATHS['evp_terminado'], confidence=0.97)
                    if location:
                        x, y = location
                        pyautogui.click(x, y)
                        time.sleep(0.5)
                        pyautogui.press('e')

                battle_start_image_HP_Try = 3
                while not is_image_on_screen(IMAGE_PATHS['battle_start_hp']) and self.is_running and not self.is_paused:
                    if is_image_on_screen(IMAGE_PATHS['captcha_exists']):
                        dividir_e_desenhar_contornos()
                    if battle_start_image_HP_Try == 0:
                        self.status_update.emit("Imagem de inicio de batalha não encontrada.")
                        if not is_image_on_screen(IMAGE_PATHS['janela_digimon']):
                            pyautogui.press('v')                        
                        break
                    battle_start_image_HP_Try -= 1
                    time.sleep(1)

                if not self.is_running or self.is_paused:
                    continue

                time.sleep(1)
                self.status_update.emit("Buscando imagem de inicio de batalha")
                
                if all(is_image_on_screen(IMAGE_PATHS[img]) for img in ['battle_start_hp', 'battle_start_sp', 'battle_start_evp']):
                    self.status_update.emit("Imagem de início de batalha detectada.")                
                    pyautogui.press('i')
                    
                    if keyboard.is_pressed('r'):
                        self.status_update.emit(f"Bot encerrado. Tempo de execução: {elapsed_time_str}")
                        break
                    
                    if is_image_on_screen(IMAGE_PATHS['captcha_exists']):
                        dividir_e_desenhar_contornos()
                        
                    initiate_battle(IMAGE_PATHS['battle_detection'], self.main_window.battle_keys)
                    
                    if is_image_on_screen(IMAGE_PATHS['captcha_exists']):
                        dividir_e_desenhar_contornos()
                        
                    battle_actions(IMAGE_PATHS['battle_detection'], IMAGE_PATHS['battle_finish'], self.main_window.battle_keys)
                    
                    if is_image_on_screen(IMAGE_PATHS['captcha_exists']):
                        dividir_e_desenhar_contornos()
                else:
                    if not is_image_on_screen(IMAGE_PATHS['battle_start_evp']):
                        pyautogui.press('v')
                        for _ in range(35):
                            if not self.is_running or self.is_paused:
                                break
                            if is_image_on_screen(IMAGE_PATHS['captcha_exists']):
                                dividir_e_desenhar_contornos()
                            pyautogui.press('5')
                            time.sleep(0.5)                       
                        pyautogui.press('v')
                    refill_digimons(self.main_window.digievolucao_combobox.currentText())
                    
            except Exception as e:
                self.status_update.emit(f"Erro na automação: {str(e)}")
            
            time.sleep(0.1)  # Previne uso excessivo de CPU

    def stop(self):
        self.is_running = False
        
    def pause(self):
        self.is_paused = True
        
    def resume(self):
        self.is_paused = False

class KeyButton(QPushButton):
    def __init__(self, key, parent=None):
        super().__init__(key, parent)
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

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Digimon Automation")
        self.setGeometry(100, 100, 800, 600)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f0f0f0;
            }
            QTabWidget::pane {
                border: none;
                background-color: #ffffff;
            }
            QTabWidget::tab-bar {
                alignment: center;
            }
            QTabBar::tab {
                background-color: #4682B4;
                color: white;
                padding: 10px 20px;
                margin: 2px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                font-size: 14px;
                min-width: 120px;
            }
            QTabBar::tab:selected {
                background-color: #1E90FF;
            }
            QPushButton {
                background-color: #4682B4;
                color: white;
                border: none;
                padding: 10px;
                border-radius: 5px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #1E90FF;
            }
            QComboBox {
                background-color: white;
                border: 1px solid #4682B4;
                border-radius: 5px;
                padding: 5px;
                min-width: 100px;
            }
            QLabel {
                color: #333333;
                font-size: 14px;
            }
            QGroupBox {
                font-size: 18px;
                font-weight: bold;
                border: 2px solid #4682B4;
                border-radius: 5px;
                margin-top: 20px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        
        self.is_authenticated = False
        self.automation_thread = None
        self.app_state = APP_STATES['STOPPED']
        
        self.battle_keys = {
            'group1': '',
            'group2': '',
            'group3': ''
        }
        
        self.setup_ui()
        self.carregar_imagens()

    def setup_ui(self):
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        self.tabs = QTabWidget()
        self.layout.addWidget(self.tabs)
        
        self.setup_auth_tab()
        self.setup_play_tab()
        self.setup_config_tab()
        
        self.tabs.setTabEnabled(1, False)
        self.tabs.setTabEnabled(2, False)

    def setup_auth_tab(self):
        self.tab_auth = QWidget()
        self.tabs.addTab(self.tab_auth, "Login")
        
        # Main container with fixed width
        container = QWidget()
        container.setFixedWidth(400)
        container_layout = QVBoxLayout(container)
        container_layout.setAlignment(Qt.AlignCenter)
        container_layout.setSpacing(20)
        
        # Center the container
        main_layout = QHBoxLayout(self.tab_auth)
        main_layout.addWidget(container)
        
        # Logo and title
        title_label = QLabel("Digimon Automation")
        title_label.setStyleSheet("""
            font-size: 28px;
            font-weight: bold;
            color: #4682B4;
            margin: 20px 0;
        """)
        title_label.setAlignment(Qt.AlignCenter)
        container_layout.addWidget(title_label)
        
        # Login form
        login_form = QGroupBox()
        login_form.setStyleSheet("""
            QGroupBox {
                background-color: white;
                border-radius: 10px;
                padding: 20px;
            }
        """)
        form_layout = QVBoxLayout(login_form)
        form_layout.setSpacing(15)
        
        # Username
        username_label = QLabel("Username")
        username_label.setStyleSheet("color: #666; font-size: 14px;")
        form_layout.addWidget(username_label)
        
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Enter your username")
        self.username_input.setStyleSheet("""
            QLineEdit {
                padding: 12px;
                border: 2px solid #e0e0e0;
                border-radius: 5px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border-color: #4682B4;
            }
        """)
        form_layout.addWidget(self.username_input)
        
        # Password
        password_label = QLabel("Password")
        password_label.setStyleSheet("color: #666; font-size: 14px;")
        form_layout.addWidget(password_label)
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Enter your password")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setStyleSheet("""
            QLineEdit {
                padding: 12px;
                border: 2px solid #e0e0e0;
                border-radius: 5px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border-color: #4682B4;
            }
        """)
        form_layout.addWidget(self.password_input)
        
        # Login button
        login_button = QPushButton("Login")
        login_button.setCursor(Qt.PointingHandCursor)
        login_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 12px;
                font-size: 16px;
                font-weight: bold;
                margin-top: 10px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        login_button.clicked.connect(self.authenticate)
        form_layout.addWidget(login_button)
        
        container_layout.addWidget(login_form)
        container_layout.addStretch()

    def setup_play_tab(self):
        self.tab_jogar = QWidget()
        self.tabs.addTab(self.tab_jogar, "Jogar")
        
        # Main container with fixed width
        container = QWidget()
        container.setFixedWidth(400)
        container_layout = QVBoxLayout(container)
        container_layout.setAlignment(Qt.AlignCenter)
        container_layout.setSpacing(20)
        
        # Center the container
        main_layout = QHBoxLayout(self.tab_jogar)
        main_layout.addWidget(container)
        
        # Title
        title_label = QLabel("Digimon Automation")
        title_label.setStyleSheet("""
            font-size: 28px;
            font-weight: bold;
            color: #4682B4;
            margin: 20px 0;
        """)
        title_label.setAlignment(Qt.AlignCenter)
        container_layout.addWidget(title_label)
        
        # Main content group
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
        
        # Description
        description = QLabel("Prepare-se para uma aventura emocionante no mundo dos Digimons!")
        description.setStyleSheet("""
            font-size: 16px;
            color: #666;
            margin-bottom: 20px;
        """)
        description.setAlignment(Qt.AlignCenter)
        description.setWordWrap(True)
        content_layout.addWidget(description)
        
        # Status label
        self.status_label = QLabel("Status: Parado")
        self.status_label.setStyleSheet("""
            font-size: 14px;
            color: #666;
            margin: 10px 0;
        """)
        self.status_label.setAlignment(Qt.AlignCenter)
        content_layout.addWidget(self.status_label)
        
        # Buttons container
        buttons_container = QWidget()
        buttons_layout = QHBoxLayout(buttons_container)
        buttons_layout.setSpacing(10)
        
        # Start button
        self.start_button = QPushButton("Iniciar Automação")
        self.start_button.setStyleSheet("""
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
        """)
        self.start_button.clicked.connect(self.toggle_automation)
        buttons_layout.addWidget(self.start_button)
        
        # Pause button
        self.pause_button = QPushButton("Pausar")
        self.pause_button.setStyleSheet("""
            QPushButton {
                background-color: #FFA500;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 12px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #FF8C00;
            }
        """)
        self.pause_button.clicked.connect(self.toggle_pause)
        self.pause_button.setEnabled(False)
        buttons_layout.addWidget(self.pause_button)
        
        content_layout.addWidget(buttons_container)
        container_layout.addWidget(content_group)
        container_layout.addStretch()

    def setup_config_tab(self):
        self.tab_configurar = QWidget()
        self.tabs.addTab(self.tab_configurar, "Configurar")
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_area.setWidget(scroll_content)
        
        self.layout_configurar = QVBoxLayout(scroll_content)
        self.layout_configurar.setAlignment(Qt.AlignTop)
        self.layout_configurar.setSpacing(20)
        
        main_layout = QVBoxLayout(self.tab_configurar)
        main_layout.addWidget(scroll_area)
        title_label = QLabel("Configurações")
        title_label.setStyleSheet("""
            font-size: 28px;
            font-weight: bold;
            color: #4682B4;
            margin: 20px 0;
        """)
        title_label.setAlignment(Qt.AlignCenter)
        self.layout_configurar.addWidget(title_label)
        
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
        
        self.setup_resolution_config(general_layout)
        self.setup_digievolution_config(general_layout)
        self.setup_battle_keys_config(general_layout)
        self.layout_configurar.addWidget(general_group)

        capture_group = QGroupBox("Captura de Imagens")
        capture_layout = QVBoxLayout()
        capture_group.setLayout(capture_layout)
        self.mensagem_info = QLabel("Certifique-se de que a tela de informações do Digimon está aberta!")
        self.mensagem_info.setStyleSheet("font-style: italic; font-size: 16px; color: #4682B4;")
        capture_layout.addWidget(self.mensagem_info)
        self.setup_capture_cards(capture_layout)
        self.layout_configurar.addWidget(capture_group)

    def toggle_automation(self):
        if self.app_state == APP_STATES['STOPPED']:
            self.start_automation()            
        else:
            self.stop_automation()
    
    def toggle_pause(self):
        if self.app_state == APP_STATES['RUNNING']:
            self.pause_automation()
        elif self.app_state == APP_STATES['PAUSED']:
            self.resume_automation()

    def start_automation(self):
        if not self.is_authenticated:
            QMessageBox.warning(self, "Erro", "Por favor, autentique-se primeiro!")
            return

        self.app_state = APP_STATES['RUNNING']
        self.start_button.setText("Parar")
        self.start_button.setStyleSheet("""
            font-size: 16px;
            background-color: #dc3545;
            color: white;
            border-radius: 5px;
            padding: 12px 24px;
        """)
        self.pause_button.setEnabled(True)
        self.status_label.setText("Status: Em execução")

        self.automation_thread = AutomationThread(self)
        self.automation_thread.status_update.connect(self.update_status)
        self.automation_thread.start()

    def pause_automation(self):
        if self.automation_thread:
            self.app_state = APP_STATES['PAUSED']
            self.automation_thread.pause()
            self.pause_button.setText("Continuar")
            self.status_label.setText("Status: Pausado")

    def resume_automation(self):
        if self.automation_thread:
            self.app_state = APP_STATES['RUNNING']
            self.automation_thread.resume()
            self.pause_button.setText("Pausar")
            self.status_label.setText("Status: Em execução")

    def stop_automation(self):
        if self.automation_thread:
            self.automation_thread.stop()
            self.automation_thread.wait()
            self.automation_thread = None

        self.app_state = APP_STATES['STOPPED']
        self.start_button.setText("Iniciar Automação")
        self.start_button.setStyleSheet("""
            font-size: 16px;
            background-color: #4CAF50;
            color: white;
            border-radius: 5px;
            padding: 12px 24px;
        """)
        self.pause_button.setEnabled(False)
        self.pause_button.setText("Pausar")
        self.status_label.setText("Status: Parado")

    def update_status(self, message):
        self.status_label.setText(f"Status: {message}")

    def run_automation_cycle(self, start_time):
        # Move the automation logic from executar_script here
        # This is the same code as before, just moved to a new method
        if is_image_on_screen(IMAGE_PATHS['captcha_exists']):
            dividir_e_desenhar_contornos()
        
        elapsed_time = time.time() - start_time
        elapsed_hours = int(elapsed_time // 3600)
        elapsed_minutes = int((elapsed_time % 3600) // 60)
        elapsed_seconds = int(elapsed_time % 60)
        elapsed_time_str = f"{elapsed_hours:02}:{elapsed_minutes:02}:{elapsed_seconds:02}"

        log("Automação principal em execução...")
        
        for _ in range(3):
            if is_image_on_screen(IMAGE_PATHS['captcha_exists']):
                dividir_e_desenhar_contornos()
        
        time.sleep(1)
        for _ in range(4):
            pyautogui.press('g')
        pyautogui.press('v')
        time.sleep(1)
        
    def setup_resolution_config(self, layout):
        config_layout = QHBoxLayout()
        layout.addLayout(config_layout)

        label_resolucao = QLabel("Resolução do Jogo:")
        label_resolucao.setFixedWidth(150)
        config_layout.addWidget(label_resolucao)

        self.resolucao_combobox = QComboBox()
        self.resolucao_combobox.addItems(["800x600", "1024x768"])
        self.resolucao_combobox.setFixedWidth(120)
        self.resolucao_combobox.currentIndexChanged.connect(self.escolher_resolucao)
        config_layout.addWidget(self.resolucao_combobox)
        config_layout.addStretch()

    def setup_digievolution_config(self, layout):
        digievolucao_layout = QHBoxLayout()
        layout.addLayout(digievolucao_layout)

        label_digievolucao = QLabel("Digievolução:")
        label_digievolucao.setFixedWidth(150)
        digievolucao_layout.addWidget(label_digievolucao)

        self.digievolucao_combobox = QComboBox()
        self.digievolucao_combobox.addItems(["mega", "ultimate", "champion", "rookie"])
        self.digievolucao_combobox.setFixedWidth(120)
        self.digievolucao_combobox.currentIndexChanged.connect(self.atualizar_digievolucao)
        digievolucao_layout.addWidget(self.digievolucao_combobox)
        digievolucao_layout.addStretch()

    def setup_battle_keys_config(self, layout):
        battle_keys_group = QGroupBox("Configuração de Teclas de Batalha")
        battle_keys_layout = QVBoxLayout()
        battle_keys_group.setLayout(battle_keys_layout)

        # Define the key groups
        key_groups = [
            ('group1', ['Q', 'W', 'E']),
            ('group2', ['A', 'S', 'D']),
            ('group3', ['Z', 'X', 'C'])
        ]

        # Create buttons for each group
        for group_name, keys in key_groups:
            group_layout = QHBoxLayout()
            
            # Add group label
            label = QLabel(f"Grupo {group_name[-1]}:")
            label.setFixedWidth(100)
            group_layout.addWidget(label)

            # Create button group to handle exclusive selection within group
            button_group = QHBoxLayout()
            
            # Create buttons for each key in the group
            for key in keys:
                button = KeyButton(key)
                button.setProperty('group', group_name)  # Store group name as property
                button.clicked.connect(lambda checked, k=key, g=group_name: self.update_battle_key(k, g))
                button_group.addWidget(button)

            group_layout.addLayout(button_group)
            battle_keys_layout.addLayout(group_layout)

        layout.addWidget(battle_keys_group)

    def update_battle_key(self, key, group):
        button = self.sender()
        is_checked = button.isChecked()

        # If the button was unchecked, clear the key for this group
        if not is_checked:
            self.battle_keys[group] = ''
            return

        # Update the key for this group
        self.battle_keys[group] = key

        # Uncheck other buttons in the same group
        parent = button.parent()
        for other_button in parent.findChildren(KeyButton):
            if other_button != button and other_button.property('group') == group:
                other_button.setChecked(False)

        # Print current state of battle keys
        print("Current battle keys:", self.battle_keys)

    def setup_capture_cards(self, layout):
        self.image_filenames = [
            "battle_start_hp.png",
            "battle_start_sp.png",
            "battle_start_evp.png",
            "battle_finish.png",
            "janela_digimon.png",
            "battle_detection.png"
        ]
        
        self.coordenadas = [
            (503, 377, 596, 393),
            (503, 417, 563, 433),
            (503, 459, 521, 475),
            (468, 565, 485, 576),
            (503, 192, 666, 203),
            (768, 541, 779, 554)
        ]

        os.makedirs(SCREENSHOTS_DIR, exist_ok=True)

        self.cards = []
        cards_layout = QHBoxLayout()
        cards_layout.setAlignment(Qt.AlignCenter)
        cards_layout.setSpacing(20)
        
        for i in range(len(self.image_filenames)):
            card = self.create_card(i)
            self.cards.append(card)
            cards_layout.addWidget(card)
            
            if (i + 1) % 3 == 0 or i == len(self.image_filenames) - 1:
                layout.addLayout(cards_layout)
                cards_layout = QHBoxLayout()
                cards_layout.setAlignment(Qt.AlignCenter)
                cards_layout.setSpacing(20)

    def create_card(self, index):
        card = QFrame()
        card.setStyleSheet("""
            background-color: #ffffff;
            border: 2px solid #4682B4;
            border-radius: 10px;
            padding: 10px;
        """)
        card_layout = QVBoxLayout(card)
        title = QLabel(f"{index + 1} - {self.get_title(index)}")
        title.setStyleSheet("font-size: 12px; font-weight: bold; color: #4682B4;")
        title.setWordWrap(True)
        title.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(title)
        label = QLabel(self)
        label.setFixedSize(150, 100)
        label.setStyleSheet("background-color: #f0f0f0; border: 1px solid #cccccc;")
        label.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(label)
        
        botao_captura = QPushButton("Capturar")
        botao_captura.setStyleSheet("""
            font-size: 12px;
            background-color: #4682B4;
            color: white;
            border-radius: 5px;
            padding: 5px;
        """)
        botao_captura.setCursor(Qt.PointingHandCursor)
        botao_captura.clicked.connect(lambda checked, idx=index: self.capturar_imagem(idx))
        card_layout.addWidget(botao_captura)
        
        card.label = label
        
        return card

    def get_title(self, index):
        titles = [
            "HP digimon na tela de informações do digimon",
            "SP digimon na tela de informações do digimon",
            "EVP digimon na tela de informações do digimon",
            "Item no 5 * atalho de itens",
            "Seção de descrição dos status do digimon",
            "3* item de batalha dentro da batalha digimon"
        ]
        return titles[index] if index < len(titles) else "Título Desconhecido"

    def escolher_resolucao(self):
        resolucao_selecionada = self.resolucao_combobox.currentText()
        largura, altura = map(int, resolucao_selecionada.split("x"))
        
        hwnd = win32gui.FindWindow(None, 'Digimon SuperRumble  ')
        if hwnd == 0:
            QMessageBox.warning(self, "Erro", "Janela 'Digimon SuperRumble' não encontrada.")
            return
            
        style = win32gui.GetWindowLong(hwnd, win32con.GWL_STYLE)
        win32gui.SetWindowLong(hwnd, win32con.GWL_STYLE, style & ~win32con.WS_BORDER)
        win32gui.SetWindowPos(hwnd, 0, 0, 0, largura, altura,
                            win32con.SWP_NOZORDER | win32con.SWP_FRAMECHANGED)

    def atualizar_digievolucao(self):
        digievolucao = self.digievolucao_combobox.currentText()
        print(f"Digievolução selecionada: {digievolucao}")

    def capturar_imagem(self, index):
        imagem_data = self.capturar_tela_e_salvar(*self.coordenadas[index])
        if imagem_data:
            imagem = QImage.fromData(imagem_data)
            pixmap = QPixmap(imagem)
            self.cards[index].label.setPixmap(pixmap)
            
            filename = os.path.join(SCREENSHOTS_DIR, self.image_filenames[index])
            with open(filename, 'wb') as f:
                f.write(imagem_data)

    def capturar_tela_e_salvar(self, x_inicio, y_inicio, x_fim, y_fim):
        hwnd = win32gui.FindWindow(None, 'Digimon SuperRumble  ')
        if hwnd == 0:
            QMessageBox.warning(self, "Erro", "Janela 'Digimon SuperRumble' não encontrada.")
            return None

        resolucao_selecionada = self.resolucao_combobox.currentText()
        largura, altura = map(int, resolucao_selecionada.split("x"))
        
        proporcao_x = largura / RESOLUCAO_PADRAO[0]
        proporcao_y = altura / RESOLUCAO_PADRAO[1]
        
        x_inicio = int(x_inicio * proporcao_x)
        y_inicio = int(y_inicio * proporcao_y)
        x_fim = int(x_fim * proporcao_x)
        y_fim = int(y_fim * proporcao_y)
        
        rect = win32gui.GetWindowRect(hwnd)
        client_rect = win32gui.GetClientRect(hwnd)
        x_tela, y_tela = win32gui.ClientToScreen(hwnd, (client_rect[0], client_rect[1]))
        
        x_inicio += x_tela
        y_inicio += y_tela
        x_fim += x_tela
        y_fim += y_tela
        
        try:
            screenshot = ImageGrab.grab(bbox=(x_inicio, y_inicio, x_fim, y_fim))
            buffer = io.BytesIO()
            screenshot.save(buffer, format="PNG")
            return buffer.getvalue()
        except Exception as e:
            print(f"Erro ao capturar a tela: {e}")
            return None

    def carregar_imagens(self):
        for index, filename in enumerate(self.image_filenames):
            filepath = os.path.join(SCREENSHOTS_DIR, filename)
            if os.path.exists(filepath):
                imagem = QImage(filepath)
                pixmap = QPixmap.fromImage(imagem)
                self.cards[index].label.setPixmap(pixmap)

    def authenticate(self):
        username = self.username_input.text()
        password = self.password_input.text()
        
        if username == "Admin" and password == "123":
            self.is_authenticated = True
            self.tabs.setTabEnabled(1, True)
            self.tabs.setTabEnabled(2, True)
            self.tabs.setCurrentIndex(1)  # Muda para a aba "Jogar" após o login
            QMessageBox.information(self, "Sucesso", "Login realizado com sucesso!")
        else:
            QMessageBox.warning(self, "Erro", "Credenciais inválidas!")

    def executar_script(self):
        if not self.is_authenticated:
            QMessageBox.warning(self, "Erro", "Por favor, autentique-se primeiro!")
            return

        start_time = time.time()
        while True:
            if is_image_on_screen(IMAGE_PATHS['captcha_exists']):
                dividir_e_desenhar_contornos()
            elapsed_time = time.time() - start_time
            elapsed_hours = int(elapsed_time // 3600)
            elapsed_minutes = int((elapsed_time % 3600) // 60)
            elapsed_seconds = int(elapsed_time % 60)
            elapsed_time_str = f"{elapsed_hours:02}:{elapsed_minutes:02}:{elapsed_seconds:02}"

            log("Automação principal em execução...")
            
            for _ in range(3):
                if is_image_on_screen(IMAGE_PATHS['captcha_exists']):
                    dividir_e_desenhar_contornos()
            
            time.sleep(1)
            for _ in range(4):
                pyautogui.press('g')
            pyautogui.press('v')
            time.sleep(1)

            if is_image_on_screen(IMAGE_PATHS['captcha_exists']):
                dividir_e_desenhar_contornos()
            
            log("Tela de digimons aberta...")
            if is_image_on_screen(IMAGE_PATHS['evp_terminado']):
                location = pyautogui.locateCenterOnScreen(IMAGE_PATHS['evp_terminado'], confidence=0.97)
                if location:
                    x, y = location
                    pyautogui.click(x, y)
                    time.sleep(0.5)
                    pyautogui.press('e')

            battle_start_image_HP_Try = 3
            while not is_image_on_screen(IMAGE_PATHS['battle_start_hp']):
                if is_image_on_screen(IMAGE_PATHS['captcha_exists']):
                    dividir_e_desenhar_contornos()
                if battle_start_image_HP_Try == 0:
                    log("Imagem de inicio de batalha não encontrada.")
                    if not is_image_on_screen(IMAGE_PATHS['janela_digimon']):
                        pyautogui.press('v')                        
                    break
                battle_start_image_HP_Try -= 1
                time.sleep(1)

            time.sleep(1)
            log("Buscando imagem de inicio de batalha")
            
            if all(is_image_on_screen(IMAGE_PATHS[img]) for img in ['battle_start_hp', 'battle_start_sp', 'battle_start_evp']):
                log("Imagem de início de batalha detectada.")                
                pyautogui.press('i')
                
                if keyboard.is_pressed('r'):
                    log(f"Bot encerrado. Tempo de execução: {elapsed_time_str}")
                    break
                
                if is_image_on_screen(IMAGE_PATHS['captcha_exists']):
                    dividir_e_desenhar_contornos()
                    
                initiate_battle(IMAGE_PATHS['battle_detection'], self.battle_keys)
                
                if is_image_on_screen(IMAGE_PATHS['captcha_exists']):
                    dividir_e_desenhar_contornos()
                    
                battle_actions(IMAGE_PATHS['battle_detection'], IMAGE_PATHS['battle_finish'], self.battle_keys)
                
                if is_image_on_screen(IMAGE_PATHS['captcha_exists']):
                    dividir_e_desenhar_contornos()
            else:
                if not is_image_on_screen(IMAGE_PATHS['battle_start_evp']):
                    pyautogui.press('v')
                    for _ in range(35):
                        if is_image_on_screen(IMAGE_PATHS['captcha_exists']):
                            dividir_e_desenhar_contornos()
                        pyautogui.press('5')
                        time.sleep(0.5)                       
                    pyautogui.press('v')
                refill_digimons(self.digievolucao_combobox.currentText())

