from fastapi import APIRouter, HTTPException, Response, status

from app.users.schemas import UserCreate, UserLogin
from app.users.services import UsersServices
from app.users.auth import get_password_hash, authenticated_user, create_access_token


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