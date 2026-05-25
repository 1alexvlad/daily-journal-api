from datetime import datetime, timedelta
from typing import List
import uuid

from fastapi import APIRouter, Request, Response, Depends, Body
from fastapi.responses import JSONResponse


from app.schemas import UserCreate, UserLogin, UserRead, SUserUpdate, SNote
from app.services import UsersServices, UserSessionServices, NoteServices, delete_note, update_note_is_done, change_note
from app.users.auth import get_password_hash
from app.users.dependencies import get_current_user, get_staff_or_admin
from app.models import User, Role
from app.users.auth import verify_password
from app.exceptions import *

auth_router = APIRouter(prefix="/auth", tags=["authentication"])
note_router = APIRouter(prefix='/entries', tags=['notes'])


@auth_router.post("/register")
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


@auth_router.post("/login")
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
        limit=3
    )
    
    response = JSONResponse(content={"message": "Успешный вход"})
    response.set_cookie(
        key="session_id",
        value=new_session_id,
        httponly=True,
        secure=False, 
        samesite="lax",
        max_age=30 * 24 * 3600
    )
    
    return response


@auth_router.post('/logout')
async def logout_user(request: Request, response: Response):
    session_id = request.cookies.get("session_id")
    
    if session_id:
        await UserSessionServices.delete_session(session_id)
    
    response.delete_cookie("session_id")
    return {"message": "Вы вышли из системы"}


@auth_router.get('/me')
async def get_users(user: User = Depends(get_current_user)) -> UserRead:
    return UserRead.model_validate(user)

@auth_router.get('/id/{user_id}')
async def get_user_by_id(user_id: int, staff_or_admin_user: User = Depends(get_staff_or_admin)) -> UserRead:
    user = await UsersServices.find_by_id(user_id)
    if not user:
        raise UserNotFoundException
    return user

@auth_router.get('/all')
async def get_all_users(staff_or_admin_user: User = Depends(get_staff_or_admin)) -> List[UserRead]:
    return await UsersServices.find_all()

@auth_router.patch('/update')
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


@auth_router.delete('')
async def delete_user(current_user: User = Depends(get_current_user)):
    user_id = current_user.id
    deleted = await UsersServices.delete(user_id)

    if not deleted:
        raise UserNotFoundException

    return {
        'message': f'Пользователь {current_user.email} успешно удалён',
        'user_id': user_id
    }



@note_router.get('/')
async def get_list_entries(current_user: User = Depends(get_current_user)) -> List[SNote]:
    try:
        notes = await NoteServices.find_all(current_user)
        if not notes:
            return []  

        return [SNote.model_validate(note) for note in notes]
    except Exception as e:
        raise ShowNotesException

@note_router.post('/')
async def create_entries(title: str, content: str, current_user: User = Depends(get_current_user)) -> SNote:
    entries = await NoteServices.add(title=title, content=content, user_id = current_user.id)
    if not entries:
        raise AddNotedException
    return SNote.model_validate(entries)


@note_router.put('/{id}')
async def change_entrie_by_id(
    id: int,
    title: str | None = None,
    content: str | None = None,
    is_done: bool | None = None,
    current_user: User = Depends(get_current_user)
) -> SNote:
    try:
        updated_note = await change_note(id, current_user, title, content, is_done)
        if not updated_note:
            raise NotesNotFoundOrEditingRightsException
        return SNote.model_validate(updated_note)
    except Exception as e:
        raise UpdateNoteException

@note_router.delete('/{id}')
async def delete_entrie_by_id(id: int, current_user: User = Depends(get_current_user)):
    try:
        note = await delete_note(id, current_user)
        if not note:
            raise NotesNotFoundOrEditingRightsException
        return {'message': 'Запись удалена'}

    except Exception as e:
        raise InternalServerException


@note_router.patch('/{id}')
async def change_entrie_by_id(id: int, is_done: bool = Body(..., embed=True), current_user: User = Depends(get_current_user)) -> SNote:
    try:
        updated_note  = await update_note_is_done(id, is_done, current_user)
        if not updated_note :
            raise NotesNotFoundOrEditingRightsException
        return SNote.model_validate(updated_note)

    except Exception as e:
        raise UpdateNoteException
