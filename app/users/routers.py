from fastapi import APIRouter


router = APIRouter(prefix="/auth", tags=["authentication"])

@router.post("/register")
def register_user():
    pass

@router.post("/login")
def login_user():
    pass