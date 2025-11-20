from __future__ import annotations
from typing import List, Literal
from pydantic import BaseModel, Field, field_validator, ValidationError
import json
import re


Owner = Literal["rep", "manager"]
Priority = Literal["high", "med", "low"]


class NextBestAction(BaseModel):
    action: str = Field(..., min_length=2, description="Cosa fare")
    why: str = Field(..., min_length=2, description="Perché farlo (collega a obiezione/rischio)")
    owner: Owner
    priority: Priority


class InsightsPayload(BaseModel):
    lead_summary: str = Field(..., min_length=2)
    deal_risks: List[str] = Field(default_factory=list)
    objections: List[str] = Field(default_factory=list)
    confidence_contract_within_14d: int = Field(..., ge=0, le=100)
    next_best_actions: List[NextBestAction] = Field(default_factory=list)
    upsell_cross_sell: List[str] = Field(default_factory=list)
    missing_info_to_ask: List[str] = Field(default_factory=list)
    citations: List[int] = Field(default_factory=list)

    @field_validator("deal_risks", "objections", "upsell_cross_sell", "missing_info_to_ask")
    @classmethod
    def strip_items(cls, v: List[str]) -> List[str]:
        return [s.strip() for s in v if isinstance(s, str) and s.strip()]

    @field_validator("citations")
    @classmethod
    def non_negative_citations(cls, v: List[int]) -> List[int]:
        for i in v:
            if i < 0:
                raise ValueError("Gli ID in citations devono essere >= 0")
        return v



JSON_BLOCK_RE = re.compile(
    r"```(?:json)?\s*(\{.*?\})\s*```",
    flags=re.DOTALL | re.IGNORECASE,
)

def extract_json_block(text: str) -> str | None:
    """
    1) Cerca un blocco ```json ...```
    2) Altrimenti prova a prendere la prima grande {...} bilanciata
    """
    m = JSON_BLOCK_RE.search(text)
    if m:
        return m.group(1).strip()

    
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        return text[start:end+1].strip()
    return None


def parse_and_validate_insights(text: str) -> InsightsPayload:
    """
    Estrae JSON dal testo del modello e valida con Pydantic.
    Lancia ValidationError se non conforme.
    """
    blob = extract_json_block(text)
    if not blob:
        raise ValidationError.from_exception_data(
            "InsightsPayload",
            [{"loc": ("__root__",), "msg": "JSON non trovato nell'output del modello", "type": "value_error"}],
        )
    data = json.loads(blob)
    return InsightsPayload(**data)
