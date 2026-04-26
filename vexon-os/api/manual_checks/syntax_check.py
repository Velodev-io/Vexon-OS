import asyncio
from agents.researcher_agent import ResearcherAgent
from unittest.mock import MagicMock

class MockRedis:
    def publish(self, *args):
        pass

agent = ResearcherAgent("test", "test", "test")
agent.redis_client = MockRedis()

async def run():
    print("Executing...")
    await agent.execute({"description": "testing"})
    print("Done")

asyncio.run(run())
