from fastapi import FastAPI
from sqladmin import Admin

from app.notes.routers import router as router_notes
from app.users.routers import router as router_users
from app.database import engine
from app.admin.views import UserAdmin, NoteAdmin
from app.admin.auth import authentication_backend

app = FastAPI()
admin = Admin(app, engine, authentication_backend=authentication_backend)


admin.add_view(UserAdmin)
admin.add_view(NoteAdmin)

app.include_router(router_notes)
app.include_router(router_users)