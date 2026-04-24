import os
from dotenv import load_dotenv
import redis

load_dotenv()
redis_url = os.getenv("REDIS_URL").replace("CERT_NONE", "none")
r = redis.Redis.from_url(redis_url)
try:
    r.ping()
    print("Successfully connected to Upstash Redis!")
except Exception as e:
    print(f"Failed to connect to Redis: {e}")
