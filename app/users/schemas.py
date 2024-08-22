from typing import Optional

from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str
    first_name: str
    last_name: str


class UserPublic(BaseModel):
    id: str
    username: str
    created_at: str
    updated_at: str


class User(UserPublic):
    email: EmailStr
    first_name: str
    last_name: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    token: str
    user: User


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
