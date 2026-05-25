from typing import Optional

from pydantic import BaseModel, EmailStr, ConfigDict, field_validator
from datetime import datetime  


from app.models import Role

class UserCreate(BaseModel):
    email: EmailStr
    hashed_password: str 
    full_name: str

class UserRead(BaseModel):
    id: int
    email: EmailStr
    full_name: str
    role: Role
    is_active: bool

    model_config = ConfigDict(from_attributes=True)
        

class UserLogin(BaseModel):
    email: EmailStr
    hashed_password: str


class SUserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)



class SNote(BaseModel):
    id: int
    title: str 
    content: str 
    created_at: datetime  
    updated_at: datetime  
    is_done: bool
    user_id: int

    @field_validator('id')
    def check_id_positive(cls, value: int) -> int:
        if value <= 0:
            raise ValueError("ID не может быть отрицательным")
        return value

    model_config = ConfigDict(from_attributes=True)