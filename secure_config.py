import base64
import requests

ENCRYPTION_KEY = "MySecretKey123"  # Deve ser a mesma chave usada na função Lambda
LAMBDA_API_URL = "https://7pi4qi6me6cyjkoe2rpv6w4dku0xwxxi.lambda-url.us-east-1.on.aws/"  # Substitua pela URL real da sua API Lambda

def decrypt(encrypted_text):
    decoded = base64.b64decode(encrypted_text).decode()
    decrypted = []
    for i, char in enumerate(decoded):
        key_char = ENCRYPTION_KEY[i % len(ENCRYPTION_KEY)]
        decrypted_char = chr((ord(char) - ord(key_char)) % 256)
        decrypted.append(decrypted_char)
    return ''.join(decrypted)

def get_decrypted_values():
    try:
        response = requests.get(LAMBDA_API_URL)
        response.raise_for_status()
        encrypted_data = response.json()
        
        return {
            'BOT_TOKEN': decrypt(encrypted_data['encrypted_bot_token']),
            'CHAT_ID': decrypt(encrypted_data['encrypted_chat_id']),
            'MONGO_URI': decrypt(encrypted_data['encrypted_mongo_uri'])
        }
    except Exception as e:
        print(f"Erro ao obter valores da API Lambda: {e}")
        return None

# Obtenha os valores descriptografados
SECURE_CONFIG = get_decrypted_values()

