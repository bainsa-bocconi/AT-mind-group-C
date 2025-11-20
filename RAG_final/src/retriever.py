import os
from typing import List, Tuple
import numpy as np

from sentence_transformers import SentenceTransformer
import faiss



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
    Archivio per-sessione:
    - non salva su disco
    - indicizza solo i testi caricati dal venditore in questa sessione
    - NESSUN accesso a XLSX o altre fonti
    """
    def __init__(self):
        self._model = SentenceTransformer(EMBEDDING_MODEL, device="cpu")
        self._chunks: List[str] = []
        self._index = None  
        self._dim = None
        self._vecs = None  

    def add_docs(self, docs: List[str]) -> int:
        """Aggiunge documenti (email, chat, note, offerte). Ritorna numero di chunk indicizzati."""
        new_chunks = []
        for d in docs:
            new_chunks.extend(_chunk_text(d))

        if not new_chunks:
            return 0

        
        mat = self._model.encode(new_chunks, convert_to_numpy=True, normalize_embeddings=True)

        if self._index is None:
            self._dim = mat.shape[1]
            self._index = faiss.IndexFlatIP(self._dim)
            self._vecs = mat
            self._index.add(mat)
            self._chunks = list(new_chunks)
        else:
            self._vecs = np.vstack([self._vecs, mat])
            self._index.add(mat)
            self._chunks.extend(new_chunks)

        return len(new_chunks)

    def retrieve(self, query: str, k: int = TOP_K) -> List[Tuple[str, float, int]]:
        """Ritorna lista di tuple (chunk, score, chunk_id)."""
        if self._index is None or not self._chunks:
            return []

        qv = self._model.encode([query], convert_to_numpy=True, normalize_embeddings=True)
        D, I = self._index.search(qv, k)
        hits = []
        for rank, idx in enumerate(I[0]):
            if idx == -1:
                continue
            chunk = self._chunks[idx]
            score = float(D[0][rank])
            hits.append((chunk, score, int(idx)))
        return hits

    @property
    def size(self) -> int:
        return len(self._chunks)
