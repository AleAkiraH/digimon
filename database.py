from pymongo import MongoClient
from datetime import datetime

class Database:
    def __init__(self):
        self.client = MongoClient("mongodb+srv://administrador:administrador@cluster0.8vjnvh9.mongodb.net/?retryWrites=true&w=majority")
        self.db = self.client.DigimonSuperRumble

    def validate_user(self, username, password):
        user = self.db.cadastrados.find_one({"usuario": username, "senha": password})
        if not user:
            return False, None
        
        # Get the key and validate it
        key = user.get("chave")
        key_info = self.db.chaves.find_one({"chave": key})
        
        if not key_info:
            return False, "Chave não encontrada"
            
        # Check expiration
        expiration_date = datetime.strptime(key_info["data_expiracao"], "%Y-%m-%d")
        if datetime.now() > expiration_date:
            return False, "Chave expirada"
            
        return True, None

    def close(self):
        self.client.close()