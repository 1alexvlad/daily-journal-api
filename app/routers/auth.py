import uuid
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, Request, Response
from fastapi.responses import JSONResponse

from app.core.exceptions import *
from app.models.users import Role, User
from app.schemas.users import SUserUpdate, UserCreate, UserLogin, UserRead, SUserEmail, SResetPassword
from app.services.users import UsersServices
from app.services.sessions import UserSessionServices
from app.core.auth import get_password_hash, verify_password, generate_reset_secret, hash_token, verify_token, get_reset_token_expiration
from app.core.dependencies import get_current_user, get_staff_or_admin
from tasks import send_reset_password_email 


auth_router = APIRouter(prefix="/auth", tags=["authentication"])


@auth_router.post("/register")
async def register_user(user_data: UserCreate, request: Request) -> UserRead:
    existing_user = await UsersServices.find_one_or_none(email=user_data.email)
    if existing_user:
        raise EmailAlreadyExistsException

    hashed = get_password_hash(user_data.hashed_password)
    user = await UsersServices.add(
        email=user_data.email,
        hashed_password=hashed,
        full_name=user_data.full_name,
    )

    return user


@auth_router.post("/login")
async def login_user(request: Request, user_data: UserLogin):
    user = await UsersServices.find_one_or_none(email=user_data.email)

    if not user or not verify_password(user_data.hashed_password, user.hashed_password):
        raise IncorrectEmailOrPasswordException

    if not user.is_active:
        raise AccountIsBlockedException

    new_session_id = str(uuid.uuid4())
    expires_at = datetime.now() + timedelta(days=30)

    await UserSessionServices.create_session(session_id=new_session_id, user_id=user.id, expires_at=expires_at, limit=3)

    response = JSONResponse(content={"message": "Успешный вход"})
    response.set_cookie(
        key="session_id", value=new_session_id, httponly=True, secure=False, samesite="lax", max_age=30 * 24 * 3600
    )

    return response


@auth_router.post("/logout")
async def logout_user(request: Request, response: Response):
    session_id = request.cookies.get("session_id")

    if session_id:
        await UserSessionServices.delete_session(session_id)

    response.delete_cookie("session_id")
    return {"message": "Вы вышли из системы"}


@auth_router.get("/me")
async def get_users(user: User = Depends(get_current_user)) -> UserRead:
    return UserRead.model_validate(user)


@auth_router.get("/id/{user_id}")
async def get_user_by_id(user_id: int, staff_or_admin_user: User = Depends(get_staff_or_admin)) -> UserRead:
    user = await UsersServices.find_by_id(user_id)
    if not user:
        raise UserNotFoundException
    return user


@auth_router.get("/all")
async def get_all_users(staff_or_admin_user: User = Depends(get_staff_or_admin)) -> list[UserRead]:
    return await UsersServices.find_all()


@auth_router.patch("/update")
async def update_user_by_id(
    user_id: int, user_data: SUserUpdate, staff_or_admin_user: User = Depends(get_staff_or_admin)
) -> UserRead:
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


@auth_router.delete("/delete")
async def delete_user(current_user: User = Depends(get_current_user)):
    user_id = current_user.id
    deleted = await UsersServices.delete(user_id)

    if not deleted:
        raise UserNotFoundException

    return {"message": f"Пользователь {current_user.email} успешно удалён", "user_id": user_id}


@auth_router.post('/forgot_password') 
async def forgot_password(email: SUserEmail) -> dict:
    user = await UsersServices.find_one_or_none(email=email.email)
    if not user: 
        raise UserNotFoundException

    token = generate_reset_secret()
    token_hash = hash_token(token)
    expires_at = get_reset_token_expiration()

    await UsersServices.update(
        user_id=user.id, 
        reset_token_hash=token_hash,
        reset_token_expires_at=expires_at
    )

    send_reset_password_email.delay(user.email, token)
    
    return {"message": "Ссылка для сброса пароля отправлена на email"}


@auth_router.post('/reset_password')
async def change_password(data: SResetPassword) -> dict:
    token_hash = hash_token(data.token)
    user = await UsersServices.find_one_or_none(reset_token_hash=token_hash)
    if not user: 
        raise UserNotFoundException

    current_time = datetime.now(timezone.utc)

    if user.reset_token_expires_at < current_time:
        raise TokenExpiredException

    new_hashed_password  = get_password_hash(data.new_password)

    await UsersServices.update(
        user_id=user.id,
        hashed_password=new_hashed_password,
        reset_token_hash=None,
        reset_token_expires_at=None
    ) 


    return {'message': 'Пароль успешно изменен'}
    