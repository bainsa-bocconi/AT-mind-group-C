from ...retriever.core import search
from ...llm import llm
from ...guard import ensure_in_scope
from ...scoring import compute_confidence, predict_negotiation_impact
from ...audit import log_usage

def run(brief: str) -> dict:
    hits = search("tono brand " + brief, skill="tone_writer", top_k=6)
    ctx = [h if isinstance(h, dict) else {"chunk_id": h[0], "text": h[1], "metadata": h[2], "score": h[3]} for h in hits]
    scores = [c["score"] for c in ctx]
    context_str = "\n\n".join([f"[{c['chunk_id']}] {c['text'][:450]}" for c in ctx])

    status, _ = ensure_in_scope(brief, ["brand","training"], scores)
    conf = compute_confidence(scores, context_str, brief)

    if status != "ok":
        ans = "FUORI AMBITO: non trovo le informazioni nel materiale fornito"
        impact = predict_negotiation_impact("tone_writer", ans, context_str, conf["overall"])
        log_usage(skill="tone_writer", user_input=brief, status=status, confidence=conf,
                  evidence=[c["chunk_id"] for c in ctx], response_preview=ans, predicted_impact=impact)
        return {"status": status, "confidence": conf, "text": ans, "evidence": [c["chunk_id"] for c in ctx]}

    system = open("at_mind/prompts/system.it.txt", encoding="utf-8").read()
    user = (
        f"Brief: {brief}\nContesto brand:\n{context_str}\n"
        "Riscrivi il testo con tono professionale e gentile, chiaro e breve (max 5 frasi), mantenendo cifre/condizioni identiche."
    )
    text = llm.generate(system_prompt=system, user_prompt=user)

    impact = predict_negotiation_impact("tone_writer", text, context_str, conf["overall"])
    log_usage(skill="tone_writer", user_input=brief, status="ok", confidence=conf,
              evidence=[c["chunk_id"] for c in ctx], response_preview=text, predicted_impact=impact)
    return {"status": "ok", "confidence": conf, "text": text, "evidence": [c["chunk_id"] for c in ctx]}
