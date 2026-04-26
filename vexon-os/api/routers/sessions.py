from typing import Optional

from fastapi import APIRouter, Body, Depends
from pydantic import BaseModel

from auth.local import verify_token
from db.database import get_db
from services.session_service import create_user_session, list_user_sessions, close_user_session

router = APIRouter(prefix="/sessions", tags=["sessions"])


class SessionCreateRequest(BaseModel):
    title: Optional[str] = None
    session_id: Optional[str] = None


@router.get("")
async def get_sessions(
    user: dict = Depends(verify_token),
    db=Depends(get_db),
):
    return list_user_sessions(db=db, user=user)


@router.post("")
async def create_session(
    payload: Optional[SessionCreateRequest] = Body(default=None),
    user: dict = Depends(verify_token),
    db=Depends(get_db),
):
    return create_user_session(
        db=db,
        user=user,
        title=payload.title if payload else None,
        session_id=payload.session_id if payload else None,
    )


@router.delete("/{session_id}")
async def close_session(
    session_id: str,
    user: dict = Depends(verify_token),
    db=Depends(get_db),
):
    return await close_user_session(db=db, user=user, session_id=session_id)
