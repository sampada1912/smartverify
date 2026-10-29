from pydantic import BaseModel
from typing import Optional
from app.models.user import UserRole


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: UserRole
    username: str
    institution_id: Optional[str] = None
    full_name: str


class TokenData(BaseModel):
    username: Optional[str] = None
    role: Optional[UserRole] = None
    institution_id: Optional[str] = None


class LoginRequest(BaseModel):
    username: str
    password: str


class DemoLoginRequest(BaseModel):
    role: UserRole
    username: Optional[str] = None


class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    full_name: str
    role: UserRole
    institution_id: Optional[str] = None


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    full_name: str
    role: UserRole
    institution_id: Optional[str] = None
    is_active: bool

    class Config:
        from_attributes = True
