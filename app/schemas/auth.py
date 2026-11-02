"""Schémas Pydantic des comptes et de la connexion."""

from pydantic import BaseModel, ConfigDict, EmailStr
from datetime import datetime

from app.levels import Level


class UserRegister(BaseModel):
    """Données reçues pour créer un compte ; le rôle n'en fait pas partie, il est fixé par la route."""

    email: EmailStr
    password: str
    first_name: str
    last_name: str


class StudentCreate(UserRegister):
    """Création d'un élève : les champs d'un compte, plus son niveau."""

    level: Level


class PasswordReset(BaseModel):
    """Nouveau mot de passe choisi par le staff."""

    password: str


class UserLogin(BaseModel):
    """Identifiants reçus à la connexion."""

    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """Profil renvoyé par l'API ; il n'inclut jamais le hash du mot de passe."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    first_name: str
    last_name: str
    role: str
    is_active: bool
    created_at: datetime


class Token(BaseModel):
    """Réponse de la connexion : le jeton JWT et le profil de l'utilisateur."""

    access_token: str
    token_type: str
    user: UserResponse