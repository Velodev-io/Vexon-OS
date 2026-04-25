import asyncio
import json
import logging
import os
from typing import Optional
import redis.asyncio as redis
from fastapi import HTTPException, WebSocket, WebSocketDisconnect
from starlette.websockets import WebSocketState

from auth.local import decode_token

logger = logging.getLogger(__name__)
redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0").replace("CERT_NONE", "none")


async def safe_receive(ws: WebSocket) -> Optional[str]:
    try:
        return await asyncio.wait_for(ws.receive_text(), timeout=30.0)
    except asyncio.TimeoutError:
        await ws.send_json({"type": "ping"})
        return None
    except WebSocketDisconnect:
        return None


async def websocket_endpoint(websocket: WebSocket, session_id: str):
    token = websocket.query_params.get("token")
    if not token:
        await websocket.close(code=4401)
        return
    try:
        decode_token(token)
    except HTTPException:
        await websocket.close(code=4401)
        return

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

            await safe_receive(websocket)
            if websocket.client_state == WebSocketState.DISCONNECTED:
                break

    except (WebSocketDisconnect, ConnectionResetError):
        logger.info(f"WebSocket disconnected for session {session_id}")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        try:
            await pubsub.unsubscribe(channel)
            await pubsub.close()
            await r.aclose()
        except Exception:
            pass
