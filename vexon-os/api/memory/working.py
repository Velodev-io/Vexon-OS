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


def save_memory_entry(session_id, user_id, entry, ttl=86400 * 7, limit=50):
    key = f"memory:{user_id}:{session_id}"
    r.lpush(key, json.dumps(entry))
    r.ltrim(key, 0, limit - 1)
    r.expire(key, ttl)


def load_session_memories(session_id, user_id, limit=20):
    key = f"memory:{user_id}:{session_id}"
    entries = r.lrange(key, 0, limit - 1)
    return [json.loads(item) for item in entries]


def load_all_memories(user_id, per_session_limit=20):
    pattern = f"memory:{user_id}:*"
    entries = []
    for key in r.scan_iter(pattern):
        raw_entries = r.lrange(key, 0, per_session_limit - 1)
        entries.extend(json.loads(item) for item in raw_entries)
    entries.sort(key=lambda entry: entry.get("timestamp", ""), reverse=True)
    return entries
