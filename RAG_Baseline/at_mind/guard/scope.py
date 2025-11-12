import re
from typing import List, Tuple

ALLOWED = [
    "auto","veicoli","modelli","schede tecniche","prezzi","listini","preventivi",
    "finanziamento","tasso","rata","garanzia","assicurazioni",
    "processi di vendita","lead","test drive","consegna",
    "materiali di training","script di vendita","faq",
    "feedback clienti","customer experience","motivi di mancato acquisto",
    "campagne marketing","tono di voce","brand","promozioni","politiche commerciali"
]
BANNED = [
    "consiglio medico","diagnosi","terapia","consiglio legale in tribunale",
    "elezioni","politica di partito","propaganda","armi","attività illegali","contenuti per adulti", "scommesse", "partite sportive"
]

def _norm(s: str) -> str:
    return (s or "").lower()

def _tok(s: str) -> List[str]:
    return re.findall(r"[a-zà-ù0-9]+", _norm(s))

def ensure_in_scope(user_text: str, collections: List[str], topk_scores: List[float]) -> Tuple[str, float]:
    """
    Ritorna: ("ok" | "low_evidence" | "out_of_scope", max_score)
    - out_of_scope se usa keyword vietate o non è dominio automotive e non ci sono hit buoni
    - low_evidence se gli hit sono troppo deboli
    - ok altrimenti
    """
    text = _norm(user_text)
    if any(b in text for b in BANNED):
        return ("out_of_scope", 0.0)

    has_domain = any(tok in ALLOWED for tok in _tok(text))
    max_score = max(topk_scores) if topk_scores else 0.0


    if not has_domain and max_score < 0.10:
        return ("out_of_scope", max_score)


    strong = [s for s in topk_scores if s >= 0.12]
    if len(strong) < 2:
        return ("low_evidence", max_score)

    return ("ok", max_score)
