import pyautogui
from ...config.image_paths import IMAGE_PATHS

class ImageDetection:
    @staticmethod
    def is_image_on_screen(image_path: str, confidence: float = 0.85) -> bool:
        location = pyautogui.locateCenterOnScreen(image_path, confidence=confidence)
        return location is not None
    
    def is_captcha_visible(self) -> bool:
        return self.is_image_on_screen(IMAGE_PATHS['captcha_exists'])
    
    def is_evp_finished(self) -> bool:
        return self.is_image_on_screen(IMAGE_PATHS['evp_terminado'])
    
    def get_evp_location(self):
        return pyautogui.locateCenterOnScreen(IMAGE_PATHS['evp_terminado'], confidence=0.97)