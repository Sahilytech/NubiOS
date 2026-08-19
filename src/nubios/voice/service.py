from __future__ import annotations

import json
import os
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path
from urllib import error, request


@dataclass(frozen=True)
class VoiceStatus:
    available: bool
    message: str


class VoiceService:
    """Optional voice facade. Heavy voice imports are lazy and never run at startup."""

    def __init__(self, enabled: bool = False, whisper_model: str = "tiny", tts_provider: str = "none", elevenlabs_api_key: str = "", elevenlabs_voice_id: str = "") -> None:
        self.enabled = enabled
        self.whisper_model = whisper_model
        self.tts_provider = tts_provider
        self.elevenlabs_api_key = elevenlabs_api_key
        self.elevenlabs_voice_id = elevenlabs_voice_id
        self._model = None

    def status(self) -> VoiceStatus:
        if not self.enabled:
            return VoiceStatus(False, "Voice is disabled")
        if self.tts_provider == "elevenlabs" and self.elevenlabs_api_key and self.elevenlabs_voice_id:
            return VoiceStatus(True, "ElevenLabs TTS ready")
        try:
            import sounddevice  # noqa: F401
            import faster_whisper  # noqa: F401
        except ImportError as exc:
            return VoiceStatus(False, f"Voice dependencies unavailable: {exc.name}")
        return VoiceStatus(True, "Whisper input ready")

    def transcribe_file(self, path: str) -> str:
        if not self.enabled:
            raise RuntimeError("Voice input is disabled")
        from faster_whisper import WhisperModel
        if self._model is None:
            self._model = WhisperModel(self.whisper_model, device="cpu", compute_type="int8")
        segments, _ = self._model.transcribe(path, vad_filter=True)
        return " ".join(segment.text.strip() for segment in segments).strip()

    def speak(self, text: str) -> str:
        if not self.enabled:
            raise RuntimeError("Voice output is disabled")
        if self.tts_provider != "elevenlabs":
            raise RuntimeError("No TTS provider configured")
        if not self.elevenlabs_api_key or not self.elevenlabs_voice_id:
            raise RuntimeError("ElevenLabs API key or voice ID is missing")

        payload = json.dumps({"text": text, "model_id": "eleven_multilingual_v2"}).encode("utf-8")
        req = request.Request(
            f"https://api.elevenlabs.io/v1/text-to-speech/{self.elevenlabs_voice_id}",
            data=payload,
            headers={"xi-api-key": self.elevenlabs_api_key, "Content-Type": "application/json", "Accept": "audio/mpeg"},
            method="POST",
        )
        try:
            with request.urlopen(req, timeout=45) as response:
                audio = response.read()
        except error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")[:300]
            raise RuntimeError(f"ElevenLabs returned HTTP {exc.code}: {detail}") from exc

        path = Path(tempfile.gettempdir()) / "nubios_tts.mp3"
        path.write_bytes(audio)
        if os.name == "nt":
            os.startfile(path)  # type: ignore[attr-defined]
        else:
            subprocess.Popen(["xdg-open", str(path)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return str(path)
