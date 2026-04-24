import os
import json
import firebase_admin
from firebase_admin import auth, credentials
import logging

logger = logging.getLogger(__name__)

# Initialize Firebase Admin SDK
cred_json = os.getenv("FIREBASE_CREDENTIALS")
if cred_json:
    try:
        if not firebase_admin._apps:
            # We handle both file paths and JSON strings
            if cred_json.startswith("{"):
                cred_dict = json.loads(cred_json)
                cred = credentials.Certificate(cred_dict)
            else:
                cred = credentials.Certificate(cred_json)
            firebase_admin.initialize_app(cred)
    except Exception as e:
        logger.error(f"Failed to initialize Firebase: {e}")

def verify_firebase_token(id_token: str):
    try:
        decoded_token = auth.verify_id_token(id_token)
        return {
            "uid": decoded_token.get("uid"),
            "email": decoded_token.get("email"),
            "name": decoded_token.get("name"),
            "picture": decoded_token.get("picture")
        }
    except Exception as e:
        logger.error(f"Firebase token verification failed: {e}")
        return None
