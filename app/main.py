from fastapi import FastAPI

from app.routers import router as router_notes
from app.users.routers import router as router_users

app = FastAPI()

app.include_router(router_notes)
app.include_router(router_users)