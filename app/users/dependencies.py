from datetime import datetime, timezone  
from fastapi import Depends, Request


from app.services import UsersServices, UserSessionServices
from app.exceptions import (
    AccountNotAuthorizedException, InvalidOrExpiredSessionException, 
    SessionExpiredException, AccountDeletedException, StaffOrAdminException)
from app.models import User, Role

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


async def get_staff_or_admin(user: User = Depends(get_current_user)):
    if user.role != Role.ADMIN and user.role != Role.STAFF:
        raise StaffOrAdminException 
    return user