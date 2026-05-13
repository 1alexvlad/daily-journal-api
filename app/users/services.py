from app.service.base import BaseService
from app.users.models import User, UserSession
from app.database import async_session_maker

class UsersServices(BaseService):
    model = User


class UserSessionServices(BaseService):
    model = UserSession

    @classmethod
    async def create_session(cls, session_id: str, user_id: int, expires_at):
        return await cls.add(
            session_id=session_id,
            user_id=user_id,
            expires_at=expires_at,
        )
    
    @classmethod
    async def delete_session(cls, session_id: str):
        async with async_session_maker() as session:
            from sqlalchemy import delete
            query = delete(cls.model).where(cls.model.session_id == session_id)
            await session.execute(query)
            await session.commit()
    
    @classmethod
    async def delete_all_user_sessions(cls, user_id: int):
        async with async_session_maker() as session:
            from sqlalchemy import delete
            query = delete(cls.model).where(cls.model.user_id == user_id)
            await session.execute(query)
            await session.commit()