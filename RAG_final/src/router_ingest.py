from typing import List, Optional
from fastapi import APIRouter, Query, Body

from src.router_chat import get_store, stores  
from src.retriever_chroma import HybridStore   
router = APIRouter(prefix="/ingest", tags=["ingest"])


@router.post("/")
def ingest(
    session_id: str = Query(..., description="Identificatore della sessione"),
    docs: List[str] = Body(..., description="Lista di testi: email, messaggi, note, offerte"),
    clear: Optional[bool] = Query(
        False,
        description="Se True, resetta la base della sessione prima di indicizzare",
    ),
):
    """
    Aggiunge testi alla base di sessione (parte 'session' del retriever ibrido).
    Usa `clear=true` per ripartire da zero per quella sessione.
    """


    if clear:
        stores[session_id] = HybridStore(session_id)

   
    store = get_store(session_id)

   
    if not docs or not any(s.strip() for s in docs):
        return {"ok": False, "error": "Nessun testo valido fornito."}

    added = store.add_session_docs(docs)

    return {
        "ok": True,
        "chunks_added": added,
        "session_size": store.session_size,
    }

