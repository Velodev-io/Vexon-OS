import os
import secrets

from fastapi import HTTPException

from auth.local import create_token

LOCAL_USER_ID = os.getenv("VEXON_USER_ID", "suryansh")


def login_with_password(password: str) -> dict:
    expected_password = os.getenv("VEXON_PASSWORD")
    if not expected_password:
        raise HTTPException(status_code=503, detail="Local auth is not configured")

    if not secrets.compare_digest(password, expected_password):
        raise HTTPException(status_code=401, detail="Invalid password")

    return {
        "token": create_token(LOCAL_USER_ID),
        "user_id": LOCAL_USER_ID,
    }
