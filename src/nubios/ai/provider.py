from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class AIResponse:
    text: str
    raw: Any = None


class AIProvider(ABC):
    name = "abstract"

    @abstractmethod
    def chat(self, message: str, *, context: list[dict[str, str]] | None = None) -> AIResponse:
        raise NotImplementedError

    def structured(self, prompt: str, schema: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError


class MockAIProvider(AIProvider):
    name = "mock"

    def chat(self, message: str, *, context: list[dict[str, str]] | None = None) -> AIResponse:
        return AIResponse(f"Mock Nubi: I received your message: {message}")


class LocalAIProvider(AIProvider):
    name = "ollama"

    def __init__(self, model: str = "llama3.2", base_url: str = "http://127.0.0.1:11434") -> None:
        self.model, self.base_url = model, base_url.rstrip("/")

    def chat(self, message: str, *, context: list[dict[str, str]] | None = None) -> AIResponse:
        import json
        import urllib.request
        body = json.dumps({"model": self.model, "prompt": message, "stream": False}).encode()
        req = urllib.request.Request(f"{self.base_url}/api/generate", data=body, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=60) as response:
            payload = json.loads(response.read().decode())
        return AIResponse(str(payload.get("response", "")), payload)


class CloudAIProvider(AIProvider):
    name = "cloud"

    def __init__(self, callback: Any) -> None:
        self.callback = callback

    def chat(self, message: str, *, context: list[dict[str, str]] | None = None) -> AIResponse:
        return AIResponse(str(self.callback(message, context=context)))
