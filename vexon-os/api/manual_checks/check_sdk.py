import asyncio
import os
import logging
from dotenv import load_dotenv
from llm.sdk import call_with_fallback

# Setup logging to see which provider is used
logging.basicConfig(level=logging.INFO)

async def test_llm():
    # Load environment variables from .env
    load_dotenv()
    
    messages = [{"role": "user", "content": "Say 'Vexon OS is online' in a futuristic way."}]
    system = "You are the Vexon OS core kernel."
    
    print("\n--- Testing Regular Mode ---")
    try:
        response = await call_with_fallback(messages, system=system, stream=False)
        print(f"\nResponse: {response}")
    except Exception as e:
        print(f"Regular Mode Error: {e}")

    print("\n--- Testing Streaming Mode ---")
    try:
        gen = await call_with_fallback(messages, system=system, stream=True)
        print("Response: ", end="", flush=True)
        async for token in gen:
            print(token, end="", flush=True)
        print("\n")
    except Exception as e:
        print(f"Streaming Mode Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_llm())
