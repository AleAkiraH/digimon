import json
from cryptography.fernet import Fernet

# Use a chave gerada anteriormente
key = b'-bXN0fDV-N_GSf8yxkR2DDhF1wiTJ2xv9IX4fg1wIuc='
cipher_suite = Fernet(key)

# Informações sensíveis
BOT_TOKEN = "7787489780:AAHsHx__UcKkfpAkXUPDES2TahBtUFzJSx8"
CHAT_ID = "975349421"
MONGO_URI = "mongodb+srv://administrador:administrador@cluster0.8vjnvh9.mongodb.net/?retryWrites=true&w=majority"

def encrypt_data(data):
    return cipher_suite.encrypt(data.encode()).decode()

def lambda_handler(event, context):
    encrypted_bot_token = encrypt_data(BOT_TOKEN)
    encrypted_chat_id = encrypt_data(CHAT_ID)
    encrypted_mongo_uri = encrypt_data(MONGO_URI)

    return {
        'statusCode': 200,
        'body': json.dumps({
            'encrypted_bot_token': encrypted_bot_token,
            'encrypted_chat_id': encrypted_chat_id,
            'encrypted_mongo_uri': encrypted_mongo_uri
        })
    }