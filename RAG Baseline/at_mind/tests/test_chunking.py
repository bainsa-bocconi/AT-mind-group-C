from at_mind.ingest.chunk import chunk_text


def test_chunks_not_empty():
doc = {"doc_id": "training/x.md", "title": "x", "text": "word "*1000}
chunks = chunk_text(doc)
assert len(chunks) > 1
assert all("text" in c and c["text"] for c in chunks)
