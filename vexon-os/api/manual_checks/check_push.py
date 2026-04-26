import os
from dotenv import load_dotenv
load_dotenv()
from celery_app import app
from agents.tasks import run_researcher_task

intent = {"goal": "test", "description": "test"}
task = run_researcher_task.delay(intent, "sess", "usr")
print("Pushed task:", task.id)
