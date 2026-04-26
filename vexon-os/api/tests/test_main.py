import pytest
from starlette.websockets import WebSocketDisconnect


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_login_and_auth_me(client):
    login_response = client.post("/auth/login", json={"password": "phase1-password"})
    assert login_response.status_code == 200

    token = login_response.json()["token"]
    me_response = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me_response.status_code == 200
    assert me_response.json()["sub"] == "phase1-local-user"


def test_sessions_and_agent_run_require_auth(client):
    list_response = client.get("/sessions")
    create_response = client.post("/sessions", json={"title": "Unauthorized"})
    intent_response = client.post("/agent/run", json={"message": "hello"})

    assert list_response.status_code == 401
    assert create_response.status_code == 401
    assert intent_response.status_code == 401


def test_owned_session_lifecycle_and_inline_tasks(client, auth_headers):
    create_response = client.post("/sessions", json={"title": "Research Session"}, headers=auth_headers("user-a"))
    assert create_response.status_code == 200
    session_id = create_response.json()["session_id"]

    list_response = client.get("/sessions", headers=auth_headers("user-a"))
    assert list_response.status_code == 200
    assert [session["session_id"] for session in list_response.json()] == [session_id]

    available_tasks = client.post(
        "/agent/run",
        json={"message": "available tasks", "session_id": session_id},
        headers=auth_headers("user-a"),
    )
    assert available_tasks.status_code == 200
    payload = available_tasks.json()
    assert payload["status"] == "done"
    assert payload["session_id"] == session_id
    assert "You can ask Vexon OS" in payload["answer"]


def test_cross_session_access_is_rejected(client, auth_headers):
    create_response = client.post("/sessions", json={"title": "Private Session"}, headers=auth_headers("user-a"))
    session_id = create_response.json()["session_id"]

    agent_response = client.post(
        "/agent/run",
        json={"message": "what can you do", "session_id": session_id},
        headers=auth_headers("user-b"),
    )
    close_response = client.delete(f"/sessions/{session_id}", headers=auth_headers("user-b"))

    assert agent_response.status_code == 403
    assert close_response.status_code == 404


def test_websocket_requires_owned_session(client, auth_headers):
    create_response = client.post("/sessions", json={"title": "Socket Session"}, headers=auth_headers("user-a"))
    session_id = create_response.json()["session_id"]

    with pytest.raises(WebSocketDisconnect) as missing_token:
        with client.websocket_connect(f"/ws/{session_id}"):
            pass
    assert missing_token.value.code == 4401

    foreign_token = auth_headers("user-b")["Authorization"].split(" ", 1)[1]
    with pytest.raises(WebSocketDisconnect) as foreign_user:
        with client.websocket_connect(f"/ws/{session_id}?token={foreign_token}"):
            pass
    assert foreign_user.value.code == 4404


def test_close_session_sets_summary(client, auth_headers, monkeypatch):
    import memory.longterm as longterm

    async def fake_summary(user_id: str, session_id: str, llm_call=None):
        return f"Summary for {session_id}"

    monkeypatch.setattr(longterm, "summarize_session_async", fake_summary)

    create_response = client.post("/sessions", json={"title": "Close Me"}, headers=auth_headers("user-a"))
    session_id = create_response.json()["session_id"]

    close_response = client.delete(f"/sessions/{session_id}", headers=auth_headers("user-a"))
    assert close_response.status_code == 200

    list_response = client.get("/sessions", headers=auth_headers("user-a"))
    session = list_response.json()[0]
    assert session["status"] == "closed"
    assert session["summary"] == f"Summary for {session_id}"
