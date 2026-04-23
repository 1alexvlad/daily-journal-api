from sqlalchemy import func, select, insert, delete, update
from sqlalchemy.exc import SQLAlchemyError

from app.database import async_session_maker
from app.models import Note

async def find_all(**filter_by):
    async with async_session_maker() as session:
        query = select(Note).filter_by(**filter_by)
        result = await session.execute(query)
        return result.scalars().all()

async def add(**kwargs):
    try:
        async with async_session_maker() as session:
            note = Note(**kwargs)
            session.add(note)
            await session.commit()
            await session.refresh(note)
            return note
    except Exception as e:
        return None  
    
async def get_one_or_none(**filter_by):
    async with async_session_maker() as session:
        query = select(Note).filter_by(**filter_by)
        result = await session.execute(query)
        return result.scalar_one_or_none()

async def change_note(id: int, title: str, content: str):
    async with async_session_maker() as session:
        try:
            # Проверяем существование записи
            check_query = select(Note).where(Note.id == id)
            result = await session.execute(check_query)
            existing_note = result.scalar_one_or_none()

            if not existing_note:
                return None

            update_query = (
                update(Note)
                .where(Note.id == id)
                .values(title=title, content=content, updated_at=func.now())
            )
            result = await session.execute(update_query)
            await session.commit()

            select_query = select(Note).where(Note.id == id)
            result = await session.execute(select_query)
            updated_note = result.scalar_one_or_none()

            return updated_note
        except SQLAlchemyError as e:
            await session.rollback()
            raise e


async def delete_note(id: int) -> bool:
    async with async_session_maker() as session:
        try:
            result = await session.execute(delete(Note).where(Note.id==id))
            await session.commit()
            return result.rowcount > 0
        except SQLAlchemyError as e:
            await session.rollback()
            raise e
        

async def update_note_is_done(id: int, is_done: bool) -> bool:
    async with async_session_maker() as session:
        try:
            check_query = select(Note).where(Note.id == id)
            result = await session.execute(check_query)
            note = result.scalar_one_or_none()

            if not note:
                return False

            update_query = (
                update(Note)
                .where(Note.id == id)
                .values(is_done=is_done)
            )
            result = await session.execute(update_query)
            await session.commit()

            return result.rowcount > 0
        except SQLAlchemyError as e:
            await session.rollback()
            raise e