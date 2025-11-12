from ...guard import ensure_in_scope
from ...scoring import compute_confidence, predict_negotiation_impact
from ...audit import log_usage

def run(quote: Dict) -> Dict:
    if "notes" in quote and isinstance(quote["notes"], str):
        quote["notes"] = pii_mask(quote["notes"])

    v = quote.get("vehicle", {}) or {}
    f = quote.get("finance", {}) or {}
    w = quote.get("warranty", {}) or {}
    q = f"{v.get('make','')} {v.get('model','')} {v.get('version','')} financing {f.get('months','')} apr {f.get('apr','')} garanzia {w.get('months','')}"

    hits = search(q, skill="contract", top_k=8)
    ctx = [h if isinstance(h, dict) else {"chunk_id": h[0], "text": h[1], "metadata": h[2], "score": h[3]} for h in hits]
    scores = [c["score"] for c in ctx]
    context_str = "\n\n".join([f"[{c['chunk_id']}] {c['text'][:400]}" for c in ctx])

    status, _ = ensure_in_scope(json.dumps(quote, ensure_ascii=False), ["pricing","product","process","brand"], scores)
    conf = compute_confidence(scores, context_str, json.dumps(quote, ensure_ascii=False))

    if status != "ok":
        impact = predict_negotiation_impact("contract", "FUORI AMBITO", context_str, conf["overall"])
        log_usage(skill="contract", user_input=json.dumps(quote, ensure_ascii=False), status=status,
                  confidence=conf, evidence=[c["chunk_id"] for c in ctx],
                  response_preview="", predicted_impact=impact)
        return {"status": status, "confidence": conf, "contract_markdown": None, "evidence": [c["chunk_id"] for c in ctx]}

    system = open("at_mind/prompts/system.it.txt", encoding="utf-8").read()
    user = (
        "Contesto (fonti RAG con ID):\n" + context_str +
        "\n\nPreventivo (JSON):\n" + json.dumps(quote, ensure_ascii=False) +
        "\n\nCompito: estrai 'special_terms' e 'legal_block'. Rispondi in JSON con chiavi: "
        "special_terms, legal_block, placeholders_missing (array). Stile: professionale e gentile; sintetico e operativo."
    )
    raw = llm.generate(system_prompt=system, user_prompt=user, json_mode=True)
    payload = {"special_terms":"", "legal_block":"", "placeholders_missing":[]}
    try:
        payload.update(json.loads(raw))
    except Exception:
        pass

    md = _render_template(TEMPLATE, {**quote, **payload})
    impact = predict_negotiation_impact("contract", md, context_str, conf["overall"])
    log_usage(skill="contract", user_input=json.dumps(quote, ensure_ascii=False), status="ok",
              confidence=conf, evidence=[c["chunk_id"] for c in ctx],
              response_preview=md, predicted_impact=impact)
    return {"status": "ok", "confidence": conf, "contract_markdown": md, "evidence": [c["chunk_id"] for c in ctx]}
