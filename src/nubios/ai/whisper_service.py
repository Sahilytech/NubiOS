from __future__ import annotations

from pathlib import Path


class WhisperService:
    """Optional speech-to-text adapter. Importing NubiOS never requires Whisper."""

    def __init__(self, model: str = "base") -> None:
        try:
            from faster_whisper import WhisperModel
        except ImportError as exc:
            raise RuntimeError("Voice support is unavailable; install the optional voice extra") from exc
        self._model = WhisperModel(model)

    def transcribe(self, audio_path: Path) -> str:
        segments, _ = self._model.transcribe(str(audio_path))
        return " ".join(segment.text.strip() for segment in segments).strip()
