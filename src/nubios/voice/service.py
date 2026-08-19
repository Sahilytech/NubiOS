from __future__ import annotations

import logging
from dataclasses import dataclass

log = logging.getLogger(__name__)


@dataclass(frozen=True)
class VoiceStatus:
    available: bool
    message: str


class VoiceService:
    """Optional STT/TTS facade. Import-heavy voice libraries stay out of startup."""

    def __init__(self, enabled: bool = False, whisper_model: str = "tiny") -> None:
        self.enabled = enabled
        self.whisper_model = whisper_model
        self._model = None

    def status(self) -> VoiceStatus:
        if not self.enabled:
            return VoiceStatus(False, "Voice is disabled")
        try:
            import sounddevice  # noqa: F401
            import faster_whisper  # noqa: F401
        except ImportError as exc:
            return VoiceStatus(False, f"Voice dependencies unavailable: {exc.name}")
        return VoiceStatus(True, "Voice input ready")

    def transcribe_file(self, path: str) -> str:
        """Transcribe an audio file when voice is enabled; never runs during UI startup."""
        if not self.enabled:
            raise RuntimeError("Voice input is disabled")
        from faster_whisper import WhisperModel

        if self._model is None:
            self._model = WhisperModel(self.whisper_model, device="cpu", compute_type="int8")
        segments, _ = self._model.transcribe(path, vad_filter=True)
        return " ".join(segment.text.strip() for segment in segments).strip()

    def speak(self, text: str) -> str:
        """Placeholder for the configured TTS provider; kept non-blocking for now."""
        return text
