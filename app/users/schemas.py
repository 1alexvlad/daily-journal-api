from pydantic import BaseModel, EmailStr
from typing import Optional


from app.users.models import Role

class UserCreate(BaseModel):
    email: EmailStr
    hashed_password: str 
    full_name: str
    role: Role = Role.USER  
    is_active: bool = True 

class UserRead(BaseModel):
    id: int
    email: EmailStr
    full_name: str
    role: Role
    is_active: bool

    class Config:
        from_attributes = True  
        

class UserLogin(BaseModel):
    email: EmailStr
    hashed_password: str