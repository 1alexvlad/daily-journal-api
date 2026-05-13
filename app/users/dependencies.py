from datetime import datetime, timezone  
from fastapi import HTTPException, status, Request


from app.users.services import UsersServices, UserSessionServices


async def get_current_user(request: Request):
    session_id = request.cookies.get('session_id')

    if not session_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Аккаунт не авторизован')
    
    user_session = await UserSessionServices.find_one_or_none(session_id=session_id)


    if not user_session:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Невалидный или просроченный сеанс")

    if user_session.expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Сессия истекла")

    user = await UsersServices.find_by_id(user_session.user_id)
    
    if not user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Учётная запись удалена")

    return user