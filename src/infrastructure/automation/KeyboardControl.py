import pyautogui

class KeyboardControl:
    @staticmethod
    def press(key: str):
        pyautogui.press(key)