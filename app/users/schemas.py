from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str
    first_name: str
    last_name: str


class User(BaseModel):
    id: str
    email: EmailStr
    username: str
    first_name: str
    last_name: str
    created_at: str
    updated_at: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    token: str
    user: User
