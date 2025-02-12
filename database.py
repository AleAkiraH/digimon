from secure_config import SECURE_CONFIG
from pymongo import MongoClient
from datetime import datetime
import requests
from dateutil import parser
from statistics import median
import pytz
from bson import ObjectId
import uuid

class Database:
    def __init__(self):
        self.client = MongoClient(SECURE_CONFIG['MONGO_URI'])
        self.db = self.client.DigimonSuperRumble
    
    def validate_version(self):
        """Validates if the current app version matches the required version"""
        try:
            version_doc = self.db.versao.find_one({})
            if not version_doc:
                return False, "Não foi possível verificar a versão do aplicativo"
            
            required_version = version_doc.get("versao")
            if required_version != "1.0":
                return False, f"Versão incompatível. Por favor, atualize para a versão {required_version}"
            
            return True, None
        except Exception as e:
            return False, f"Erro ao verificar versão: {str(e)}"

    def get_current_date_from_internet(self):
        # Lista de servidores de tempo para tentar
        time_servers = [
            "http://worldclockapi.com/api/json/utc/nowx",
            "https://timeapi.io/api/time/current/zone?timeZone=America%2FSao_Paulox"
        ]
        
        times = []
        
        for server in time_servers:
            try:
                response = requests.get(server, timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    
                    if "timeapi.io" in server:
                        # Parse TimeAPI.io response
                        time = datetime(
                            data['year'], data['month'], data['day'],
                            data['hour'], data['minute'], data['seconds']
                        )
                    elif server.endswith("Sao_Paulo"):
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
                continue
        
        if not times:
            # Se todas as APIs falharem, tenta usar o histórico do usuário
            print("Failed to fetch time from all servers, checking user history...")
            return None
        
        # Use the median time to avoid potential outliers
        median_time = median(times)
        return median_time.replace(tzinfo=None)
    
    def get_last_login_time(self, username):
        """Recupera o último login do usuário do histórico"""
        last_login = self.db.historico.find_one(
            {"username": username, "acao": "login"},
            sort=[("timestamp", -1)]
        )
        return last_login['timestamp'] if last_login else None
    
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
        
        # Tenta obter a data atual da internet
        current_date = self.get_current_date_from_internet()
        
        # Se falhar em obter a data da internet, verifica o histórico
        if current_date is None:
            last_login_time = self.get_last_login_time(username)
            if last_login_time:
                current_date = datetime.now()
                # Verifica se a data atual é menor que o último login
                if current_date < last_login_time:
                    return False, "Data do sistema está incorreta. Por favor, ajuste o relógio do seu computador."
            else:
                current_date = datetime.now()
        
        if current_date.date() > expiration_date:
            return False, "Chave expirada"
        
        return True, None
    
    def record_action(self, username, acao):
        current_time = self.get_current_date_from_internet()
        if current_time is None:
            current_time = datetime.now()
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
    
    def get_monitoring_status(self):
        """Fetch the monitoring status from the database"""
        try:
            # Use ObjectId para garantir que o _id está no formato correto
            monitor_doc = self.db.monitoramento.find_one({"_id": ObjectId("67a9227d15c87405944dfad2")})
            print(monitor_doc)
            if monitor_doc:
                return monitor_doc.get("ativado", False)
            return False
        except Exception as e:
            print(f"Erro ao buscar status de monitoramento: {str(e)}")
            return False

    def check_user_online(self, username):
        try:
            result = self.db.usuarios_online.find_one({"username": username})
            return result
        except Exception as e:
            print(f"Erro ao verificar usuário online: {e}")
            return None

    def add_user_online(self, username):
        try:
            session_id = str(uuid.uuid4())
            login_time = datetime.now()
            self.db.usuarios_online.insert_one({
                "username": username,
                "login_time": login_time,
                "session_id": session_id
            })
            return session_id
        except Exception as e:
            print(f"Erro ao adicionar usuário online: {e}")
            return None

    def remove_user_online(self, username):
        try:
            self.db.usuarios_online.delete_one({"username": username})
            return True
        except Exception as e:
            print(f"Erro ao remover usuário online: {e}")
            return False

    def validate_session(self, username, session_id):
        try:
            result = self.db.usuarios_online.find_one({
                "username": username,
                "session_id": session_id
            })
            return result is not None
        except Exception as e:
            print(f"Erro ao validar sessão: {e}")
            return False