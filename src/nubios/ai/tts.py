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
    """ElevenLabs Text-to-Speech backend for Nubi.

    Uses the official HTTP API directly so NubiOS does not need an additional
    runtime SDK dependency. The API key is read from the environment and is
    never stored in the repository.
    """

    API_URL = "https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"

    def __init__(
        self,
        api_key: str,
        voice_id: str = "fJ2BRu9MMKDzgQZh6OiH",
        model_id: str = "eleven_multilingual_v2",
        output_format: str = "mp3_44100_128",
        data_dir: Path | None = None,
    ) -> None:
        if not api_key.strip():
            raise ValueError("ElevenLabs API key is required")
        self.api_key = api_key.strip()
        self.voice_id = voice_id.strip() or "fJ2BRu9MMKDzgQZh6OiH"
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
            return None

        suffix = ".mp3" if self.output_format.startswith("mp3") else ".audio"
        directory = self.data_dir / "tts" if self.data_dir else None
        if directory:
            directory.mkdir(parents=True, exist_ok=True)
            path = directory / "nubi_latest{0}".format(suffix)
            path.write_bytes(audio)
        else:
            handle = tempfile.NamedTemporaryFile(delete=False, suffix=suffix, prefix="nubi_")
            handle.write(audio)
            handle.close()
            path = Path(handle.name)

        self.last_audio_path = path
        _play_audio(path)


def _json_string(value: str) -> str:
    import json

    return json.dumps(value, ensure_ascii=False)


def _play_audio(path: Path) -> None:
    """Play generated audio using the native Windows player or ffplay."""
    if sys.platform == "win32" and path.suffix.lower() == ".wav":
        import winsound

        winsound.PlaySound(str(path), winsound.SND_FILENAME | winsound.SND_ASYNC)
        return

    # MP3 playback is delegated to ffplay when available. NubiOS remains
    # usable without it; the generated audio is still kept on disk.
    try:
        subprocess.Popen(
            ["ffplay", "-nodisp", "-autoexit", "-loglevel", "quiet", str(path)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except (FileNotFoundError, OSError):
        return None
