import re

SPORT_TERMS = [
    "partita", "gol", "champions", "serie a", "calcio",
    "nba", "formula 1", "motogp", "mondiali", "olimpiadi", "score"
]
OTHER_BLOCKED = [
    "politica", "governo", "elezioni", "diagnosi", "malattia",
    "virus", "covid", "contenuti per adulti", "religione"
]

def hard_block(user_text: str) -> str | None:
    """
    Controlla se il testo contiene parole chiave vietate.
    Se sì, ritorna un messaggio d’errore; altrimenti None.
    """
    text = user_text.lower()

    # Cerca termini sportivi o non pertinenti
    for term in SPORT_TERMS + OTHER_BLOCKED:
        if re.search(rf"\b{term}\b", text):
            return (
                "Posso solo fornire insight legati alle **vendite e ai clienti**. "
                "Richieste su sport o altri argomenti non commerciali non sono consentite."
            )
    return None
