
import os
from typing import List, Tuple
import chromadb
from src.embeddings import embed_texts, embed_query

CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", "./data/chroma_store")
CORPUS_COLL = os.getenv("CHROMA_CORPUS_COLLECTION", "corpus_v1")
SESSION_PREFIX = os.getenv("CHROMA_SESSION_PREFIX", "session_")
TOP_K = int(os.getenv("TOP_K", "6"))

def _chunk_text(text: str, chunk_size=600, overlap=120) -> List[str]:
    text = text.strip()
    if not text: return []
    out, i = [], 0
    while i < len(text):
        out.append(text[i:i+chunk_size])
        i += max(1, chunk_size - overlap)
    return out

class HybridStore:
    """
    1) Collection corpus (persistente, condivisa)
    2) Collection di sessione (ephemeral, solo per input ad-hoc)
    Retrieval: unione risultati (corpus + sessione), ordinati per similarità.
    """
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.client = chromadb.PersistentClient(path=CHROMA_PERSIST_DIR)
        self.corpus = self.client.get_or_create_collection(CORPUS_COLL)
        self.session = self.client.get_or_create_collection(f"{SESSION_PREFIX}{session_id}")

    def add_session_docs(self, docs: List[str]) -> int:
        chunks, ids = [], []
        base = self.session.count()
        for d in docs:
            for c in _chunk_text(d):
                chunks.append(c)
                ids.append(f"{self.session_id}_{base+len(ids)}")
        if not chunks: return 0
        self.session.add(documents=chunks, embeddings=embed_texts(chunks), ids=ids)
        return len(chunks)

    def clear(self):
        try:
            self.client.delete_collection(name=f"{SESSION_PREFIX}{self.session_id}")
            self.session = self.client.get_or_create_collection(f"{SESSION_PREFIX}{self.session_id}")
            print(f"Cleared collection: {self.session_id}")
        except Exception as e:
            print(f"Error clearing collection: {e}")


    def retrieve(self, query: str, k: int = TOP_K) -> List[Tuple[str, float, str]]:
        q = embed_query(query)

        def _q(coll):
            if coll.count() == 0:
                return []
            r = coll.query(query_embeddings=[q], n_results=k)
            docs = r.get("documents", [[]])[0]
            dists = r.get("distances", [[]])[0] 
            ids = r.get("ids", [[]])[0]
            
            return [(docs[i], 1.0 - float(dists[i]), ids[i]) for i in range(len(docs))]

        hits = _q(self.corpus) + _q(self.session)
        
        best = {}
        for doc, s, id_ in hits:
            if id_ not in best or s > best[id_][1]:
                best[id_] = (doc, s, id_)
        
        ordered = sorted(best.values(), key=lambda x: x[1], reverse=True)[:k]
        return ordered

    @property
    def session_size(self) -> int:
        return self.session.count()
