import base64

ENCRYPTION_KEY = "MySecretKey123"  # Deve ser a mesma chave usada na função Lambda

def decrypt(encrypted_text):
    decoded = base64.b64decode(encrypted_text).decode()
    decrypted = []
    for i, char in enumerate(decoded):
        key_char = ENCRYPTION_KEY[i % len(ENCRYPTION_KEY)]
        decrypted_char = chr((ord(char) - ord(key_char)) % 256)
        decrypted.append(decrypted_char)
    return ''.join(decrypted)

# Função para obter e descriptografar os valores da API Lambda
def get_decrypted_values():
    # Aqui você deve fazer uma chamada para a API Lambda
    # Por exemplo, usando a biblioteca 'requests':
    # import requests
    # response = requests.get('URL_DA_SUA_API_LAMBDA')
    # data = response.json()

    # Para fins de demonstração, vamos supor que você já tem os valores criptografados:
    encrypted_data = {
        'encrypted_bot_token': 'SEU_TOKEN_CRIPTOGRAFADO',
        'encrypted_chat_id': 'SEU_CHAT_ID_CRIPTOGRAFADO',
        'encrypted_mongo_uri': 'SUA_URI_MONGO_CRIPTOGRAFADA'
    }

    decrypted_values = {
        'bot_token': decrypt(encrypted_data['encrypted_bot_token']),
        'chat_id': decrypt(encrypted_data['encrypted_chat_id']),
        'mongo_uri': decrypt(encrypted_data['encrypted_mongo_uri'])
    }

    return decrypted_values

# Uso:
values = get_decrypted_values()
print(f"Bot Token: {values['bot_token']}")
print(f"Chat ID: {values['chat_id']}")
print(f"Mongo URI: {values['mongo_uri']}")

