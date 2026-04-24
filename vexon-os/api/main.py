from fastapi import FastAPI, Depends, HTTPException, WebSocket, Body
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Dict, Any
import uuid
from dotenv import load_dotenv
load_dotenv()

from db.database import get_db
from intent.parser import parse_intent
from intent.router import route_intent
from ws.handler import websocket_endpoint

app = FastAPI(title="Vexon OS")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/intent")
async def handle_intent(
    message: str = Body(..., embed=True),
    session_id: str = Body(..., embed=True),
    user_id: str = Body(..., embed=True)
):
    # Parse the user's message into an intent
    intent = await parse_intent(message)
    
    # Route the intent to the appropriate Celery task
    task_id = route_intent(intent, session_id, user_id)
    
    return {
        "task_id": task_id,
        "intent": intent,
        "status": "dispatched"
    }

@app.websocket("/ws/{session_id}")
async def ws_handler(websocket: WebSocket, session_id: str):
    await websocket_endpoint(websocket, session_id)

@app.get("/health")
def health():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
