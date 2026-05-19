from datetime import datetime, timedelta
from typing import List
import uuid

from fastapi import APIRouter, Request, Response, Depends
from fastapi.responses import JSONResponse


from app.users.schemas import UserCreate, UserLogin, UserRead, SUserUpdate
from app.users.services import UsersServices, UserSessionServices
from app.users.auth import get_password_hash
from app.users.dependencies import get_current_user, get_staff_or_admin
from app.users.models import User, Role
from app.users.auth import verify_password
from app.exceptions import (
    EmailAlreadyExistsException, IncorrectEmailOrPasswordException, UserNotFoundException,
    AccountIsBlockedException, NoDataUpdateException, NoDataException, 
    StaffNoChangeAdminException, StaffNoChangeStaffException, EmailAlreadyExistsException)


router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/register")
async def register_user(user_data: UserCreate, request: Request):
    existing_user = await UsersServices.find_one_or_none(email=user_data.email)
    if existing_user:
        raise EmailAlreadyExistsException
    
    hashed = get_password_hash(user_data.hashed_password) 
    user = await UsersServices.add(
        email = user_data.email,
        hashed_password = hashed,
        full_name = user_data.full_name,    
    )
    
    return user


@router.post("/login")
async def login_user(request: Request, user_data: UserLogin):
    user = await UsersServices.find_one_or_none(email=user_data.email)
    
    if not user or not verify_password(user_data.hashed_password, user.hashed_password):
        raise IncorrectEmailOrPasswordException
    
    if not user.is_active:
        raise AccountIsBlockedException

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

@router.get('/id/{user_id}')
async def get_user_by_id(user_id: int, staff_or_admin_user: User = Depends(get_staff_or_admin)) -> UserRead:
    user = await UsersServices.find_by_id(user_id)
    if not user:
        raise UserNotFoundException
    return user

@router.get('/all')
async def get_all_users(staff_or_admin_user: User = Depends(get_staff_or_admin)) -> List[UserRead]:
    return await UsersServices.find_all()

@router.patch('/update')
async def update_user_by_id(user_id: int, user_data: SUserUpdate,  staff_or_admin_user: User = Depends(get_staff_or_admin)) -> UserRead:
    update_data = user_data.model_dump(exclude_unset=True)

    if not update_data:
        raise NoDataUpdateException
    
    target_user = await UsersServices.find_by_id(user_id)

    if not target_user:
        raise NoDataException
    
    if staff_or_admin_user.role == Role.STAFF and target_user.role == Role.ADMIN:
        raise StaffNoChangeAdminException
    
    if staff_or_admin_user.role == Role.STAFF and target_user.role == Role.STAFF:
        raise StaffNoChangeStaffException
    
    if "email" in update_data:
        existing_user = await UsersServices.find_one_or_none(email=update_data["email"])
        if existing_user and existing_user.id != user_id:
            raise EmailAlreadyExistsException
    
    updated_user = await UsersServices.update(user_id, **update_data)
    
    return UserRead.model_validate(updated_user)


@router.delete('')
async def delete_user(current_user: User = Depends(get_current_user)):
    user_id = current_user.id
    deleted = await UsersServices.delete(user_id)

    if not deleted:
        raise UserNotFoundException

    return {
        'message': f'Пользователь {current_user.email} успешно удалён',
        'user_id': user_id
    }
