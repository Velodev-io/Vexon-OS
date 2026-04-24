import asyncio
import os
from dotenv import load_dotenv

# Load env before importing llm.sdk
load_dotenv()
from llm.sdk import call_with_fallback

async def test():
    messages = [
        {
            "role": "user",
            "content": "Original goal: testing\n\nSearch Results:\nNone\n\nNow write your structured final answer."
        }
    ]
    try:
        # Force it to skip Groq by removing GROQ_API_KEY from environment
        os.environ.pop("GROQ_API_KEY", None)
        
        print(f"Gemini Key: {os.getenv('GEMINI_API_KEY')[:10]}...")
        stream = await call_with_fallback(messages, system="You are a researcher.", stream=True)
        print("Got stream generator!")
        async for token in stream:
            print(token, end="")
        print("\nDone!")
    except Exception as e:
        print("Error:", e)
        import traceback
        traceback.print_exc()

asyncio.run(test())
