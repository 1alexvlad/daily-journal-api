from pydantic import BaseModel, ConfigDict, EmailStr

from app.models.users import Role


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
    email: EmailStr | None = None
    full_name: str | None = None

    model_config = ConfigDict(from_attributes=True)
