import secrets
import hashlib
from pwdlib import PasswordHash
from datetime import datetime, timedelta, timezone


pwd_context = PasswordHash.recommended()


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def generate_reset_secret() -> str:
    return secrets.token_urlsafe(32)


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()

def verify_token(token: str, stored_hash: str) -> bool:
    return hash_token(token) == stored_hash

def get_reset_token_expiration() -> datetime:
    return datetime.now(timezone.utc) + timedelta(minutes=15)
