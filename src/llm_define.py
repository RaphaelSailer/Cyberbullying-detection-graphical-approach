# src/llm_define.py
import os
import requests
from dotenv import load_dotenv
from pathlib import Path

ENV_PATH = Path(__file__).resolve().parents[1] / ".env"
load_dotenv(dotenv_path=ENV_PATH)

class LLMClient:
    def __init__(self):
        self.provider = os.getenv("LLM_PROVIDER", "ollama")
        self.model = os.getenv("MODEL_NAME", "llama3.1:8b")
        self.ollama_url = os.getenv("OLLAMA_URL", "http://localhost:11434")

    def generate(self, prompt: str) -> str:
        if self.provider == "ollama":
            return self._ollama(prompt)
        raise ValueError(f"Unsupported provider: {self.provider}")

    def _ollama(self, prompt: str) -> str:
        url = f"{self.ollama_url}/api/generate"
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.8
            }
        }
        r = requests.post(url, json=payload, timeout=120)
        r.raise_for_status()
        data = r.json()
        return data["response"]