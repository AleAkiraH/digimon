import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QMessageBox, QVBoxLayout, 
    QHBoxLayout, QWidget, QLabel, QPushButton, QComboBox, QGroupBox, QTabWidget, 
    QLineEdit, QScrollArea, QFrame, QProgressBar)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer, QObject
from PyQt5.QtGui import QPixmap, QImage

import pyautogui
import time
import keyboard
import win32gui
import win32con
import os
from PIL import ImageGrab
import io
from datetime import datetime, timedelta

# Importe as funções e variáveis necessárias dos outros arquivos
from variables import WINDOW_NAME, RESOLUCAO_PADRAO, SCREENSHOTS_DIR, IMAGE_PATHS, APP_STATES
from functions import log, is_image_on_screen, dividir_e_desenhar_contornos, initiate_battle, battle_actions, refill_digimons
from database import Database

class AutomationWorker(QObject):
    finished = pyqtSignal()

    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window

    def run(self):
        self.main_window.start_automation()
        self.finished.emit()

class LoginThread(QThread):
    finished = pyqtSignal(bool, str)
    progress = pyqtSignal(int)

    def __init__(self, db, username, password):
        super().__init__()
        self.db = db
        self.username = username
        self.password = password

    def run(self):
        try:
            # Emite progresso de acordo com as etapas concluídas
            self.progress.emit(10)  # 10% ao iniciar o processo de login

            version_valid, version_error = self.db.validate_version()
            if not version_valid:
                self.finished.emit(False, version_error)
                return
            self.progress.emit(30)  # 30% após validação da versão

            is_valid, error_message = self.db.validate_user(self.username, self.password)
            if not is_valid:
                self.finished.emit(False, error_message if error_message else "Credenciais inválidas!")
                return
            self.progress.emit(60)  # 60% após validação do usuário

            # Emite sucesso
            self.progress.emit(90)  # 90% antes de finalizar com sucesso
            self.finished.emit(True, None)
            self.progress.emit(99)  # 99% após login bem-sucedido

        except Exception as e:
            self.finished.emit(False, f"Erro ao conectar ao banco de dados: {str(e)}")

class AutomationThread(QThread):
    status_update = pyqtSignal(str)
    time_update = pyqtSignal(str)
    battles_update = pyqtSignal(int)
    battles_per_minute_update = pyqtSignal(float)  # New signal
    
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.is_running = True
        self.is_paused = False
        self.battles_count = 0
        self.start_time = datetime.now()  # Changed to datetime
        self.last_battle_time = self.start_time
    
    def run(self):   
        while self.is_running:
            if self.is_paused:
                time.sleep(0.1)
                continue
            
            try:
                if is_image_on_screen(IMAGE_PATHS['captcha_exists']):
                    
                    dividir_e_desenhar_contornos()
                
                elapsed_time = (datetime.now() - self.start_time).total_seconds()
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
                    
                    if is_image_on_screen(IMAGE_PATHS['captcha_exists']):
                        dividir_e_desenhar_contornos()
                        
                    initiate_battle(IMAGE_PATHS['battle_detection'], self.main_window.battle_keys)
                    
                    if is_image_on_screen(IMAGE_PATHS['captcha_exists']):
                        dividir_e_desenhar_contornos()
                        
                    battle_actions(IMAGE_PATHS['battle_detection'], IMAGE_PATHS['battle_finish'], self.main_window.battle_keys)
                    self.battles_count += 1
                    current_time = datetime.now()
                    elapsed_time = (current_time - self.start_time).total_seconds() / 60  # in minutes
                    battles_per_minute = self.battles_count / elapsed_time if elapsed_time > 0 else 0
                    self.battles_per_minute_update.emit(battles_per_minute)
                    
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
            
            current_time = datetime.now()
            elapsed_time = current_time - self.start_time
            elapsed_time_str = str(elapsed_time).split('.')[0]  # Remove microseconds
            self.time_update.emit(elapsed_time_str)
            self.battles_update.emit(self.battles_count)
            time.sleep(0.1)  # Previne uso excessivo de CPU

    def stop(self):
        self.is_running = False
        
    def pause(self):
        self.is_paused = True
        
    def resume(self):
        self.is_paused = False

    def reset(self): # Added reset method
        self.start_time = datetime.now()
        self.battles_count = 0
        self.last_battle_time = self.start_time

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
        self.current_user = None
        self.automation_thread = None
        self.app_state = APP_STATES['STOPPED']
        self.license_expiration = None

        self.battle_keys = {
            'group1': '',
            'group2': '',
            'group3': ''
        }

        self.db = Database()

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

        # Add progress bar after the password input
        self.login_progress = QProgressBar()
        self.login_progress.setStyleSheet("""
            QProgressBar {
                border: 2px solid #e0e0e0;
                border-radius: 5px;
                text-align: center;
                height: 25px;
            }
            QProgressBar::chunk {
                background-color: #4CAF50;
                border-radius: 3px;
            }
        """)
        self.login_progress.hide()  # Initially hidden
        form_layout.addWidget(self.login_progress)

        # Add status label
        self.login_status = QLabel("")
        self.login_status.setStyleSheet("""
            color: #666;
            font-size: 14px;
            margin-top: 5px;
        """)
        self.login_status.setAlignment(Qt.AlignCenter)
        self.login_status.hide()  # Initially hidden
        form_layout.addWidget(self.login_status)
        
        # Login button
        self.login_button = QPushButton("Login")
        self.login_button.setCursor(Qt.PointingHandCursor)
        self.login_button.setStyleSheet("""
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
        self.login_button.clicked.connect(self.authenticate)
        form_layout.addWidget(self.login_button)
        
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

        self.time_label = QLabel("Tempo decorrido: 00:00:00")
        self.time_label.setStyleSheet("""
            font-size: 14px;
            color: #666;
            margin: 5px 0;
        """)
        self.time_label.setAlignment(Qt.AlignCenter)
        content_layout.addWidget(self.time_label)

        self.battles_label = QLabel("Batalhas realizadas: 0")
        self.battles_label.setStyleSheet("""
            font-size: 14px;
            color: #666;
            margin: 5px 0;
        """)
        self.battles_label.setAlignment(Qt.AlignCenter)
        content_layout.addWidget(self.battles_label)
        
        # Add new label for battles per minute
        self.battles_per_minute_label = QLabel("Batalhas por minuto: 0.00")
        self.battles_per_minute_label.setStyleSheet("""
            font-size: 14px;
            color: #666;
            margin: 5px 0;
        """)
        self.battles_per_minute_label.setAlignment(Qt.AlignCenter)
        content_layout.addWidget(self.battles_per_minute_label)

        # License information label
        self.license_info_label = QLabel("Informações da licença não disponíveis")
        self.license_info_label.setStyleSheet("""
            font-size: 14px;
            color: #666;
            margin: 10px 0;
        """)
        self.license_info_label.setAlignment(Qt.AlignCenter)
        content_layout.addWidget(self.license_info_label)

        # Buttons container
        buttons_container = QWidget()
        buttons_layout = QHBoxLayout(buttons_container)
        
        # Start/Stop button
        self.start_stop_button = QPushButton("Iniciar Automação")
        self.start_stop_button.setStyleSheet("""
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
        self.start_stop_button.clicked.connect(self.toggle_automation)
        self.start_stop_button.clicked.connect(self.escolher_resolucao)
        buttons_layout.addWidget(self.start_stop_button)
        
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
        self.layout_configurar.addWidget(general_group)

        # Adiciona diretamente a configuração das teclas sem a group box
        self.setup_battle_keys_config(self.layout_configurar)

        capture_group = QGroupBox("Captura de Imagens")
        capture_layout = QVBoxLayout()
        capture_group.setLayout(capture_layout)
        self.mensagem_info = QLabel("Certifique-se de que a tela de informações do Digimon está aberta!")
        self.mensagem_info.setStyleSheet("font-style: italic; font-size: 16px; color: #4682B4;")
        capture_layout.addWidget(self.mensagem_info)
        self.setup_capture_cards(capture_layout)
        self.layout_configurar.addWidget(capture_group)

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
        battle_keys_layout = QVBoxLayout()

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

        layout.addLayout(battle_keys_layout)

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

    def authenticate(self):
        username = self.username_input.text().lower()
        password = self.password_input.text()

        # Oculta o botão de login imediatamente após o clique
        self.login_button.hide()

        # Mostra a barra de progresso e o status label
        self.login_progress.show()
        self.login_status.show()
        self.login_progress.setValue(10)  # Inicia a barra de progresso em 10%
        self.login_status.setText("Validando credenciais...")

        # Cria e inicia a thread de login
        self.login_thread = LoginThread(self.db, username, password)
        self.login_thread.finished.connect(self.handle_login_result)
        self.login_thread.progress.connect(self.login_progress.setValue)
        self.login_thread.start()

    def handle_login_result(self, success, error_message):
        # Exibe o botão de login novamente

        if success:
            self.login_progress.setValue(99)  # Preenche a barra de progresso
            self.login_status.setText("Login realizado com sucesso!")
            self.is_authenticated = True
            self.current_user = self.username_input.text().lower()
            self.license_expiration = self.db.get_license_expiration(self.current_user)
            self.tabs.setTabEnabled(1, True)
            self.tabs.setTabEnabled(2, True)
            self.tabs.setCurrentIndex(1)  # Muda para a aba "Jogar" após o login
            self.update_license_info()
            self.db.record_action(self.current_user, "login")
            QMessageBox.information(self, "Sucesso", "Login realizado com sucesso!")
        else:
            self.login_status.setText("Falha no login.")
            QMessageBox.warning(self, "Erro", error_message if error_message else "Credenciais inválidas!")
        
        # Esconde a barra de progresso após o login
        self.login_progress.hide()
        self.login_status.hide()
        self.login_button.show()

    def closeEvent(self, event):
        if hasattr(self, 'db'):
            self.db.close()
        super().closeEvent(event)

    def toggle_automation(self):
        self.start_stop_button.hide()  # Esconde o botão imediatamente após o clique
        QTimer.singleShot(100, self._start_automation_thread)  # Aguarda um breve momento antes de iniciar a automação  # Aguarda um breve momento antes de iniciar a automação

    def _start_automation_thread(self):
        if self.app_state == APP_STATES['STOPPED']:
            self.start_automation_thread = QThread()
            self.start_automation_worker = AutomationWorker(self)
            self.start_automation_worker.moveToThread(self.start_automation_thread)
            
            self.start_automation_thread.started.connect(self.start_automation_worker.run)
            self.start_automation_worker.finished.connect(self.start_automation_thread.quit)
            self.start_automation_worker.finished.connect(self.start_automation_worker.deleteLater)
            self.start_automation_thread.finished.connect(self.start_automation_thread.deleteLater)
            
            self.start_automation_worker.finished.connect(self.on_automation_started)
            
            self.start_automation_thread.start()
        else:
            self.stop_automation()

    def on_automation_started(self):
        self.start_stop_button.show()
        
    def hide_start_stop_button(self):
        self.start_stop_button.hide()
    
    def start_automation(self):
        if not self.is_authenticated:
            QMessageBox.warning(self, "Erro", "Por favor, autentique-se primeiro!")
            self.start_stop_button.show()  # Mostra o botão novamente em caso de erro
            return

        self.db.record_action(self.current_user, "inicio automacao")
        self.app_state = APP_STATES['RUNNING']
        self.start_stop_button.setText("Parar Automação")
        self.start_stop_button.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 12px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c82333;
            }
        """)
        self.status_label.setText("Status: Em execução")

        if self.automation_thread is None:
            self.automation_thread = AutomationThread(self)
            self.automation_thread.status_update.connect(self.update_status)
            self.automation_thread.time_update.connect(self.update_time)
            self.automation_thread.battles_update.connect(self.update_battles)
            self.automation_thread.battles_per_minute_update.connect(self.update_battles_per_minute)
            self.automation_thread.start()
        else:
            self.automation_thread.reset()
            self.automation_thread.resume()

        self.update_time("00:00:00")
        self.update_battles(0)
        self.update_battles_per_minute(0.00)
        self.start_stop_button.show()  # Mostra o botão "Parar Automação" ao final

    def start_automation(self):
        if not self.is_authenticated:
            QMessageBox.warning(self, "Erro", "Por favor, autentique-se primeiro!")
            self.start_stop_button.show()  # Mostra o botão novamente em caso de erro
            return

        self.db.record_action(self.current_user, "inicio automacao")
        self.app_state = APP_STATES['RUNNING']
        self.start_stop_button.setText("Parar Automação")
        self.start_stop_button.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 12px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c82333;
            }
        """)
        self.status_label.setText("Status: Em execução")

        if self.automation_thread is None:
            self.automation_thread = AutomationThread(self)
            self.automation_thread.status_update.connect(self.update_status)
            self.automation_thread.time_update.connect(self.update_time)
            self.automation_thread.battles_update.connect(self.update_battles)
            self.automation_thread.battles_per_minute_update.connect(self.update_battles_per_minute)
            self.automation_thread.start()
        else:
            self.automation_thread.reset()
            self.automation_thread.resume()

        self.update_time("00:00:00")
        self.update_battles(0)
        self.update_battles_per_minute(0.00)
        
    def stop_automation(self):
        if self.automation_thread:
            self.automation_thread.stop()
            self.automation_thread.terminate()
            self.automation_thread.wait()
            self.automation_thread = None

        self.app_state = APP_STATES['STOPPED']
        self.start_stop_button.setText("Iniciar Automação")
        self.start_stop_button.setStyleSheet("""
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
        self.start_stop_button.show()  # Mostra o botão "Iniciar Automação"
        self.status_label.setText("Status: Parado")
        self.update_time("00:00:00")
        self.update_battles(0)
        self.update_battles_per_minute(0.00)

    def update_status(self, message):
        self.status_label.setText(f"Status: {message}")

    def update_time(self, time_str):
        self.time_label.setText(f"Tempo decorrido: {time_str}")

    def update_battles(self, battles):
        self.battles_label.setText(f"Batalhas realizadas: {battles}")

    def update_battles_per_minute(self, battles_per_minute):
        self.battles_per_minute_label.setText(f"Batalhas por minuto: {battles_per_minute:.2f}")

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
        hwnd = win32gui.FindWindow(None, WINDOW_NAME)
        if hwnd == 0:
            QMessageBox.warning(self, "Erro", f"Janela '{WINDOW_NAME}' não encontrada.")
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

    def carregar_imagens(self):
        for i, card in enumerate(self.cards):
            image_path = os.path.join(SCREENSHOTS_DIR, self.image_filenames[i])
            if os.path.exists(image_path):
                imagem = QImage(image_path)
                pixmap = QPixmap.fromImage(imagem)
                scaled_pixmap = pixmap.scaled(150, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                card.label.setPixmap(scaled_pixmap)

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

    def update_license_info(self):
        if self.license_expiration:
            days_left = (self.license_expiration - datetime.now().date()).days
            expiration_text = f"Sua licença expira em {self.license_expiration.strftime('%d/%m/%Y')}"
            days_left_text = f"Faltam {days_left} dias para sua licença expirar"
            self.license_info_label.setText(f"{expiration_text}\n{days_left_text}")
        else:
            self.license_info_label.setText("Informações da licença não disponíveis")