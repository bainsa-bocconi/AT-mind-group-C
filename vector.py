import os
import json
import ollama
import chromadb
import pandas as pd
from tqdm import tqdm
import numpy as np

# config
DATA_DIR    = "excel_data"
CHROMA_DIR  = "./chroma"
EMBED_MODEL = "mxbai-embed-large"   # you can change to "nomic-embed-text"

RESP_TEXT_COLL  = "excel_respondents_text"   # one doc per respondent (row)
QUEST_TEXT_COLL = "excel_questions_text"     # one doc per question/answer

# helpers

def clean_cat(x: str) -> str:
    """Normalize categorical/text values a bit."""
    return " ".join(str(x).strip().lower().split())


def row_to_text(row: pd.Series) -> str:
    """
    Build a textual representation of a respondent (one row).
    Includes column names to give structure.
    """
    parts = []
    for k, v in row.items():
        if k == "__source__":
            continue
        if pd.isna(v):
            continue

        if isinstance(v, (int, float, np.floating, np.integer)):
            # keep numbers in the text too, with basic explanation
            parts.append(f"{k} is {v}")
        else:
            parts.append(f"{k}: {clean_cat(v)}")

    return " | ".join(parts)


def build_question_doc(col_name: str, value, row: pd.Series) -> str:
    """
    Build a per-question document:
      - question is the column name
      - answer is the cell value
      - plus respondent context (all other fields)
    """
    if isinstance(value, (int, float, np.floating, np.integer)):
        answer_str = f"{value}"
    else:
        answer_str = clean_cat(value)

    # Respondent context (excluding the current question column)
    context_row = row.copy()
    if col_name in context_row:
        context_row = context_row.drop(labels=[col_name])

    context_text = row_to_text(context_row)

    doc = (
        f"Question: {col_name}\n"
        f"Answer: {answer_str}\n"
        f"Respondent context: {context_text}\n"
        f"Source file: {row.get('__source__', 'unknown')}"
    )
    return doc


# chroma batch 

def batch_add(collection, ids, documents, embeddings, metadatas, batch_size: int = 1000):
    """
    Add records to a Chroma collection in safe batches to avoid
    'batch size > max batch size' errors.
    """
    n = len(ids)
    assert n == len(documents) == len(embeddings) == len(metadatas), \
        "ids, documents, embeddings and metadatas must have the same length"

    for start in range(0, n, batch_size):
        end = min(start + batch_size, n)

        batch_ids   = ids[start:end]
        batch_docs  = documents[start:end]
        batch_embs  = embeddings[start:end]
        batch_metas = metadatas[start:end]

        collection.add(
            ids=batch_ids,
            documents=batch_docs,
            embeddings=batch_embs,
            metadatas=batch_metas,
        )


#load excels files 
frames = []
for fn in os.listdir(DATA_DIR):
    if fn.lower().endswith((".xlsx", ".xls")):
        path = os.path.join(DATA_DIR, fn)
        try:
            df = pd.read_excel(path, engine="openpyxl")
            df["__source__"] = fn
            frames.append(df)
        except Exception as e:
            print(f"[WARN] Failed to read {fn}: {e}")

if not frames:
    raise SystemExit("No Excel files found in excel_data/")

DF = pd.concat(frames, ignore_index=True)

import sys

# Allow: python vector.py 0 5000
start = int(sys.argv[1]) if len(sys.argv) > 1 else 0
end   = int(sys.argv[2]) if len(sys.argv) > 2 else len(DF)

# Make sure 'end' doesn't exceed total rows
end = min(end, len(DF))

# Slice the dataframe
DF = DF.iloc[start:end].reset_index(drop=True)

print(f"Processing rows {start} to {end} (total {len(DF)})")


# Identify columns
all_cols = DF.columns.tolist()
non_num_cols = [
    c for c in all_cols
    if c != "__source__" and not pd.api.types.is_numeric_dtype(DF[c])
]

print(f"Loaded {len(DF)} rows.")
print(f"Non-numeric (candidate question) columns: {non_num_cols}")

# setup chroma 

os.makedirs(CHROMA_DIR, exist_ok=True)
client = chromadb.PersistentClient(path=CHROMA_DIR)

resp_text_col  = client.get_or_create_collection(RESP_TEXT_COLL)
quest_text_col = client.get_or_create_collection(QUEST_TEXT_COLL)


# respondednt-embeddings

resp_ids = []
resp_docs = []
resp_embs = []
resp_metas = []

print("\n[Step 1/2] Embedding respondents (per-row)...")

for i, row in tqdm(DF.iterrows(), total=len(DF)):
    rid = f"resp_{i}"
    txt = row_to_text(row)

    if not txt.strip():
        continue

    emb = ollama.embeddings(model=EMBED_MODEL, prompt=txt)["embedding"]

    meta = {"source": row.get("__source__", "unknown")}
    # keep raw numeric values as metadata (useful for filters later)
    for c in all_cols:
        if c in ("__source__",):
            continue
        v = row[c]
        if isinstance(v, (int, float, np.floating, np.integer)) and not pd.isna(v):
            meta[c] = float(v)

    resp_ids.append(rid)
    resp_docs.append(txt)
    resp_embs.append(emb)
    resp_metas.append(meta)

if resp_ids:
    print(f"[Chroma] Writing {len(resp_ids)} respondent embeddings in batches...")
    batch_add(
        collection=resp_text_col,
        ids=resp_ids,
        documents=resp_docs,
        embeddings=resp_embs,
        metadatas=resp_metas,
        batch_size=1000,   # safe value << 5461
    )

print(f"✅ Stored {len(resp_ids)} respondent-level embeddings in '{RESP_TEXT_COLL}'.")


# question embeddings

q_ids = []
q_docs = []
q_embs = []
q_metas = []

print("\n[Step 2/2] Embedding per-question (per row, per non-numeric column)...")

for i, row in tqdm(DF.iterrows(), total=len(DF)):
    source = row.get("__source__", "unknown")

    for col in non_num_cols:
        val = row[col]
        if pd.isna(val):
            continue
        if isinstance(val, str) and not val.strip():
            continue

        qid = f"resp_{i}_q_{col}"
        doc = build_question_doc(col, val, row)

        emb = ollama.embeddings(model=EMBED_MODEL, prompt=doc)["embedding"]

        meta = {
            "source": source,
            "question_col": col,
            "answer": str(val),   # raw answer for filtering/inspection
        }

        q_ids.append(qid)
        q_docs.append(doc)
        q_embs.append(emb)
        q_metas.append(meta)

if q_ids:
    print(f"[Chroma] Writing {len(q_ids)} question embeddings in batches...")
    batch_add(
        collection=quest_text_col,
        ids=q_ids,
        documents=q_docs,
        embeddings=q_embs,
        metadatas=q_metas,
        batch_size=1000,
    )

print(f"✅ Stored {len(q_ids)} question-level embeddings in '{QUEST_TEXT_COLL}'.")

print("\n🎉 Vectorization complete: per-respondent + per-question.")
print("Respondents collection:", RESP_TEXT_COLL)
print("Questions collection:  ", QUEST_TEXT_COLL)


# simple query demo (at the end)

if __name__ == "__main__":
    query = "main reasons for dissatisfaction with assistance"
    print(f"\nExample query: {query}\n")

    # Query respondents
    q_emb = ollama.embeddings(model=EMBED_MODEL, prompt=query)["embedding"]
    resp_res = resp_text_col.query(query_embeddings=[q_emb], n_results=3)
    print("Top respondents:")
    for rid, doc in zip(resp_res["ids"][0], resp_res["documents"][0]):
        print("\nID:", rid)
        print(doc[:400], "...")
        print("-" * 40)

    # Query questions
    quest_res = quest_text_col.query(query_embeddings=[q_emb], n_results=5)
    print("\nTop question/answers:")
    for rid, doc, meta in zip(
        quest_res["ids"][0],
        quest_res["documents"][0],
        quest_res["metadatas"][0],
    ):
        print("\nID:", rid)
        print("Question col:", meta.get("question_col"))
        print("Answer:", meta.get("answer"))
        print("Source:", meta.get("source"))
        print(doc[:400], "...")
        print("-" * 40)
