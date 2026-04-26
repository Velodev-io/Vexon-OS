import uuid
from typing import Any, Dict, Optional

from fastapi import HTTPException
from sqlalchemy.orm import Session as DBSession

from db.services import get_or_create_session_record, sync_user_record
from intent.parser import parse_intent
from intent.router import route_intent


AVAILABLE_TASKS_RESPONSE = """You can ask Vexon OS to:

- Answer questions and explain concepts.
- Summarize or reason through notes from the current session.
- Search memory from previous sessions.
- Run available tools when a task needs them.
- Help plan, debug, or draft technical work.

For local testing, this path is using a fast direct response instead of spawning background agents."""


def _is_available_tasks_request(message: str) -> bool:
    normalized = message.strip().lower()
    return normalized in {
        "list available tasks",
        "list all available tasks",
        "available tasks",
        "what can you do",
        "what can vexon do",
    }


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
    try:
        session = get_or_create_session_record(
            db,
            user_id=user_id,
            session_id=session_id or "",
            title=session_title,
        )
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc

    if _is_available_tasks_request(message):
        agent_id = str(uuid.uuid4())
        return {
            "task_id": agent_id,
            "agent_id": agent_id,
            "answer": AVAILABLE_TASKS_RESPONSE,
            "intent": {
                "goal": "available tasks",
                "description": message,
                "parameters": {},
                "priority": "low",
                "requires_tools": False,
            },
            "status": "done",
            "session_id": session.session_id,
        }

    intent = await parse_intent(message)
    task_id = route_intent(intent, session.session_id, user_id)
    return {
        "task_id": task_id,
        "agent_id": task_id,
        "intent": intent,
        "status": "dispatched",
        "session_id": session.session_id,
    }
