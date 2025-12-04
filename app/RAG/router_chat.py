from fastapi import APIRouter, Query, Body
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi import Request
from src.retriever_chroma import HybridStore
from src.guardrails import hard_block
from src.prompts import SYSTEM, INSIGHT_TASK
from src.llm_local import generate
from src.schema import parse_and_validate_insights

router = APIRouter(prefix="/chat", tags=["chat"])


stores: dict[str, HybridStore] = {}

def get_store(session_id: str) -> HybridStore:
    if session_id not in stores:
        stores[session_id] = HybridStore(session_id)
    return stores[session_id]

templates = Jinja2Templates(directory="src/templates")

@router.get("/", response_class=HTMLResponse)
async def chat_page(request: Request):
    """Serve the chat HTML interface"""
    return templates.TemplateResponse("chat.html", {"request": request})
from pydantic import BaseModel
from typing import Optional

class ChatRequest(BaseModel):
    session_id: str
    query: str

@router.post("/")
def chat(payload: ChatRequest):
    user_text = payload.query
    session_id = payload.session_id
   
    block = hard_block(user_text)
    if block:
        return {"blocked": True, "message": block}

    store = get_store(session_id)  # Use get_store, not HybridStore directly
    if store.session_size == 0:  # Use session_size property
        return {"ok": False, "error": "Nessun documento indicizzato. Usa /ingest prima di /chat."}

    hits = store.retrieve(user_text)
   
    snippets = "\n\n---\n\n".join([f"SNIPPET_{idx}:\n{chunk}" for idx, (chunk, _, _) in enumerate(hits)])

    messages = [
        {"role": "system", "content": SYSTEM},
        {
            "role": "user",
            "content": f"{INSIGHT_TASK}\n\nSALES_INPUT:\n{user_text}\n\nRETRIEVED_SNIPPETS:\n{snippets}",
        },
    ]

    raw_output = generate(messages)
    print(raw_output)
    
    try:
        parsed = parse_and_validate_insights(raw_output)
    except Exception as e:
        return {
            "ok": False,
            "error": f"Errore di validazione output: {e}",
            "raw_output": raw_output,
        }

    return {
        "ok": True,
        "answer": parsed.model_dump().get("answer", raw_output),  # Return 'answer' key for the HTML
        "json": parsed.model_dump(),
        "raw_text": raw_output,
    }
