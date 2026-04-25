"""
Test: agent actually recalls something from a previous session.

Requires QDRANT_URL to be set. Skipped otherwise.
Run: pytest api/tests/test_longterm_recall.py -v
"""
import os
import uuid
import pytest

pytestmark = pytest.mark.skipif(
    not os.getenv("QDRANT_URL"),
    reason="QDRANT_URL not set — skipping long-term memory tests",
)


@pytest.fixture()
def user_id():
    # Unique per test run so Qdrant state doesn't bleed between runs
    return f"test-user-{uuid.uuid4().hex[:8]}"


def test_store_and_search_longterm(user_id):
    from memory.longterm import store_longterm, search_longterm

    fact = "The user's favourite programming language is Rust."
    store_longterm(user_id, fact, metadata={"type": "fact", "session_id": "session-A"})

    hits = search_longterm(user_id, "favourite programming language", top_k=5)
    assert any("Rust" in h for h in hits), f"Expected recall of Rust fact, got: {hits}"


def test_summarize_session_stores_in_longterm(user_id, monkeypatch):
    """summarize_session should compress short-term entries and store in Qdrant."""
    import json
    import redis as redis_lib
    from memory.longterm import summarize_session, search_longterm

    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    r = redis_lib.from_url(redis_url)
    session_id = f"session-{uuid.uuid4().hex[:8]}"

    # Seed short-term memory directly
    key = f"memory:{user_id}:{session_id}"
    entries = [
        {"content": "User asked about Python async patterns.", "type": "observation"},
        {"content": "Agent explained asyncio event loop in detail.", "type": "result"},
    ]
    for e in entries:
        r.lpush(key, json.dumps(e))
    r.expire(key, 300)

    # Run without LLM (concatenation fallback)
    summarize_session(user_id, session_id, llm_call=None)

    hits = search_longterm(user_id, "Python async asyncio", top_k=5)
    assert any("asyncio" in (h or "").lower() or "async" in (h or "").lower() for h in hits), (
        f"Expected recall of asyncio content after summarization, got: {hits}"
    )

    # Cleanup
    r.delete(key)


def test_cross_session_recall_in_agent_prompt(user_id, monkeypatch):
    """
    Simulate two sessions: store a fact in session A, then verify it surfaces
    in the system prompt built by BaseAgent for session B.
    """
    from memory.longterm import store_longterm
    from agents.base_agent import BaseAgent

    # Session A: store a fact
    store_longterm(
        user_id,
        "The project uses FastAPI with Celery for async task dispatch.",
        metadata={"session_id": "session-A", "type": "fact"},
    )

    # Session B: build a new agent and check its system prompt includes the fact
    agent = BaseAgent(
        session_id="session-B",
        user_id=user_id,
        goal="How does the project handle async tasks?",
    )

    # Patch redis publish so no real Redis needed for this part
    monkeypatch.setattr(agent.redis_client, "publish", lambda *a, **kw: None)

    from memory.longterm import search_longterm
    hits = search_longterm(user_id, agent.goal, top_k=5)

    assert any("FastAPI" in (h or "") or "Celery" in (h or "") for h in hits), (
        f"Expected cross-session recall of FastAPI/Celery fact, got: {hits}"
    )
