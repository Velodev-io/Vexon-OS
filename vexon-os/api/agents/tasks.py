import asyncio
from celery_app import app
from .base_agent import BaseAgent, AgentStatus
from .researcher_agent import ResearcherAgent

@app.task(bind=True, name="agents.tasks.run_agent_task", max_retries=3, default_retry_delay=5)
def run_agent_task(self, intent, session_id, user_id):
    agent = BaseAgent(session_id, user_id, intent.get("goal", "unknown"))
    try:
        agent.load_memory()
        result = asyncio.run(agent.execute(intent))
        agent.save_memory()
        return result
    except Exception as exc:
        agent.set_status(AgentStatus.ERROR)
        raise self.retry(exc=exc)

@app.task(bind=True, name="agents.tasks.run_researcher_task", max_retries=3, default_retry_delay=5)
def run_researcher_task(self, intent, session_id, user_id):
    agent = ResearcherAgent(session_id, user_id, intent.get("goal", intent.get("description", "unknown")))
    try:
        agent.load_memory()
        result = asyncio.run(agent.execute(intent))
        agent.save_memory()
        return result
    except Exception as exc:
        agent.set_status(AgentStatus.ERROR)
        agent.publish_event("error", {"message": str(exc)})
        with open("celery_error.log", "w") as f:
            f.write(f"Task Failed: {str(exc)}")
        raise self.retry(exc=exc)
