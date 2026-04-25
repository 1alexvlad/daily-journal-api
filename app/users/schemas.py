from pydantic import BaseModel, EmailStr
from enum import Enum
from typing import Optional


from app.users.models import Role

class UserCreate(BaseModel):
    email: EmailStr
    hashed_password: str  # На практике здесь будет plain_password, который затем хешируется
    full_name: str
    role: Role = Role.USER  # Дефолтное значение по умолчанию
    is_active: bool = True  # Дефолтное значение

    class Config:
        schema_extra = {
            "example": {
                "email": "user@example.com",
                "hashed_password": "mypassword123",  # В реальности — plain_password
                "full_name": "Иван Иванов",
                "role": "user",
                "is_active": True
            }
        }

class UserRead(BaseModel):
    id: int
    email: EmailStr
    full_name: str
    role: Role
    is_active: bool

    class Config:
        from_attributes = True  # Ранее orm_mode = True


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    role: Optional[Role] = None
    is_active: Optional[bool] = None
    new_password: Optional[str] = None  # Отдельное поле для нового пароля

    class Config:
        schema_extra = {
            "example": {
                "email": "updated@example.com",
                "full_name": "Иван Петров",
                "role": "staff",
                "is_active": False,
                "new_password": "newsecurepassword"
            }
        }
