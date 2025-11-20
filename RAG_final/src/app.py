from fastapi import FastAPI

app = FastAPI(title="Sales RAG (Llama 3.3-3B)")

@app.get("/")
def root():
    return {"message": "RAG API attiva. Usa /ingest e /chat per interagire."}
