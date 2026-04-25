from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, JSON, String
from sqlalchemy.orm import relationship
import datetime
import uuid

from .database import Base


class User(Base):
    __tablename__ = "users"

    user_id = Column(String, primary_key=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=True)
    display_name = Column(String, nullable=True)
    avatar_url = Column(String, nullable=True)
    plan = Column(String, default="free")
    api_keys = Column(JSON, nullable=True)
    preferences = Column(JSON, nullable=True)
    memory_quota = Column(Integer, default=100)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    last_active = Column(DateTime, default=datetime.datetime.utcnow)

    sessions = relationship("Session", back_populates="user")
    agent_logs = relationship("AgentLog", back_populates="user")

class Session(Base):
    __tablename__ = "sessions"

    session_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.user_id"), nullable=False, index=True)
    title = Column(String, nullable=True)
    status = Column(String, default="active")
    summary = Column(String, nullable=True)
    agent_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    last_active = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("User", back_populates="sessions")
    agent_logs = relationship("AgentLog", back_populates="session")

class AgentLog(Base):
    __tablename__ = "agent_logs"

    log_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    agent_id = Column(String, nullable=False)
    session_id = Column(String, ForeignKey("sessions.session_id"), nullable=False, index=True)
    user_id = Column(String, ForeignKey("users.user_id"), nullable=False, index=True)
    goal = Column(String, nullable=True)
    status = Column(String, nullable=True)
    provider_used = Column(String, nullable=True)
    tokens_used = Column(Integer, default=0)
    duration_ms = Column(Integer, default=0)
    trace = Column(JSON, nullable=True)
    output = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("User", back_populates="agent_logs")
    session = relationship("Session", back_populates="agent_logs")

class ToolCall(Base):
    __tablename__ = "tool_calls"

    call_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    agent_id = Column(String, nullable=False)
    tool_name = Column(String, nullable=False)
    input = Column(JSON, nullable=True)
    output = Column(JSON, nullable=True)
    duration_ms = Column(Integer, default=0)
    success = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
