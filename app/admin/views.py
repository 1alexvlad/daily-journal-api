from sqladmin import ModelView

from app.users.models import User
from app.notes.models import Note

class UserAdmin(ModelView, model=User):
    column_list = [User.id, User.email, User.full_name, User.role]
    column_details_exclude_list = [User.hashed_password]
    can_delete = False 
    name = 'Пользователь'
    name_plural = "Пользователи"
    icon = 'fa-solid fa-user'

class NoteAdmin(ModelView, model=Note):
    column_list = [c.name for c in Note.__table__.c] + [Note.user]
    name = 'Запись'
    name_plural = "Записи"
    icon = 'fa-solid fa-user'
