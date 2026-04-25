import os
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt

ALGORITHM = "HS256"
TOKEN_TTL_DAYS = 30

bearer_scheme = HTTPBearer(auto_error=False)


def _get_secret() -> str:
    secret = os.getenv("JWT_SECRET")
    if not secret:
        raise HTTPException(status_code=503, detail="JWT auth is not configured")
    return secret


def create_token(user_id: str) -> str:
    expires_at = datetime.now(timezone.utc) + timedelta(days=TOKEN_TTL_DAYS)
    payload = {
        "sub": user_id,
        "exp": expires_at,
    }
    return jwt.encode(payload, _get_secret(), algorithm=ALGORITHM)


def decode_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, _get_secret(), algorithms=[ALGORITHM])
    except JWTError as exc:
        raise HTTPException(status_code=401, detail="Invalid or expired token") from exc

    if not payload.get("sub"):
        raise HTTPException(status_code=401, detail="Invalid token payload")

    return payload


async def verify_token(
    creds: HTTPAuthorizationCredentials = Security(bearer_scheme),
) -> dict:
    if creds is None or not creds.credentials:
        raise HTTPException(status_code=401, detail="Missing bearer token")

    return decode_token(creds.credentials)
