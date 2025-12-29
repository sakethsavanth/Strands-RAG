import requests
from config.settings import OLLAMA_BASE_URL, OLLAMA_MODEL

class GemmaLocalLLM:
    def generate(self, prompt: str) -> str:
        r = requests.post(
            f"{OLLAMA_BASE_URL}/api/generate",
            json={
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False
            },
            timeout=300
        )
        r.raise_for_status()
        return r.json()["response"].strip()
