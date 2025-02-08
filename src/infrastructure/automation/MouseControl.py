import pyautogui
import time

class MouseControl:
    @staticmethod
    def move(x_inicial: int, y_inicial: int, x_final: int, y_final: int):
        num_etapas = 15
        x_step = (x_final - x_inicial) / num_etapas
        y_step = (y_final - y_inicial) / num_etapas
        
        for i in range(num_etapas + 1):
            xi = int(x_inicial + x_step * i)
            yi = int(y_inicial + y_step * i)
            pyautogui.moveTo(xi, yi, duration=0.01)
            time.sleep(0.01)
        pyautogui.mouseUp(x=xi, y=yi)
    
    @staticmethod
    def click(x: int, y: int):
        pyautogui.click(x=x, y=y)