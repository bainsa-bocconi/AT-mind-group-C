from typing import Dict, List
from ..ingest.index import load_index


DEFAULT_TOPK = 8


COLL_BOOSTS = {
"contract": ["pricing", "product", "process", "brand"],
"policy_qa": ["process", "training"],
"pricing_lookup": ["pricing"],
"product_qa": ["product"],
"tone_writer": ["brand", "training"],
"objections": ["training", "interactions", "cx"],
"cx_insights": ["cx"],
}


def search(query: str, skill: str, top_k: int = DEFAULT_TOPK) -> List[Dict]:
idx = load_index()
filters = None
if skill in COLL_BOOSTS:
filters = {"collection": COLL_BOOSTS[skill]}
hits = idx.search(query, top_k=top_k, filters=filters)
results = []
for cid, text, meta, score in hits:
results.append({
"chunk_id": cid,
"text": text,
"metadata": meta,
"score": score,
})
return results
