from ...retriever.core import search
from ...llm import llm


def run(objection: str) -> dict:
ctx = search(objection, skill="objections", top_k=6)
context_str = "\n\n".join([f"[{c['chunk_id']}] {c['text'][:400]}" for c in ctx])
user_prompt = f"Obiezione: {objection}\nContesto:\n{context_str}\nRestituisci: 1) risposta breve; 2) follow-up; 3) alternativa; 4) fonti."
out = llm.generate(system_prompt="", user_prompt=user_prompt)
return {"plan": out, "evidence": [c["chunk_id"] for c in ctx]}
