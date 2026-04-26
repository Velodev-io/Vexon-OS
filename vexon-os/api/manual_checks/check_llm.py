import asyncio
from dotenv import load_dotenv
load_dotenv()

from llm.sdk import call_with_fallback

async def test():
    result = await call_with_fallback(
        messages=[{"role": "user", "content": "Say hello in 5 words."}],
        stream=False
    )
    print("Result:", result)

asyncio.run(test())
