import asyncio
from dotenv import load_dotenv
load_dotenv()
from agents.tasks import run_researcher_task

intent = {"goal": "what are the latest developments in AI agents 2026", "description": ""}
try:
    print("Running task locally...")
    run_researcher_task(intent, "sess123", "user123")
except Exception as e:
    print("Caught exception:")
    import traceback
    traceback.print_exc()
