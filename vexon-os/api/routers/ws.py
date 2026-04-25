from fastapi import APIRouter, WebSocket

from ws.handler import websocket_endpoint

router = APIRouter(tags=["ws"])


@router.websocket("/ws/{session_id}")
async def ws_handler(websocket: WebSocket, session_id: str):
    await websocket_endpoint(websocket, session_id)
