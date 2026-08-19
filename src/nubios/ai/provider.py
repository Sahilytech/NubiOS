from __future__ import annotations

from abc import ABC, abstractmethod
import json
from urllib import error, request


class AIProvider(ABC):
    @abstractmethod
    def chat(self, message: str) -> str:
        raise NotImplementedError


class MockAIProvider(AIProvider):
    def chat(self, message: str) -> str:
        return f"I got you. You said: {message}"


class OpenAICompatibleProvider(AIProvider):
    """Small dependency-free client for OpenAI-compatible chat APIs."""

    def __init__(self, api_key: str, model: str, base_url: str, timeout: float = 45.0) -> None:
        if not api_key:
            raise ValueError("OPENAI_API_KEY is not configured")
        self.api_key = api_key
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def chat(self, message: str) -> str:
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "You are Nubi, a concise, friendly desktop assistant."},
                {"role": "user", "content": message},
            ],
            "temperature": 0.7,
        }
        data = json.dumps(payload).encode("utf-8")
        req = request.Request(
            f"{self.base_url}/chat/completions",
            data=data,
            headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
            method="POST",
        )
        try:
            with request.urlopen(req, timeout=self.timeout) as response:
                body = json.loads(response.read().decode("utf-8"))
        except error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")[:500]
            raise RuntimeError(f"AI provider returned HTTP {exc.code}: {detail}") from exc
        except (error.URLError, TimeoutError) as exc:
            raise RuntimeError(f"AI provider unavailable: {exc}") from exc

        try:
            return str(body["choices"][0]["message"]["content"]).strip()
        except (KeyError, IndexError, TypeError) as exc:
            raise RuntimeError("AI provider returned an unexpected response") from exc
