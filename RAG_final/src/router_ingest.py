from typing import List, Optional
from fastapi import APIRouter, Query

from src.router_chat import get_store, stores
from src.retriever_chroma import HybridStore

router = APIRouter(prefix="/ingest", tags=["ingest"])

@router.get("/")
def ingest(
    session_id: str = Query(..., description="Session ID"),
    docs: List[str] = Query(
        ..., 
        description="Lista di testi (usa ?docs=...&docs=... per più elementi)"
    ),
    clear: Optional[bool] = Query(
        False,
        description="Se True, resetta la base della sessione prima di indicizzare"
    ),
):
    """
    Aggiunge testi alla base di sessione tramite GET.
    """

    if clear:
        stores[session_id] = HybridStore(session_id)

    store = get_store(session_id)

    docs = [d.strip() for d in docs if d and d.strip()]
    if not docs:
        return {"ok": False, "error": "Nessun testo valido fornito."}

    added = store.add_session_docs(docs)

    return {
        "ok": True,
        "chunks_added": added,
        "session_size": store.session_size,
    }
