from ...retriever.core import search
from ...llm import llm


def run(brief: str) -> dict:
ctx = search("tono brand " + brief, skill="tone_writer", top_k=6)
context_str = "\n\n".join([f"[{c['chunk_id']}] {c['text'][:400]}" for c in ctx])
user_prompt = f"Brief: {brief}\nContesto brand:\n{context_str}\nRiscrivi nello stile del brand mantenendo cifre e condizioni."
out = llm.generate(system_prompt="", user_prompt=user_prompt)
return {"text": out, "evidence": [c["chunk_id"] for c in ctx]}
