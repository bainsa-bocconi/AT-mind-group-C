from pathlib import Path
from typing import List, Dict

SUPPORTED_EXT = {".md", ".txt", ".csv", ".pdf"}

def _csv_to_text(path: Path) -> str:
    try:
        import pandas as pd
        df = pd.read_csv(path)
        head = df.head(100).to_string(index=False)
        return f"CSV: {path.name}\n{head}"
    except Exception:
        import csv
        rows = []
        with path.open(encoding="utf-8", errors="ignore") as f:
            for i, row in enumerate(csv.reader(f)):
                rows.append(", ".join(row))
                if i >= 100: break
        return f"CSV: {path.name}\n" + "\n".join(rows)

def _pdf_to_text(path: Path) -> str:
    try:
        from pypdf import PdfReader
        reader = PdfReader(str(path))
        pages = []
        for i, p in enumerate(reader.pages):
            if i >= 30:
                break
            pages.append(p.extract_text() or "")
        return f"PDF: {path.name}\n" + "\n\n".join(pages)
    except Exception as e:
        return f"PDF: {path.name}\n(estrazione testo non riuscita: {e})"

def load_documents(src: Path) -> List[Dict]:
    docs = []
    for p in src.rglob("*"):
        if p.is_file() and p.suffix.lower() in SUPPORTED_EXT:
            if p.suffix.lower() == ".csv":
                text = _csv_to_text(p)
            elif p.suffix.lower() == ".pdf":
                text = _pdf_to_text(p)
            else:
                text = p.read_text(encoding="utf-8", errors="ignore")
            docs.append({
                "doc_id": p.relative_to(src).as_posix(),
                "title": p.stem,
                "text": text,
                "path": str(p),
            })
    return docs
