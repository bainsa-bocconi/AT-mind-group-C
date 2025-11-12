from typing import Dict

FOLDER_TO_COLLECTION = {
    "pricing": "pricing", "listini": "pricing", "promozioni": "pricing", "promo": "pricing",
    "product": "product", "schede": "product", "brochure": "product",
    "process": "process", "policy": "process", "procedure": "process",
    "training": "training", "faq": "training", "scripts": "training",
    "brand": "brand", "marketing": "brand", "tone": "brand",
    "cx": "cx", "feedback": "cx", "survey": "cx",
    "interactions": "interactions", "chat": "interactions", "trascrizioni": "interactions",
}

KEYWORDS_TO_COLLECTION = {
    "apr": "pricing", "tan": "pricing", "rata": "pricing", "finanziamento": "pricing", "garanzia": "pricing",
    "scheda": "product", "motore": "product", "versione": "product",
    "policy": "process", "procedura": "process", "test drive": "process",
    "script": "training", "obiezioni": "training", "faq": "training",
    "tono": "brand", "linee guida": "brand", "brand": "brand",
    "feedback": "cx", "soddisfazione": "cx", "mancato acquisto": "cx",
    "chat": "interactions", "trascrizione": "interactions"
}

def infer_collection(doc_id: str) -> str:
    path_lower = doc_id.lower()
    top = path_lower.split("/", 1)[0]
    if top in FOLDER_TO_COLLECTION:
        return FOLDER_TO_COLLECTION[top]
    for kw, coll in KEYWORDS_TO_COLLECTION.items():
        if kw in path_lower:
            return coll
    return "general"

def attach_metadata(chunk: Dict) -> Dict:
    coll = infer_collection(chunk["doc_id"])
    chunk["metadata"] = {
        "collection": coll,
        "language": "it",
        "title": chunk.get("title", ""),
    }
    return chunk
