from ...retriever.core import search
from ...llm import llm
from ...guard import ensure_in_scope
from ...scoring import compute_confidence, predict_negotiation_impact
from ...audit import log_usage

def run(request: str = "riassumi feedback clienti") -> dict:
    hits = search(request, skill="cx_insights", top_k=8)
    ctx = [h if isinstance(h, dict) else {"chunk_id": h[0], "text": h[1], "metadata": h[2], "score": h[3]} for h in hits]
    scores = [c["score"] for c in ctx]
    context_str = "\n\n".join([f"[{c['chunk_id']}] {c['text'][:450]}" for c in ctx])

    status, _ = ensure_in_scope(request, ["cx"], scores)
    conf = compute_confidence(scores, context_str, request)

    if status != "ok":
        ans = "FUORI AMBITO: non trovo le informazioni nel materiale fornito"
        impact = predict_negotiation_impact("cx_insights", ans, context_str, conf["overall"])
        log_usage(skill="cx_insights", user_input=request, status=status, confidence=conf,
                  evidence=[c["chunk_id"] for c in ctx], response_preview=ans, predicted_impact=impact)
        return {"status": status, "confidence": conf, "insights": ans, "evidence": [c["chunk_id"] for c in ctx]}

    system = open("at_mind/prompts/system.it.txt", encoding="utf-8").read()
    user = (
        "Contesto CX:\n" + context_str + "\n"
        "Estrai in modo sintetico 3 temi principali con 1 evidenza ciascuno (ID [doc#chunk]). "
        "Stile: professionale e gentile; breve e operativo."
    )
    insights = llm.generate(system_prompt=system, user_prompt=user)

    impact = predict_negotiation_impact("cx_insights", insights, context_str, conf["overall"])
    log_usage(skill="cx_insights", user_input=request, status="ok", confidence=conf,
              evidence=[c["chunk_id"] for c in ctx], response_preview=insights, predicted_impact=impact)
    return {"status": "ok", "confidence": conf, "insights": insights, "evidence": [c["chunk_id"] for c in ctx]}
