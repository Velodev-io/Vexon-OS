from fastapi import APIRouter, Depends
from pydantic import BaseModel

from auth.local import verify_token
from services.auth_service import login_with_password

router = APIRouter(prefix="/auth", tags=["auth"])


class LoginRequest(BaseModel):
    password: str


@router.post("/login")
async def login(payload: LoginRequest):
    return login_with_password(payload.password)


@router.get("/me")
async def auth_me(user: dict = Depends(verify_token)):
    return user
