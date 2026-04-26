import os
import sys
import tempfile
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient


API_ROOT = Path(__file__).resolve().parents[1]
TEST_DB_PATH = Path(tempfile.gettempdir()) / "vexon_phase1_test.db"

os.environ["DATABASE_URL"] = f"sqlite:///{TEST_DB_PATH}"
os.environ["JWT_SECRET"] = "phase1-test-secret"
os.environ["VEXON_PASSWORD"] = "phase1-password"
os.environ["VEXON_USER_ID"] = "phase1-local-user"
os.environ["VEXON_SKIP_DB_INIT"] = "1"

if str(API_ROOT) not in sys.path:
    sys.path.insert(0, str(API_ROOT))


@pytest.fixture(scope="session", autouse=True)
def migrated_test_db():
    if TEST_DB_PATH.exists():
        TEST_DB_PATH.unlink()

    config = Config(str(API_ROOT / "alembic.ini"))
    config.set_main_option("sqlalchemy.url", os.environ["DATABASE_URL"])
    config.set_main_option("script_location", str(API_ROOT / "db/migrations"))
    command.upgrade(config, "head")

    yield

    if TEST_DB_PATH.exists():
        TEST_DB_PATH.unlink()


@pytest.fixture(autouse=True)
def clean_db(migrated_test_db):
    from db.database import SessionLocal
    from db.models import AgentLog, Session, ToolCall, User

    db = SessionLocal()
    try:
        db.query(AgentLog).delete()
        db.query(ToolCall).delete()
        db.query(Session).delete()
        db.query(User).delete()
        db.commit()
    finally:
        db.close()

    yield


@pytest.fixture()
def client(migrated_test_db):
    from main import app

    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture()
def auth_headers():
    from auth.local import create_token

    def _headers(user_id: str = "phase1-local-user"):
        return {"Authorization": f"Bearer {create_token(user_id)}"}

    return _headers
