from __future__ import annotations

from typing import Sequence
import httpx

from app.config import Settings


class OllamaClient:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.base_url = settings.ollama_base_url.rstrip("/")
        self.timeout = httpx.Timeout(120.0, connect=10.0)

    def healthcheck(self) -> bool:
        try:
            response = httpx.get(f"{self.base_url}/tags", timeout=10.0)
            response.raise_for_status()
            return True
        except Exception:
            return False

    def embed(self, texts: Sequence[str]) -> list[list[float]]:
        payload = {
            "model": self.settings.ollama_embed_model,
            "input": list(texts),
            "truncate": True,
        }

        endpoints = [
            f"{self.base_url}/embed",
            f"{self.base_url}/embeddings",
        ]

        last_error = None

        for endpoint in endpoints:
            try:
                response = httpx.post(endpoint, json=payload, timeout=self.timeout)
                response.raise_for_status()
                data = response.json()

                if "embeddings" in data and data["embeddings"]:
                    return data["embeddings"]

                if "embedding" in data and data["embedding"]:
                    return [data["embedding"]]

            except Exception as exc:
                last_error = exc

        raise RuntimeError(f"Ollama embedding endpoint çağrısı başarısız oldu: {last_error}")

    def chat(self, system_prompt: str, user_prompt: str) -> str:
        response = httpx.post(
            f"{self.base_url}/chat",
            json={
                "model": self.settings.ollama_chat_model,
                "stream": False,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                "options": {"temperature": 0.1},
            },
            timeout=self.timeout,
        )
        response.raise_for_status()
        data = response.json()
        return data["message"]["content"].strip()