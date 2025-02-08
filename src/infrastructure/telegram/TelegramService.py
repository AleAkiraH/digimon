from datetime import datetime
import pyautogui
from telegram import Bot
import os
from ...core.entities.Battle import Battle
from ...core.entities.Config import Config

class TelegramService:
    def __init__(self, config: Config):
        self.config = config
        self.last_message_time = datetime.now()
        self.bot = Bot(token=config.bot_token)
    
    def should_send_message(self) -> bool:
        time_diff = (datetime.now() - self.last_message_time).total_seconds() / 60
        return time_diff >= self.config.telegram_interval
    
    async def send_battle_update(self, battle: Battle):
        if not self.should_send_message():
            return
            
        try:
            # Captura a screenshot
            screenshot_path = f'screenshot_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png'
            screenshot = pyautogui.screenshot()
            screenshot.save(screenshot_path)
            
            # Prepara a mensagem
            elapsed_time = datetime.now() - battle.start_time
            hours = int(elapsed_time.total_seconds() // 3600)
            minutes = int((elapsed_time.total_seconds() % 3600) // 60)
            
            message = (
                f"🎮 Status da Automação:\n\n"
                f"⏱️ Tempo em execução: {hours:02d}:{minutes:02d}\n"
                f"⚔️ Batalhas realizadas: {battle.count}\n"
                f"⚡ Batalhas por minuto: {battle.get_battles_per_minute():.2f}"
            )
            
            # Envia a mensagem com a screenshot
            with open(screenshot_path, 'rb') as photo:
                await self.bot.send_photo(
                    chat_id=self.config.chat_id,
                    photo=photo,
                    caption=message
                )
            
            # Atualiza o tempo da última mensagem
            self.last_message_time = datetime.now()
            
            # Remove a screenshot temporária
            os.remove(screenshot_path)
            
        except Exception as e:
            print(f"Erro ao enviar mensagem para o Telegram: {str(e)}")