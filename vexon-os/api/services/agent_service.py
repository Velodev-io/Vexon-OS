from typing import Any, Dict, Optional

from fastapi import HTTPException
from sqlalchemy.orm import Session as DBSession

from db.services import get_or_create_session_record, sync_user_record
from intent.parser import parse_intent
from intent.router import route_intent


async def dispatch_intent(
    db: DBSession,
    user: dict,
    message: str,
    session_id: Optional[str] = None,
    requested_user_id: Optional[str] = None,
) -> Dict[str, Any]:
    user_id = user["sub"]
    if requested_user_id and requested_user_id != user_id:
        raise HTTPException(status_code=403, detail="User id does not match the authenticated token")

    sync_user_record(db, user)
    session_title = message.strip()[:80] or "New session"
    session = get_or_create_session_record(
        db,
        user_id=user_id,
        session_id=session_id or "",
        title=session_title,
    )

    intent = await parse_intent(message)
    task_id = route_intent(intent, session.session_id, user_id)
    return {
        "task_id": task_id,
        "intent": intent,
        "status": "dispatched",
        "session_id": session.session_id,
    }
