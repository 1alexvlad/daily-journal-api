from fastapi import FastAPI
from sqladmin import Admin

from app.routers import auth_router, note_router
from app.database import engine
from app.admin.views import UserAdmin, NoteAdmin
from app.admin.auth import authentication_backend

app = FastAPI()
admin = Admin(app, engine, authentication_backend=authentication_backend)


admin.add_view(UserAdmin)
admin.add_view(NoteAdmin)

app.include_router(auth_router)
app.include_router(note_router)