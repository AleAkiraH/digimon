import json
from dataclasses import dataclass, asdict
from typing import Dict

@dataclass
class Config:
    resolution: str = "800x600"
    telegram_interval: int = 15  # minutos
    bot_token: str = ""
    chat_id: str = ""
    battle_keys: Dict[str, str] = None
    digivolution_type: str = "mega"
    
    def __post_init__(self):
        if self.battle_keys is None:
            self.battle_keys = {
                'group1': '',
                'group2': '',
                'group3': ''
            }
    
    @classmethod
    def load(cls) -> 'Config':
        try:
            with open('config.json', 'r') as f:
                data = json.load(f)
                return cls(**data)
        except FileNotFoundError:
            return cls()
    
    def save(self):
        with open('config.json', 'w') as f:
            json.dump(asdict(self), f, indent=4)