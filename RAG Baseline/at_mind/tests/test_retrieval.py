from at_mind.ingest.index import InMemoryIndex


def test_search_returns_results():
idx = InMemoryIndex()
idx.upsert([
{"chunk_id": "a#0", "text": "fiat panda promo tasso 3.9%", "metadata": {"collection": "pricing"}},
{"chunk_id": "b#0", "text": "procedura test drive documento identità", "metadata": {"collection": "process"}},
])
hits = idx.search("promo panda", top_k=1, filters={"collection":["pricing"]})
assert len(hits) == 1
