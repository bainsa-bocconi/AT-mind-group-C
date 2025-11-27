from fastapi import APIRouter, Query, Body
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


@router.post("/")
def chat(
    session_id: str = Query(..., description="Identificatore della sessione utente"),
    user_text: str = Body(..., description="Messaggio del venditore o appunto cliente"),
):
   
    block = hard_block(user_text)
    if block:
        return {"blocked": True, "message": block}

   
    store = EphemeralStore(session_id)
    if store.size == 0:
        return {"error": "Nessun documento indicizzato. Usa /ingest prima di /chat."}

   
    hits = store.retrieve(user_text)
    snippets = "\n\n---\n\n".join([f"[{i}] {chunk}" for chunk, _, i in hits])

    
    messages = [
        {"role": "system", "content": SYSTEM},
        {
            "role": "user",
            "content": f"{INSIGHT_TASK}\n\nSALES_INPUT:\n{user_text}\n\nRETRIEVED_SNIPPETS:\n{snippets}",
        },
    ]

    raw_output = generate(messages)

   
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
        "json": parsed.model_dump(),
        "raw_text": raw_output,
    }
