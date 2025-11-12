import json, os, time, hashlib
from pathlib import Path
from typing import Dict, List, Optional

LOG_DIR = Path(os.getenv("AT_MIND_LOG_DIR", "logs"))
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOG_DIR / "usage.log.jsonl"

def _hash(s: str) -> str:
    return hashlib.sha256((s or "").encode("utf-8")).hexdigest()

def log_usage(
    *,
    skill: str,
    user_input: str,
    status: str,
    confidence: Dict,
    evidence: List[str],
    response_preview: str,
    predicted_impact: Dict,
    extra: Optional[Dict] = None
) -> None:
    rec = {
        "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "skill": skill,
        "status": status,
        "confidence": confidence,
        "evidence": evidence,
        "resp_len": len(response_preview or ""),
        "resp_hash": _hash(response_preview),
        "input_hash": _hash(user_input),
        "predicted_impact": predicted_impact,
        "extra": extra or {}
    }
    with LOG_FILE.open("a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")
