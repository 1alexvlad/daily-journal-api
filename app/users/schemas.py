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
        

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    role: Optional[Role] = None
    is_active: Optional[bool] = None
    new_password: Optional[str] = None  


class UserLogin(BaseModel):
    email: EmailStr
    hashed_password: str