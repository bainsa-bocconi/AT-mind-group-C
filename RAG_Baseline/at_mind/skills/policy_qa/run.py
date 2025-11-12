from ...retriever.core import search
from ...llm import llm
from ...guard import ensure_in_scope
from ...scoring import compute_confidence, predict_negotiation_impact
from ...audit import log_usage

def run(question: str) -> dict:
    hits = search(question, skill="product_qa", top_k=6)
    ctx = [h if isinstance(h, dict) else {"chunk_id": h[0], "text": h[1], "metadata": h[2], "score": h[3]} for h in hits]
    scores = [c["score"] for c in ctx]
    context_str = "\n\n".join([f"[{c['chunk_id']}] {c['text'][:450]}" for c in ctx])

    status, _ = ensure_in_scope(question, ["product"], scores)
    conf = compute_confidence(scores, context_str, question)

    if status != "ok":
        ans = "FUORI AMBITO: non trovo le informazioni nel materiale fornito"
        impact = predict_negotiation_impact("product_qa", ans, context_str, conf["overall"])
        log_usage(skill="product_qa", user_input=question, status=status, confidence=conf,
                  evidence=[c["chunk_id"] for c in ctx], response_preview=ans, predicted_impact=impact)
        return {"status": status, "confidence": conf, "answer": ans, "evidence": [c["chunk_id"] for c in ctx]}

    system = open("at_mind/prompts/system.it.txt", encoding="utf-8").read()
    user = (
        f"Domanda: {question}\nContesto:\n{context_str}\n"
        "Rispondi in modo professionale e gentile, sintetico ma esaustivo (max 5 frasi), con passaggi operativi. Cita [doc#chunk]."
    )
    answer = llm.generate(system_prompt=system, user_prompt=user)

    impact = predict_negotiation_impact("product_qa", answer, context_str, conf["overall"])
    log_usage(skill="product_qa", user_input=question, status="ok", confidence=conf,
              evidence=[c["chunk_id"] for c in ctx], response_preview=answer, predicted_impact=impact)
    return {"status": "ok", "confidence": conf, "answer": answer, "evidence": [c["chunk_id"] for c in ctx]}
