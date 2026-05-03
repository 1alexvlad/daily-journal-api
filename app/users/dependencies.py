from datetime import datetime, timezone
import os

from fastapi import HTTPException, status, Request, Depends
from jose import jwt
from jose.exceptions import JWTError, ExpiredSignatureError

from app.users.models import Role
from app.users.services import UsersServices
from app.users.models import User

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


async def get_current_admin_user(current_user: User = Depends(get_current_user)):
    if current_user.role.value != 'admin':
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    return current_user