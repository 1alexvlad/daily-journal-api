from sqlalchemy import desc, select, delete

from app.service.base import BaseService
from app.users.models import User, UserSession
from app.database import async_session_maker

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
    