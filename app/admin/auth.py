from datetime import datetime, timedelta, timezone
import uuid

from fastapi.responses import JSONResponse
from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request

from app.services import UsersServices, UserSessionServices
from app.users.auth import verify_password
from app.models import Role


class AdminAuth(AuthenticationBackend):
    async def login(self, request: Request) -> bool:
        session_id = request.cookies.get('session_id')
        if session_id:
            user_session = await UserSessionServices.find_one_or_none(session_id=session_id)

            if user_session and user_session.expires_at > datetime.now():
                user = await UsersServices.find_by_id(user_session.user_id)
                if user and user.role == Role.ADMIN:
                    return True
                
        form = await request.form()
        email = form["username"]
        password = form["password"]

        if not email or not password:
            return False

        user = await UsersServices.find_one_or_none(email=email)
        if not user:
            return False
                
        if not verify_password(password, user.hashed_password):
            return False
        
        if user.role != Role.ADMIN:
            return False

        new_session_id = str(uuid.uuid4())
        expires_at = datetime.now() + timedelta(days=30)

        await UserSessionServices.create_session(
            session_id=new_session_id,
            user_id=user.id,
            expires_at=expires_at,
        )
        response = JSONResponse(content={"message": "Успешный вход", "user_id": user.id})
        response.set_cookie(
            key="session_id",
            value=new_session_id,
            httponly=True,
            secure=False, 
            samesite="lax",
            max_age=30 * 24 * 3600
        )
        
        return True

    async def logout(self, request: Request) -> bool:
        session_id = request.cookies.get('session_id')
        if session_id:
            await UserSessionServices.delete_session(session_id)
        return True


    async def authenticate(self, request: Request) -> bool:
        session_id = request.cookies.get('session_id')
        
        if not session_id:
            return False
        user_session = await UserSessionServices.find_one_or_none(session_id=session_id)
        
        if not user_session or user_session.expires_at < datetime.now(timezone.utc):
            return False    
        user = await UsersServices.find_by_id(user_session.user_id)
        
        if not user or user.role != Role.ADMIN:
            return False
        
        return True


authentication_backend = AdminAuth(secret_key="...")

