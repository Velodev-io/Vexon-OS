import asyncio
import redis.asyncio as redis
import json

async def monitor():
    # Connect to the Redis specified in .env
    from dotenv import load_dotenv
    import os
    load_dotenv()
    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0").replace("CERT_NONE", "none")
    
    r = redis.from_url(redis_url)
    pubsub = r.pubsub()
    await pubsub.subscribe("agent_events")
    
    print("Listening for agent events...")
    async for message in pubsub.listen():
        if message["type"] == "message":
            data = json.loads(message["data"])
            event = json.loads(data["event"])
            print(f"[{event['type']}] {event.get('data', {})}")

asyncio.run(monitor())
