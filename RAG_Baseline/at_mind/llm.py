import os
import requests

OPENAI_API_BASE = os.getenv("OPENAI_API_BASE", "http://localhost:8000/v1")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "not-needed") 
MODEL_ID        = os.getenv("LLM_MODEL", "llama-3.2-3b-instruct")
TEMPERATURE     = float(os.getenv("LLM_TEMPERATURE", "0.2"))
MAX_TOKENS      = int(os.getenv("LLM_MAX_TOKENS", "1024"))
TIMEOUT         = int(os.getenv("LLM_TIMEOUT", "60"))

HEADERS = {
    "Authorization": f"Bearer {OPENAI_API_KEY}",
    "Content-Type": "application/json",
}

class VLLMClient:
    """Minimal OpenAI-compatible client for vLLM."""
    def __init__(self):
        self.base = OPENAI_API_BASE
        self.model = MODEL_ID
        self.temperature = TEMPERATURE
        self.max_tokens = MAX_TOKENS
        self.timeout = TIMEOUT

    def generate(self, system_prompt: str, user_prompt: str) -> str:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": user_prompt})

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
        }
        resp = requests.post(
            f"{self.base}/chat/completions",
            headers=HEADERS,
            json=payload,
            timeout=self.timeout,
        )
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"]

llm = VLLMClient()
