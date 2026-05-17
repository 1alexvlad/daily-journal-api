from sqlalchemy import select, delete, update
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import selectinload
from typing import List

from app.database import async_session_maker
from app.notes.models import Note
from app.notes.schemas import SNote
from app.users.models import User, Role
from app.service.base import BaseService

class NoteServices(BaseService):
    model = Note


async def change_note(note_id: int, current_user: User, title: str | None = None, content: str | None = None, is_done: bool | None = None) -> Note | None:
    async with async_session_maker() as session:
        try:
            result = await session.execute(
                select(Note)
                .where(Note.id == note_id)
                .options(selectinload(Note.user))
            )

            note = result.scalar_one_or_none()

            if not note:
                return None
            
            if current_user.role == Role.ADMIN:
                pass 
            elif current_user.role == Role.STAFF:
                if note.user.role == Role.ADMIN:
                    return None
            else:
                if note.user_id != current_user.id:
                    return None
                
            update_data = {}
            if title is not None:
                update_data['title'] = title
            if content is not None:
                update_data['content'] = content
            if is_done is not None:
                update_data['is_done'] = is_done

            if update_data:
                await session.execute(
                    update(Note)
                    .where(Note.id == note_id)
                    .values(update_data)
                )
                await session.commit()
                await session.refresh(note)

            return note
        except SQLAlchemyError as e:
            await session.rollback()
            raise e



async def delete_note(note_id: int, current_user: User) -> bool:
    async with async_session_maker() as session:
        try:
            result = await session.execute(
                select(Note)
                .where(Note.id == note_id)
                .options(selectinload(Note.user))
            )
            note = result.scalar_one_or_none()

            if not note:
                return False 

            if current_user.role == Role.ADMIN:
                pass 
            elif current_user.role == Role.STAFF:
                if note.user.role == Role.ADMIN:
                    return False 
            else:
                if note.user_id != current_user.id:
                    return False 
                
            result = await session.execute(
                delete(Note).where(Note.id == note_id)
            )
            await session.commit()

            return result.rowcount > 0
        except SQLAlchemyError as e:
            await session.rollback()
            raise e

        

async def update_note_is_done(note_id: int, is_done: bool, current_user: User) -> bool:
    async with async_session_maker() as session:
        try:
            result = await session.execute(
                select(Note)
                .where(Note.id == note_id)
                .options(selectinload(Note.user))
            )
            note = result.scalar_one_or_none()

            if not note:
                return None  
            if current_user.role == Role.ADMIN:
                pass 
            elif current_user.role == Role.STAFF:
                if note.user.role == Role.ADMIN:
                    return None 
            else: 
                if note.user_id != current_user.id:
                    return None  
                
            await session.execute(
                update(Note)
                .where(Note.id == note_id)
                .values(is_done=is_done)
            )
            await session.commit()
            await session.refresh(note)

            return note
        except SQLAlchemyError as e:
            await session.rollback()
            raise e

async def find_by_id_with_access_check(task_id: int, current_user: User) -> Note | None:
    async with async_session_maker() as session:
        if current_user.role == Role.ADMIN:
            result = await session.execute(
                select(Note).where(Note.id == task_id)
            )
        elif current_user.role == Role.STAFF:
            result = await session.execute(
                select(Note).join(User).where(Note.id == task_id, User.role != Role.ADMIN)
            )
        else:
            result = await session.execute(
                select(Note).where(Note.id == task_id, Note.user_id == current_user.id)
            )

        return result.scalar_one_or_none()
