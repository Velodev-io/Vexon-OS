import redis
import json
import os

redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
r = redis.from_url(redis_url)

def set_context(session_id, user_id, data, ttl=3600):
    key = f"vexon:user:{user_id}:session:{session_id}:context"
    r.setex(key, ttl, json.dumps(data))

def get_context(session_id, user_id):
    key = f"vexon:user:{user_id}:session:{session_id}:context"
    data = r.get(key)
    return json.loads(data) if data else {}

def set_task_status(task_id, status):
    key = f"vexon:task:{task_id}:status"
    r.setex(key, 3600, status)

def get_task_status(task_id):
    key = f"vexon:task:{task_id}:status"
    status = r.get(key)
    return status.decode() if status else "unknown"
