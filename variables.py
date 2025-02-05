import os

# Configuration settings
WINDOW_NAME = 'Digimon SuperRumble  '
RESOLUCAO_PADRAO = (800, 600)
SCREENSHOTS_DIR = "ScreenSaved"

# Screen coordinates
COORDINATES = {
    'x_inicial': '282', # ponta de cima do captcha
    'y_inicial': '183', # ponta de cima do captcha
    'x_final': '514', # ponta de baixo do captcha
    'y_final': '413' # ponta de baixo do captcha
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

# Application states
APP_STATES = {
    'RUNNING': 'running',
    'PAUSED': 'paused',
    'STOPPED': 'stopped'
}

# Initialize logging
last_log_message = None