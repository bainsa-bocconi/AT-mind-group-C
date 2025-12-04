import os
import requests

BASE_URL = os.getenv("LLM_BASE_URL", "http://localhost:8000")
BASE_URL = "https://unhieratically-exponible-angeles.ngrok-free.dev/v1"

def generate(messages, temperature: float = 0.2, max_tokens: int = 700) -> str:
    payload = {
        "model": "meta-llama/Llama-3.2-3B-Instruct",
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens
    }

    headers = {
        "ngrok-skip-browser-warning": "true",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(
            f"{BASE_URL}/chat/completions", 
            json=payload,
            headers=headers,
            timeout=120
        )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except requests.exceptions.RequestException as e:
        return f"⚠️ Errore nel contattare il modello locale: {e}"
