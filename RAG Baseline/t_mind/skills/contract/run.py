import json
from pathlib import Path
from typing import Dict
from ...retriever.core import search
from ...llm import llm


TEMPLATE = Path("at_mind/contracts/templates/vehicle_purchase_v1.md").read_text(encoding="utf-8")


def _render_template(template: str, data: Dict) -> str:

out = template
def rep(key_path: str, default: str = ""):
keys = key_path.split('.')
cur = data
for k in keys:
cur = cur.get(k, {}) if isinstance(cur, dict) else {}
return str(cur) if cur else default

out = out.replace("{{customer.full_name}}", rep("customer.full_name"))
out = out.replace("{{customer.email}}", rep("customer.email"))
out = out.replace("{{customer.phone}}", rep("customer.phone"))
out = out.replace("{{meta.contract_date}}", rep("meta.contract_date"))
out = out.replace("{{vehicle.make}}", rep("vehicle.make"))
out = out.replace("{{vehicle.model}}", rep("vehicle.model"))
out = out.replace("{{vehicle.version}}", rep("vehicle.version"))
out = out.replace("{{vehicle.year}}", rep("vehicle.year"))
out = out.replace("{{pricing.list_price}}", rep("pricing.list_price"))
out = out.replace("{{pricing.discounts}}", rep("pricing.discounts"))
out = out.replace("{{pricing.trade_in_value}}", rep("pricing.trade_in_value"))
out = out.replace("{{pricing.extras}}", rep("pricing.extras"))
out = out.replace("{{finance.plan_name}}", rep("finance.plan_name"))
out = out.replace("{{finance.apr}}", rep("finance.apr"))
out = out.replace("{{finance.months}}", rep("finance.months"))
out = out.replace("{{warranty.name}}", rep("warranty.name"))
out = out.replace("{{warranty.months}}", rep("warranty.months"))
return out


def run(quote: Dict) -> Dict:
q = f"{quote['vehicle']['make']} {quote['vehicle']['model']} {quote['vehicle']['version']} financing {quote['finance']['months']} apr {quote['finance']['apr']} garanzia {quote['warranty']['months']}"
ctx = search(q, skill="contract", top_k=8)
context_str = "\n\n".join([f"[{c['chunk_id']}] {c['text'][:400]}" for c in ctx])


user_prompt = f"CONTESTO:\n{context_str}\n\nQUOTE:\n{json.dumps(quote, ensure_ascii=False)}\n\nRICHIESTA: produce special_terms e legal_block."
out = llm.generate(system_prompt="", user_prompt=user_prompt)


result = {
"special_terms": "(demo) Vedi promozione Panda 2023 e condizioni finanziamento.",
"legal_block": "(demo) Clausole standard su recesso, consegna, garanzia.",
"placeholders_missing": []
}


md = _render_template(TEMPLATE, {**quote, **result})
return {
"contract_markdown": md,
"evidence": [c["chunk_id"] for c in ctx],
}
