from src.guardrails import hard_block

def test_sport_block():
    text = "Hai visto la partita di Champions?"
    assert hard_block(text) is not None

def test_valid_sales_text():
    text = "Il cliente ha detto che vuole la rata sotto i 300 euro."
    assert hard_block(text) is None
