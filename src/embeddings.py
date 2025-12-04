import os
from sentence_transformers import SentenceTransformer

_EMBED_MODEL_NAME = os.getenv("EMBEDDING_MODEL", "intfloat/multilingual-e5-base")
_embedder = SentenceTransformer(_EMBED_MODEL_NAME, device="cpu")

def embed_texts(texts: list[str]) -> list[list[float]]:
    if not texts: return []
    return _embedder.encode(texts, normalize_embeddings=True).tolist()

def embed_query(text: str) -> list[float]:
    return embed_texts([text])[0]
