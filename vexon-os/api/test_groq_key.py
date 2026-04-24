import asyncio
from groq import AsyncGroq

async def test():
    client = AsyncGroq(api_key="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")
    try:
        res = await client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[{"role": "user", "content": "hi"}],
            max_tokens=5
        )
        print("Success:", res.choices[0].message.content)
    except Exception as e:
        print("Error:", e)

asyncio.run(test())
