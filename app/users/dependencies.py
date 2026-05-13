from datetime import datetime, timezone  
from fastapi import Request


from app.users.services import UsersServices, UserSessionServices
from app.exceptions import (
    AccountNotAuthorizedException, InvalidOrExpiredSessionException, 
    SessionExpiredException, AccountDeletedException)

async def get_current_user(request: Request):
    session_id = request.cookies.get('session_id')

    if not session_id:
        raise AccountNotAuthorizedException
    
    user_session = await UserSessionServices.find_one_or_none(session_id=session_id)

    if not user_session:
        raise InvalidOrExpiredSessionException

    if user_session.expires_at < datetime.now(timezone.utc):
        raise SessionExpiredException

    user = await UsersServices.find_by_id(user_session.user_id)
    
    if not user:
        raise AccountDeletedException

    return user