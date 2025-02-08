import pyautogui
import time
from typing import Dict
from ..entities.Battle import Battle
from ...infrastructure.automation.ImageDetection import ImageDetection
from ...infrastructure.automation.MouseControl import MouseControl
from ...infrastructure.automation.KeyboardControl import KeyboardControl

class BattleAutomationUseCase:
    def __init__(self, battle: Battle, image_detection: ImageDetection, 
                 mouse_control: MouseControl, keyboard_control: KeyboardControl):
        self.battle = battle
        self.image_detection = image_detection
        self.mouse_control = mouse_control
        self.keyboard_control = keyboard_control
        self.is_running = True
        self.is_paused = False
    
    def execute(self, battle_keys: Dict[str, str]):
        while self.is_running:
            if self.is_paused:
                time.sleep(0.1)
                continue
                
            try:
                if self.image_detection.is_captcha_visible():
                    self.handle_captcha()
                
                self.handle_evp()
                self.handle_battle(battle_keys)
                
            except Exception as e:
                print(f"Erro na automação: {str(e)}")
            
            time.sleep(0.1)
    
    def handle_captcha(self):
        # Implementação do tratamento do captcha
        pass
    
    def handle_evp(self):
        if self.image_detection.is_evp_finished():
            location = self.image_detection.get_evp_location()
            if location:
                x, y = location
                self.mouse_control.click(x, y)
                time.sleep(0.5)
                self.keyboard_control.press('e')
    
    def handle_battle(self, battle_keys: Dict[str, str]):
        # Implementação da lógica de batalha
        pass
    
    def stop(self):
        self.is_running = False
    
    def pause(self):
        self.is_paused = True
    
    def resume(self):
        self.is_paused = False