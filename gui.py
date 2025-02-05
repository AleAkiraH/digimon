import sys
import win32gui
import win32con
from PyQt5.QtWidgets import (QApplication, QMainWindow, QLabel, QComboBox,
                             QPushButton, QVBoxLayout, QHBoxLayout,
                             QWidget, QMessageBox, QFrame,
                             QSizePolicy, QTabWidget)
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt
from PIL import ImageGrab
import io
import os

# Resolução padrão usada como referência
RESOLUCAO_PADRAO = (800, 600)

# Diretório para salvar as imagens capturadas
SCREENSHOTS_DIR = "ScreenSaved"

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Digimon Info")
        self.setGeometry(100, 100, 400, 600)
        self.setStyleSheet("background-color: white; color: black;")

        # Widget central e layout principal
        self.central_widget = QWidget()
        self.central_widget.setStyleSheet("background-color: white;")
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        self.layout.setAlignment(Qt.AlignTop)

        # Tab widget
        self.tabs = QTabWidget()
        self.layout.addWidget(self.tabs)

        # Tab "Jogar"
        self.tab_jogar = QWidget()
        self.tabs.addTab(self.tab_jogar, "Jogar")
        self.layout_jogar = QVBoxLayout(self.tab_jogar)

        # Título
        title_label = QLabel("Bem-vindo ao projeto TERAS")
        title_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #4682B4;")
        title_label.setAlignment(Qt.AlignCenter)
        self.layout_jogar.addWidget(title_label)

        # Imagem Digimon
        try:
            digimon_image = QPixmap("digimon.png")
            digimon_label = QLabel()
            digimon_label.setPixmap(digimon_image.scaledToWidth(200))  # Ajusta o tamanho da imagem
            digimon_label.setAlignment(Qt.AlignCenter)
            self.layout_jogar.addWidget(digimon_label)
        except:
            label_jogar = QLabel("Imagem Digimon não encontrada")
            self.layout_jogar.addWidget(label_jogar)

        # Tab "Configurar"
        self.tab_configurar = QWidget()
        self.tabs.addTab(self.tab_configurar, "Configurar")
        self.layout_configurar = QVBoxLayout(self.tab_configurar)
        self.layout_configurar.setAlignment(Qt.AlignTop)

        # Layout para configuração da resolução
        self.config_layout = QHBoxLayout()
        self.layout_configurar.addLayout(self.config_layout)

        # Label para Resolução do Jogo
        self.label_resolucao = QLabel("Resolução do Jogo:")
        self.config_layout.addWidget(self.label_resolucao)

        # Combobox para selecionar a resolução
        self.resolucoes = ["800x600", "1024x768"]
        self.resolucao_combobox = QComboBox()
        self.resolucao_combobox.addItems(self.resolucoes)
        self.config_layout.addWidget(self.resolucao_combobox)

        # Botão para definir a resolução
        self.botao_definir = QPushButton("Definir")
        self.botao_definir.clicked.connect(self.escolher_resolucao)
        self.config_layout.addWidget(self.botao_definir)

        # Mensagem informativa
        self.mensagem_info = QLabel("Certifique-se de que a tela de informações do Digimon está aberta!")
        self.layout_configurar.addWidget(self.mensagem_info)

        # Coordenadas de captura
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

        # Garante que o diretório de screenshots exista
        os.makedirs(SCREENSHOTS_DIR, exist_ok=True)

        # Cards para exibir as imagens e capturá-las
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

        # Carrega as imagens existentes
        self.carregar_imagens()

    def create_card(self, index):
        # Card Frame
        card = QFrame()
        card.setStyleSheet("background-color: #4682B4; color: white; border: 1px solid lightgray; padding: 10px; margin: 5px; border-radius: 10px; box-shadow: 2px 2px 5px lightgray;")
        card_layout = QVBoxLayout(card)

        # Título da imagem
        title = QLabel(f"{index + 1} - " + self.get_title(index))
        title.setStyleSheet("font-size: 10px;")
        card_layout.addWidget(title)

        # Layout vertical para a imagem e o botão
        image_button_layout = QVBoxLayout()
        image_button_layout.setAlignment(Qt.AlignCenter)

        # Label para exibir a imagem
        label = QLabel(self)
        label.setFixedSize(150, 100)  # Define um tamanho fixo para todas as imagens
        label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        label.setAlignment(Qt.AlignCenter)  # Centraliza a imagem no label
        image_button_layout.addWidget(label)

        # Botão para capturar a imagem
        botao_captura = QPushButton("Capturar")
        botao_captura.setStyleSheet("font-size: 10px; background-color: #4682B4; color: white; border-radius: 5px;")
        botao_captura.clicked.connect(lambda checked, idx=index: self.capturar_imagem(idx))
        image_button_layout.addWidget(botao_captura)

        card_layout.addLayout(image_button_layout)

        # Armazenar o label no card para fácil acesso
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
        if index < len(titles):
            return titles[index]
        else:
            return "Título Desconhecido"

    def escolher_resolucao(self):
        resolucao_selecionada = self.resolucao_combobox.currentText()
        print(f"Resolução selecionada: {resolucao_selecionada}")
        largura, altura = map(int, resolucao_selecionada.split("x"))
        hwnd = win32gui.FindWindow(None, 'Digimon SuperRumble  ')
        if hwnd == 0:
            QMessageBox.warning(self, "Erro", "Janela 'Digimon SuperRumble' não encontrada.")
            return
        style = win32gui.GetWindowLong(hwnd, win32con.GWL_STYLE)
        win32gui.SetWindowLong(hwnd, win32con.GWL_STYLE, style & ~win32con.WS_BORDER)
        win32gui.SetWindowPos(hwnd, 0, 0, 0, largura, altura, win32con.SWP_NOZORDER | win32con.SWP_FRAMECHANGED)

    def capturar_tela_e_salvar(self, x_inicio, y_inicio, x_fim, y_fim):
        hwnd = win32gui.FindWindow(None, 'Digimon SuperRumble  ')
        if hwnd == 0:
            QMessageBox.warning(self, "Erro", "Janela 'Digimon SuperRumble' não encontrada.")
            return None
        resolucao_selecionada = self.resolucao_combobox.currentText()
        largura, altura = map(int, resolucao_selecionada.split("x"))
       # Calcula a escala com base na resolução
        proporcao_x = largura / RESOLUCAO_PADRAO[0]
        proporcao_y = altura / RESOLUCAO_PADRAO[1]

        # Ajusta as coordenadas para a nova resolução
        x_inicio = int(x_inicio * proporcao_x)
        y_inicio = int(y_inicio * proporcao_y)
        x_fim = int(x_fim * proporcao_x)
        y_fim = int(y_fim * proporcao_y)

        # Obtém a posição da janela do jogo
        rect = win32gui.GetWindowRect(hwnd)
        client_rect = win32gui.GetClientRect(hwnd)
        x_tela, y_tela = win32gui.ClientToScreen(hwnd, (client_rect[0], client_rect[1]))

        # Ajusta as coordenadas para a tela
        x_inicio += x_tela
        y_inicio += y_tela
        x_fim += x_tela
        y_fim += y_tela

        # Captura a tela na área especificada
        try:
            screenshot = ImageGrab.grab(bbox=(x_inicio, y_inicio, x_fim, y_fim))
            buffer = io.BytesIO()
            screenshot.save(buffer, format="PNG")
            return buffer.getvalue()
        except Exception as e:
            print(f"Erro ao capturar a tela: {e}")
            return None

    def capturar_imagem(self, index):
        imagem_data = self.capturar_tela_e_salvar(*self.coordenadas[index])
        if imagem_data:
            imagem = QImage.fromData(imagem_data)
            pixmap = QPixmap(imagem)
            self.cards[index].label.setPixmap(pixmap)

            # Salvar a imagem no diretório SCREENSHOTS_DIR com os nomes corretos
            filename = os.path.join(SCREENSHOTS_DIR, self.image_filenames[index])
            hwnd = win32gui.FindWindow(None, 'Digimon SuperRumble  ')
            if hwnd == 0:
                QMessageBox.warning(self, "Erro", "Janela 'Digimon SuperRumble' não encontrada.")
                return
            resolucao_selecionada = self.resolucao_combobox.currentText()
            largura, altura = map(int, resolucao_selecionada.split("x"))
           # Calcula a escala com base na resolução
            proporcao_x = largura / RESOLUCAO_PADRAO[0]
            proporcao_y = altura / RESOLUCAO_PADRAO[1]

            # Ajusta as coordenadas para a nova resolução
            x_inicio = int(self.coordenadas[index][0] * proporcao_x)
            y_inicio = int(self.coordenadas[index][1] * proporcao_y)
            x_fim = int(self.coordenadas[index][2] * proporcao_x)
            y_fim = int(self.coordenadas[index][3] * proporcao_y)

            # Obtém a posição da janela do jogo
            rect = win32gui.GetWindowRect(hwnd)
            client_rect = win32gui.GetClientRect(hwnd)
            x_tela, y_tela = win32gui.ClientToScreen(hwnd, (client_rect[0], client_rect[1]))

            # Ajusta as coordenadas para a tela
            x_inicio += x_tela
            y_inicio += y_tela
            x_fim += x_tela
            y_fim += y_tela
            screenshot = ImageGrab.grab(bbox=(x_inicio, y_inicio, x_fim, y_fim))
            screenshot.save(filename, "PNG")

    def carregar_imagens(self):
        for index, filename in enumerate(self.image_filenames):
            filepath = os.path.join(SCREENSHOTS_DIR, filename)
            if os.path.exists(filepath):
                imagem = QImage(filepath)
                pixmap = QPixmap.fromImage(imagem)
                self.cards[index].label.setPixmap(pixmap)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
