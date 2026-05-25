from sqlalchemy import desc, select, delete, update
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import selectinload

from app.service.base import BaseService
from app.database import async_session_maker
from app.models import User, Role, Note, UserSession



class UsersServices(BaseService):
    model = User


    @classmethod
    async def update(cls, user_id: int, **data) -> User | None:
        async with async_session_maker() as session:
            query = select(cls.model).filter_by(id=user_id)
            result = await session.execute(query)
            user = result.scalar_one_or_none()
        
            if not user:
                return None
            
            for key, value in data.items():
                if value is not None:
                    setattr(user, key, value)
        
            await session.commit()
            await session.refresh(user)
            
            return user




class UserSessionServices(BaseService):
    model = UserSession

    @classmethod
    async def create_session(cls, session_id: str, user_id: int, expires_at, limit: int = 3):
        async with async_session_maker() as session:
            query = (
                select(cls.model.id)
                .where(cls.model.user_id == user_id)
                .order_by(desc(cls.model.created_at))
            )
            result = await session.execute(query)
            session_ids = result.scalars().all()
            
            
            if len(session_ids) >= limit:
                keep_count = limit - 1
                ids_to_delete = session_ids[keep_count:]
                
                delete_query = delete(cls.model).where(cls.model.id.in_(ids_to_delete))
                delete_result = await session.execute(delete_query)
            
            new_session = cls.model(
                session_id=session_id,
                user_id=user_id,
                expires_at=expires_at
            )
            session.add(new_session)
            
            await session.commit()
            
            
            return new_session

             
    @classmethod
    async def delete_session(cls, session_id: str):
        async with async_session_maker() as session:
            query = delete(cls.model).where(cls.model.session_id == session_id)
            await session.execute(query)
            await session.commit()
    


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



async def delete_note(note_id: int, current_user: User):
    async with async_session_maker() as session:
        try:
            if current_user.role == Role.ADMIN:
                result = await session.execute(
                    delete(Note).where(Note.id == note_id)
                )
            else:
                result = await session.execute(
                    delete(Note).where(
                        Note.id == note_id,
                        Note.user_id == current_user.id
                    )
                )
            
            await session.commit()
            return result.rowcount > 0
            
        except SQLAlchemyError:
            await session.rollback()
            raise

        

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
