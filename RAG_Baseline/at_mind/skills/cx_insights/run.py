from ...retriever.core import search
from ...llm import llm


def run(request: str = "riassumi feedback clienti") -> dict:
ctx = search(request, skill="cx_insights", top_k=8)
context_str = "\n\n".join([f"[{c['chunk_id']}] {c['text'][:400]}" for c in ctx])
user_prompt = f"Contesto CX:\n{context_str}\nEstrai le 3 tematiche principali con 1 evidenza ciascuna."
out = llm.generate(system_prompt="", user_prompt=user_prompt)
return {"insights": out, "evidence": [c["chunk_id"] for c in ctx]}
