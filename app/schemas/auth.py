from pydantic import BaseModel, ConfigDict, EmailStr
from datetime import datetime

from app.levels import Level


class UserRegister(BaseModel):
    email: EmailStr
    password: str
    first_name: str
    last_name: str


class StudentCreate(UserRegister):
    level: Level


class PasswordReset(BaseModel):
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    first_name: str
    last_name: str
    role: str
    is_active: bool
    created_at: datetime


class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse