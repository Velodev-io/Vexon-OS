import os
from typing import Awaitable, Callable

from qdrant_client import QdrantClient
from qdrant_client.http import models

from memory.embeddings import EMBEDDING_DIMENSION, encode_text

qdrant_url = os.getenv("QDRANT_URL")
qdrant_api_key = os.getenv("QDRANT_API_KEY")

# Initialize client only if URL is provided
client = QdrantClient(url=qdrant_url, api_key=qdrant_api_key) if qdrant_url else None

COLLECTION_NAME = "vexon_memory"

def ensure_collection():
    if not client:
        return

    try:
        client.get_collection(COLLECTION_NAME)
    except Exception:
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=models.VectorParams(
                size=EMBEDDING_DIMENSION,
                distance=models.Distance.COSINE,
            ),
        )


def store_longterm(user_id, text, metadata=None):
    if not client:
        return

    embedding = encode_text(text)
    if embedding is None:
        return

    ensure_collection()
    payload = {"user_id": str(user_id), "text": text, **(metadata or {})}

    client.upsert(
        collection_name=COLLECTION_NAME,
        points=[
            models.PointStruct(
                id=os.urandom(16).hex(),
                vector=embedding.tolist(),
                payload=payload,
            )
        ],
    )


def search_longterm(user_id, query, top_k=5):
    if not client:
        return []

    embedding = encode_text(query)
    if embedding is None:
        return []

    ensure_collection()
    results = client.search(
        collection_name=COLLECTION_NAME,
        query_vector=embedding.tolist(),
        query_filter=models.Filter(
            must=[
                models.FieldCondition(
                    key="user_id",
                    match=models.MatchValue(value=str(user_id)),
                )
            ]
        ),
        limit=top_k,
    )
    return [hit.payload.get("text") for hit in results if hit.payload.get("text")]


def summarize_session(user_id: str, session_id: str, llm_call=None):
    """
    Compress all short-term memories for a session into a single long-term summary.
    llm_call: optional async callable(messages) -> str for LLM summarization.
              If None, falls back to concatenation.
    """
    from memory.working import load_session_memories
    entries = load_session_memories(session_id, user_id, limit=50)
    if not entries:
        return

    text_parts = [
        f"[{e.get('type', 'memory')}] {e.get('content', '')}"
        for e in entries
        if e.get("content")
    ]
    if not text_parts:
        return

    combined = "\n".join(text_parts)

    if llm_call is not None:
        import asyncio
        messages = [
            {
                "role": "user",
                "content": (
                    "Summarize the following agent session memories into a concise paragraph "
                    "capturing key facts, decisions, and results:\n\n" + combined[:4000]
                ),
            }
        ]
        try:
            summary = asyncio.run(llm_call(messages))
        except Exception:
            summary = combined[:2000]
    else:
        summary = combined[:2000]

    store_longterm(
        user_id,
        summary,
        metadata={"session_id": session_id, "type": "session_summary"},
    )
    return summary


async def summarize_session_async(
    user_id: str,
    session_id: str,
    llm_call: Callable[[list[dict]], Awaitable[str]] | None = None,
):
    from memory.working import load_session_memories

    entries = load_session_memories(session_id, user_id, limit=50)
    if not entries:
        return None

    text_parts = [
        f"[{e.get('type', 'memory')}] {e.get('content', '')}"
        for e in entries
        if e.get("content")
    ]
    if not text_parts:
        return None

    combined = "\n".join(text_parts)
    summary = combined[:2000]

    if llm_call is not None:
        messages = [
            {
                "role": "user",
                "content": (
                    "Summarize the following agent session memories into a concise paragraph "
                    "capturing key facts, decisions, and results:\n\n" + combined[:4000]
                ),
            }
        ]
        try:
            summary = await llm_call(messages)
        except Exception:
            summary = combined[:2000]

    store_longterm(
        user_id,
        summary,
        metadata={"session_id": session_id, "type": "session_summary"},
    )
    return summary


def search_memory(user_id, query_embedding=None, top_k=5, query=None):
    if query is not None:
        return search_longterm(user_id, query, top_k=top_k)

    if not client or query_embedding is None:
        return []

    ensure_collection()
    vector = query_embedding.tolist() if hasattr(query_embedding, "tolist") else query_embedding
    results = client.search(
        collection_name=COLLECTION_NAME,
        query_vector=vector,
        query_filter=models.Filter(
            must=[
                models.FieldCondition(
                    key="user_id",
                    match=models.MatchValue(value=str(user_id)),
                )
            ]
        ),
        limit=top_k,
    )
    return [hit.payload.get("text") or hit.payload.get("content") for hit in results]
