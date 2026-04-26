from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session as DBSession

from db.models import Session as SessionModel
from db.models import User


def sync_user_record(db: DBSession, claims: dict) -> User:
    user_id = claims["sub"]
    user = db.get(User, user_id)

    if user is None:
        user = User(
            user_id=user_id,
            email=claims.get("email") or f"{user_id}@local.vexon",
        )
        db.add(user)

    user.email = claims.get("email") or user.email
    user.display_name = claims.get("name") or user.display_name
    user.avatar_url = claims.get("picture") or user.avatar_url
    user.last_active = datetime.utcnow()
    db.commit()
    db.refresh(user)
    return user


def create_session_record(
    db: DBSession,
    user_id: str,
    session_id: Optional[str] = None,
    title: Optional[str] = None,
) -> SessionModel:
    session = SessionModel(
        session_id=session_id or str(uuid.uuid4()),
        user_id=user_id,
        title=title,
        status="active",
        created_at=datetime.utcnow(),
        last_active=datetime.utcnow(),
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


def get_or_create_session_record(
    db: DBSession,
    user_id: str,
    session_id: str,
    title: Optional[str] = None,
) -> SessionModel:
    if not session_id:
        return create_session_record(db, user_id=user_id, title=title)

    session = db.get(SessionModel, session_id)
    if session is None:
        return create_session_record(db, user_id=user_id, session_id=session_id, title=title)

    if session.user_id != user_id:
        raise PermissionError("Session does not belong to the authenticated user")

    if title and not session.title:
        session.title = title
    session.last_active = datetime.utcnow()
    db.commit()
    db.refresh(session)
    return session


def get_session_for_user(db: DBSession, user_id: str, session_id: str) -> SessionModel | None:
    session = db.get(SessionModel, session_id)
    if session is None or session.user_id != user_id:
        return None
    return session


def list_sessions_for_user(db: DBSession, user_id: str, limit: int = 50) -> list[SessionModel]:
    return (
        db.query(SessionModel)
        .filter(SessionModel.user_id == user_id)
        .order_by(SessionModel.last_active.desc())
        .limit(limit)
        .all()
    )
