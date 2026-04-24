import json
import os
from dotenv import load_dotenv
import redis

load_dotenv()
url = os.getenv("REDIS_URL").replace("CERT_NONE", "none")
r = redis.Redis.from_url(url)
print("Connected", r.ping())
