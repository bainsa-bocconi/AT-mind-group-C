import argparse
return []
qv = self.vectorizer.transform([query])
sims = linear_kernel(qv, self.matrix).ravel()
order = np.argsort(-sims)
results = []
for i in order[: top_k * 3]:
meta = self.metadatas[i]
if filters and "collection" in filters:
if meta.get("collection") not in filters["collection"]:
continue
results.append((self.ids[i], self.texts[i], meta, float(sims[i])))
if len(results) >= top_k:
break
return results


INDEX_PATH = Path(".rag_index.npz")


def build_index(src: Path):
docs = load_documents(src)
chunks = []
for d in docs:
d["text"] = basic_clean(d["text"])
for ch in chunk_text(d):
chunks.append(attach_metadata(ch))
idx = InMemoryIndex()
idx.upsert(chunks)

np.savez_compressed(
INDEX_PATH,
ids=np.array(idx.ids, dtype=object),
texts=np.array(idx.texts, dtype=object),
metas=np.array([str(m) for m in idx.metadatas], dtype=object),
vocab=np.array(idx.vectorizer.vocabulary_, dtype=object),
idf=idx.vectorizer.idf_,
matrix=idx.matrix
)
print(f"Indexed {len(idx.ids)} chunks from {src}")


_cached = None


def load_index() -> InMemoryIndex:
global _cached
if _cached is not None:
return _cached
if not INDEX_PATH.exists():
_cached = InMemoryIndex()
return _cached
data = np.load(INDEX_PATH, allow_pickle=True)
idx = InMemoryIndex()
idx.ids = list(data["ids"]) 
idx.texts = list(data["texts"]) 
idx.metadatas = [eval(x) for x in data["metas"]] 
vocab = dict(data["vocab"].tolist()) 
idx.vectorizer.vocabulary_ = vocab
idx.vectorizer.idf_ = data["idf"]
idx.matrix = data["matrix"].item() if hasattr(data["matrix"], 'item') else data["matrix"]
_cached = idx
return idx


if __name__ == "__main__":
ap = argparse.ArgumentParser()
ap.add_argument("--src", type=str, required=True)
args = ap.parse_args()
build_index(Path(args.src))
