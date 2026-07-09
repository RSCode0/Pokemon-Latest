from cryptography.fernet import Fernet
import os
import json

SECRET_KEY = b'kxdjqgBFMqExL6OT4oT7CjhBG3hIPf2KzfrCiTdMytA='

def encrypt_save(data: str) -> bytes:
    f = Fernet(SECRET_KEY)
    return f.encrypt(data.encode())

def decrypt_save(data: bytes) -> str:
    f = Fernet(SECRET_KEY)
    return f.decrypt(data).decode()

