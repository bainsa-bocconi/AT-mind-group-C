from fastapi import FastAPI
from pydantic import BaseModel


from .skills.policy_qa.run import run as run_policy
from .skills.pricing_lookup.run import run as run_pricing
from .skills.product_qa.run import run as run_product
from .skills.tone_writer.run import run as run_tone
from .skills.objections.run import run as run_obj
from .skills.cx_insights.run import run as run_cx
from .skills.contract.run import run as run_contract


app = FastAPI(title="AT Mind RAG Baseline")


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


@app.post("/contract")
async def contract(payload: Quote):
return run_contract(payload.data)
