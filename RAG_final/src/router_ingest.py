from typing import List, Optional
from fastapi import APIRouter, Query, Body
from src.router_chat import get_store 
router = APIRouter(prefix="/ingest", tags=["ingest"])

@router.post("/")
def ingest(
    session_id: str = Query(..., description="Identificatore della sessione"),
    docs: List[str] = Body(..., description="Lista di testi: email, messaggi, note, offerte"),
    clear: Optional[bool] = Query(False, description="Se True, resetta la base della sessione prima di indicizzare"),
):
    """
    Aggiunge testi alla base effimera della sessione.
    Usa `clear=true` per ripartire da zero.
    """
    stores[session_id] = EphemeralStore(session_id)


    if clear:
        from src.retriever import EphemeralStore
        from src.router_chat import stores  
        stores[session_id] = EphemeralStore()
        store = stores[session_id]

    if not docs or not any(s.strip() for s in docs):
        return {"ok": False, "error": "Nessun testo valido fornito."}

    added = store.add_docs(docs)
    return {
        "ok": True,
        "chunks_added": added,
        "session_size": store.size
    }
