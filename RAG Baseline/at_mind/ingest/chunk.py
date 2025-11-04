from typing import List, Dict


MAX_TOKENS = 750
OVERLAP = 120
def _split_words(text: str) -> List[str]:
return text.split()


def chunk_text(doc: Dict) -> List[Dict]:
words = _split_words(doc["text"])
chunks = []
start = 0
idx = 0
while start < len(words):
end = min(start + MAX_TOKENS, len(words))
chunk_words = words[start:end]
chunk_text = " ".join(chunk_words)
chunks.append({
"doc_id": doc["doc_id"],
"title": doc.get("title", ""),
"text": chunk_text,
"chunk_id": f"{doc['doc_id']}#chunk{idx}",
})
idx += 1
start = end - OVERLAP
if start < 0:
start = 0
if end == len(words):
break
return chunks
