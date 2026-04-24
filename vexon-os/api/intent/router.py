import logging
from typing import Dict, Any

from agents.tasks import run_agent_task, run_researcher_task
from agents.supervisor import run_supervisor_task

logger = logging.getLogger(__name__)

# Keywords that trigger the Researcher Agent
RESEARCH_KEYWORDS = [
    "search", "find", "latest", "news", "what is", "who is", "how does",
    "research", "look up", "tell me about", "explain", "what are", "how do",
    "when did", "where is", "why does", "recent", "current", "today",
    "2024", "2025", "2026", "update", "article", "report"
]

def _is_research_intent(intent: Dict[str, Any]) -> bool:
    text = (intent.get("goal", "") + " " + intent.get("description", "")).lower()
    return any(kw in text for kw in RESEARCH_KEYWORDS)

def route_intent(intent: Dict[str, Any], session_id: str, user_id: str) -> str:
    goal = intent.get("goal", "").lower()
    description = intent.get("description", "").lower()
    requires_tools = intent.get("requires_tools", False)

    is_complex = (
        ("build" in goal or "create" in goal) and requires_tools
        or intent.get("priority") == "high" and requires_tools
    )
    is_research = _is_research_intent(intent)

    if is_complex:
        logger.info(f"Routing to SUPERVISOR for session {session_id}")
        task = run_supervisor_task.delay(intent, session_id, user_id)
    elif is_research:
        logger.info(f"Routing to RESEARCHER for session {session_id} | goal: {intent.get('goal')}")
        task = run_researcher_task.delay(intent, session_id, user_id)
    else:
        logger.info(f"Routing to BASE AGENT for session {session_id}")
        task = run_agent_task.delay(intent, session_id, user_id)

    return task.id
