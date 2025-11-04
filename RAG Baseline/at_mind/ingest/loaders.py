from pathlib import Path
from typing import List, Dict


SUPPORTED_EXT = {".md", ".txt"}


def load_documents(src: Path) -> List[Dict]:
docs = []
for p in src.rglob("*"):
if p.is_file() and p.suffix.lower() in SUPPORTED_EXT:
text = p.read_text(encoding="utf-8", errors="ignore")
docs.append({
"doc_id": p.relative_to(src).as_posix(),
"title": p.stem,
"text": text,
"path": str(p),
})
return docs
