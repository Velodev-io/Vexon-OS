import asyncio
from dotenv import load_dotenv
load_dotenv("api/.env")

from api.agents.base_agent import BaseAgent

async def main():
    agent = BaseAgent("test_session", "test_user", "what is 2+2")
    result = await agent.execute({"description": "what is 2+2"})
    print("Result:", result)

asyncio.run(main())
