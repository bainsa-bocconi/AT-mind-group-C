from typing import Dict, List
import regex as re

def _coverage(query: str, context: str) -> float:
    tok = lambda s: set(re.findall(r"[\p{L}\p{N}]+", (s or "").lower()))
    q, c = tok(query), tok(context)
    return 0.0 if not q else len(q & c) / max(1, len(q))

def compute_confidence(retrieval_scores: List[float], context_text: str, query: str) -> Dict:
    max_s = max(retrieval_scores) if retrieval_scores else 0.0
    margin = 0.0
    if len(retrieval_scores) >= 2:
        margin = max(0.0, retrieval_scores[0] - retrieval_scores[1])
    cov = _coverage(query, context_text)
    overall = 0.5*max_s + 0.2*margin + 0.3*cov
    return {
        "retrieval_score": round(max_s, 3),
        "retrieval_margin": round(margin, 3),
        "coverage": round(cov, 3),
        "overall": round(100*max(0.0, min(1.0, overall)), 1)
    }

def predict_negotiation_impact(skill: str, answer_text: str, context_text: str, confidence_overall: float) -> Dict:
    t = (answer_text or "").lower()
    ctx = (context_text or "").lower()
    bonus = 0
    if any(k in t or k in ctx for k in ["promo","promozione","tan","apr","36 mesi","garanzia","rata"]):
        bonus += 15
    if any(k in t for k in ["contattaci","prenota","ti propongo","passi","step","procedi","firma","appuntamento","test drive"]):
        bonus += 10
    base = confidence_overall/2.0
    score = max(0.0, min(100.0, round(base + bonus, 1)))
    band = "alto" if score >= 70 else ("medio" if score >= 40 else "basso")
    return {"predicted_impact_score": score, "band": band}
