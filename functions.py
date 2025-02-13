import time
import pyautogui
import numpy as np
import cv2
import keyboard
import win32gui
import win32con
from PIL import ImageGrab
import io
from variables import COORDINATES, IMAGE_PATHS, DIGIVOLUCAO, WINDOW_NAME
from secure_config import SECURE_CONFIG
from telegram.ext import Updater
from telegram import Bot
from datetime import datetime, timedelta
import os
import getpass
import pygetwindow as gw
from database import Database  # Certifique-se de importar a classe Database corretamente

# Initialize logging
last_log_message = None

# Telegram configuration
BOT_TOKEN = SECURE_CONFIG['BOT_TOKEN']
CHAT_ID = SECURE_CONFIG['CHAT_ID']

def send_screenshot_telegram(bot_token=BOT_TOKEN, chat_id=CHAT_ID, message="Aqui está a screenshot"):
    """Send screenshot to Telegram"""
    try:
        # Activate the window
        hwnd = activate_window(WINDOW_NAME)
        if hwnd:
            # Get active window
            window = gw.getWindowsWithTitle(WINDOW_NAME)[0]
            
            # Get window coordinates
            left, top, width, height = window.left, window.top, window.width, window.height
            
            # Capture window area
            screenshot = pyautogui.screenshot(region=(left, top, width, height))
            
            # Save screenshot to temporary file
            screenshot_path = f'screenshot_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png'
            screenshot.save(screenshot_path)

            # Configure Telegram bot
            bot = Bot(token=bot_token)
            
            # Send image to specified chat
            with open(screenshot_path, 'rb') as photo:
                bot.send_photo(chat_id=chat_id, photo=photo, caption=message)

            os.remove(screenshot_path)
        else:
            log("Window was not activated")
    except Exception as e:
        log(f"Error sending screenshot to Telegram: {str(e)}")

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

def is_image_on_screen(image_path, confidence=0.85, region=None):
    """Check if an image is present on screen"""
    if region:
        x1, y1, x2, y2 = region
        location = pyautogui.locateCenterOnScreen(image_path, confidence=confidence, region=(x1, y1, x2 - x1, y2 - y1))
    else:
        location = pyautogui.locateCenterOnScreen(image_path, confidence=confidence)
    return location is not None

def mover_mouse(x_inicial, y_inicial, x_final, y_final):
    """Move mouse de um ponto a outro com diferentes velocidades"""    
    num_etapas = 15
    x_step = (x_final - x_inicial) / num_etapas
    y_step = (y_final - y_inicial) / num_etapas
    
    for i in range(num_etapas + 1):  # Inclui o ponto final
        xi = int(x_inicial + x_step * i)
        yi = int(y_inicial + y_step * i)
        pyautogui.moveTo(xi, yi, duration=0.01)  # Duração fixa para cada movimento
        time.sleep(0.01)
    pyautogui.mouseUp(x=xi, y=yi)

def calcular_area_homogenea(quadrado):
    """Calculate homogeneous area in a square"""
    pixels = quadrado.reshape(-1, quadrado.shape[-1])
    unique_pixels, counts = np.unique(pixels, axis=0, return_counts=True)
    return max(counts)

def dividir_e_desenhar_contornos(username):    
    """Process captcha by dividing and drawing contours"""
    left = min(int(COORDINATES['x_inicial']), int(COORDINATES['x_final'])) 
    top = min(int(COORDINATES['y_inicial']), int(COORDINATES['y_final']))
    width = abs(int(COORDINATES['x_final']) - int(COORDINATES['x_inicial']))
    height = abs(int(COORDINATES['y_final']) - int(COORDINATES['y_inicial']))

    screenshot = pyautogui.screenshot(region=(left, top, width, height))
    image = np.array(screenshot)
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    cv2.imwrite("CaptchaSolution\\screenshot.png", image)

    # Send screenshot to Telegram when captcha is detected
    send_screenshot_telegram(message=f"{username}: Captcha detectado!")

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
        temp_image_path = "CaptchaSolution\\quadrado_azul.png"
        cv2.imwrite(temp_image_path, quadrado_azul)

        location = pyautogui.locateCenterOnScreen(temp_image_path, confidence=0.85)
        if location:
            x_final, y_final = location
            x_inicial, y_inicial = 296, 438  # centro do objeto a ser arrastado do captcha

            pyautogui.mouseDown(x=x_inicial, y=y_inicial)
            mover_mouse(x_inicial, y_inicial, x_final, y_final)

            log(f"Mouse movido para o quadrado azul.")
            time.sleep(1)
        else:
            log("Falha ao localizar o quadrado azul na tela.")

def battle_actions(battle_keys, skill_coords):
    """Execute battle actions"""
    log("Executando ações de batalha.")
    while is_image_on_screen(IMAGE_PATHS['battle_detection'], region=(768, 541, 779, 554)):
        # if not is_image_on_screen(IMAGE_PATHS['skill1'], region=skill_coords['skill1']):
        if battle_keys['group1']:
            pyautogui.press(battle_keys['group1'].lower())
            pyautogui.press("1")
        # if not is_image_on_screen(IMAGE_PATHS['skill2'], region=skill_coords['skill2']):
        if battle_keys['group2']:
            pyautogui.press(battle_keys['group2'].lower())
            pyautogui.press("1")
        # if not is_image_on_screen(IMAGE_PATHS['skill3'], region=skill_coords['skill3']):
        if battle_keys['group3']:
            pyautogui.press(battle_keys['group3'].lower())
            pyautogui.press("1")
        time.sleep(3)

    log("Batalha finalizada.")
    while not is_image_on_screen(IMAGE_PATHS['battle_finish'], region=(468, 565, 485, 576)):
        log("Aguardando para iniciar uma nova batalha.")

def record_historical_action(username, action):
    """Record an action in the historical collection"""
    db = Database()
    db.record_action(username, action)
    db.close()
    log(f"Ação '{action}' registrada para o usuário {username}.")

def initiate_battle(battle_keys):    
    pyautogui.press('v')
    while is_image_on_screen(IMAGE_PATHS['battle_finish'], region=(468, 565, 485, 576)):
        
        if is_image_on_screen(IMAGE_PATHS['captcha_exists']):
            dividir_e_desenhar_contornos()
        
        log("Procurando batalha: pressionando 'F'.")
        
        if is_image_on_screen(IMAGE_PATHS['battle_detection'], region=(768, 541, 779, 554)):
            break
        
        for _ in range(5):
            pyautogui.press('g')
            pyautogui.press('f')

    while not is_image_on_screen(IMAGE_PATHS['battle_detection'], region=(768, 541, 779, 554)):
        if battle_keys['group1']:
            pyautogui.press(battle_keys['group1'].lower())
            pyautogui.press("1")
        if battle_keys['group2']:
            pyautogui.press(battle_keys['group2'].lower())
            pyautogui.press("1")
        if battle_keys['group3']:
            pyautogui.press(battle_keys['group3'].lower())
            pyautogui.press("1")

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