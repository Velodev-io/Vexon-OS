import os
import logging
from typing import AsyncGenerator, Union, List, Dict, Any

from groq import AsyncGroq
from anthropic import AsyncAnthropic
from openai import AsyncOpenAI

logger = logging.getLogger(__name__)

def get_groq_client():
    api_key = os.getenv("GROQ_API_KEY")
    return AsyncGroq(api_key=api_key) if api_key else None

def get_gemini_client():
    import google.generativeai as genai
    api_key = os.getenv("GEMINI_API_KEY")
    if api_key:
        genai.configure(api_key=api_key)
        return genai.GenerativeModel("gemini-1.5-pro")
    return None

def get_anthropic_client():
    api_key = os.getenv("ANTHROPIC_API_KEY")
    return AsyncAnthropic(api_key=api_key) if api_key else None

def get_perplexity_client():
    api_key = os.getenv("PERPLEXITY_API_KEY")
    return AsyncOpenAI(api_key=api_key, base_url="https://api.perplexity.ai") if api_key else None

def get_ollama_client():
    return os.getenv("OLLAMA_BASE_URL")

async def _call_groq(client, messages, system, stream):
    sys_msg = [{"role": "system", "content": system}] if system else []
    response = await client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=sys_msg + messages,
        stream=stream,
        temperature=0.7
    )
    if stream:
        async def generator():
            async for chunk in response:
                if chunk.choices and chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        return generator()
    else:
        return response.choices[0].message.content

async def _call_gemini(model, messages, system, stream):
    import google.generativeai as genai
    gemini_messages = []
    if system:
        gemini_messages.append({"role": "user", "parts": [f"System Instructions: {system}\n\nUnderstood."]})
        gemini_messages.append({"role": "model", "parts": ["Understood. I will follow the system instructions."]})
        
    for msg in messages:
        role = "user" if msg["role"] == "user" else "model"
        gemini_messages.append({"role": role, "parts": [msg["content"]]})
        
    response = await model.generate_content_async(
        contents=gemini_messages,
        generation_config=genai.types.GenerationConfig(temperature=0.7),
        stream=stream
    )
    if stream:
        async def generator():
            async for chunk in response:
                if chunk.text:
                    yield chunk.text
        return generator()
    else:
        return response.text

async def _call_anthropic(client, messages, system, stream):
    anthropic_messages = [{"role": msg["role"], "content": msg["content"]} for msg in messages if msg["role"] in ["user", "assistant"]]
    kwargs = {
        "model": "claude-3-5-sonnet-20241022",
        "max_tokens": 4096,
        "messages": anthropic_messages,
        "temperature": 0.7,
    }
    if system:
        kwargs["system"] = system

    if stream:
        async def generator():
            async with client.messages.stream(**kwargs) as stream_response:
                async for text in stream_response.text_stream:
                    yield text
        return generator()
    else:
        response = await client.messages.create(**kwargs)
        return response.content[0].text

async def _call_perplexity(client, messages, system, stream):
    sys_msg = [{"role": "system", "content": system}] if system else []
    response = await client.chat.completions.create(
        model="llama-3.1-sonar-large-128k-online",
        messages=sys_msg + messages,
        stream=stream,
        temperature=0.7
    )
    if stream:
        async def generator():
            async for chunk in response:
                if chunk.choices and chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        return generator()
    else:
        return response.choices[0].message.content

import httpx

def get_ollama_client():
    base_url = os.getenv("OLLAMA_BASE_URL")
    return base_url if base_url else None

async def _call_ollama(base_url, messages, system, stream):
    import json
    sys_msg = [{"role": "system", "content": system}] if system else []
    model = os.getenv("OLLAMA_MODEL", "llama3.2")
    
    payload = {
        "model": model,
        "messages": sys_msg + messages,
        "stream": stream,
        "options": {"temperature": 0.7}
    }
    
    if stream:
        async def generator():
            async with httpx.AsyncClient(timeout=60.0) as client:
                async with client.stream("POST", f"{base_url}/api/chat", json=payload) as response:
                    async for line in response.aiter_lines():
                        if line:
                            try:
                                data = json.loads(line)
                                if "message" in data and "content" in data["message"]:
                                    yield data["message"]["content"]
                            except:
                                continue
        return generator()
    else:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(f"{base_url}/api/chat", json=payload)
            data = response.json()
            return data["message"]["content"]
    
async def call_with_fallback(messages: List[Dict[str, str]], system: str = None, stream: bool = False) -> Union[str, AsyncGenerator[str, None]]:
    providers = [
        ("Ollama", get_ollama_client, _call_ollama),
        ("Groq", get_groq_client, _call_groq),
        ("Gemini", get_gemini_client, _call_gemini),
        ("Claude", get_anthropic_client, _call_anthropic),
        ("Perplexity", get_perplexity_client, _call_perplexity)
    ]
    
    last_error = None
    
    for provider_name, get_client_func, call_func in providers:
        try:
            client = get_client_func()
            if not client:
                logger.warning(f"Provider {provider_name} skipped (no configuration).")
                continue
            
            logger.info(f"Attempting to call {provider_name}...")
            result = await call_func(client, messages, system, stream)
            logger.info(f"Successfully called {provider_name}.")
            return result
        except Exception as e:
            logger.error(f"Provider {provider_name} failed: {str(e)}")
            last_error = e
            continue
            
    if last_error:
        raise Exception(f"All LLM providers failed. Last error: {str(last_error)}")
    else:
        raise Exception("No LLM providers available (missing API keys or configuration).")
