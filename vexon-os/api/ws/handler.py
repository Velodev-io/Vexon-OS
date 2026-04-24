import asyncio
import json
import logging
import redis.asyncio as redis
from fastapi import WebSocket, WebSocketDisconnect
import os

logger = logging.getLogger(__name__)
redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0").replace("CERT_NONE", "none")

async def websocket_endpoint(websocket: WebSocket, session_id: str):
    await websocket.accept()
    logger.info(f"WebSocket connected for session {session_id}")
    
    r = redis.from_url(redis_url)
    pubsub = r.pubsub()
    channel = f"vexon:stream:{session_id}"
    
    await pubsub.subscribe(channel)
    
    try:
        while True:
            # Listen for messages from Redis Pub/Sub
            message = await pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0)
            if message:
                data = message["data"]
                if isinstance(data, bytes):
                    data = data.decode()
                await websocket.send_text(data)
            
            # Check for client-side disconnects or messages
            try:
                # Use a small timeout to avoid blocking the Redis loop
                await asyncio.wait_for(websocket.receive_text(), timeout=0.1)
            except asyncio.TimeoutError:
                pass
                
    except (WebSocketDisconnect, ConnectionResetError):
        logger.info(f"WebSocket disconnected for session {session_id}")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        try:
            await pubsub.unsubscribe(channel)
            await r.close()
        except:
            pass
