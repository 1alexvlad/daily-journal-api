from app.service.base import BaseService
from app.users.models import User


class UsersServices(BaseService):
    model = User