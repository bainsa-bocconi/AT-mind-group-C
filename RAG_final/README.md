# Sales RAG (RAG_final)

Virtual Assistant with local Llama 3.3-3B.  

## Functions
-Ephemeral RAG on session input (retriever + local FAISS)
-Guardrail: block out-of-scope requests (e.g., sports)
-Dual output: JSON with insights + short Markdown recap
-Metrics: basic retrieval and groundedness

## Structure
- `src/` with `app.py`, `retriever.py`, `guardrails.py`, ecc.
- `requirements.txt`, `.env.example`, `.gitignore`
