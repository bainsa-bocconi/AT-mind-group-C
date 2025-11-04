from typing import List
from openai import OpenAI
import os

class OpenAILikeLLM:
    def __init__(self):
        self.client = OpenAI(base_url=os.getenv("OPENAI_API_BASE"), api_key=os.getenv("OPENAI_API_KEY"))
        self.model = os.getenv("LLM_MODEL", "llama-3.2-3b-instruct")
        self.temperature = float(os.getenv("LLM_TEMPERATURE", "0.2"))
        self.max_tokens = int(os.getenv("LLM_MAX_TOKENS", "1024"))

    def generate(self, system_prompt, user_prompt, json_mode=False):
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=self.temperature,
            max_tokens=self.max_tokens,
        )
        return response.choices[0].message.content

llm = OpenAILikeLLM()
