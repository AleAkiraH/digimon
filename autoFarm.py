from pymongo import MongoClient
import os
import time
import pyautogui
import numpy as np
import cv2
import random
import json
import pygetwindow as gw
from datetime import datetime
import threading
import mss
from telegram import Bot
from telegram.utils.request import Request
import win32gui
import win32con
import keyboard

def verificar_senha_temporaria(senha):
    # URL de conexão com o MongoDB
    mongo_url = "mongodb+srv://administrador:administrador@cluster0.8vjnvh9.mongodb.net/?retryWrites=true&w=majority"
    
    # Conectar ao cliente MongoDB
    client = MongoClient(mongo_url)
    
    # Acessar a base de dados e a coleção
    db = client['DigimonSuperRumble']
    collection = db['LicencaTemporaria']
    
    # Buscar o documento que contém o campo SenhaTemporaria
    documento = collection.find_one({"licenca": senha})
    
    if documento:
        senha_temporaria = documento['licenca']
        log(f"Senha Temporária válida!")
        
        # Verifica se a senha é a esperada
        if senha_temporaria == senha:
            log("Senha Temporária correta. Continuando o código..." + senha_temporaria == "123")
            return True
        else:
            log("Senha Temporária incorreta. Encerrando o código." + senha_temporaria == "123")
            return False
    else:
        log("Nenhum documento encontrado com o campo SenhaTemporaria.")
        return False
    
def record_and_send_screen_video(bot_token, chat_id, duration=30):
    """Grava a tela do computador por 30 segundos e envia para o Telegram."""
    # Configurações do vídeo
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    video_path = f'video_{datetime.now().strftime("%Y%m%d_%H%M%S")}.mp4'
    
    # Use a largura e altura da tela para o VideoWriter
    screen_width = 1920  # Substitua pela largura da sua tela
    screen_height = 1080  # Substitua pela altura da sua tela
    out = cv2.VideoWriter(video_path, fourcc, 30.0, (screen_width, screen_height))
    
    # Gravar vídeo
    with mss.mss() as sct:
        start_time = time.time()
        while int(time.time() - start_time) < duration:
            img = sct.grab(sct.monitors[1])  # Captura a tela principal (monitor 1)
            img_np = np.array(img)
            frame = cv2.cvtColor(img_np, cv2.COLOR_BGRA2BGR)
            out.write(frame)
    
    # Liberar os recursos
    out.release()
    
    # Enviar vídeo para o Telegram com timeout
    request = Request(con_pool_size=8, read_timeout=100, connect_timeout=100)  # Aumenta o timeout
    bot = Bot(token=bot_token, request=request)  # Passa o objeto Request
    
    try:
        with open(video_path, 'rb') as video:
            bot.send_video(chat_id=chat_id, video=video, timeout=360, caption="Vídeo Enviado!")
        log("Vídeo da tela gravado e enviado com sucesso.")
        
        # Deletar o vídeo após o envio
        os.remove(video_path)
        log("Vídeo deletado com sucesso.")
        
    except Exception as e:
        log(f"Erro ao enviar vídeo: {e}")

# Função para capturar a tela e enviar pelo Telegram
def send_screenshot_telegram(bot_token, chat_id, message="Aqui está a screenshot"):
    try:    
        # Ativa a janela
        hwnd = activate_window(window_name)
        if hwnd:
            # Obtém a janela ativa
            window = gw.getWindowsWithTitle(window_name)[0]
            
            # Obtém as coordenadas da janela
            left, top, width, height = window.left, window.top, window.width, window.height
            
            # Captura a área da janela
            screenshot = pyautogui.screenshot(region=(left, top, width, height))
            
            # Salva a screenshot em um arquivo temporário
            screenshot_path = f'screenshot_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png'
            screenshot.save(screenshot_path)

            # Configura o bot do Telegram
            bot = Bot(token=bot_token)
            
            # Envia a imagem para o chat especificado
            with open(screenshot_path, 'rb') as photo:
                bot.send_photo(chat_id=chat_id, photo=photo, caption=message)

            os.remove(screenshot_path)
        else:
            print("A janela não foi ativada.")
    except Exception as e:
        print(f"Erro ao capturar a tela: {e}")
        
def log(message, log_file="script_logs.txt"):
    try:
        """Loga uma mensagem no console e salva em um arquivo, evitando repetições consecutivas."""
        global last_log_message
        if message != last_log_message:
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")  # Adiciona um timestamp ao log
            formatted_message = f"[{timestamp}] {message}"
            print(formatted_message)  # Mostra no terminal
            
            # Salva no arquivo de log
            with open(log_file, "a", encoding="utf-8") as file:
                file.write(formatted_message + "\n")
            
            last_log_message = message
    except Exception as e:
        print(f"Erro ao registrar a mensagem: {e}")

last_log_message = None
window_name = 'Digimon SuperRumble  '  # Nome da janela

image_path_captcha_exists = "ScreenSaved\captcha_exists.PNG"
battle_start_image_HP = "ScreenSaved\battle_start_hp.png"
battle_start_image_SP = "ScreenSaved\battle_start_sp.png"
battle_start_image_EVP = "ScreenSaved\battle_start_evp.png"
battle_detection_image = "ScreenSaved\battle_detection.png"
battle_finish_image = "ScreenSaved\battle_finish.png"
janela_digimon = "ScreenSaved\janela_digimon.png"
EVP_Terminado = "ScreenSaved\EVP_Terminado.png"

x_inicial = "540"
y_inicial = "239"
x_final = "825"
y_final = "525"

bot_token,chat_id = "", ""

def calcular_area_homogenea(quadrado):
    """
    Função para calcular a homogeneidade de um quadrado, ou seja, quantos pixels têm a mesma cor.
    """
    # Converte o quadrado para um vetor de pixels
    pixels = quadrado.reshape(-1, quadrado.shape[-1])
    
    # Conta a quantidade de pixels únicos
    unique_pixels, counts = np.unique(pixels, axis=0, return_counts=True)
    
    # Retorna o maior número de pixels idênticos
    return max(counts)

def mover_mouse_humano(x_inicial, y_inicial, x_final, y_final):
    """
    Função para mover o mouse de forma "humana", com movimentos mais naturais, em vez de uma linha reta.
    """
    num_etapas = random.randint(10, 20)  # Número de etapas do movimento
    x_step = (x_final - x_inicial) / num_etapas
    y_step = (y_final - y_inicial) / num_etapas

    # Movimenta o mouse em etapas pequenas, com desvios aleatórios
    for i in range(num_etapas):
        x = int(x_inicial + x_step * i + random.randint(-3, 3))  # Desvio aleatório no eixo X
        y = int(y_inicial + y_step * i + random.randint(-3, 3))  # Desvio aleatório no eixo Y
        pyautogui.moveTo(x, y, duration=random.uniform(0.05, 0.1))  # Variação na duração do movimento
        time.sleep(random.uniform(0.01, 0.03))  # Pequeno delay entre os movimentos

def dividir_e_desenhar_contornos():
    send_screenshot_telegram(bot_token,chat_id, "Captcha detectado")
    video_thread = threading.Thread(target=record_and_send_screen_video, args=(bot_token, chat_id))
    video_thread.start()  # Inicia a thread
    time.sleep(1)
    # Captura a área da tela
    left = min(x_inicial, x_final)
    top = min(y_inicial, y_final)
    width = abs(x_final - x_inicial)
    height = abs(y_final - y_inicial)
    screenshot = pyautogui.screenshot(region=(left, top, width, height))

    # Converte a imagem PIL para um array numpy (OpenCV)
    image = np.array(screenshot)

    # Converte de RGB para BGR, pois OpenCV usa BGR como padrão
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

    # Obter as dimensões da imagem
    altura, largura, _ = image.shape

    # Calcular o tamanho de cada quadrado
    tamanho_quadrado_largura = largura // 8
    tamanho_quadrado_altura = altura // 8

    max_homogeneidade = 0  # Para armazenar a maior homogeneidade encontrada
    quadrado_mais_homogeneo = None  # Para armazenar o quadrado com maior homogeneidade

    # Desenhar os contornos dos quadrados e verificar homogeneidade
    for i in range(8):
        for j in range(8):
            # Coordenadas do quadrado
            x_inicio = i * tamanho_quadrado_largura
            y_inicio = j * tamanho_quadrado_altura
            x_fim = (i + 1) * tamanho_quadrado_largura
            y_fim = (j + 1) * tamanho_quadrado_altura

            # Recortar o quadrado da imagem
            quadrado = image[y_inicio:y_fim, x_inicio:x_fim]

            # Calcular a homogeneidade do quadrado
            homogeneidade = calcular_area_homogenea(quadrado)
            
            # Se a homogeneidade for maior que a atual, atualiza
            if homogeneidade > max_homogeneidade:
                max_homogeneidade = homogeneidade
                quadrado_mais_homogeneo = (x_inicio, y_inicio, x_fim, y_fim)

    # Destaca o quadrado azul
    if quadrado_mais_homogeneo:
        x_inicio, y_inicio, x_fim, y_fim = quadrado_mais_homogeneo

        # Recorta o quadrado azul da imagem original
        quadrado_azul = image[y_inicio:y_fim, x_inicio:x_fim]

        # Salva o quadrado azul como imagem temporáriagv
        temp_image_path = "quadrado_azul.png"
        cv2.imwrite(temp_image_path, quadrado_azul)
    
        # Move o mouse usando a imagem recortada
        if PressHoldImage(temp_image_path):
            log(f"Mouse movido para o quadrado azul usando a imagem {temp_image_path}.")
        else:
            log("Falha ao localizar o quadrado azul na tela.")
    else:
        log("Nenhum quadrado azul encontrado.")

    if is_image_on_screen(image_path_captcha_exists):
        print(f"Imagem {image_path_captcha_exists} encontrada na tela (2). Processando...")
        send_screenshot_telegram(bot_token,chat_id, "Captcha detectado")
        video_thread = threading.Thread(target=record_and_send_screen_video, args=(bot_token, chat_id))
        video_thread.start()  # Inicia a thread
        time.sleep(1)
        # Captura a área da tela
        left = min(x_inicial, x_final)
        top = min(y_inicial, y_final)
        width = abs(x_final - x_inicial)
        height = abs(y_final - y_inicial)
        screenshot = pyautogui.screenshot(region=(left, top, width, height))

        # Converte a imagem PIL para um array numpy (OpenCV)
        image = np.array(screenshot)

        # Converte de RGB para BGR, pois OpenCV usa BGR como padrão
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        # Obter as dimensões da imagem
        altura, largura, _ = image.shape

        # Calcular o tamanho de cada quadrado
        tamanho_quadrado_largura = largura // 8
        tamanho_quadrado_altura = altura // 8

        max_homogeneidade = 0  # Para armazenar a maior homogeneidade encontrada
        quadrado_mais_homogeneo = None  # Para armazenar o quadrado com maior homogeneidade

        # Desenhar os contornos dos quadrados e verificar homogeneidade
        for i in range(8):
            for j in range(8):
                # Coordenadas do quadrado
                x_inicio = i * tamanho_quadrado_largura
                y_inicio = j * tamanho_quadrado_altura
                x_fim = (i + 1) * tamanho_quadrado_largura
                y_fim = (j + 1) * tamanho_quadrado_altura

                # Recortar o quadrado da imagem
                quadrado = image[y_inicio:y_fim, x_inicio:x_fim]

                # Calcular a homogeneidade do quadrado
                homogeneidade = calcular_area_homogenea(quadrado)
                
                # Se a homogeneidade for maior que a atual, atualiza
                if homogeneidade > max_homogeneidade:
                    max_homogeneidade = homogeneidade
                    quadrado_mais_homogeneo = (x_inicio, y_inicio, x_fim, y_fim)

        # Destaca o quadrado azul
        if quadrado_mais_homogeneo:
            x_inicio, y_inicio, x_fim, y_fim = quadrado_mais_homogeneo

            # Recorta o quadrado azul da imagem original
            quadrado_azul = image[y_inicio:y_fim, x_inicio:x_fim]

            # Salva o quadrado azul como imagem temporáriagv
            temp_image_path = "quadrado_azul.png"
            cv2.imwrite(temp_image_path, quadrado_azul)
        
            # Move o mouse usando a imagem recortada
            if PressHoldImage(temp_image_path):
                log(f"Mouse movido para o quadrado azul usando a imagem {temp_image_path}.")
            else:
                log("Falha ao localizar o quadrado azul na tela.")
        else:
            log("Nenhum quadrado azul encontrado.")

    if is_image_on_screen(image_path_captcha_exists):
        print(f"Imagem {image_path_captcha_exists} encontrada na tela (3). Processando...")
        send_screenshot_telegram(bot_token,chat_id, "Captcha detectado")
        video_thread = threading.Thread(target=record_and_send_screen_video, args=(bot_token, chat_id))
        video_thread.start()  # Inicia a thread
        time.sleep(1)
        # Captura a área da tela
        left = min(x_inicial, x_final)
        top = min(y_inicial, y_final)
        width = abs(x_final - x_inicial)
        height = abs(y_final - y_inicial)
        screenshot = pyautogui.screenshot(region=(left, top, width, height))

        # Converte a imagem PIL para um array numpy (OpenCV)
        image = np.array(screenshot)

        # Converte de RGB para BGR, pois OpenCV usa BGR como padrão
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        # Obter as dimensões da imagem
        altura, largura, _ = image.shape

        # Calcular o tamanho de cada quadrado
        tamanho_quadrado_largura = largura // 8
        tamanho_quadrado_altura = altura // 8

        max_homogeneidade = 0  # Para armazenar a maior homogeneidade encontrada
        quadrado_mais_homogeneo = None  # Para armazenar o quadrado com maior homogeneidade

        # Desenhar os contornos dos quadrados e verificar homogeneidade
        for i in range(8):
            for j in range(8):
                # Coordenadas do quadrado
                x_inicio = i * tamanho_quadrado_largura
                y_inicio = j * tamanho_quadrado_altura
                x_fim = (i + 1) * tamanho_quadrado_largura
                y_fim = (j + 1) * tamanho_quadrado_altura

                # Recortar o quadrado da imagem
                quadrado = image[y_inicio:y_fim, x_inicio:x_fim]

                # Calcular a homogeneidade do quadrado
                homogeneidade = calcular_area_homogenea(quadrado)
                
                # Se a homogeneidade for maior que a atual, atualiza
                if homogeneidade > max_homogeneidade:
                    max_homogeneidade = homogeneidade
                    quadrado_mais_homogeneo = (x_inicio, y_inicio, x_fim, y_fim)

        # Destaca o quadrado azul
        if quadrado_mais_homogeneo:
            x_inicio, y_inicio, x_fim, y_fim = quadrado_mais_homogeneo

            # Recorta o quadrado azul da imagem original
            quadrado_azul = image[y_inicio:y_fim, x_inicio:x_fim]

            # Salva o quadrado azul como imagem temporáriagv
            temp_image_path = "quadrado_azul.png"
            cv2.imwrite(temp_image_path, quadrado_azul)
        
            # Move o mouse usando a imagem recortada
            if PressHoldImage(temp_image_path):
                log(f"Mouse movido para o quadrado azul usando a imagem {temp_image_path}.")
            else:
                log("Falha ao localizar o quadrado azul na tela.")
        else:
            log("Nenhum quadrado azul encontrado.")

def activate_window(window_name):
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
    location = pyautogui.locateCenterOnScreen(image_path, confidence=confidence)
    return location is not None


def click_image_and_press_key(image_path, key_after_click, confidence=0.97):
    if is_image_on_screen(image_path_captcha_exists):
        print(f"Imagem {image_path_captcha_exists} encontrada na tela. Processando...")
        dividir_e_desenhar_contornos()
    location = pyautogui.locateCenterOnScreen(image_path, confidence=confidence)
    if location:
        x, y = location
        pyautogui.click(x, y)
        log(f"Imagem {image_path} encontrada em ({x}, {y}) e clicada.")
        time.sleep(0.5)
        pyautogui.press(key_after_click)
        return True
    return False

def PressHoldImage(image_path, confidence=0.85):
    """
    Localiza uma imagem na tela, move o mouse de forma simulada (como humano) até o ponto
    e realiza o clique pressionado (click e hold) se a imagem for encontrada.
    """
    location = pyautogui.locateCenterOnScreen(image_path, confidence=confidence)
    if location:
        x_final, y_final = location  # Coordenadas da imagem encontrada
        x_inicial, y_inicial = 555, 554  # Coordenada inicial

        log(f"Movendo o mouse para a imagem encontrada em ({x_final}, {y_final}) com movimentos simulados.")
        
        # Pressiona o botão do mouse no início
        pyautogui.mouseDown(x=x_inicial, y=y_inicial)

        # # Movimenta o mouse de forma simulada e natural
        mover_mouse_humano(x_inicial, y_inicial, x_final, y_final)
        
        # Solta o botão do mouse ao chegar no destino
        pyautogui.mouseUp(x=x_final, y=y_final)

        log(f"Imagem {image_path} encontrada em ({x_final}, {y_final}), movimento concluído e botão solto.")
        time.sleep(5)
        return True
    else:
        log(f"Imagem {image_path} não encontrada na tela.")
        return False

def initiate_battle(battle_detection_image):
    global num_battles
    while is_image_on_screen(battle_finish_image):
        pyautogui.press('v')
        log("Procurando batalha: pressionando 'F'.")
        for _ in range(20):  # Pressionar 'g' 20 vezes
            if is_image_on_screen(battle_detection_image):
                break
            pyautogui.press('g')
            pyautogui.press('g')
            pyautogui.press('g')
            pyautogui.press('g')
            pyautogui.press('g')
            if not is_image_on_screen(battle_finish_image):
                # log("Iniciando batalha: pressionando 'E1'.")
                pyautogui.press("e")  # w
                pyautogui.press("1")  # 1
                # time.sleep(0.1)
                pyautogui.press("d");  # a
                pyautogui.press("1");  # 1
                # time.sleep(0.15)
                pyautogui.press("c");  # z
                pyautogui.press(1);  # 1
                # time.sleep(0.12)
            else:
                pyautogui.press('f')

        if is_image_on_screen(image_path_captcha_exists):
            print(f"Imagem {image_path_captcha_exists} encontrada na tela. Processando...")
            dividir_e_desenhar_contornos()
        
        time.sleep(0.5)
    log("Batalha iniciada.")

def battle_actions(battle_detection_image, battle_finish_image):
    log("Executando ações de batalha.")
    while is_image_on_screen(battle_detection_image):
        pyautogui.press("e")  # w
        pyautogui.press("1")  # 1
        pyautogui.press("d");  # a
        pyautogui.press("1");  # 1
        pyautogui.press("c");  # z

    log("Batalha finalizada.")
    while not is_image_on_screen(battle_finish_image):
        log("Aguardando para iniciar uma nova batalha.")

def refill_digimons():
    digievolucao = config["digievolucao"]
    if is_image_on_screen(image_path_captcha_exists):
        print(f"Imagem {image_path_captcha_exists} encontrada na tela. Processando...")
        dividir_e_desenhar_contornos()
    # Coordenadas para tirar digivolução dos Digimons
    digivolucao_tirar = [
        [(484, 254), (731, 248), (728, 269)],  # Primeiro Digimon
        [(484, 294), (731, 248), (728, 269)],  # Segundo Digimon
        [(484, 340), (731, 248), (728, 269)],  # Terceiro Digimon
    ]
    
    # Coordenadas para digivoluir os Digimons
    if digievolucao == "rookie":
        digivolucao_colocar = config["digivolucao_colocar"]["rookie"]
        log("Realizando digivolução para rookie.")
    elif digievolucao == "champion":
        digivolucao_colocar = config["digivolucao_colocar"]["champion"]
        log("Realizando digivolução para champion.")
    elif digievolucao == "ultimate":
        digivolucao_colocar = config["digivolucao_colocar"]["ultimate"]
        log("Realizando digivolução para Ultimate.")
    elif digievolucao == "mega":
        digivolucao_colocar = config["digivolucao_colocar"]["mega"]
        log("Realizando digivolução para Mega.")
    elif digievolucao == "custom":
        digivolucao_colocar = config["digivolucao_colocar"]["custom"]
        log("Realizando digivolução para custom.")
    else:
        log("Tipo de digivolução desconhecido. Usando mega como padrão.")
        digivolucao_colocar = config["digivolucao_colocar"]["mega"]
    
    # Realiza o processo de tirar digivolução
    for digivolucao in digivolucao_tirar:
        for coord in digivolucao:
            if is_image_on_screen(image_path_captcha_exists):
                print(f"Imagem {image_path_captcha_exists} encontrada na tela. Processando...")
                dividir_e_desenhar_contornos()
            pyautogui.click(x=coord[0], y=coord[1])
        log("Digivolução retirada.")
    
    # Realiza o processo de digivoluir
    for digivolucao in digivolucao_colocar:
        for coord in digivolucao:
            time.sleep(0.5)  # Pequeno delay entre os cliques
            pyautogui.click(x=coord[0], y=coord[1])            
        log("Digivolução aplicada.")
    pyautogui.press('v')
    log("Refill concluído.")

def executar_script():
    hwnd = activate_window(window_name)
    send_screenshot_telegram(bot_token,chat_id, "Bot Iniciado")

    if hwnd:
        start_time = time.time()
        last_screenshot_time = time.time()
        while True:
            elapsed_time = time.time() - start_time
            
            # Converte o tempo decorrido em horas, minutos e segundos
            elapsed_hours = int(elapsed_time // 3600)
            elapsed_minutes = int((elapsed_time % 3600) // 60)
            elapsed_seconds = int(elapsed_time % 60)
            elapsed_time_str = f"{elapsed_hours:02}:{elapsed_minutes:02}:{elapsed_seconds:02}"

            # Continua com o ciclo principal de automação
            log("Automação principal em execução...")
            
            if is_image_on_screen(image_path_captcha_exists):
                print(f"Imagem {image_path_captcha_exists} encontrada na tela. Processando...")
                dividir_e_desenhar_contornos()
            if is_image_on_screen(image_path_captcha_exists):
                print(f"Imagem {image_path_captcha_exists} encontrada na tela. Processando...")
                dividir_e_desenhar_contornos()
            if is_image_on_screen(image_path_captcha_exists):
                print(f"Imagem {image_path_captcha_exists} encontrada na tela. Processando...")
                dividir_e_desenhar_contornos()
            
            time.sleep(1)
            pyautogui.press('g')
            pyautogui.press('g')
            if is_image_on_screen(image_path_captcha_exists):
                print(f"Imagem {image_path_captcha_exists} encontrada na tela. Processando...")
                dividir_e_desenhar_contornos()
            pyautogui.press('g')
            pyautogui.press('g')
            pyautogui.press('v')
            time.sleep(1)
            if is_image_on_screen(image_path_captcha_exists):
                print(f"Imagem {image_path_captcha_exists} encontrada na tela. Processando...")
                dividir_e_desenhar_contornos()
            log("Tela de digimons aberta...")
            if is_image_on_screen(EVP_Terminado):
                click_image_and_press_key(EVP_Terminado, 'e')

            battle_start_image_HP_Try = 3
            while not is_image_on_screen(battle_start_image_HP):
                if is_image_on_screen(image_path_captcha_exists):
                    print(f"Imagem {image_path_captcha_exists} encontrada na tela. Processando...")
                    dividir_e_desenhar_contornos()
                if battle_start_image_HP_Try == 0:
                    log("Imagem de inicio de batalha não encontrada.")
                    if not is_image_on_screen(janela_digimon):
                        pyautogui.press('v')                        
                    break
                battle_start_image_HP_Try = battle_start_image_HP_Try - 1
                time.sleep(1)

            time.sleep(1)
            log("Buscando imagem de inicio de batalha")
            if (is_image_on_screen(battle_start_image_HP) and is_image_on_screen(battle_start_image_SP) and is_image_on_screen(battle_start_image_EVP)):
                log("Imagem de início de batalha detectada.")                
                pyautogui.press('i')
                if keyboard.is_pressed('r'):
                    send_screenshot_telegram(bot_token, chat_id, f"O bot foi encerrado. Tempo de execução foi {elapsed_time_str}. Total de batalhas iniciadas: {num_battles}")
                    break
                if time.time() - last_screenshot_time >= 1800:
                    time.sleep(0.5)
                    send_screenshot_telegram(bot_token, chat_id, f"O bot está em execução há {elapsed_time_str}. Total de batalhas iniciadas: {num_battles}")
                    last_screenshot_time = time.time()  # Atualiza o tempo da última captura
                if is_image_on_screen(image_path_captcha_exists):
                    print(f"Imagem {image_path_captcha_exists} encontrada na tela. Processando...")
                    dividir_e_desenhar_contornos()
                initiate_battle(battle_detection_image)
                if is_image_on_screen(image_path_captcha_exists):
                    print(f"Imagem {image_path_captcha_exists} encontrada na tela. Processando...")
                    dividir_e_desenhar_contornos()
                battle_actions(battle_detection_image, battle_finish_image)
                if is_image_on_screen(image_path_captcha_exists):
                    print(f"Imagem {image_path_captcha_exists} encontrada na tela. Processando...")
                    dividir_e_desenhar_contornos()
                # for _ in range(50):
                #     pyautogui.press('1')
                #     time.sleep(0.050)
                # for _ in range(30):
                #     pyautogui.press('2')
                #     time.sleep(0.050)
            else:
                if not is_image_on_screen(battle_start_image_EVP):
                    pyautogui.press('v')
                    for _ in range(35):  # Pressionar 'g' 20 vezes
                        if is_image_on_screen(image_path_captcha_exists):
                            print(f"Imagem {image_path_captcha_exists} encontrada na tela. Processando...")
                            dividir_e_desenhar_contornos()
                        pyautogui.press('5')
                        time.sleep(0.5)                       
                    pyautogui.press('v')
                refill_digimons()

senha = input("Digite aqui sua senha temporária: ")

if verificar_senha_temporaria(senha):
    hwnd = win32gui.FindWindow(None, 'Digimon SuperRumble  ')
    style = win32gui.GetWindowLong(hwnd, win32con.GWL_STYLE)
    win32gui.SetWindowLong(hwnd, win32con.GWL_STYLE, style & ~win32con.WS_BORDER)
    win32gui.SetWindowPos(hwnd, 0, 0, 0, 1366, 768, win32con.SWP_NOZORDER | win32con.SWP_FRAMECHANGED)
    executar_script()
else:
    exit("Acesso negado.")
