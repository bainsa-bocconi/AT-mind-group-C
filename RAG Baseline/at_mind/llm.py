from typing import List
from openai import OpenAI
import os

import os, requests

class LlamaCppLLM:
    def __init__(self):
        self.url = os.getenv("LLAMACPP_URL", "http://localhost:8080")
        self.model = os.getenv("LLM_MODEL", "llama-3.2-3b-instruct")
        self.temperature = float(os.getenv("LLM_TEMPERATURE", "0.2"))
        self.max_tokens = int(os.getenv("LLM_MAX_TOKENS", "1024"))
        self.seed = int(os.getenv("LLM_SEED", "42"))
        self.timeout = int(os.getenv("LLM_TIMEOUT", "60"))

    def generate(self, system_prompt: str, user_prompt: str, json_mode: bool = False) -> str:
        headers = {"Content-Type": "application/json"}
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": user_prompt})
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "seed": self.seed,
        }
        if json_mode:
            payload["response_format"] = {"type": "json_object"}
        r = requests.post(f"{self.url}/v1/chat/completions", json=payload, headers=headers, timeout=self.timeout)
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"]

llm = LlamaCppLLM()
