from celery_app import app
import asyncio

from .base_agent import BaseAgent, AgentStatus
from .researcher_agent import ResearcherAgent

AGENT_REGISTRY = {
    "research": ResearcherAgent,
    "default": BaseAgent,
}


class SupervisorAgent(BaseAgent):
    def _pick_agent(self, intent: dict):
        text = f"{intent.get('goal', '')} {intent.get('description', '')}".lower()
        if any(keyword in text for keyword in ["search", "research", "find", "latest", "news"]):
            return AGENT_REGISTRY["research"]
        return AGENT_REGISTRY["default"]

    async def execute(self, intent: dict):
        agent_class = self._pick_agent(intent)
        delegated_agent = agent_class(self.session_id, self.user_id, intent.get("goal", self.goal))
        self.publish_event(
            "THINKING",
            {"message": f"Supervisor delegating to {delegated_agent.__class__.__name__}..."},
        )
        return await delegated_agent.execute(intent)

@app.task(bind=True)
def run_supervisor_task(self, intent, session_id, user_id):
    agent = SupervisorAgent(session_id, user_id, "Supervisor: " + intent.get("goal", "unknown"))
    try:
        agent.set_status(AgentStatus.THINKING)
        return asyncio.run(agent.execute(intent))
    except Exception as exc:
        agent.set_status(AgentStatus.ERROR)
        agent.publish_event("error", {"message": str(exc)})
        raise self.retry(exc=exc)
