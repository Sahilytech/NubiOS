from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import urllib.error
import urllib.request
from abc import ABC, abstractmethod
from pathlib import Path


class TTSProvider(ABC):
    @abstractmethod
    def speak(self, text: str) -> None:
        raise NotImplementedError


class NoOpTTS(TTSProvider):
    """Safe default when no TTS backend is configured."""

    def speak(self, text: str) -> None:
        return None


class ElevenLabsTTS(TTSProvider):
    """ElevenLabs Text-to-Speech backend for Nubi."""

    API_URL = "https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"

    def __init__(
        self,
        api_key: str,
        voice_id: str,
        model_id: str = "eleven_multilingual_v2",
        output_format: str = "mp3_44100_128",
        data_dir: Path | None = None,
    ) -> None:
        if not api_key.strip():
            raise ValueError("ElevenLabs API key is required")
        if not voice_id.strip():
            raise ValueError("ElevenLabs voice ID is required")
        self.api_key = api_key.strip()
        self.voice_id = voice_id.strip()
        self.model_id = model_id
        self.output_format = output_format
        self.data_dir = data_dir
        self.last_audio_path: Path | None = None

    def synthesize(self, text: str) -> bytes:
        text = text.strip()
        if not text:
            return b""
        url = f"{self.API_URL.format(voice_id=self.voice_id)}?output_format={self.output_format}"
        payload = (
            '{"text":' + _json_string(text)
            + ',"model_id":' + _json_string(self.model_id)
            + ',"voice_settings":{"stability":0.45,"similarity_boost":0.8,"style":0.35,"use_speaker_boost":true}}'
        ).encode("utf-8")
        request = urllib.request.Request(
            url,
            data=payload,
            method="POST",
            headers={
                "xi-api-key": self.api_key,
                "Content-Type": "application/json",
                "Accept": "audio/mpeg",
            },
        )
        try:
            with urllib.request.urlopen(request, timeout=60) as response:
                return response.read()
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")[:500]
            raise RuntimeError(f"ElevenLabs TTS failed ({exc.code}): {detail}") from exc
        except urllib.error.URLError as exc:
            raise RuntimeError(f"ElevenLabs TTS connection failed: {exc.reason}") from exc

    def speak(self, text: str) -> None:
        audio = self.synthesize(text)
        if not audio:
            return

        directory = self.data_dir / "tts" if self.data_dir else None
        if directory:
            directory.mkdir(parents=True, exist_ok=True)
            # Use unique files so Windows' media subsystem never races with a file
            # that another TTS request is still playing.
            path = directory / f"nubi_{os.getpid()}_{next(tempfile._get_candidate_names())}.mp3"
            path.write_bytes(audio)
        else:
            handle = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3", prefix="nubi_")
            handle.write(audio)
            handle.close()
            path = Path(handle.name)

        self.last_audio_path = path
        _play_audio(path)


def _json_string(value: str) -> str:
    import json
    return json.dumps(value, ensure_ascii=False)


def _play_audio(path: Path) -> None:
    """Delegate MP3 playback to the user's Windows default media application.

    This intentionally avoids ctypes/MCI calls because native multimedia calls can
    terminate the Python process on some Windows audio configurations.
    """
    if sys.platform == "win32":
        try:
            os.startfile(str(path))
            return
        except OSError:
            pass

    try:
        subprocess.Popen(
            ["ffplay", "-nodisp", "-autoexit", "-loglevel", "quiet", str(path)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except (FileNotFoundError, OSError):
        raise RuntimeError("No compatible audio player is available")
