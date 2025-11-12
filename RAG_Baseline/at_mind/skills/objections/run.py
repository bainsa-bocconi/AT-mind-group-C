from ...retriever.core import search
from ...llm import llm
from ...guard import ensure_in_scope
from ...scoring import compute_confidence, predict_negotiation_impact
from ...audit import log_usage

def run(objection: str) -> dict:
    hits = search(objection, skill="objections", top_k=6)
    ctx = [h if isinstance(h, dict) else {"chunk_id": h[0], "text": h[1], "metadata": h[2], "score": h[3]} for h in hits]
    scores = [c["score"] for c in ctx]
    context_str = "\n\n".join([f"[{c['chunk_id']}] {c['text'][:450]}" for c in ctx])

    status, _ = ensure_in_scope(objection, ["training","interactions","cx"], scores)
    conf = compute_confidence(scores, context_str, objection)

    if status != "ok":
        ans = "FUORI AMBITO: non trovo le informazioni nel materiale fornito"
        impact = predict_negotiation_impact("objections", ans, context_str, conf["overall"])
        log_usage(skill="objections", user_input=objection, status=status, confidence=conf,
                  evidence=[c["chunk_id"] for c in ctx], response_preview=ans, predicted_impact=impact)
        return {"status": status, "confidence": conf, "plan": ans, "evidence": [c["chunk_id"] for c in ctx]}

    system = open("at_mind/prompts/system.it.txt", encoding="utf-8").read()
    user = (
        f"Obiezione: {objection}\nContesto:\n{context_str}\n"
        "Restituisci 1) risposta breve al cliente; 2) domanda di follow-up; 3) proposta alternativa; 4) fonti [doc#chunk]. "
        "Stile: professionale e gentile, sintetico e operativo."
    )
    plan = llm.generate(system_prompt=system, user_prompt=user)

    impact = predict_negotiation_impact("objections", plan, context_str, conf["overall"])
    log_usage(skill="objections", user_input=objection, status="ok", confidence=conf,
              evidence=[c["chunk_id"] for c in ctx], response_preview=plan, predicted_impact=impact)
    return {"status": "ok", "confidence": conf, "plan": plan, "evidence": [c["chunk_id"] for c in ctx]}
