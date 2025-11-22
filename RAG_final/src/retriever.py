import os
from typing import List, Tuple
import chromadb
from chromadb.utils import embedding_functions
from sentence_transformers import SentenceTransformer

CHUNK_SIZE = 600
CHUNK_OVERLAP = 120
TOP_K = 6

EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "intfloat/multilingual-e5-base")

def _chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> List[str]:
    text = text.strip()
    if not text:
        return []
    chunks = []
    i = 0
    while i < len(text):
        chunks.append(text[i:i + chunk_size])
        i += max(1, chunk_size - overlap)
    return chunks

class EphemeralStore:
    """
    Archivio per sessione basato su Chroma:
    - indicizza solo testi caricati in questa sessione
    - nessun accesso a XLSX
    - si cancella se la sessione viene resettata
    """
    def __init__(self, session_id: str):
        self.session_id = session_id
        self._embedder = SentenceTransformer(EMBEDDING_MODEL, device="cpu")
        self._client = chromadb.Client()  # in-memory
        self._collection = self._client.create_collection(name=session_id)
        self._chunks = []

    def add_docs(self, docs: List[str]) -> int:
        new_chunks = []
        for d in docs:
            new_chunks.extend(_chunk_text(d))
        if not new_chunks:
            return 0
        ids = [f"{self.session_id}_{i+len(self._chunks)}" for i in range(len(new_chunks))]
        embeds = self._embedder.encode(new_chunks).tolist()
        self._collection.add(documents=new_chunks, embeddings=embeds, ids=ids)
        self._chunks.extend(new_chunks)
        return len(new_chunks)

    def retrieve(self, query: str, k: int = TOP_K) -> List[Tuple[str, float, int]]:
        if len(self._chunks) == 0:
            return []
        q_emb = self._embedder.encode([query]).tolist()
        results = self._collection.query(query_embeddings=q_emb, n_results=k)
        docs = results["documents"][0]
        scores = results["distances"][0]
        hits = [(docs[i], float(1 - scores[i]), i) for i in range(len(docs))]
        return hits

    @property
    def size(self) -> int:
        return len(self._chunks)
