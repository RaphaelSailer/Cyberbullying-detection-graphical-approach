# src/llm_define.py

import os
from pathlib import Path
from typing import List, Dict, Optional

import requests
from dotenv import load_dotenv

ENV_PATH = Path(__file__).resolve().parents[1] / ".env"
load_dotenv(dotenv_path=ENV_PATH)


def _messages_to_prompt(messages: List[Dict[str, str]]) -> str:
    parts = []
    for m in messages:
        role = (m.get("role") or "").strip().lower()
        content = (m.get("content") or "").strip()
        if not content:
            continue

        if role == "system":
            parts.append(f"[SYSTEM]\n{content}\n")
        elif role == "user":
            parts.append(f"[USER]\n{content}\n")
        elif role == "assistant":
            parts.append(f"[ASSISTANT]\n{content}\n")
        else:
            parts.append(f"[{role.upper() or 'MESSAGE'}]\n{content}\n")

    parts.append("[ASSISTANT]\n")
    return "\n".join(parts)


class LLMClient:
    def __init__(self, model_name: Optional[str] = None):
        self.provider = os.getenv("LLM_PROVIDER", "ollama")
        self.model = model_name or os.getenv("MODEL_NAME", "llama3.1:8b")
        self.ollama_url = os.getenv("OLLAMA_URL", "http://localhost:11434")

        self.temperature = float(os.getenv("TEMPERATURE", "0.2"))
        self.top_p = float(os.getenv("TOP_P", "0.9"))

    def generate(self, prompt: str, max_tokens: int = 700) -> str:
        if self.provider == "ollama":
            return self._ollama(prompt, max_tokens=max_tokens)
        raise ValueError(f"Unsupported provider: {self.provider}")

    def generate_from_messages(self, messages, max_tokens: int = 700) -> str:
        prompt = _messages_to_prompt(messages)
        return self.generate(prompt, max_tokens=max_tokens)

    def _ollama(self, prompt: str, max_tokens: int = 700) -> str:
        url = f"{self.ollama_url}/api/generate"
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": self.temperature,
                "top_p": self.top_p,
                "num_predict": int(max_tokens),
            },
        }

        r = requests.post(url, json=payload, timeout=300)
        r.raise_for_status()
        data = r.json()
        return data.get("response", "")
