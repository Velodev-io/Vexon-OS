from typing import Optional

from fastapi import APIRouter, Body, Depends
from pydantic import BaseModel

from auth.local import verify_token
from db.database import get_db
from services.session_service import create_user_session, list_user_sessions, close_user_session

# BYPASS AUTH - Commenting out verify_token for testing
router = APIRouter(prefix="/sessions", tags=["sessions"]) # dependencies=[Depends(verify_token)]


class SessionCreateRequest(BaseModel):
    title: Optional[str] = None
    session_id: Optional[str] = None


@router.get("")
async def get_sessions(
    # BYPASS AUTH
    # user: dict = Depends(verify_token),
    user: dict = None,
    db=Depends(get_db),
):
    if user is None:
        user = {"sub": "suryansh"}
    return list_user_sessions(db=db, user=user)


@router.post("")
async def create_session(
    payload: Optional[SessionCreateRequest] = Body(default=None),
    # BYPASS AUTH
    # user: dict = Depends(verify_token),
    user: dict = None,
    db=Depends(get_db),
):
    if user is None:
        user = {"sub": "suryansh"}
    return create_user_session(
        db=db,
        user=user,
        title=payload.title if payload else None,
        session_id=payload.session_id if payload else None,
    )


@router.delete("/{session_id}")
async def close_session(
    session_id: str,
    # BYPASS AUTH
    # user: dict = Depends(verify_token),
    user: dict = None,
    db=Depends(get_db),
):
    if user is None:
        user = {"sub": "suryansh"}
    return await close_user_session(db=db, user=user, session_id=session_id)
