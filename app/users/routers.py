from datetime import datetime, timedelta
import uuid

from fastapi import APIRouter, HTTPException, Request, Response, status, Depends
from fastapi.responses import JSONResponse


from app.users.schemas import UserCreate, UserLogin, UserRead
from app.users.services import UsersServices, UserSessionServices
from app.users.auth import get_password_hash
from app.users.dependencies import get_current_user
from app.users.models import User
from app.users.auth import verify_password


router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/register")
async def register_user(user_data: UserCreate, request: Request):
    existing_user = await UsersServices.find_one_or_none(email=user_data.email)
    if existing_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='Пользователь с таким email уже существует')
    
    hashed_password = get_password_hash(user_data.hashed_password)
    user = await UsersServices.add(
        email = user_data.email,
        hashed_password = hashed_password,
        full_name = user_data.full_name,    
    )
    
    return user


@router.post("/login")
async def login_user(request: Request, user_data: UserLogin):
    user = await UsersServices.find_one_or_none(email=user_data.email)
    
    if not user or not verify_password(user_data.hashed_password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Неверные учётные данные")
    
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Аккаунт заблокирован")

    new_session_id = str(uuid.uuid4())
    expires_at = datetime.now() + timedelta(days=30)

    await UserSessionServices.create_session(
        session_id=new_session_id,
        user_id=user.id,
        expires_at=expires_at,
    )
    
    response = JSONResponse(content={"message": "Успешный вход", "user_id": user.id})
    response.set_cookie(
        key="session_id",
        value=new_session_id,
        httponly=True,
        secure=False, 
        samesite="lax",
        max_age=30 * 24 * 3600
    )
    
    return response


@router.post('/logout')
async def logout_user(request: Request, response: Response):
    session_id = request.cookies.get("session_id")
    
    if session_id:
        await UserSessionServices.delete_session(session_id)
    
    response.delete_cookie("session_id")
    return {"message": "Вы вышли из системы"}


@router.get('/me')
async def get_users(user: User = Depends(get_current_user)) -> UserRead:
    return UserRead.model_validate(user)

