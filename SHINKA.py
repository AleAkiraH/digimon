import os
import time
import pyautogui
import numpy as np
import cv2
import random
import keyboard
import win32gui
import win32con
import mss
from datetime import datetime
import threading
import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QLabel, QComboBox,
                           QPushButton, QVBoxLayout, QHBoxLayout,
                           QWidget, QMessageBox, QFrame,
                           QSizePolicy, QTabWidget, QGroupBox, QLineEdit)
from PyQt5.QtGui import QPixmap, QImage, QPainter, QColor, QLinearGradient
from PyQt5.QtCore import Qt, QSize
from PIL import ImageGrab
import io

# Configuration settings
WINDOW_NAME = 'Digimon SuperRumble  '
RESOLUCAO_PADRAO = (800, 600)
SCREENSHOTS_DIR = "ScreenSaved"

# Screen coordinates
COORDINATES = {
    'x_inicial': '540',
    'y_inicial': '239',
    'x_final': '825',
    'y_final': '525'
}

# Image paths
IMAGE_PATHS = {
    'captcha_exists': "ScreenSaved/captcha_exists.PNG",
    'battle_start_hp': "ScreenSaved/battle_start_hp.png",
    'battle_start_sp': "ScreenSaved/battle_start_sp.png",
    'battle_start_evp': "ScreenSaved/battle_start_evp.png",
    'battle_detection': "ScreenSaved/battle_detection.png",
    'battle_finish': "ScreenSaved/battle_finish.png",
    'janela_digimon': "ScreenSaved/janela_digimon.png",
    'evp_terminado': "ScreenSaved/EVP_Terminado.png"
}

# Digivolução coordinates
DIGIVOLUCAO = {
    'rookie': [
        [[236,190], [438,190], [436,208]],
        [[236,227], [438,190], [436,208]],
        [[236,258], [438,190], [436,208]]
    ],
    'champion': [
        [[236,190], [438,190], [436,208]],
        [[236,227], [438,190], [436,208]],
        [[236,258], [438,190], [436,208]]
    ],
    'ultimate': [
        [[236,190], [438,190], [436,225]],
        [[236,227], [438,190], [436,225]],
        [[236,258], [438,190], [436,225]]
    ],
    'mega': [
        [[236,190], [438,190], [436,241]],
        [[236,227], [438,190], [436,241]],
        [[236,258], [438,190], [436,241]]
    ]
}

# Initialize logging
last_log_message = None

def log(message, log_file="script_logs.txt"):
    """Log messages to file and console"""
    global last_log_message
    if message != last_log_message:
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        formatted_message = f"[{timestamp}] {message}"
        print(formatted_message)
        
        with open(log_file, "a", encoding="utf-8") as file:
            file.write(formatted_message + "\n")
        
        last_log_message = message

def activate_window(window_name):
    """Activate the game window"""
    hwnd = win32gui.FindWindow(None, window_name)
    if hwnd:
        win32gui.SetForegroundWindow(hwnd)
        time.sleep(3)
        log("Janela ativada com sucesso.")
        return hwnd
    else:
        log("A janela não foi encontrada.")
        return None

def is_image_on_screen(image_path, confidence=0.85):
    """Check if an image is present on screen"""
    location = pyautogui.locateCenterOnScreen(image_path, confidence=confidence)
    return location is not None

def mover_mouse_humano(x_inicial, y_inicial, x_final, y_final):
    """Move mouse in a human-like pattern"""
    num_etapas = random.randint(10, 20)
    x_step = (x_final - x_inicial) / num_etapas
    y_step = (y_final - y_inicial) / num_etapas

    for i in range(num_etapas):
        x = int(x_inicial + x_step * i + random.randint(-3, 3))
        y = int(y_inicial + y_step * i + random.randint(-3, 3))
        pyautogui.moveTo(x, y, duration=random.uniform(0.05, 0.1))
        time.sleep(random.uniform(0.01, 0.03))

def calcular_area_homogenea(quadrado):
    """Calculate homogeneous area in a square"""
    pixels = quadrado.reshape(-1, quadrado.shape[-1])
    unique_pixels, counts = np.unique(pixels, axis=0, return_counts=True)
    return max(counts)

def dividir_e_desenhar_contornos():
    """Process captcha by dividing and drawing contours"""
    left = min(int(COORDINATES['x_inicial']), int(COORDINATES['x_final']))
    top = min(int(COORDINATES['y_inicial']), int(COORDINATES['y_final']))
    width = abs(int(COORDINATES['x_final']) - int(COORDINATES['x_inicial']))
    height = abs(int(COORDINATES['y_final']) - int(COORDINATES['y_inicial']))
    
    screenshot = pyautogui.screenshot(region=(left, top, width, height))
    image = np.array(screenshot)
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

    altura, largura, _ = image.shape
    tamanho_quadrado_largura = largura // 8
    tamanho_quadrado_altura = altura // 8

    max_homogeneidade = 0
    quadrado_mais_homogeneo = None

    for i in range(8):
        for j in range(8):
            x_inicio = i * tamanho_quadrado_largura
            y_inicio = j * tamanho_quadrado_altura
            x_fim = (i + 1) * tamanho_quadrado_largura
            y_fim = (j + 1) * tamanho_quadrado_altura

            quadrado = image[y_inicio:y_fim, x_inicio:x_fim]
            homogeneidade = calcular_area_homogenea(quadrado)
            
            if homogeneidade > max_homogeneidade:
                max_homogeneidade = homogeneidade
                quadrado_mais_homogeneo = (x_inicio, y_inicio, x_fim, y_fim)

    if quadrado_mais_homogeneo:
        x_inicio, y_inicio, x_fim, y_fim = quadrado_mais_homogeneo
        quadrado_azul = image[y_inicio:y_fim, x_inicio:x_fim]
        temp_image_path = "quadrado_azul.png"
        cv2.imwrite(temp_image_path, quadrado_azul)
        
        location = pyautogui.locateCenterOnScreen(temp_image_path, confidence=0.85)
        if location:
            x_final, y_final = location
            x_inicial, y_inicial = 555, 554

            pyautogui.mouseDown(x=x_inicial, y=y_inicial)
            mover_mouse_humano(x_inicial, y_inicial, x_final, y_final)
            pyautogui.mouseUp(x=x_final, y=y_final)
            
            log(f"Mouse movido para o quadrado azul.")
            time.sleep(5)
        else:
            log("Falha ao localizar o quadrado azul na tela.")

def battle_actions(battle_detection_image, battle_finish_image):
    """Execute battle actions"""
    log("Executando ações de batalha.")
    while is_image_on_screen(battle_detection_image):
        pyautogui.press("e")
        pyautogui.press("1")
        pyautogui.press("d")
        pyautogui.press("1")
        pyautogui.press("c")
        pyautogui.press("1")

    log("Batalha finalizada.")
    while not is_image_on_screen(battle_finish_image):
        log("Aguardando para iniciar uma nova batalha.")

def initiate_battle(battle_detection_image):
    """Initiate battle sequence"""
    while is_image_on_screen(IMAGE_PATHS['battle_finish']):
        pyautogui.press('v')
        log("Procurando batalha: pressionando 'F'.")
        for _ in range(20):
            if is_image_on_screen(battle_detection_image):
                break
            for _ in range(5):
                pyautogui.press('g')
            if not is_image_on_screen(IMAGE_PATHS['battle_finish']):
                pyautogui.press("e")
                pyautogui.press("1")
                pyautogui.press("d")
                pyautogui.press("1")
                pyautogui.press("c")
                pyautogui.press("1")
            else:
                pyautogui.press('f')

        if is_image_on_screen(IMAGE_PATHS['captcha_exists']):
            dividir_e_desenhar_contornos()
        
        time.sleep(0.5)
    log("Batalha iniciada.")

def refill_digimons(digivolucao_type='mega'):
    """Refill digimons with specified evolution"""
    if is_image_on_screen(IMAGE_PATHS['captcha_exists']):
        dividir_e_desenhar_contornos()

    remove_coords = DIGIVOLUCAO['rookie']
    digivolucao_coords = DIGIVOLUCAO.get(digivolucao_type, DIGIVOLUCAO['mega'])
    
    for coords in remove_coords:
        for coord in coords:
            if is_image_on_screen(IMAGE_PATHS['captcha_exists']):
                dividir_e_desenhar_contornos()
            pyautogui.click(x=coord[0], y=coord[1])
        log("Digivolução retirada.")
    
    for coords in digivolucao_coords:
        for coord in coords:
            time.sleep(0.5)
            pyautogui.click(x=coord[0], y=coord[1])            
        log("Digivolução aplicada.")
    
    pyautogui.press('v')
    log("Refill concluído.")

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Digimon Automation")
        self.setGeometry(100, 100, 400, 600)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f0f0f0;
            }
            QTabWidget::pane {
                border: none;
            }
            QTabWidget::tab-bar {
                alignment: center;
            }
            QTabBar::tab {
                background-color: #4682B4;
                color: white;
                padding: 8px 20px;
                margin: 2px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            QTabBar::tab:selected {
                background-color: #1E90FF;
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
        
        background_label = QLabel(self.tab_auth)
        background_label.setGeometry(0, 0, 400, 600)
        
        background_image = QImage("https://img.odcdn.com.br/wp-content/uploads/2024/03/Digimon-Toei-1.jpg")
        background_pixmap = QPixmap.fromImage(background_image).scaled(
            QSize(800, 600), 
            Qt.AspectRatioMode.KeepAspectRatioByExpanding,
            Qt.TransformationMode.SmoothTransformation
        )
        background_label.setPixmap(background_pixmap)
        
        gradient = QPixmap(800, 600)
        gradient.fill(Qt.transparent)
        painter = QPainter(gradient)
        gradient_bg = QLinearGradient(0, 0, 0, 800)
        gradient_bg.setColorAt(0, QColor(0, 0, 0, 180))
        gradient_bg.setColorAt(1, QColor(0, 0, 0, 120))
        painter.fillRect(gradient.rect(), gradient_bg)
        painter.end()
        
        overlay_label = QLabel(self.tab_auth)
        overlay_label.setGeometry(0, 0, 800, 800)
        overlay_label.setPixmap(gradient)
        
        login_layout = QVBoxLayout(self.tab_auth)
        login_layout.setAlignment(Qt.AlignCenter)
        
        title_label = QLabel("Digimon Automation")
        title_label.setStyleSheet("""
            color: white;
            font-size: 24px;
            font-weight: bold;
            margin-bottom: 20px;
        """)
        login_layout.addWidget(title_label, alignment=Qt.AlignCenter)
        
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Username")
        self.username_input.setStyleSheet("""
            background-color: rgba(255, 255, 255, 0.8);
            border: none;
            border-radius: 5px;
            padding: 10px;
            margin-bottom: 10px;
            font-size: 16px;
        """)
        login_layout.addWidget(self.username_input)
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setStyleSheet("""
            background-color: rgba(255, 255, 255, 0.8);
            border: none;
            border-radius: 5px;
            padding: 10px;
            margin-bottom: 20px;
            font-size: 16px;
        """)
        login_layout.addWidget(self.password_input)
        
        login_button = QPushButton("Login")
        login_button.clicked.connect(self.authenticate)
        login_button.setStyleSheet("""
            background-color: #4682B4;
            color: white;
            border: none;
            border-radius: 5px;
            padding: 10px;
            font-size: 16px;
            font-weight: bold;
        """)
        login_button.setCursor(Qt.PointingHandCursor)
        login_layout.addWidget(login_button)

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

    def setup_play_tab(self):
        self.tab_jogar = QWidget()
        self.tabs.addTab(self.tab_jogar, "Jogar")
        self.layout_jogar = QVBoxLayout(self.tab_jogar)
        
        title_label = QLabel("Bem-vindo ao projeto TERAS")
        title_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #4682B4;")
        title_label.setAlignment(Qt.AlignCenter)
        self.layout_jogar.addWidget(title_label)

        try:
            digimon_image = QPixmap("digimon.png")
            digimon_label = QLabel()
            digimon_label.setPixmap(digimon_image.scaledToWidth(200))
            digimon_label.setAlignment(Qt.AlignCenter)
            self.layout_jogar.addWidget(digimon_label)
        except:
            self.layout_jogar.addWidget(QLabel("Imagem Digimon não encontrada"))

        play_button = QPushButton("Play")
        play_button.setStyleSheet("""
            font-size: 16px;
            background-color: #4682B4;
            color: white;
            border-radius: 5px;
            padding: 10px;
        """)
        play_button.clicked.connect(self.start_automation)
        self.layout_jogar.addWidget(play_button)

    def setup_config_tab(self):
        self.tab_configurar = QWidget()
        self.tabs.addTab(self.tab_configurar, "Configurar")
        self.layout_configurar = QVBoxLayout(self.tab_configurar)
        self.layout_configurar.setAlignment(Qt.AlignTop)

        self.setup_resolution_config()
        self.setup_digievolution_config()
        
        self.mensagem_info = QLabel("Certifique-se de que a tela de informações do Digimon está aberta!")
        self.layout_configurar.addWidget(self.mensagem_info)

        self.setup_capture_cards()

    def setup_resolution_config(self):
        config_layout = QHBoxLayout()
        self.layout_configurar.addLayout(config_layout)

        label_resolucao = QLabel("Resolução do Jogo:")
        label_resolucao.setFixedWidth(120)
        config_layout.addWidget(label_resolucao)

        self.resolucao_combobox = QComboBox()
        self.resolucao_combobox.addItems(["800x600", "1024x768"])
        self.resolucao_combobox.setFixedWidth(100)
        self.resolucao_combobox.currentIndexChanged.connect(self.escolher_resolucao)
        config_layout.addWidget(self.resolucao_combobox)

    def setup_digievolution_config(self):
        digievolucao_layout = QHBoxLayout()
        self.layout_configurar.addLayout(digievolucao_layout)

        label_digievolucao = QLabel("Digievolução:")
        label_digievolucao.setFixedWidth(100)
        digievolucao_layout.addWidget(label_digievolucao)

        self.digievolucao_combobox = QComboBox()
        self.digievolucao_combobox.addItems(["rookie", "champion", "ultimate", "mega"])
        self.digievolucao_combobox.setFixedWidth(100)
        self.digievolucao_combobox.currentIndexChanged.connect(self.atualizar_digievolucao)
        digievolucao_layout.addWidget(self.digievolucao_combobox)

    def setup_capture_cards(self):
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
        card_layouts = []
        
        for i in range(len(self.image_filenames)):
            if i % 2 == 0:
                cards_layout = QHBoxLayout()
                cards_layout.setAlignment(Qt.AlignTop)
                cards_layout.setSpacing(20)
                card_layouts.append(cards_layout)
                self.layout_configurar.addLayout(cards_layout)
            
            card = self.create_card(i)
            self.cards.append(card)
            cards_layout.addWidget(card)

    def create_card(self, index):
        card = QFrame()
        card.setStyleSheet("""
            background-color: #4682B4;
            color: white;
            border: 1px solid lightgray;
            padding: 10px;
            margin: 5px;
            border-radius: 10px;
            box-shadow: 2px 2px 5px lightgray;
        """)
        
        card_layout = QVBoxLayout(card)
        
        title = QLabel(f"{index + 1} - {self.get_title(index)}")
        title.setStyleSheet("font-size: 10px;")
        card_layout.addWidget(title)
        
        image_button_layout = QVBoxLayout()
        image_button_layout.setAlignment(Qt.AlignCenter)
        
        label = QLabel(self)
        label.setFixedSize(150, 100)
        label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        label.setAlignment(Qt.AlignCenter)
        image_button_layout.addWidget(label)
        
        botao_captura = QPushButton("Capturar")
        botao_captura.setStyleSheet("""
            font-size: 10px;
            background-color: #4682B4;
            color: white;
            border-radius: 5px;
        """)
        botao_captura.clicked.connect(lambda checked, idx=index: self.capturar_imagem(idx))
        image_button_layout.addWidget(botao_captura)
        
        card_layout.addLayout(image_button_layout)
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

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

