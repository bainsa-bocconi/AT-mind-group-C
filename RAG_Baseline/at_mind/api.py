
from typing import Optional
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel


from .skills.policy_qa.run import run as run_policy
from .skills.pricing_lookup.run import run as run_pricing
from .skills.product_qa.run import run as run_product
from .skills.tone_writer.run import run as run_tone
from .skills.objections.run import run as run_obj
from .skills.cx_insights.run import run as run_cx
from .skills.contract.run import run as run_contract


from .retriever.core import search as rag_search

app = FastAPI(title="AT Mind RAG Baseline")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],      
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Question(BaseModel):
    question: str

class Query(BaseModel):
    query: str

class Brief(BaseModel):
    brief: str

class Objection(BaseModel):
    objection: str

class Quote(BaseModel):
    data: dict  


@app.get("/health")
async def health():
    return {"ok": True}


@app.post("/policy_qa")
async def policy(payload: Question):
    return run_policy(payload.question)

@app.post("/pricing_lookup")
async def pricing(payload: Query):
    return run_pricing(payload.query)

@app.post("/product_qa")
async def product(payload: Question):
    return run_product(payload.question)

@app.post("/tone_writer")
async def tone(payload: Brief):
    return run_tone(payload.brief)

@app.post("/objections")
async def objections(payload: Objection):
    return run_obj(payload.objection)

@app.post("/cx_insights")
async def cx_insights():
    return run_cx()

@app.post("/contract")
async def contract(payload: Quote):
    return run_contract(payload.data)


class SearchUI(BaseModel):
    query: str
    skill: str = "product_qa"
    top_k: int = 8

@app.post("/ui/retrieval")
async def ui_retrieval(payload: SearchUI):
    hits = rag_search(payload.query, payload.skill, payload.top_k)
    return {
        "query": payload.query,
        "skill": payload.skill,
        "retrieval": [
            {
                "id": h["chunk_id"],
                "score": h["score"],
                "norm_score": h.get("norm_score", 0.0),
                "collection": h["metadata"].get("collection"),
                "title": h["metadata"].get("title"),
                "preview": h.get("preview", h["text"][:280]),
            }
            for h in hits
        ],
    }


class RunUI(BaseModel):
    
    skill: str
    
    query: Optional[str] = None        
    question: Optional[str] = None     
    brief: Optional[str] = None        
    objection: Optional[str] = None    
    data: Optional[dict] = None        
    top_k: int = 8

@app.post("/ui/run")
async def ui_run(payload: RunUI):
    """
    Unified endpoint:
    - Accepts the input for any skill
    - Calls the corresponding skill (which produces the final output)
    - Also returns a retrieval trace for the UI (top-K evidence with scores + previews)
    """
    s = payload.skill

    
    if s == "pricing_lookup":
        body = payload.query or ""
        result = run_pricing(body)
        q_for_retrieval = body
    elif s == "policy_qa":
        body = payload.question or ""
        result = run_policy(body)
        q_for_retrieval = body
    elif s == "product_qa":
        body = payload.question or ""
        result = run_product(body)
        q_for_retrieval = body
    elif s == "tone_writer":
        body = payload.brief or ""
        result = run_tone(body)
        q_for_retrieval = "tono brand " + body
    elif s == "objections":
        body = payload.objection or ""
        result = run_obj(body)
        q_for_retrieval = body
    elif s == "cx_insights":
        result = run_cx()
        q_for_retrieval = "riassumi feedback clienti"
    elif s == "contract":
        body = payload.data or {}
        result = run_contract(body)
        q_for_retrieval = "contract context"
    else:
        return {"error": f"unknown skill: {s}"}

   
    skill_for_trace = s
    hits = rag_search(q_for_retrieval, skill_for_trace, payload.top_k)
    trace = [
        {
            "id": h["chunk_id"],
            "score": h["score"],
            "norm_score": h.get("norm_score", 0.0),
            "collection": h["metadata"].get("collection"),
            "title": h["metadata"].get("title"),
            "preview": h.get("preview", h["text"][:280]),
        }
        for h in hits
    ]

    return {
        "skill": s,
        "input": {
            "query": payload.query,
            "question": payload.question,
            "brief": payload.brief,
            "objection": payload.objection,
            "data": payload.data,
        },
        "result": result,    
        "retrieval": trace,   
    }
