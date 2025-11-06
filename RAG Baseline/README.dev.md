```bash
make setup
make ingest
make serve
make pricing
make policy
make product
make tone
make objections
---


## File: `at_mind/__init__.py`


```python
__all__ = []

## Run vLLM (Llama 3.2 3B) and set env

Start vLLM (on the inference box):
```bash
python -m vllm.entrypoints.openai.api_server \
  --model /models/Llama-3.2-3B-Instruct \
  --port 8000
