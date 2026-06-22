from sqlalchemy import select

from app.core.database import async_session_maker
from app.models.users import User
from app.services.base import BaseService


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
