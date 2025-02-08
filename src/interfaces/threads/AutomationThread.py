from PyQt5.QtCore import QThread, pyqtSignal
from datetime import datetime
import time
import pyautogui
from functions import is_image_on_screen, dividir_e_desenhar_contornos, initiate_battle, battle_actions, refill_digimons
from variables import IMAGE_PATHS

class AutomationThread(QThread):
    status_update = pyqtSignal(str)
    time_update = pyqtSignal(str)
    battles_update = pyqtSignal(int)
    battles_per_minute_update = pyqtSignal(float)
    
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.is_running = True
        self.is_paused = False
        self.battles_count = 0
        self.start_time = datetime.now()
        self.last_battle_time = self.start_time
    
    def run(self):   
        while self.is_running:
            if self.is_paused:
                time.sleep(0.1)
                continue
            
            try:
                self._process_automation()
            except Exception as e:
                self.status_update.emit(f"Erro na automação: {str(e)}")
            
            self._update_metrics()
            time.sleep(0.1)

    def _process_automation(self):
        if is_image_on_screen(IMAGE_PATHS['captcha_exists']):
            dividir_e_desenhar_contornos()
        
        self._handle_evp()
        self._handle_battle()
        
    def _handle_evp(self):
        if is_image_on_screen(IMAGE_PATHS['evp_terminado']):
            location = pyautogui.locateCenterOnScreen(IMAGE_PATHS['evp_terminado'], confidence=0.97)
            if location:
                x, y = location
                pyautogui.click(x, y)
                time.sleep(0.5)
                pyautogui.press('e')

    def _handle_battle(self):
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

    def _update_metrics(self):
        current_time = datetime.now()
        elapsed_time = current_time - self.start_time
        elapsed_time_str = str(elapsed_time).split('.')[0]
        self.time_update.emit(elapsed_time_str)
        self.battles_update.emit(self.battles_count)
        
        elapsed_minutes = elapsed_time.total_seconds() / 60
        battles_per_minute = self.battles_count / elapsed_minutes if elapsed_minutes > 0 else 0
        self.battles_per_minute_update.emit(battles_per_minute)

    def stop(self):
        self.is_running = False
        
    def pause(self):
        self.is_paused = True
        
    def resume(self):
        self.is_paused = False

    def reset(self):
        self.start_time = datetime.now()
        self.battles_count = 0
        self.last_battle_time = self.start_time