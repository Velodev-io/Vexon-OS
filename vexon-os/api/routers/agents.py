from typing import Optional

from fastapi import APIRouter, Body, Depends, Request
from pydantic import BaseModel

from auth.local import verify_token
from core.rate_limit import limiter
from db.database import get_db
from services.agent_service import dispatch_intent

router = APIRouter(tags=["agents"])


class IntentRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    user_id: Optional[str] = None


@router.post("/intent")
@router.post("/agent/run")
@limiter.limit("10/minute")
async def handle_intent(
    request: Request,
    payload: IntentRequest = Body(...),
    user: dict = Depends(verify_token),
    db=Depends(get_db),
):
    return await dispatch_intent(
        db=db,
        user=user,
        message=payload.message,
        session_id=payload.session_id,
        requested_user_id=payload.user_id,
    )
