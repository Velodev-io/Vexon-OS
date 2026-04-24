from sqlalchemy import Column, String, Integer, DateTime, Boolean, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
import datetime

from .database import Base

class User(Base):
    __tablename__ = "users"

    user_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
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

    session_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=False)
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

    log_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    agent_id = Column(String, nullable=False)
    session_id = Column(UUID(as_uuid=True), ForeignKey("sessions.session_id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=False)
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

    call_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    agent_id = Column(String, nullable=False)
    tool_name = Column(String, nullable=False)
    input = Column(JSON, nullable=True)
    output = Column(JSON, nullable=True)
    duration_ms = Column(Integer, default=0)
    success = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
