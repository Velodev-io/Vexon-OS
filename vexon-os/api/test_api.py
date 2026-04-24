import requests

try:
    res = requests.post("http://localhost:8000/intent", json={
        "message": "test",
        "session_id": "test",
        "user_id": "test"
    })
    print(res.status_code)
    print(res.json())
except Exception as e:
    print("Error:", e)
