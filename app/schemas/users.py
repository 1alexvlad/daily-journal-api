from typing_extensions import Self

from pydantic import BaseModel, ConfigDict, EmailStr, model_validator

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

class SUserEmail(BaseModel):
    email: EmailStr

class SResetPassword(BaseModel):
    token: str 
    new_password: str 
    confirm_password: str 

    @model_validator(mode='after')
    def check_passwords_match(self) -> Self:
        if self.new_password != self.confirm_password:
            raise ValueError('Passwords do not match')
        return self
    