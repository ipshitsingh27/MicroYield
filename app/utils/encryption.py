from cryptography.fernet import Fernet
import os
from dotenv import load_dotenv

load_dotenv()

ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY")

fernet = Fernet(ENCRYPTION_KEY)

def encrypt_secret(secret: str):
    return fernet.encrypt(secret.encode()).decode()

def decrypt_secret(encrypted_secret: str):
    return fernet.decrypt(encrypted_secret.encode()).decode()
