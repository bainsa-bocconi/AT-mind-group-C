from fastapi import FastAPI
from src.router_chat import router as chat_router
from src.router_ingest import router as ingest_router

app = FastAPI(
    title="Sales RAG API",
    description="Assistente vendite (RAG + Llama 3.3-3B locale).",
    version="1.0.0"
)


app.include_router(ingest_router)
app.include_router(chat_router)

@app.get("/")
def root():
    return {
        "message": "API attiva Usa /ingest per caricare testi e /chat per chiedere insight."
    }
