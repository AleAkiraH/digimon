from datetime import datetime

class Battle:
    def __init__(self):
        self.count = 0
        self.start_time = datetime.now()
        self.last_battle_time = self.start_time
    
    def increment(self):
        self.count += 1
        self.last_battle_time = datetime.now()
    
    def get_battles_per_minute(self) -> float:
        elapsed_minutes = (datetime.now() - self.start_time).total_seconds() / 60
        return self.count / elapsed_minutes if elapsed_minutes > 0 else 0.0
    
    def reset(self):
        self.count = 0
        self.start_time = datetime.now()
        self.last_battle_time = self.start_time