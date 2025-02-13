import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QMessageBox, QVBoxLayout, 
    QHBoxLayout, QWidget, QLabel, QPushButton, QComboBox, QGroupBox, QTabWidget, 
    QLineEdit, QScrollArea, QFrame, QProgressBar, QGridLayout)  # Added QGridLayout
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer, QObject
from PyQt5.QtGui import QPixmap, QImage
from functions import send_screenshot_telegram
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

MODERN_STYLES = {
    'PRIMARY_COLOR': '#2196F3',
    'SECONDARY_COLOR': '#FF4081',
    'SUCCESS_COLOR': '#4CAF50',
    'WARNING_COLOR': '#FFC107',
    'DANGER_COLOR': '#F44336',
    'BACKGROUND_COLOR': '#F5F5F5',
    'SURFACE_COLOR': '#FFFFFF',
    'TEXT_PRIMARY': '#212121',
    'TEXT_SECONDARY': '#757575',
    'BORDER_RADIUS': '8px',
    'GRADIENT_PRIMARY': 'qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #2196F3, stop:1 #1976D2)'
}

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

class TimeUpdateThread(QThread):
    time_update = pyqtSignal(str)
    
    def __init__(self, start_time):
        super().__init__()
        self.start_time = start_time
        self.is_running = True
        
    def run(self):
        while self.is_running:
            current_time = datetime.now()
            elapsed_time = current_time - self.start_time
            elapsed_time_str = str(elapsed_time).split('.')[0]
            self.time_update.emit(elapsed_time_str)
            time.sleep(1)
            
    def stop(self):
        self.is_running = False

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
        self.time_thread = None

    def setup_timer(self):
        # Create timer in the correct thread
        self.update_timer = QTimer()
        self.update_timer.setInterval(1000)  # 1 second
        self.update_timer.timeout.connect(self.update_elapsed_time)
        self.update_timer.start()

    def run(self):   
        # Inicia thread separada para atualização do tempo
        self.time_thread = TimeUpdateThread(self.start_time)
        self.time_thread.time_update.connect(self.main_window.update_time)
        self.time_thread.start()
        
        send_screenshot_telegram(message=f"{self.main_window.current_user}: iniciou automacao!")
        
        while self.is_running:
            try:
                # Force process events to handle timer
                QApplication.processEvents()
                
                if self.is_paused:
                    time.sleep(0.1)
                    continue
                    
                # Validate session
                if not self.main_window.validate_automation_session():
                    self.status_update.emit("Sessão inválida! Automação interrompida.")
                    self.is_running = False
                    break
                    
                try:
                    if is_image_on_screen(IMAGE_PATHS['captcha_exists']):
                        
                        dividir_e_desenhar_contornos(self.main_window.current_user)
                    
                    elapsed_time = (datetime.now() - self.start_time).total_seconds()
                    elapsed_hours = int(elapsed_time // 3600)
                    elapsed_minutes = int((elapsed_time % 3600) // 60)
                    elapsed_seconds = int(elapsed_time % 60)
                    elapsed_time_str = f"{elapsed_hours:02}:{elapsed_minutes:02}:{elapsed_seconds:02}"

                    self.status_update.emit("Automação principal em execução...")
                    
                    for _ in range(3):
                        if is_image_on_screen(IMAGE_PATHS['captcha_exists']):
                            dividir_e_desenhar_contornos(self.main_window.current_user)
                    
                    time.sleep(1)
                    for _ in range(4):
                        pyautogui.press('g')
                    pyautogui.press('v')
                    time.sleep(1)

                    if is_image_on_screen(IMAGE_PATHS['captcha_exists']):
                        dividir_e_desenhar_contornos(self.main_window.current_user)
                    
                    self.status_update.emit("Tela de digimons aberta...")
                    if is_image_on_screen(IMAGE_PATHS['evp_terminado']):
                        location = pyautogui.locateCenterOnScreen(IMAGE_PATHS['evp_terminado'], confidence=0.97)
                        if location:
                            x, y = location
                            pyautogui.click(x, y)
                            time.sleep(0.5)

                    battle_start_image_HP_Try = 3
                    while not is_image_on_screen(IMAGE_PATHS['battle_start_hp'], region=(503, 377, 596, 393)) and self.is_running and not self.is_paused:
                        if is_image_on_screen(IMAGE_PATHS['captcha_exists']):
                            dividir_e_desenhar_contornos(self.main_window.current_user)
                        if battle_start_image_HP_Try == 0:
                            self.status_update.emit("Imagem de inicio de batalha não encontrada.")
                            if not is_image_on_screen(IMAGE_PATHS['janela_digimon'], region=(503, 192, 666, 203)):
                                pyautogui.press('v')                        
                            break
                        battle_start_image_HP_Try -= 1
                        time.sleep(1)

                    if not self.is_running or self.is_paused:
                        continue

                    time.sleep(1)
                    self.status_update.emit("Buscando imagem de inicio de batalha")
                    
                    if all(is_image_on_screen(IMAGE_PATHS[img], region=self.main_window.coordenadas[idx]) for img, idx in [('battle_start_hp', 0), ('battle_start_sp', 1), ('battle_start_evp', 2)]):
                        self.status_update.emit("Imagem de início de batalha detectada.")                       
                        self.status_update.emit("Procurando batalha: pressionando 'F'.")
                        if is_image_on_screen(IMAGE_PATHS['captcha_exists']):
                            dividir_e_desenhar_contornos(self.main_window.current_user)
                        time.sleep(0.5)
                        initiate_battle(self.main_window.battle_keys)
                            
                        battle_actions(self.main_window.battle_keys, self.main_window.skill_positions)
                        self.battles_count += 1
                        current_time = datetime.now()
                        elapsed_time = (current_time - self.start_time).total_seconds() / 60  # in minutes
                        battles_per_minute = self.battles_count / elapsed_time if elapsed_time > 0 else 0
                        self.battles_per_minute_update.emit(battles_per_minute)
                        
                        if is_image_on_screen(IMAGE_PATHS['captcha_exists']):
                            dividir_e_desenhar_contornos(self.main_window.current_user)
                    else:
                        if not is_image_on_screen(IMAGE_PATHS['battle_start_evp'], region=(503, 459, 521, 475)):
                            pyautogui.press('v')
                            for _ in range(35):
                                if not self.is_running or self.is_paused:
                                    break
                                if is_image_on_screen(IMAGE_PATHS['captcha_exists']):
                                    dividir_e_desenhar_contornos(self.main_window.current_user)
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

            except Exception as e:
                self.status_update.emit(f"Erro na automação: {str(e)}")
                time.sleep(0.1)

    def stop(self):
        self.is_running = False
        if hasattr(self, 'update_timer'):
            self.update_timer.stop()
            self.update_timer.deleteLater()
        if self.time_thread:
            self.time_thread.stop()
            self.time_thread.wait()
            self.time_thread.deleteLater()
            self.time_thread = None
        
    def pause(self):
        self.is_paused = True
        
    def resume(self):
        self.is_paused = False

    def reset(self): # Added reset method
        if self.time_thread:
            self.time_thread.stop()
            self.time_thread.wait()
            self.time_thread.deleteLater()
        self.start_time = datetime.now()
        self.battles_count = 0
        self.last_battle_time = self.start_time
        # Reinicia thread de tempo com novo start_time
        self.time_thread = TimeUpdateThread(self.start_time)
        self.time_thread.time_update.connect(self.main_window.update_time)
        self.time_thread.start()

    def update_elapsed_time(self):
        if not self.is_running or self.is_paused:
            return
        current_time = datetime.now()
        elapsed_time = current_time - self.start_time
        elapsed_time_str = str(elapsed_time).split('.')[0]
        self.time_update.emit(elapsed_time_str)

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
        # Make window vertical and responsive
        screen = QApplication.primaryScreen().geometry()
        window_width = min(600, screen.width() * 0.4)  # Narrower width
        window_height = min(900, screen.height() * 0.9)  # Taller height
        
        # Center the window
        self.setGeometry(
            (screen.width() - window_width) // 2,
            (screen.height() - window_height) // 2,
            window_width, 
            window_height
        )
        
        # Define container limits first
        self.MIN_CONTAINER_WIDTH = int(window_width * 0.9)
        self.MAX_CONTAINER_WIDTH = int(window_width * 0.95)
        
        self.setWindowTitle("DigiBOT")
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {MODERN_STYLES['BACKGROUND_COLOR']};
            }}
            
            QTabWidget::pane {{
                border: none;
                background-color: {MODERN_STYLES['SURFACE_COLOR']};
                border-radius: {MODERN_STYLES['BORDER_RADIUS']};
            }}
            
            QTabBar {{
                alignment: center;
                background: transparent;
            }}
            
            QTabBar::tab {{
                background-color: transparent;
                color: {MODERN_STYLES['TEXT_SECONDARY']};
                padding: 15px 30px;
                margin: 0 5px;
                border: none;
                font-size: 18px;  /* Increased font size */
                font-weight: bold;
                min-width: 180px;  /* Increased min width */
                max-width: 300px;
            }}
            
            QTabBar::tab:selected {{
                color: {MODERN_STYLES['PRIMARY_COLOR']};
                border-bottom: 3px solid {MODERN_STYLES['PRIMARY_COLOR']};
                background-color: rgba(33, 150, 243, 0.1);
            }}
            
            QTabBar::tab:hover {{
                background-color: rgba(33, 150, 243, 0.05);
                color: {MODERN_STYLES['PRIMARY_COLOR']};
            }}
        """)
        self.session_id = None
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

        # Initialize skill positions and coordinates before setup_ui
        self.skill_positions = {
            'group1': {
                'Q': (240, 562, 255, 577),
                'W': (265, 562, 281, 578),
                'E': (288, 563, 305, 578)
            },
            'group2': {
                'A': (392, 562, 409, 577),
                'S': (417, 562, 432, 577),
                'D': (441, 562, 457, 577)
            },
            'group3': {
                'Z': (543, 562, 560, 577),
                'X': (569, 562, 585, 577),
                'C': (594, 562, 611, 577)
            }
        }

        self.coordenadas = [
            (503, 377, 596, 393),  # HP bar
            (503, 417, 563, 433),  # SP bar
            (503, 459, 521, 475),  # EVP bar
            (468, 565, 485, 576),  # Battle finish
            (503, 192, 666, 203),  # Janela digimon
            (768, 541, 779, 554),  # Battle detection
            (288, 563, 305, 578),  # Skill 1 (E)
            (441, 562, 457, 577),  # Skill 2 (D)
            (594, 562, 611, 577)   # Skill 3 (C)
        ]

        self.image_filenames = [
            "battle_start_hp.png",
            "battle_start_sp.png",
            "battle_start_evp.png",
            "battle_finish.png",
            "janela_digimon.png",
            "battle_detection.png",
            "skill1.png",
            "skill2.png",
            "skill3.png"
        ]

        # Initialize combo boxes
        self.resolucao_combobox = QComboBox()
        self.resolucao_combobox.addItems(["800x600", "1366x768"])
        
        self.digievolucao_combobox = QComboBox()
        self.digievolucao_combobox.addItems(["mega", "ultimate", "champion", "rookie"])
        self.digievolucao_combobox.currentIndexChanged.connect(self.atualizar_digievolucao)

        # Initialize this before setup_ui
        self.cards = []
        self.skill_cards = {}  # Add this line

        self.setup_ui()
        self.carregar_imagens()  # This will now work since self.cards is initialized

        # Make window responsive
        screen = QApplication.primaryScreen().geometry()
        window_width = min(1000, screen.width() * 0.8)
        window_height = min(700, screen.height() * 0.8)
        self.setGeometry(
            (screen.width() - window_width) // 2,
            (screen.height() - window_height) // 2,
            window_width, 
            window_height
        )
        
        # Make container widths responsive
        self.MIN_CONTAINER_WIDTH = 400
        self.MAX_CONTAINER_WIDTH = 900

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
        self.tabs.addTab(self.tab_auth, "Entrar")
        
        # Main container
        container = QWidget()
        container.setFixedWidth(500)  # Increased width
        container_layout = QVBoxLayout(container)
        container_layout.setAlignment(Qt.AlignCenter)
        container_layout.setSpacing(24)  # Increased spacing
        
        # Center container
        main_layout = QHBoxLayout(self.tab_auth)
        main_layout.addWidget(container)

        # Logo and title with modern styling
        title_label = QLabel("DigiBOT")
        title_label.setStyleSheet(f"""
            font-size: 36px;
            font-weight: bold;
            color: {MODERN_STYLES['PRIMARY_COLOR']};
            margin: 32px 0;
            letter-spacing: 1px;
        """)
        title_label.setAlignment(Qt.AlignCenter)
        container_layout.addWidget(title_label)

        # Modern login form
        login_form = QGroupBox()
        login_form.setStyleSheet(f"""
            QGroupBox {{
                background-color: {MODERN_STYLES['SURFACE_COLOR']};
                border-radius: {MODERN_STYLES['BORDER_RADIUS']};
                padding: 32px;
                border: none;
            }}
        """)
        form_layout = QVBoxLayout(login_form)
        form_layout.setSpacing(20)

        # Username field with modern styling
        username_label = QLabel("Usuário")
        username_label.setStyleSheet(f"color: {MODERN_STYLES['TEXT_SECONDARY']}; font-size: 14px; font-weight: bold;")
        form_layout.addWidget(username_label)
        
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Digite seu usuário")
        self.username_input.setMinimumHeight(45)
        form_layout.addWidget(self.username_input)

        # Password field with modern styling
        password_label = QLabel("Senha")
        password_label.setStyleSheet(f"color: {MODERN_STYLES['TEXT_SECONDARY']}; font-size: 14px; font-weight: bold;")
        form_layout.addWidget(password_label)
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Digite sua senha")
        self.password_input.setMinimumHeight(45)
        self.password_input.setEchoMode(QLineEdit.Password)
        form_layout.addWidget(self.password_input)

        # Modern progress bar
        self.login_progress = QProgressBar()
        self.login_progress.setStyleSheet(f"""
            QProgressBar {{
                border: none;
                border-radius: 4px;
                background-color: #E0E0E0;
                height: 8px;
                text-align: center;
            }}
            QProgressBar::chunk {{
                background-color: {MODERN_STYLES['PRIMARY_COLOR']};
                border-radius: 4px;
            }}
        """)
        self.login_progress.hide()  # Initially hidden
        form_layout.addWidget(self.login_progress)

        # Status label with modern styling
        self.login_status = QLabel("")
        self.login_status.setStyleSheet(f"""
            color: {MODERN_STYLES['TEXT_SECONDARY']};
            font-size: 14px;
            margin-top: 8px;
        """)
        self.login_status.setAlignment(Qt.AlignCenter)
        self.login_status.hide()  # Initially hidden
        form_layout.addWidget(self.login_status)

        # Modern login button
        self.login_button = QPushButton("Entrar")
        self.login_button.setCursor(Qt.PointingHandCursor)
        self.login_button.setMinimumHeight(45)
        self.login_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {MODERN_STYLES['PRIMARY_COLOR']};
                color: white;
                border: none;
                border-radius: {MODERN_STYLES['BORDER_RADIUS']};
                padding: 12px;
                font-size: 16px;
                font-weight: bold;
                margin-top: 16px;
            }}
            QPushButton:hover {{
                background-color: #1976D2;
                transform: translateY(-1px);
            }}
            QPushButton:pressed {{
                transform: translateY(1px);
            }}
        """)
        self.login_button.clicked.connect(self.authenticate)
        form_layout.addWidget(self.login_button)
        
        container_layout.addWidget(login_form)
        container_layout.addStretch()

    def setup_play_tab(self):
        self.tab_jogar = QWidget()
        self.tabs.addTab(self.tab_jogar, "Jogar")
        
        # Main container with modern styling
        container = QWidget()
        container_width = int(self.width() * 0.95)  # Use 95% of window width
        container.setFixedWidth(container_width)
        container_layout = QVBoxLayout(container)
        container_layout.setAlignment(Qt.AlignTop)  # Changed to top alignment
        container_layout.setSpacing(15)  # Reduced spacing
        
        # Main layout setup
        main_layout = QHBoxLayout(self.tab_jogar)
        main_layout.addWidget(container)

        # Header Section with gradient background
        header_widget = QWidget()
        header_layout = QVBoxLayout(header_widget)
        header_widget.setStyleSheet(f"""
            QWidget {{
                background: {MODERN_STYLES['GRADIENT_PRIMARY']};
                border-radius: 20px;
                padding: 30px;
                margin: 20px;
            }}
        """)

        # Header content
        title_label = QLabel("DigiBOT")
        title_label.setStyleSheet("""
            font-size: 36px;
            font-weight: bold;
            color: white;
            margin: 15px 0;
        """)
        title_label.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(title_label)

        # Status Cards Container with vertical layout
        stats_container = QWidget()
        stats_layout = QVBoxLayout(stats_container)
        stats_layout.setSpacing(10)
        stats_layout.setContentsMargins(10, 10, 10, 10)
        
        # Create cards with full width - removed status card
        cards_data = [
            ("Tempo", "00:00:00", "time_label", "#2196F3"),
            ("Batalhas", "0", "battles_label", "#FF9800"),
            ("Taxa", "0.00/min", "battles_per_minute_label", "#9C27B0")
        ]
        
        for title, initial_value, label_name, color in cards_data:
            card = self.create_info_card(title, initial_value, label_name, color)
            card.setMinimumWidth(int(container_width * 0.9))
            card.setFixedHeight(70)  # Fixed height for cards
            stats_layout.addWidget(card)
        
        container_layout.addWidget(stats_container)

        # License Info Card with proper initialization
        license_card = QWidget()
        license_card.setStyleSheet("""
            QWidget {
                background: white;
                border: 2px solid #e0e0e0;
                border-radius: 15px;
                padding: 25px;
                margin: 10px;
            }
        """)
        license_layout = QVBoxLayout(license_card)
        
        self.license_info_label = QLabel("Informações da licença não disponíveis")
        self.license_info_label.setStyleSheet("""
            font-size: 16px;
            color: #666;
            padding: 10px;
        """)
        self.license_info_label.setAlignment(Qt.AlignCenter)
        license_layout.addWidget(self.license_info_label)
        container_layout.addWidget(license_card)

        # Action Buttons Container
        buttons_container = QWidget()
        buttons_layout = QHBoxLayout(buttons_container)
        buttons_layout.setSpacing(20)
        buttons_layout.setAlignment(Qt.AlignCenter)

        # Start/Stop Button with modern design
        self.start_stop_button = QPushButton("Iniciar Automação")
        self.start_stop_button.setMinimumWidth(250)
        self.start_stop_button.setMinimumHeight(50)
        self.start_stop_button.setCursor(Qt.PointingHandCursor)
        self.start_stop_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {MODERN_STYLES['SUCCESS_COLOR']};
                color: white;
                border: none;
                border-radius: 25px;
                font-size: 16px;
                font-weight: bold;
                padding: 15px 30px;
            }}
            QPushButton:hover {{
                background-color: #45a049;
            }}
        """)
        self.start_stop_button.clicked.connect(self.toggle_automation)
        self.start_stop_button.clicked.connect(self.escolher_resolucao)
        buttons_layout.addWidget(self.start_stop_button)

        # Logoff Button with modern design
        self.logoff_button = QPushButton("Sair")
        self.logoff_button.setMinimumWidth(250)
        self.logoff_button.setMinimumHeight(50)
        self.logoff_button.setCursor(Qt.PointingHandCursor)
        self.logoff_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {MODERN_STYLES['DANGER_COLOR']};
                color: white;
                border: none;
                border-radius: 25px;
                font-size: 16px;
                font-weight: bold;
                padding: 15px 30px;
            }}
            QPushButton:hover {{
                background-color: #d32f2f;
            }}
        """)
        self.logoff_button.clicked.connect(self.do_logoff)
        buttons_layout.addWidget(self.logoff_button)

        # Add buttons container to main layout
        container_layout.addWidget(buttons_container)
        container_layout.addStretch()

        # Set the main layout
        main_layout.addWidget(container)

    def create_info_card(self, title, initial_value, label_name, accent_color):
        card = QWidget()
        card.setStyleSheet(f"""
            QWidget {{
                background: white;
                border: 2px solid #e0e0e0;
                border-radius: 15px;
                padding: 10px;
            }}
        """)
        
        # Use horizontal layout for better spacing
        layout = QHBoxLayout(card)
        layout.setSpacing(10)
        layout.setContentsMargins(15, 5, 15, 5)

        # Create labels
        title_label = QLabel(title)
        title_label.setStyleSheet(f"""
            font-size: 14px;
            color: {accent_color};
            font-weight: bold;
        """)
        title_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        
        value_label = QLabel(initial_value)
        value_label.setStyleSheet(f"""
            font-size: 18px;
            color: {MODERN_STYLES['TEXT_PRIMARY']};
            font-weight: bold;
        """)
        value_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        
        # Add labels to layout
        layout.addWidget(title_label)
        layout.addWidget(value_label)
        setattr(self, label_name, value_label)
        
        return card

    def setup_config_tab(self):
        self.tab_configurar = QWidget()
        self.tabs.addTab(self.tab_configurar, "Configurar")
        
        # Main layout with scroll
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea { border: none; background: transparent; }
            QScrollBar:vertical { width: 8px; background: #F0F0F0; }
            QScrollBar::handle:vertical { background: #BDBDBD; border-radius: 4px; }
        """)

        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)

        # Header
        header = self._create_config_header()
        layout.addWidget(header)

        # Config sections
        layout.addWidget(self._create_game_settings())
        layout.addWidget(self._create_battle_settings())

        scroll.setWidget(content)
        
        # Set main layout
        main_layout = QVBoxLayout(self.tab_configurar)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll)

    def _create_config_header(self):
        header = QWidget()
        header.setStyleSheet(f"""
            QWidget {{
                background: {MODERN_STYLES['GRADIENT_PRIMARY']};
                border-radius: 15px;
                min-height: 80px;
            }}
            QLabel {{ color: white; }}
        """)
        
        layout = QHBoxLayout(header)
        layout.setContentsMargins(20, 10, 20, 10)
        
        title = QLabel("⚙️ Configurações")
        title.setStyleSheet("font-size: 24px; font-weight: bold;")
        layout.addWidget(title)
        
        return header

    def _create_game_settings(self):
        section = QWidget()
        section.setStyleSheet(f"""
            QWidget {{
                background: {MODERN_STYLES['SURFACE_COLOR']};
                border-radius: 12px;
                padding: 15px;
            }}
        """)
        
        layout = QVBoxLayout(section)
        layout.setSpacing(15)

        # Resolution section
        res_group = QWidget()
        res_layout = QHBoxLayout(res_group)
        res_layout.setContentsMargins(0, 0, 0, 0)

        res_label = QLabel("🎮 Resolução")
        res_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        res_layout.addWidget(res_label)
        
        self.resolucao_combobox.setStyleSheet("""
            QComboBox {
                padding: 8px;
                border: 1px solid #E0E0E0;
                border-radius: 6px;
                min-width: 150px;
            }
        """)
        res_layout.addWidget(self.resolucao_combobox)
        
        update_btn = QPushButton("Atualizar")
        update_btn.setStyleSheet(self._get_button_style())
        update_btn.clicked.connect(self.escolher_resolucao)
        res_layout.addWidget(update_btn)
        res_layout.addStretch()
        
        layout.addWidget(res_group)

        # Digievolution section
        digi_group = QWidget()
        digi_layout = QHBoxLayout(digi_group)
        digi_layout.setContentsMargins(0, 0, 0, 0)

        digi_label = QLabel("⚔️ Digievolução")
        digi_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        digi_layout.addWidget(digi_label)
        
        self.digievolucao_combobox.setStyleSheet(self.resolucao_combobox.styleSheet())
        digi_layout.addWidget(self.digievolucao_combobox)
        digi_layout.addStretch()
        
        layout.addWidget(digi_group)
        
        return section

    def _create_battle_settings(self):
        section = QWidget()
        section.setStyleSheet(f"""
            QWidget {{
                background: {MODERN_STYLES['SURFACE_COLOR']};
                border-radius: 12px;
                padding: 15px;
            }}
        """)
        
        layout = QVBoxLayout(section)
        
        title = QLabel("⚔️ Teclas de Batalha")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(title)

        keys_layout = QVBoxLayout()
        keys_layout.setSpacing(10)
        
        # Keep the original key groups
        key_groups = [
            ('Grupo 1', 'group1', ['Q', 'W', 'E']),
            ('Grupo 2', 'group2', ['A', 'S', 'D']),
            ('Grupo 3', 'group3', ['Z', 'X', 'C'])
        ]
        
        for group_name, group_id, keys in key_groups:
            group_layout = QHBoxLayout()
            group_layout.addWidget(QLabel(group_name))
            
            for key in keys:
                btn = KeyButton(key)
                btn.setProperty('group', group_id)
                btn.clicked.connect(lambda checked, k=key, g=group_id: self.update_battle_key(k, g))
                group_layout.addWidget(btn)
            
            group_layout.addStretch()
            keys_layout.addLayout(group_layout)
        
        layout.addLayout(keys_layout)
        
        # Add capture settings after the battle keys
        capture_settings = self._create_capture_settings()
        layout.addWidget(capture_settings)
        
        return section

    # Keep the _create_capture_card method for creating capture cards
    def _create_capture_card(self, index, description, coords):
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background: white;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                padding: 12px;
            }}
            QLabel[title="true"] {{
                color: {MODERN_STYLES['TEXT_PRIMARY']};
                font-weight: bold;
                font-size: 14px;
            }}
            QLabel[coords="true"] {{
                color: {MODERN_STYLES['TEXT_SECONDARY']};
                font-size: 12px;
                margin-top: 4px;
            }}
        """)
        
        layout = QVBoxLayout(card)
        layout.setSpacing(8)
        
        # Title
        title = QLabel(description)
        title.setProperty("title", True)
        layout.addWidget(title)
        
        # Coordinates
        coords_text = f"Região: {coords[0]}, {coords[1]} → {coords[2]}, {coords[3]}"
        coords_label = QLabel(coords_text)
        coords_label.setProperty("coords", True)
        layout.addWidget(coords_label)
        
        # Preview
        preview = QLabel()
        preview.setFixedSize(180, 100)
        preview.setStyleSheet("""
            border: 1px dashed #ccc;
            border-radius: 4px;
            background: #fafafa;
            padding: 4px;
        """)
        preview.setAlignment(Qt.AlignCenter)
        layout.addWidget(preview)
        
        # Capture button
        capture_btn = QPushButton("Capturar")
        capture_btn.setCursor(Qt.PointingHandCursor)
        capture_btn.setStyleSheet(self._get_button_style())
        capture_btn.clicked.connect(lambda: self.capturar_imagem(index))
        layout.addWidget(capture_btn)
        
        card.label = preview
        return card

    def authenticate(self):
        username = self.username_input.text().lower()
        password = self.password_input.text()

        # Verifica se usuário já está online
        online_status = self.db.check_user_online(username)
        if (online_status):
            login_time = online_status["login_time"].strftime("%d/%m/%Y %H:%M:%S")
            reply = QMessageBox.question(
                self,
                "Usuário já conectado",
                f"Este usuário já está conectado desde {login_time}.\nDeseja continuar e desconectar a sessão anterior?",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.No:
                self.login_button.show()
                return
            else:
                # Remove sessão anterior
                self.db.remove_user_online(username)

        # Continua com o processo de login
        self.login_button.hide()
        self.login_progress.show()
        self.login_status.show()
        self.login_progress.setValue(10)
        self.login_status.setText("Validando credenciais...")

        self.login_thread = LoginThread(self.db, username, password)
        self.login_thread.finished.connect(self.handle_login_result)
        self.login_thread.progress.connect(self.login_progress.setValue)
        self.login_thread.start()

    def handle_login_result(self, success, error_message):
        if (success):
            # Adiciona usuário à collection de usuários online
            self.session_id = self.db.add_user_online(self.username_input.text().lower())
            if not self.session_id:
                QMessageBox.warning(self, "Erro", "Erro ao criar sessão online")
                self.login_button.show()
                return

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
        self.logoff_button.hide()  # Esconde o botão de logoff também
        QTimer.singleShot(100, self._start_automation_thread)  # Aguarda um breve momento antes de iniciar a automação

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
        # O botão de logoff permanece escondido durante a automação

    def hide_start_stop_button(self):
        self.start_stop_button.hide()
        self.logoff_button.hide()
    
    def start_automation(self):
        if not self.is_authenticated:
            QMessageBox.warning(self, "Erro", "Por favor, autentique-se primeiro!")
            self.start_stop_button.show()
            self.logoff_button.show()
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

        if self.automation_thread is None:
            self.automation_thread = AutomationThread(self)
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
        self.start_stop_button.show()

    def stop_automation(self):
        if self.automation_thread:
            try:
                self.automation_thread.is_running = False
                self.automation_thread.stop()
                if not self.automation_thread.wait(3000):
                    self.automation_thread.terminate()
                    self.automation_thread.wait()
                self.automation_thread.deleteLater()
                self.automation_thread = None
            except Exception as e:
                print(f"Error stopping automation: {e}")
                if self.automation_thread:
                    self.automation_thread.terminate()
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
        
        self.start_stop_button.show()
        self.logoff_button.show()
        self.update_time("00:00:00")
        self.update_battles(0)
        self.update_battles_per_minute(0.00)

    def escolher_resolucao(self):
        resolucao_selecionada = self.resolucao_combobox.currentText()
        # Check if the selected resolution is 1366x768
        if resolucao_selecionada == "1366x768":
            QMessageBox.warning(self, "Aviso", "No momento a automação não é capaz de rodar nessa resolução.")
            return

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

        # Update coordinates based on selected key
        if key in self.skill_positions[group]:
            coords = self.skill_positions[group][key]
            group_index = {'group1': 6, 'group2': 7, 'group3': 8}
            idx = group_index[group]
            self.coordenadas[idx] = coords

            # Update the capture card display
            if group in self.skill_cards:
                card = self.skill_cards[group]
                coords_label = card.findChild(QLabel, "coords_label")
                if coords_label:
                    coords_label.setText(f"Região: {coords[0]}, {coords[1]} → {coords[2]}, {coords[3]}")

        # Uncheck other buttons in the same group
        parent = button.parent()
        for other_button in parent.findChildren(KeyButton):
            if other_button != button and other_button.property('group') == group:
                other_button.setChecked(False)

    def carregar_imagens(self):
        os.makedirs(SCREENSHOTS_DIR, exist_ok=True)
        for i, card in enumerate(self.cards):
            image_path = os.path.join(SCREENSHOTS_DIR, self.image_filenames[i])
            if (os.path.exists(image_path)):
                imagem = QImage(image_path)
                pixmap = QPixmap.fromImage(imagem)
                scaled_pixmap = pixmap.scaled(150, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                card.label.setPixmap(scaled_pixmap)

    def validate_automation_session(self):
        if not self.session_id:
            QMessageBox.warning(self, "Erro", "Sessão inválida, por favor faça login novamente")
            sys.exit()  # Encerra completamente o programa
            return False

        if not self.db.validate_session(self.current_user, self.session_id):
            QMessageBox.warning(self, "Erro", "Sessão inválida, por favor faça login novamente")
            sys.exit()  # Encerra completamente o programa
            return False

        return True

    def do_logoff(self):
        if self.automation_thread and self.automation_thread.is_running:
            QMessageBox.warning(self, "Erro", "Por favor, pare a automação antes de fazer logoff")
            return

        self.db.remove_user_online(self.current_user)
        self.is_authenticated = False
        self.current_user = None
        self.session_id = None
        self.tabs.setTabEnabled(1, False)
        self.tabs.setTabEnabled(2, False)
        self.tabs.setCurrentIndex(0)
        self.username_input.clear()
        self.password_input.clear()
        QMessageBox.information(self, "Sucesso", "Desconectado com sucesso!")

    def update_license_info(self):
        if self.license_expiration:
            days_left = (self.license_expiration - datetime.now().date()).days
            expiration_text = f"Sua licença expira em {self.license_expiration.strftime('%d/%m/%Y')}"
            days_left_text = f"Faltam {days_left} dias para sua licença expirar"
            self.license_info_label.setText(f"{expiration_text}\n{days_left_text}")
        else:
            self.license_info_label.setText("Informações da licença não disponíveis")

    def update_status(self, message):
        pass  # Status updates removed since status card was removed

    def update_time(self, time_str):
        self.time_label.setText(f"Tempo decorrido: {time_str}")

    def update_battles(self, battles):
        self.battles_label.setText(f"Batalhas realizadas: {battles}")

    def update_battles_per_minute(self, bpm):
        self.battles_per_minute_label.setText(f"Taxa: {bpm:.2f}/min")

    def _create_capture_card(self, index, description, coords):
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background: white;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                padding: 12px;
            }}
            QLabel[title="true"] {{
                color: {MODERN_STYLES['TEXT_PRIMARY']};
                font-weight: bold;
                font-size: 14px;
            }}
            QLabel[coords="true"] {{
                color: {MODERN_STYLES['TEXT_SECONDARY']};
                font-size: 12px;
                margin-top: 4px;
            }}
        """)
        
        layout = QVBoxLayout(card)
        layout.setSpacing(8)
        
        # Title
        title = QLabel(description)
        title.setProperty("title", True)
        layout.addWidget(title)
        
        # Coordinates
        coords_text = f"Região: {coords[0]}, {coords[1]} → {coords[2]}, {coords[3]}"
        coords_label = QLabel(coords_text)
        coords_label.setProperty("coords", True)
        coords_label.setObjectName("coords_label")  # For finding later
        layout.addWidget(coords_label)
        
        # Preview
        preview = QLabel()
        preview.setFixedSize(180, 100)
        preview.setStyleSheet("""
            border: 1px dashed #ccc;
            border-radius: 4px;
            background: #fafafa;
            padding: 4px;
        """)
        preview.setAlignment(Qt.AlignCenter)
        layout.addWidget(preview)
        
        # Capture button
        capture_btn = QPushButton("Capturar")
        capture_btn.setCursor(Qt.PointingHandCursor)
        capture_btn.setStyleSheet(self._get_button_style())
        capture_btn.clicked.connect(lambda: self.capturar_imagem(index))
        layout.addWidget(capture_btn)
        
        # Set preview label as card.label for image updating
        card.label = preview
        return card

    def _get_button_style(self):
        return f"""
            QPushButton {{
                background: {MODERN_STYLES['PRIMARY_COLOR']};
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 15px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background: #1976D2;
            }}
        """

    def _create_capture_settings(self):
        capture_section = QWidget()
        capture_section.setStyleSheet(f"""
            QWidget {{
                background: {MODERN_STYLES['SURFACE_COLOR']};
                border-radius: 12px;
                padding: 15px;
            }}
        """)
        
        layout = QVBoxLayout(capture_section)
        layout.setSpacing(15)

        # Title
        title = QLabel("📸 Áreas de Captura")
        title.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(title)

        # Create grid layout for capture cards
        grid = QGridLayout()
        grid.setSpacing(15)
        
        # Add cards to grid (2 columns)
        captures = [
            ("Barra de HP", 0),
            ("Barra de SP", 1),
            ("Barra de EVP", 2),
            ("Fim de Batalha", 3),
            ("Janela Digimon", 4),
            ("Detecção de Batalha", 5)
        ]

        for i, (desc, idx) in enumerate(captures):
            card = self._create_capture_card(idx, desc, self.coordenadas[idx])
            row = i // 2
            col = i % 2
            grid.addWidget(card, row, col)
            self.cards.append(card)

        layout.addLayout(grid)
        return capture_section

    # ...rest of the class remains unchanged...
