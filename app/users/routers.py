from fastapi import APIRouter, HTTPException, Response, status, Depends
from typing import List 

from app.users.schemas import UserCreate, UserLogin, UserRead
from app.users.services import UsersServices
from app.users.auth import get_password_hash, authenticated_user, create_access_token
from app.users.dependencies import get_current_user, get_current_admin_user
from app.users.models import User


router = APIRouter(prefix="/auth", tags=["authentication"])

@router.post("/register")
async def register_user(user_data: UserCreate):
    existing_user = await UsersServices.find_one_or_none(email=user_data.email)
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Пользователь с таким email уже существует')
    
    hashed_password = get_password_hash(user_data.hashed_password)
    await UsersServices.add(
        email = user_data.email,
        hashed_password = hashed_password,
        full_name = user_data.full_name,    
        role = user_data.role,
        is_active = user_data.is_active
    )
    return {"message": "Пользователь успешно зарегистрирован"}

@router.post("/login")
async def login_user(response: Response, user_data: UserLogin):
    user = await authenticated_user(user_data.email, user_data.hashed_password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    access_token = create_access_token({'sub': str(user.id), 'role': user.role.value})
    response.set_cookie('daily_access_token', access_token, httponly=True)
    return access_token

@router.post('/logout')
async def logout_user(response: Response):
    response.delete_cookie('daily_access_token')


@router.get('/me')
async def get_users(user: User = Depends(get_current_user)) -> UserRead:
    return UserRead.model_validate(user)


@router.get('/all')
async def all_users(user: User = Depends(get_current_admin_user)) -> list[UserRead]:
    return await UsersServices.find_all()