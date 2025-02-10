import json
import base64

# Chave de criptografia (mantenha isso seguro!)
ENCRYPTION_KEY = "MySecretKey123"

def encrypt(text):
    encrypted = []
    for i, char in enumerate(text):
        key_char = ENCRYPTION_KEY[i % len(ENCRYPTION_KEY)]
        encrypted_char = chr((ord(char) + ord(key_char)) % 256)
        encrypted.append(encrypted_char)
    return base64.b64encode(''.join(encrypted).encode()).decode()

def lambda_handler(event, context):
    BOT_TOKEN = "7787489780:AAHsHx__UcKkfpAkXUPDES2TahBtUFzJSx8"
    CHAT_ID = "975349421"
    MONGO_URI = "mongodb+srv://administrador:administrador@cluster0.8vjnvh9.mongodb.net/?retryWrites=true&w=majority"

    encrypted_bot_token = encrypt(BOT_TOKEN)
    encrypted_chat_id = encrypt(CHAT_ID)
    encrypted_mongo_uri = encrypt(MONGO_URI)

    return {
        'statusCode': 200,
        'body': json.dumps({
            'encrypted_bot_token': encrypted_bot_token,
            'encrypted_chat_id': encrypted_chat_id,
            'encrypted_mongo_uri': encrypted_mongo_uri
        })
    }