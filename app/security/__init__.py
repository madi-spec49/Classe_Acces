"""Sécurité : hachage des mots de passe (bcrypt) et jetons JWT."""

from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta, timezone
import os

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY = os.getenv("JWT_SECRET_KEY", "change-me-in-production")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
EXPIRATION_MINUTES = int(os.getenv("JWT_EXPIRATION_MINUTES", "60"))


def hash_password(password: str) -> str:
    """Renvoie le hash bcrypt du mot de passe (le mot de passe en clair n'est jamais stocké)."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, password_hash: str) -> bool:
    """Vérifie un mot de passe en clair par rapport au hash enregistré."""
    return pwd_context.verify(plain_password, password_hash)


def create_access_token(user_id: int, email: str) -> str:
    """Crée un jeton JWT signé : `sub` (id de l'utilisateur), email et date d'expiration `exp`."""
    expire = datetime.now(timezone.utc) + timedelta(minutes=EXPIRATION_MINUTES)
    payload = {
        "sub": str(user_id),
        "email": email,
        "exp": expire
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token


def verify_token(token: str) -> dict:
    """Décode un jeton JWT ; renvoie son contenu, ou None s'il est invalide ou expiré."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None