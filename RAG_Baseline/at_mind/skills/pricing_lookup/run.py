import json
from ...retriever.core import search
from ...llm import llm
from ...guard import ensure_in_scope
from ...scoring import compute_confidence, predict_negotiation_impact
from ...audit import log_usage

def run(query: str) -> dict:
    hits = search(query, skill="pricing_lookup", top_k=6)

    ctx = [
        h if isinstance(h, dict) else {"chunk_id": h[0], "text": h[1], "metadata": h[2], "score": h[3]}
        for h in hits
    ]
    scores = [c["score"] for c in ctx]
    context_str = "\n\n".join([f"[{c['chunk_id']}] {c['text'][:500]}" for c in ctx])

    status, _ = ensure_in_scope(query, ["pricing"], scores)
    conf = compute_confidence(scores, context_str, query)

    if status != "ok":
        ans = {
            "price": None, "currency": "EUR", "promo": None, "apr": None, "months": None,
            "valid_from": None, "valid_to": None, "evidence": [c["chunk_id"] for c in ctx]
        }
        impact = predict_negotiation_impact("pricing_lookup", json.dumps(ans), context_str, conf["overall"])
        log_usage(skill="pricing_lookup", user_input=query, status=status, confidence=conf,
                  evidence=ans["evidence"], response_preview=json.dumps(ans), predicted_impact=impact)
        return {"status": status, "confidence": conf, "result": ans}


    system = open("at_mind/prompts/system.it.txt", encoding="utf-8").read()
    user = (
        f"Query: {query}\nContesto:\n{context_str}\n"
        "Rispondi SOLO in JSON con chiavi: price, currency, promo, apr, months, valid_from, valid_to, evidence (array di ID [doc#chunk]). "
        "Stile: professionale e gentile; sintetico."
    )


    try:
        raw = llm.generate(system_prompt=system, user_prompt=user, json_mode=True) 
    except TypeError:
        raw = llm.generate(system_prompt=system, user_prompt=user) 

    try:
        data = json.loads(raw)
    except Exception:
        data = {}

    result = {
        "price": data.get("price"),
        "currency": data.get("currency", "EUR"),
        "promo": data.get("promo"),
        "apr": data.get("apr"),
        "months": data.get("months"),
        "valid_from": data.get("valid_from"),
        "valid_to": data.get("valid_to"),
        "evidence": data.get("evidence", [c["chunk_id"] for c in ctx[:3]])
    }

    impact = predict_negotiation_impact("pricing_lookup", json.dumps(result), context_str, conf["overall"])
    log_usage(skill="pricing_lookup", user_input=query, status="ok", confidence=conf,
              evidence=result["evidence"], response_preview=json.dumps(result), predicted_impact=impact)

    return {"status": "ok", "confidence": conf, "result": result}
