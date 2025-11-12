import json
from pathlib import Path
from typing import Dict
from ...pii.redact import mask as pii_mask
from ...retriever.core import search
from ...llm import llm

TEMPLATE = Path("at_mind/contracts/templates/vehicle_purchase_v1.md").read_text(encoding="utf-8")

def _render_template(template: str, data: Dict) -> str:
    def get(path, default=""):
        cur = data
        for k in path.split("."):
            cur = cur.get(k, {}) if isinstance(cur, dict) else {}
        if isinstance(cur, list):
            return ", ".join(map(str, cur))
        return str(cur) if cur else default

    customer_full = get("customer.full_name", "")
    customer_email = get("customer.email", "")
    customer_phone = get("customer.phone", "")


    if customer_email:
        customer_email = pii_mask(customer_email)
    if customer_phone:
        customer_phone = pii_mask(customer_phone)

    mapping = {
        "customer.full_name": customer_full,
        "customer.email": customer_email,
        "customer.phone": customer_phone,
        "meta.contract_date": get("meta.contract_date"),
        "vehicle.make": get("vehicle.make"),
        "vehicle.model": get("vehicle.model"),
        "vehicle.version": get("vehicle.version"),
        "vehicle.year": get("vehicle.year"),
        "pricing.list_price": get("pricing.list_price"),
        "pricing.discounts": get("pricing.discounts"),
        "pricing.trade_in_value": get("pricing.trade_in_value"),
        "pricing.extras": get("pricing.extras"),
        "finance.plan_name": get("finance.plan_name"),
        "finance.apr": get("finance.apr"),
        "finance.months": get("finance.months"),
        "warranty.name": get("warranty.name"),
        "warranty.months": get("warranty.months"),
        "special_terms": data.get("special_terms", ""),
        "legal_block": data.get("legal_block", ""),
    }

    out = template
    for k, v in mapping.items():
        out = out.replace("{{" + k + "}}", v)


    lines = []
    for line in out.splitlines():
        lstrip = line.strip().lower()
        if lstrip.startswith("cliente:") and not customer_full:
            continue
        if lstrip.startswith("contatto:") and (not customer_email and not customer_phone):
            continue

        if "{{" in line and "}}" in line:
            continue
        lines.append(line)
    return "\n".join(lines)

def run(quote: Dict) -> Dict:

    if "notes" in quote and isinstance(quote["notes"], str):
        quote["notes"] = pii_mask(quote["notes"])


    v = quote.get("vehicle", {}) or {}
    f = quote.get("finance", {}) or {}
    w = quote.get("warranty", {}) or {}

    q = f"{v.get('make','')} {v.get('model','')} {v.get('version','')} financing {f.get('months','')} apr {f.get('apr','')} garanzia {w.get('months','')}"
    ctx = search(q, skill="contract", top_k=8)
    context_str = "\n\n".join([f"[{c['chunk_id']}] {c['text'][:400]}" for c in ctx])

    user_prompt = (
        "CONTESTO:\n" + context_str +
        "\n\nQUOTE:\n" + json.dumps(quote, ensure_ascii=False) +
        "\n\nRICHIESTA: produce special_terms e legal_block in modo conciso e operativo."
    )
    _ = llm.generate(system_prompt="", user_prompt=user_prompt)


    result = {
        "special_terms": "(demo) Vedi promozione e condizioni di finanziamento applicabili.",
        "legal_block": "(demo) Clausole standard su recesso, consegna, garanzia.",
        "placeholders_missing": []
    }

    md = _render_template(TEMPLATE, {**quote, **result})
    return {
        "contract_markdown": md,
        "evidence": [c["chunk_id"] for c in ctx],
    }
