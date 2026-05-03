from datetime import datetime, timezone
import os

from fastapi import HTTPException, status, Request, Depends
from jose import jwt
from jose.exceptions import JWTError, ExpiredSignatureError

from app.users.models import Role
from app.users.services import UsersServices
from app.notes.services import find_by_id_with_access_check
from app.users.models import User
from app.notes.models import Note

from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")


def get_token(request: Request):
    token = request.cookies.get('daily_access_token')
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Токен не был обнаружен')
    return token 


async def get_current_user(token: str = Depends(get_token)):
    try:
        payload = jwt.decode(
            token, SECRET_KEY, algorithms=ALGORITHM
        )
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Токен истёк"
        )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный токен"
        )
    
    expire: str = payload.get('exp')
    role: str = payload.get('role')

    if not expire or (int(expire) < datetime.now(timezone.utc).timestamp()):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)   
        
    user_id: str = payload.get('sub')
    role: str = payload.get('role')

    if not user_id or not role:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Неверные данные в токене')
    
    if role not in [r.value for r in Role]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Недостаточные права доступа")

    user = await UsersServices.find_by_id(int(user_id))
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    
    return user


def get_current_admin_or_staff_user(current_user: User = Depends(get_current_user)) -> bool:
    if current_user.role != Role.ADMIN and current_user.role != Role.STAFF:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Недостаточно прав')
    return current_user


async def get_task_or_403(task_id: int, current_user: User = Depends(get_current_user)) -> Note:
    task = await find_by_id_with_access_check(task_id, current_user)

    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Задача не найдена или у вас нет доступа к ней')

    return task
