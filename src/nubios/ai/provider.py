from __future__ import annotations

from abc import ABC, abstractmethod


class AIProvider(ABC):
    @abstractmethod
    def chat(self, message: str) -> str:
        raise NotImplementedError


class MockAIProvider(AIProvider):
    def chat(self, message: str) -> str:
        return f"Mock Nubi: I received your message: {message}"
