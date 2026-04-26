import asyncio
import os
from dotenv import load_dotenv
from llm.sdk import call_with_fallback

load_dotenv()

async def test():
    messages = [
        {
            "role": "user",
            "content": "Original goal: testing\n\nSearch Results:\nNone\n\nNow write your structured final answer."
        }
    ]
    try:
        stream = await call_with_fallback(messages, system="You are a researcher.", stream=True)
        print("Got stream generator!")
        async for token in stream:
            print(token, end="")
        print("\nDone!")
    except Exception as e:
        print("Error:", e)

asyncio.run(test())
