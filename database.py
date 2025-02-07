from pymongo import MongoClient
from datetime import datetime
import requests
from datetime import datetime
import requests
from dateutil import parser
from statistics import median
import pytz

class Database:
    def __init__(self):
        self.client = MongoClient("mongodb+srv://administrador:administrador@cluster0.8vjnvh9.mongodb.net/?retryWrites=true&w=majority")
        self.db = self.client.DigimonSuperRumble
    
    def get_current_date_from_internet(self):
        time_servers = [
            "http://worldclockapi.com/api/json/utc/now"
        ]
        
        times = []
        
        for server in time_servers:
            try:
                response = requests.get(server, timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    
                    if server.endswith("Sao_Paulo"):
                        # WorldTimeAPI and TimeAPI.io already provide time in São Paulo timezone
                        time = parser.parse(data['datetime'])
                    else:
                        # WorldClockAPI provides UTC time, so we need to convert it
                        utc_time = parser.parse(data['currentDateTime'])
                        sao_paulo_tz = pytz.timezone('America/Sao_Paulo')
                        time = utc_time.replace(tzinfo=pytz.UTC).astimezone(sao_paulo_tz)
                    
                    times.append(time)
            except Exception as e:
                print(f"Error fetching time from {server}: {str(e)}")
        
        if not times:
            raise Exception("Failed to fetch time from all servers")
        
        # Use the median time to avoid potential outliers
        median_time = median(times)
        return median_time.replace(tzinfo=None)
    
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
        expiration_date = datetime.strptime(key_info["data_expiracao"], "%Y-%m-%d").date()
        current_date = self.get_current_date_from_internet().date()
        
        if current_date > expiration_date:
            return False, "Chave expirada"
        
        return True, None 
    
    def record_action(self, username, acao):
        current_time = self.get_current_date_from_internet()
        action_record = {
            "username": username,
            "acao": acao,
            "timestamp": current_time
        }
        self.db.historico.insert_one(action_record)
        print(f"Ação '{acao}' registrada para o usuário {username} em {current_time}")
    

        
    def close(self):
        self.client.close()

    def get_license_expiration(self, username):
        user = self.db.cadastrados.find_one({"usuario": username})
        if not user:
            return None
        
        key = user.get("chave")
        key_info = self.db.chaves.find_one({"chave": key})
        if not key_info:
            return None
        
        return datetime.strptime(key_info["data_expiracao"], "%Y-%m-%d").date()