import pytest 

from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import NullPool, delete, text

from app.main import app as fastapi_app
from app.config import settings
from app.database import Base, async_session_maker
from app.users.models import User, Role
from app.users.services import UsersServices
from app.users.auth import get_password_hash



@pytest.fixture(scope='session', autouse=True)
async def prepare_database():
    assert settings.MODE == 'TEST'

    test_engine = create_async_engine(settings.TEST_DATABASE_URL, poolclass=NullPool)

    async with test_engine.begin() as conn:

        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    
    yield

@pytest.fixture(scope='function', autouse=True)
async def clean_database():
    yield
    async with async_session_maker() as session:
        
        await session.execute(text("TRUNCATE TABLE user_sessions CASCADE"))
        await session.execute(text("TRUNCATE TABLE notes CASCADE"))
        await session.execute(text("TRUNCATE TABLE users CASCADE"))
        await session.commit()


@pytest.fixture(scope='function')
async def session():
    async with async_session_maker() as session:
        yield session
        await session.rollback()


@pytest.fixture(scope='function')
async def ac():
    async with AsyncClient(transport=ASGITransport(app=fastapi_app), base_url='http://test') as ac:
        yield ac

        
@pytest.fixture(scope='function')
async def authenticated_ac():
    async with AsyncClient(transport=ASGITransport(app=fastapi_app), base_url="http://test") as ac:
        async with async_session_maker() as session:
            await session.execute(delete(User).where(User.email == "test@test.com"))
            await session.commit()
        
        register_response  = await ac.post('/auth/register', json={
            "email": "test@test.com",
            "hashed_password": "test", 
            "full_name": "Test User",
        })

        assert register_response .status_code == 200, f"Ошибка регистрации {register_response.text}"

        login_response = await ac.post('/auth/login', json={
            "email": "test@test.com",
            "hashed_password": "test", 
        })

        assert login_response.status_code == 200, f"Ошибка входа {login_response.text}"
        assert 'session_id' in ac.cookies, "'session_id' не был установлен после входа"
        yield ac 


@pytest.fixture(scope='function')
async def test_user():
   
    user = await UsersServices.add(
        email="user@example.com",
        hashed_password=get_password_hash("user_password"),
        full_name="User",
    )
    yield user

    
@pytest.fixture(scope='function')
async def test_staff():
    staff = await UsersServices.add(
        email="staff@example.com",
        hashed_password=get_password_hash("staff_password"),
        full_name="Staff",
        role=Role.STAFF
    )
    yield staff
    
@pytest.fixture(scope='function')
async def test_admin():
    admin = await UsersServices.add(
        email="admin@example.com",
        hashed_password=get_password_hash("admin_password"),
        full_name="Admin",
        role=Role.ADMIN
    )    
    yield admin
    