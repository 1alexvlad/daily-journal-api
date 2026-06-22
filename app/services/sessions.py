from sqlalchemy import delete, desc, select

from app.core.database import async_session_maker
from app.models.sessions import UserSession
from app.services.base import BaseService


class UserSessionServices(BaseService):
    model = UserSession

    @classmethod
    async def create_session(cls, session_id: str, user_id: int, expires_at, limit: int = 3):
        async with async_session_maker() as session:
            query = select(cls.model.id).where(cls.model.user_id == user_id).order_by(desc(cls.model.created_at))
            result = await session.execute(query)
            session_ids = result.scalars().all()

            if len(session_ids) >= limit:
                keep_count = limit - 1
                ids_to_delete = session_ids[keep_count:]

                delete_query = delete(cls.model).where(cls.model.id.in_(ids_to_delete))
                await session.execute(delete_query)

            new_session = cls.model(session_id=session_id, user_id=user_id, expires_at=expires_at)
            session.add(new_session)

            await session.commit()

            return new_session

    @classmethod
    async def delete_session(cls, session_id: str):
        async with async_session_maker() as session:
            query = delete(cls.model).where(cls.model.session_id == session_id)
            await session.execute(query)
            await session.commit()
