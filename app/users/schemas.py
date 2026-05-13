from pydantic import BaseModel, EmailStr, ConfigDict


from app.users.models import Role

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