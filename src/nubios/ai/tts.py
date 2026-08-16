from __future__ import annotations

from abc import ABC, abstractmethod


class TTSProvider(ABC):
    @abstractmethod
    def speak(self, text: str) -> None:
        raise NotImplementedError


class NoOpTTS(TTSProvider):
    """Safe default when no TTS backend is configured."""

    def speak(self, text: str) -> None:
        return None
