from typing import Dict


def infer_collection(doc_id: str) -> str:

if doc_id.startswith("pricing/"):
return "pricing"
if doc_id.startswith("product/"):
return "product"
if doc_id.startswith("process/"):
return "process"
if doc_id.startswith("training/"):
return "training"
if doc_id.startswith("brand/"):
return "brand"
if doc_id.startswith("cx/"):
return "cx"
if doc_id.startswith("interactions/"):
return "interactions"
return "general"


def attach_metadata(chunk: Dict) -> Dict:
coll = infer_collection(chunk["doc_id"])
chunk["metadata"] = {
"collection": coll,
"language": "it",
"title": chunk.get("title", ""),
}
return chunk
