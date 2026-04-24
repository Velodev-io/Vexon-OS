from celery_app import app
from .base_agent import BaseAgent, AgentStatus

@app.task(bind=True)
def run_supervisor_task(self, intent, session_id, user_id):
    agent = BaseAgent(session_id, user_id, "Supervisor: " + intent.get("goal", "unknown"))
    agent.set_status(AgentStatus.THINKING)
    agent.publish_event("stream_token", {"token": "Supervisor delegating tasks..."})
    agent.set_status(AgentStatus.DONE)
    return {"result": "Supervisor complete"}
