from src.retriever import EphemeralStore
import json, statistics

def eval_local(dataset_path="tests/fixtures/eval_set.json"):
    """
    Valuta precision@6, recall@6 e hit@6 su un piccolo set locale.
    """
    ds = json.load(open(dataset_path))
    store = EphemeralStore()
    for d in ds["docs"]:
        store.add_docs([d["text"]])

    results = []
    for q in ds["queries"]:
        hits = store.retrieve(q["question"], k=6)
        got = {i for _, _, i in hits}
        gold = set(q["gold_citations"])
        prec = len(got & gold) / max(1, len(got))
        rec = len(got & gold) / max(1, len(gold))
        results.append((prec, rec))

    return {
        "precision@6": round(statistics.mean(p for p, _ in results), 3),
        "recall@6": round(statistics.mean(r for _, r in results), 3),
        "hit@6": sum(1 for p, r in results if r > 0) / len(results)
    }
