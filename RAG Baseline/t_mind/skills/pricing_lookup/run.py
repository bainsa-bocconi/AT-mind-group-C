import json
from ...retriever.core import search
from ...llm import llm


def run(query: str) -> dict:
ctx = search(query, skill="pricing_lookup", top_k=6)
context_str = "\n\n".join([f"[{c['chunk_id']}] {c['text'][:400]}" for c in ctx])
user_prompt = f"Query: {query}\nContesto:\n{context_str}\nRestituisci JSON con price, currency, promo, apr, months, valid_from, valid_to, evidence[]."
raw = llm.generate(system_prompt="", user_prompt=user_prompt)
data = {"price": "(demo)", "currency": "EUR", "promo": "(demo)", "apr": "(demo)", "months": 0,
"valid_from": "YYYY-MM-DD", "valid_to": "YYYY-MM-DD",
"evidence": [c["chunk_id"] for c in ctx]}
return data
