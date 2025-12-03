from argon2 import PasswordHasher
import uuid

ph = PasswordHasher()

def hash_password(password: str):
    return ph.hash(password)

def verify_password(hash, password):
    return ph.verify(hash, password)

def generate_token():
    return str(uuid.uuid4())

def send_email(to_email: str, content: str):
    print(f"Sending email to {to_email}:\n{content}")
