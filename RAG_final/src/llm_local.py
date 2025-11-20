import os
import requests



BASE_URL = os.getenv("LLM_BASE_URL", "http://localhost:8001")


def generate(messages, temperature: float = 0.2, max_tokens: int = 700) -> str:
    """
    Invia una chat request al modello Llama locale (vLLM o llama.cpp server compatibile OpenAI).
    messages: lista di dizionari [{'role': 'system'|'user'|'assistant', 'content': '...'}]
    """
    payload = {
        "model": "local",
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens
    }

    try:
        response = requests.post(f"{BASE_URL}/v1/chat/completions", json=payload, timeout=120)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except requests.exceptions.RequestException as e:
        return f"⚠️ Errore nel contattare il modello locale: {e}"
