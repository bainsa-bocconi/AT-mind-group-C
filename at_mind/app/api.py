from fastapi import FastAPI, HTTPException
from vllm import LLM, SamplingParams
import chromadb
from chromadb.utils import embedding_functions
from sentence_transformers import SentenceTransformer
import torch #for GPU check
from dotenv import load_dotenv
import json
#----------------------------------------------------------
from .models import ChatRequest, ChatResponse
from .servicesvllm import init_vllm, call_llama_inference
#-----------------------------------------------------------

app = FastAPI()
init_vllm() # from servicesvllm.py

# ----------load system prompt from another file-------------

def load_sys_prompt():
    with open("systemprompt.md") as f:
        return f.read()
system_prompt = load_sys_prompt()

# ------------------- ChromaDB Setup -----------------------

chroma_client = chromadb.Client()
chroma_collection = chroma_client.get_or_create_collection("dataset") #need to implement this so that leads to the dataset 
embedding_func = embedding_functions.DefaultEmbeddingFunction()

# --------------------app instances-------------------------
    
@app.get("/")
async def root():
    return 0
@app.post("/chat", response_model=ChatResponse)
async def chat(request:ChatRequest):
    llm_output = call_llama_inference(prompt=request.prompt)
    return ChatResponse(
        response=llm_output["response"],
        confidence=llm_output["confidence"],
        reasoning=llm_output["reasoning"]
    )


