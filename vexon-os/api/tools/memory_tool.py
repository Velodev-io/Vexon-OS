from .registry import register_tool
from memory.embeddings import encode_text
from memory.longterm import search_longterm
from memory.working import load_all_memories


def _cosine_similarity(left, right):
    numerator = sum(a * b for a, b in zip(left, right))
    left_norm = sum(a * a for a in left) ** 0.5
    right_norm = sum(b * b for b in right) ** 0.5
    if not left_norm or not right_norm:
        return 0.0
    return float(numerator / (left_norm * right_norm))


def _keyword_score(query: str, text: str) -> float:
    query_words = {word for word in query.lower().split() if word}
    text_words = {word for word in text.lower().split() if word}
    if not query_words:
        return 0.0
    return len(query_words & text_words) / len(query_words)

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
    if not user_id:
        return []

    memories = load_all_memories(user_id)
    if not memories:
        return search_longterm(user_id, query, top_k=5)

    query_embedding = encode_text(query)
    scored = []

    for memory in memories:
        content = memory.get("content")
        if not content:
            continue

        score = _keyword_score(query, content)
        if query_embedding is not None:
            memory_embedding = encode_text(content)
            if memory_embedding is not None:
                score = _cosine_similarity(query_embedding, memory_embedding)

        scored.append((score, content))

    scored.sort(key=lambda item: item[0], reverse=True)
    matches = [content for score, content in scored if score > 0][:5]

    if len(matches) < 5:
        for item in search_longterm(user_id, query, top_k=5):
            if item not in matches:
                matches.append(item)
            if len(matches) == 5:
                break

    return matches
