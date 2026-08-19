from __future__ import annotations

import tempfile
import wave
from pathlib import Path


class VoiceController:
    """Capture a short microphone recording and transcribe it with Whisper.

    Voice dependencies are loaded lazily so the desktop application can start
    normally when microphone or Whisper support is unavailable.
    """

    def __init__(self, model: str = "base", sample_rate: int = 16_000) -> None:
        self.model = model
        self.sample_rate = sample_rate
        self._whisper = None

    def listen_once(self, duration_seconds: float = 6.0) -> str:
        """Record from the default microphone and return the recognized text."""
        if duration_seconds <= 0:
            raise ValueError("Recording duration must be positive")

        try:
            import sounddevice as sd
        except ImportError as exc:
            raise RuntimeError("Microphone support is unavailable; install the voice dependencies") from exc

        frame_count = int(self.sample_rate * duration_seconds)
        recording = sd.rec(
            frame_count,
            samplerate=self.sample_rate,
            channels=1,
            dtype="int16",
            blocking=True,
        )
        sd.wait()

        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as handle:
            audio_path = Path(handle.name)

        try:
            with wave.open(str(audio_path), "wb") as wav:
                wav.setnchannels(1)
                wav.setsampwidth(2)
                wav.setframerate(self.sample_rate)
                wav.writeframes(recording.tobytes())

            if self._whisper is None:
                from .whisper_service import WhisperService

                self._whisper = WhisperService(self.model)
            return self._whisper.transcribe(audio_path)
        finally:
            audio_path.unlink(missing_ok=True)

    @staticmethod
    def microphone_available() -> bool:
        """Return whether the optional microphone package can be imported."""
        try:
            import sounddevice  # noqa: F401
        except ImportError:
            return False
        return True
