"""initial schema

Revision ID: 20260425_000001
Revises:
Create Date: 2026-04-25 00:00:01
"""

from alembic import op
import sqlalchemy as sa


revision = "20260425_000001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("user_id", sa.String(), nullable=False),
        sa.Column("email", sa.String(), nullable=False),
        sa.Column("password_hash", sa.String(), nullable=True),
        sa.Column("display_name", sa.String(), nullable=True),
        sa.Column("avatar_url", sa.String(), nullable=True),
        sa.Column("plan", sa.String(), nullable=True),
        sa.Column("api_keys", sa.JSON(), nullable=True),
        sa.Column("preferences", sa.JSON(), nullable=True),
        sa.Column("memory_quota", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("last_active", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("user_id"),
    )
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)

    op.create_table(
        "tool_calls",
        sa.Column("call_id", sa.String(), nullable=False),
        sa.Column("agent_id", sa.String(), nullable=False),
        sa.Column("tool_name", sa.String(), nullable=False),
        sa.Column("input", sa.JSON(), nullable=True),
        sa.Column("output", sa.JSON(), nullable=True),
        sa.Column("duration_ms", sa.Integer(), nullable=True),
        sa.Column("success", sa.Boolean(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("call_id"),
    )

    op.create_table(
        "sessions",
        sa.Column("session_id", sa.String(), nullable=False),
        sa.Column("user_id", sa.String(), nullable=False),
        sa.Column("title", sa.String(), nullable=True),
        sa.Column("status", sa.String(), nullable=True),
        sa.Column("summary", sa.String(), nullable=True),
        sa.Column("agent_count", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("last_active", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.user_id"]),
        sa.PrimaryKeyConstraint("session_id"),
    )
    op.create_index(op.f("ix_sessions_user_id"), "sessions", ["user_id"], unique=False)

    op.create_table(
        "agent_logs",
        sa.Column("log_id", sa.String(), nullable=False),
        sa.Column("agent_id", sa.String(), nullable=False),
        sa.Column("session_id", sa.String(), nullable=False),
        sa.Column("user_id", sa.String(), nullable=False),
        sa.Column("goal", sa.String(), nullable=True),
        sa.Column("status", sa.String(), nullable=True),
        sa.Column("provider_used", sa.String(), nullable=True),
        sa.Column("tokens_used", sa.Integer(), nullable=True),
        sa.Column("duration_ms", sa.Integer(), nullable=True),
        sa.Column("trace", sa.JSON(), nullable=True),
        sa.Column("output", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["session_id"], ["sessions.session_id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.user_id"]),
        sa.PrimaryKeyConstraint("log_id"),
    )
    op.create_index(op.f("ix_agent_logs_session_id"), "agent_logs", ["session_id"], unique=False)
    op.create_index(op.f("ix_agent_logs_user_id"), "agent_logs", ["user_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_agent_logs_user_id"), table_name="agent_logs")
    op.drop_index(op.f("ix_agent_logs_session_id"), table_name="agent_logs")
    op.drop_table("agent_logs")
    op.drop_index(op.f("ix_sessions_user_id"), table_name="sessions")
    op.drop_table("sessions")
    op.drop_table("tool_calls")
    op.drop_index(op.f("ix_users_email"), table_name="users")
    op.drop_table("users")
