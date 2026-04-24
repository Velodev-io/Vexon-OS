import os
from qdrant_client import QdrantClient
from qdrant_client.http import models

qdrant_url = os.getenv("QDRANT_URL")
qdrant_api_key = os.getenv("QDRANT_API_KEY")

# Initialize client only if URL is provided
client = QdrantClient(url=qdrant_url, api_key=qdrant_api_key) if qdrant_url else None

COLLECTION_NAME = "vexon_memory"

def store_memory(user_id, content, embedding, metadata=None):
    if not client: return
    if metadata is None: metadata = {}
    
    metadata["user_id"] = str(user_id)
    metadata["content"] = content
    
    client.upsert(
        collection_name=COLLECTION_NAME,
        points=[
            models.PointStruct(
                id=os.urandom(16).hex(),
                vector=embedding,
                payload=metadata
            )
        ]
    )

def search_memory(user_id, query_embedding, top_k=5):
    if not client: return []
    results = client.search(
        collection_name=COLLECTION_NAME,
        query_vector=query_embedding,
        query_filter=models.Filter(
            must=[
                models.FieldCondition(
                    key="user_id",
                    match=models.MatchValue(value=str(user_id))
                )
            ]
        ),
        limit=top_k
    )
    return [hit.payload.get("content") for hit in results]
