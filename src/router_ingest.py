from typing import List, Optional
from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import os

from src.router_chat import get_store, stores
from src.retriever_chroma import HybridStore

router = APIRouter(prefix="/ingest", tags=["ingest"])

class IngestRequest(BaseModel):
    session_id: str
    docs: List[str]
    clear: Optional[bool] = False

@router.get("/", response_class=HTMLResponse)
def ingest_page():
    """Serve the HTML ingestion form"""
    template_path = os.path.join(os.path.dirname(__file__), "templates", "ingest.html")
    with open(template_path, "r", encoding="utf-8") as f:
        return f.read()

@router.post("/")
def ingest(payload: IngestRequest):
    if payload.clear:
        store = get_store(payload.session_id)
        store.clear()
    
    store = get_store(payload.session_id)
    docs = [d.strip() for d in payload.docs if d and d.strip()]
    if not docs:
        return {"ok": False, "error": "Nessun testo valido fornito."}
    
    added = store.add_session_docs(docs)
    return {"ok": True, "chunks_added": added, "session_size": store.session_size}
