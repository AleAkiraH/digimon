import os
import time
import pyautogui
import win32gui
import win32con
from PyQt5.QtWidgets import (QApplication, QMainWindow, QLabel, QComboBox,
                           QPushButton, QVBoxLayout, QHBoxLayout,
                           QWidget, QMessageBox, QFrame,
                           QSizePolicy, QTabWidget, QGroupBox, QLineEdit, QScrollArea)
from PyQt5.QtGui import QPixmap, QImage, QPainter, QColor, QLinearGradient, QFont
from PyQt5.QtCore import Qt, QSize
from PIL import ImageGrab
import io, keyboard

# Importe as funções e variáveis necessárias dos outros arquivos
from variables import WINDOW_NAME, RESOLUCAO_PADRAO, SCREENSHOTS_DIR, IMAGE_PATHS
from functions import log, is_image_on_screen, dividir_e_desenhar_contornos, initiate_battle, battle_actions, refill_digimons

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
        
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_area.setWidget(scroll_content)
        
        login_layout = QVBoxLayout(scroll_content)
        login_layout.setAlignment(Qt.AlignCenter)
        login_layout.setSpacing(20)
        
        main_layout = QVBoxLayout(self.tab_auth)
        main_layout.addWidget(scroll_area)
        
        auth_group = QGroupBox("Autenticação")
        auth_layout = QVBoxLayout()
        auth_group.setLayout(auth_layout)
        
        title_label = QLabel("Digimon Automation")
        title_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #4682B4; margin-bottom: 20px;")
        auth_layout.addWidget(title_label, alignment=Qt.AlignCenter)
        
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Username")
        self.username_input.setStyleSheet("""
            background-color: white;
            border: 1px solid #4682B4;
            border-radius: 5px;
            padding: 10px;
            margin-bottom: 10px;
            font-size: 14px;
        """)
        auth_layout.addWidget(self.username_input)
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setStyleSheet("""
            background-color: white;
            border: 1px solid #4682B4;
            border-radius: 5px;
            padding: 10px;
            margin-bottom: 20px;
            font-size: 14px;
        """)
        auth_layout.addWidget(self.password_input)
        
        login_button = QPushButton("Login")
        login_button.clicked.connect(self.authenticate)
        login_button.setStyleSheet("""
            background-color: #4CAF50;
            color: white;
            border: none;
            border-radius: 5px;
            padding: 10px;
            font-size: 16px;
            font-weight: bold;
        """)
        login_button.setCursor(Qt.PointingHandCursor)
        auth_layout.addWidget(login_button)
        
        login_layout.addWidget(auth_group)

    def setup_play_tab(self):
        self.tab_jogar = QWidget()
        self.tabs.addTab(self.tab_jogar, "Jogar")
        
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_area.setWidget(scroll_content)
        
        self.layout_jogar = QVBoxLayout(scroll_content)
        self.layout_jogar.setAlignment(Qt.AlignCenter)
        self.layout_jogar.setSpacing(20)
        
        main_layout = QVBoxLayout(self.tab_jogar)
        main_layout.addWidget(scroll_area)
        
        play_group = QGroupBox("Iniciar Jogo")
        play_layout = QVBoxLayout()
        play_group.setLayout(play_layout)
        
        title_label = QLabel("Bem-vindo ao projeto TERAS")
        title_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #4682B4; margin-bottom: 20px;")
        title_label.setAlignment(Qt.AlignCenter)
        play_layout.addWidget(title_label)

        try:
            digimon_image = QPixmap("digimon.png")
            digimon_label = QLabel()
            digimon_label.setPixmap(digimon_image.scaledToWidth(300))
            digimon_label.setAlignment(Qt.AlignCenter)
            play_layout.addWidget(digimon_label)
        except:
            play_layout.addWidget(QLabel("Imagem Digimon não encontrada"))

        description = QLabel("Prepare-se para uma aventura emocionante no mundo dos Digimons!")
        description.setStyleSheet("font-size: 16px; color: #666; margin-bottom: 20px;")
        description.setAlignment(Qt.AlignCenter)
        description.setWordWrap(True)
        play_layout.addWidget(description)

        play_button = QPushButton("Iniciar Automação")
        play_button.setStyleSheet("""
            font-size: 18px;
            background-color: #4CAF50;
            color: white;
            border-radius: 5px;
            padding: 15px 30px;
            margin-top: 20px;
        """)
        play_button.setCursor(Qt.PointingHandCursor)
        play_button.clicked.connect(self.start_automation)
        play_layout.addWidget(play_button, alignment=Qt.AlignCenter)
        
        self.layout_jogar.addWidget(play_group)

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
        title_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #4682B4; margin-bottom: 20px;")
        title_label.setAlignment(Qt.AlignCenter)
        self.layout_configurar.addWidget(title_label)

        general_group = QGroupBox("Configurações Gerais")
        general_layout = QVBoxLayout()
        general_group.setLayout(general_layout)

        self.setup_resolution_config(general_layout)
        self.setup_digievolution_config(general_layout)

        self.layout_configurar.addWidget(general_group)

        capture_group = QGroupBox("Captura de Imagens")
        capture_layout = QVBoxLayout()
        capture_group.setLayout(capture_layout)

        self.mensagem_info = QLabel("Certifique-se de que a tela de informações do Digimon está aberta!")
        self.mensagem_info.setStyleSheet("font-style: italic; color: #666;")
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

    def start_automation(self):
        if not self.is_authenticated:
            QMessageBox.warning(self, "Erro", "Por favor, autentique-se primeiro!")
            return

        hwnd = win32gui.FindWindow(None, WINDOW_NAME)
        if hwnd:
            style = win32gui.GetWindowLong(hwnd, win32con.GWL_STYLE)
            win32gui.SetWindowLong(hwnd, win32con.GWL_STYLE, style & ~win32con.WS_BORDER)

            resolucao_selecionada = self.resolucao_combobox.currentText()
            largura, altura = map(int, resolucao_selecionada.split("x"))

            win32gui.SetWindowPos(hwnd, 0, 0, 0, largura, altura, win32con.SWP_NOZORDER | win32con.SWP_FRAMECHANGED)

            self.executar_script()
        else:
            QMessageBox.warning(self, "Erro", "Janela 'Digimon SuperRumble' não encontrada.")

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
            
            if is_image_on_screen(IMAGE_PATHS['captcha_exists']):
                print(f"Imagem {IMAGE_PATHS['captcha_exists']} encontrada na tela. Processando...")
                dividir_e_desenhar_contornos()
            if is_image_on_screen(IMAGE_PATHS['captcha_exists']):
                print(f"Imagem {IMAGE_PATHS['captcha_exists']} encontrada na tela. Processando...")
                dividir_e_desenhar_contornos()
            if is_image_on_screen(IMAGE_PATHS['captcha_exists']):
                print(f"Imagem {IMAGE_PATHS['captcha_exists']} encontrada na tela. Processando...")
                dividir_e_desenhar_contornos()
            
            time.sleep(1)
            pyautogui.press('g')
            pyautogui.press('g')
            if is_image_on_screen(IMAGE_PATHS['captcha_exists']):
                print(f"Imagem {IMAGE_PATHS['captcha_exists']} encontrada na tela. Processando...")
                dividir_e_desenhar_contornos()

            pyautogui.press('g')
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
                    
                initiate_battle(IMAGE_PATHS['battle_detection'])
                
                if is_image_on_screen(IMAGE_PATHS['captcha_exists']):
                    dividir_e_desenhar_contornos()
                    
                battle_actions(IMAGE_PATHS['battle_detection'], IMAGE_PATHS['battle_finish'])
                
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

