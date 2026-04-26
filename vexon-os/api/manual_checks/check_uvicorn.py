import requests

try:
    res = requests.post("http://localhost:8000/intent", json={
        "goal": "unknown",
        "description": "what are the latest developments in AI agents 2026",
        "priority": "medium",
        "requires_tools": False
    }, timeout=5)
    print("Status:", res.status_code)
except Exception as e:
    print("Error:", e)
