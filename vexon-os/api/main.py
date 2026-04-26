import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()

from core.rate_limit import RateLimitExceeded, _rate_limit_exceeded_handler, limiter
from db.database import init_db
from routers.agents import router as agents_router
from routers.auth import router as auth_router
from routers.sessions import router as sessions_router
from routers.system import router as system_router
from routers.ws import router as ws_router

app = FastAPI(title="Vexon OS")
if os.getenv("VEXON_SKIP_DB_INIT") != "1":
    init_db()
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


def _allowed_origins() -> list[str]:
    configured = os.getenv(
        "FRONTEND_ORIGINS",
        "http://localhost:3000,http://127.0.0.1:3000",
    )
    return [origin.strip() for origin in configured.split(",") if origin.strip()]


def _allowed_origin_regex() -> str:
    return os.getenv(
        "FRONTEND_ORIGIN_REGEX",
        r"http://(localhost|127\.0\.0\.1|192\.168\.\d{1,3}\.\d{1,3}|10\.\d{1,3}\.\d{1,3}\.\d{1,3}|172\.(1[6-9]|2\d|3[0-1])\.\d{1,3}\.\d{1,3}):3000",
    )

app.add_middleware(
    CORSMiddleware,
    allow_origins=_allowed_origins(),
    allow_origin_regex=_allowed_origin_regex(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(agents_router)
app.include_router(sessions_router)
app.include_router(system_router)
app.include_router(ws_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
