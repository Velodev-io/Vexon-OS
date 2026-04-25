EMBEDDING_DIMENSION = 384

_embedding_model = None


def _get_embedding_model():
    global _embedding_model

    if _embedding_model is not None:
        return _embedding_model

    try:
        from sentence_transformers import SentenceTransformer
    except ImportError:
        return None

    _embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
    return _embedding_model


def encode_text(text: str):
    model = _get_embedding_model()
    if model is None:
        return None
    return model.encode(text)
