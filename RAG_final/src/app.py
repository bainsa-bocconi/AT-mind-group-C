from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app = FastAPI(title="Sales RAG (Llama 3.3-3B)")

@app.get("/")
def root():
    return {"message": "RAG API attiva. Usa /ingest e /chat per interagire."}
