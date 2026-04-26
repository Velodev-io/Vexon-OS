import os
from pathlib import Path

from alembic.config import Config
from alembic.runtime.migration import MigrationContext
from alembic.script import ScriptDirectory
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker, declarative_base

SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:pass@localhost:5432/vexon_os")
ALEMBIC_INI_PATH = Path(__file__).resolve().parents[1] / "alembic.ini"

engine_kwargs = {}
if SQLALCHEMY_DATABASE_URL.startswith("sqlite"):
    engine_kwargs["connect_args"] = {"check_same_thread": False}

engine = create_engine(SQLALCHEMY_DATABASE_URL, **engine_kwargs)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def _alembic_config() -> Config:
    config = Config(str(ALEMBIC_INI_PATH))
    config.set_main_option("sqlalchemy.url", SQLALCHEMY_DATABASE_URL)
    config.set_main_option("script_location", str(Path(__file__).resolve().parents[0] / "migrations"))
    return config


def _expected_revision() -> str:
    script = ScriptDirectory.from_config(_alembic_config())
    heads = script.get_heads()
    if len(heads) != 1:
        raise RuntimeError(f"Expected exactly one Alembic head revision, found {len(heads)}")
    return heads[0]


def _current_revision() -> str | None:
    with engine.connect() as connection:
        context = MigrationContext.configure(connection)
        return context.get_current_revision()


def init_db():
    inspector = inspect(engine)
    existing_tables = set(inspector.get_table_names())
    required_tables = {"users", "sessions", "agent_logs", "tool_calls"}
    missing_tables = required_tables - existing_tables

    if missing_tables:
        missing_list = ", ".join(sorted(missing_tables))
        raise RuntimeError(
            "Database schema is not up to date. "
            f"Missing tables: {missing_list}. "
            "Run `alembic upgrade head` before starting the API."
        )

    current_revision = _current_revision()
    expected_revision = _expected_revision()
    if current_revision != expected_revision:
        raise RuntimeError(
            "Database schema is not at the expected Alembic revision. "
            f"Current revision: {current_revision or 'none'}. "
            f"Expected revision: {expected_revision}. "
            "Run `alembic upgrade head` before starting the API."
        )

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
