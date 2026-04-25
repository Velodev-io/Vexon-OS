from typing import Optional

from fastapi import HTTPException
from sqlalchemy.orm import Session as DBSession

from db.services import create_session_record, list_sessions_for_user, sync_user_record
from db.models import Session as SessionModel


def list_user_sessions(db: DBSession, user: dict):
    sync_user_record(db, user)
    return list_sessions_for_user(db, user["sub"])


def create_user_session(
    db: DBSession,
    user: dict,
    title: Optional[str] = None,
    session_id: Optional[str] = None,
):
    sync_user_record(db, user)
    return create_session_record(
        db,
        user_id=user["sub"],
        session_id=session_id,
        title=title or "New session",
    )


async def close_user_session(db: DBSession, user: dict, session_id: str):
    from datetime import datetime
    from llm.sdk import call_with_fallback
    from memory.longterm import summarize_session

    user_id = user["sub"]
    session = db.get(SessionModel, session_id)
    if not session or session.user_id != user_id:
        raise HTTPException(status_code=404, detail="Session not found")

    async def _llm(messages):
        return await call_with_fallback(messages, stream=False)

    summarize_session(user_id, session_id, llm_call=_llm)

    session.status = "closed"
    session.last_active = datetime.utcnow()
    db.commit()
    return {"session_id": session_id, "status": "closed"}
