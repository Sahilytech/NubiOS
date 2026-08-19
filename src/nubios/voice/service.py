from __future__ import annotations

import json
import os
import subprocess
import tempfile
import wave
from dataclasses import dataclass
from pathlib import Path
from urllib import error, request


@dataclass(frozen=True)
class VoiceStatus:
    available: bool
    message: str


class VoiceService:
    """Optional voice facade. Microphone/Whisper imports are lazy."""

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
        try:
            import sounddevice
            devices = sounddevice.query_devices()
            input_devices = [d for d in devices if d.get("max_input_channels", 0) > 0]
            if not input_devices:
                return VoiceStatus(False, "No microphone input device was detected")
            import faster_whisper  # noqa: F401
        except ImportError as exc:
            return VoiceStatus(False, f"Voice dependencies unavailable: {exc.name}")
        except Exception as exc:
            return VoiceStatus(False, f"Microphone unavailable: {exc}")
        return VoiceStatus(True, f"Microphone ready: {input_devices[0]['name']}")

    def record_and_transcribe(self, seconds: float = 5.0, samplerate: int = 16000) -> str:
        if not self.enabled:
            raise RuntimeError("Voice input is disabled")
        import sounddevice as sd

        devices = sd.query_devices()
        input_devices = [d for d in devices if d.get("max_input_channels", 0) > 0]
        if not input_devices:
            raise RuntimeError("No microphone input device was detected by Windows")

        try:
            default_input = sd.default.device[0]
            if default_input is None or int(default_input) < 0:
                default_input = None
            if default_input is not None:
                sd.check_input_settings(device=default_input, samplerate=samplerate, channels=1, dtype="int16")
            recording = sd.rec(int(seconds * samplerate), samplerate=samplerate, channels=1, dtype="int16", blocking=True)
            sd.wait()
        except Exception as exc:
            raise RuntimeError(f"Microphone capture failed: {exc}") from exc

        path = Path(tempfile.gettempdir()) / "nubios_mic.wav"
        with wave.open(str(path), "wb") as wav:
            wav.setnchannels(1)
            wav.setsampwidth(2)
            wav.setframerate(samplerate)
            wav.writeframes(recording.tobytes())
        return self.transcribe_file(str(path))

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
