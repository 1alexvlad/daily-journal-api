from fastapi import FastAPI
from sqladmin import Admin

from app.admin.auth import authentication_backend
from app.admin.views import NoteAdmin, UserAdmin
from app.core.database import engine
from app.routers.auth import auth_router
from app.routers.notes import note_router

app = FastAPI()
admin = Admin(app, engine, authentication_backend=authentication_backend)


admin.add_view(UserAdmin)
admin.add_view(NoteAdmin)

app.include_router(auth_router)
app.include_router(note_router)
