from ...retriever.core import search
from ...llm import llm


def run(question: str) -> dict:
ctx = search(question, skill="policy_qa", top_k=6)
context_str = "\n\n".join([f"[{c['chunk_id']}] {c['text'][:400]}" for c in ctx])
user_prompt = f"Domanda: {question}\n\nContesto:\n{context_str}\n\nRispondi in 5-8 frasi con passaggi operativi e versioni/validità."
answer = llm.generate(system_prompt="", user_prompt=user_prompt)
return {"answer": answer, "evidence": [c["chunk_id"] for c in ctx]}
