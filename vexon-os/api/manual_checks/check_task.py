import asyncio
from agents.researcher_agent import ResearcherAgent

async def test():
    intent = {"goal": "what are the latest developments in AI agents 2026", "description": ""}
    agent = ResearcherAgent("test_session", "test_user", intent["goal"])
    try:
        res = await agent.execute(intent)
        print("Success:", res)
    except Exception as e:
        print("Error executing agent:", e)
        import traceback
        traceback.print_exc()

asyncio.run(test())
