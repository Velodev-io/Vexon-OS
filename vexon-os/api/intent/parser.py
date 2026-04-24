import json
import logging
from typing import Dict, Any
from llm.sdk import call_with_fallback

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are an Intent Parser for an AI-Native OS.
Your job is to analyze the user's input and extract their intent into a strict JSON format.
Output ONLY JSON, no markdown formatting, no explanations.

JSON Schema:
{
  "goal": "short summary of what the user wants to achieve (max 5 words)",
  "description": "detailed description of the task",
  "parameters": {},
  "priority": "low|medium|high",
  "requires_tools": true|false
}
"""

async def parse_intent(user_message: str) -> Dict[str, Any]:
    messages = [{"role": "user", "content": user_message}]
    
    try:
        response_text = await call_with_fallback(messages, system=SYSTEM_PROMPT, stream=False)
        
        text = response_text.strip()
        if text.startswith("```json"):
            text = text[7:]
        if text.endswith("```"):
            text = text[:-3]
        text = text.strip()
            
        parsed = json.loads(text)
        if "goal" not in parsed:
            raise ValueError("Missing goal in JSON")
            
        return parsed
    except Exception as e:
        logger.error(f"Failed to parse intent: {e}")
        return {
            "goal": "unknown",
            "description": user_message,
            "parameters": {},
            "priority": "medium",
            "requires_tools": False
        }
