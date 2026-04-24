from .registry import register_tool
from memory.longterm import search_memory
import os

@register_tool(
    name="memory_recall",
    description="Recall relevant memories from the user's past sessions",
    parameters={
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "What to search for in memory"}
        },
        "required": ["query"]
    }
)
def memory_recall(query: str, user_id: str = None):
    # This requires an embedding model. For now, we'll assume the embedding is handled.
    # In a real implementation, we would call an embedding API here.
    return "Memory recall results would appear here (requires embedding model integration)."
