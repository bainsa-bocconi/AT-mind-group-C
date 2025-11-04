from ...retriever.core import search
from ...llm import llm


def run(question: str) -> dict:
ctx = search(question, skill="product_qa", top_k=6)
context_str = "\n\n".join([f"[{c['chunk_id']}] {c['text'][:400]}" for c in ctx])
user_prompt = f"Domanda: {question}\nContesto:\n{context_str}\nRispondi in max 5 frasi citando [doc#chunk]."
answer = llm.generate(system_prompt="", user_prompt=user_prompt)
return {"answer": answer, "evidence": [c["chunk_id"] for c in ctx]}
