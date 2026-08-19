from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


def _env_bool(name: str, default: bool) -> bool:
    return os.getenv(name, str(default)).strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class Settings:
    data_dir: Path
    allowed_directories: tuple[Path, ...]
    mock_ai: bool = True
    log_level: str = "INFO"
    ai_provider: str = "mock"
    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"
    openai_base_url: str = "https://api.openai.com/v1"
    voice_enabled: bool = False
    whisper_model: str = "tiny"
    tts_provider: str = "none"
    elevenlabs_api_key: str = ""
    elevenlabs_voice_id: str = ""

    @classmethod
    def from_env(cls) -> "Settings":
        data_dir = Path(os.getenv("NUBIOS_DATA_DIR", "./nubios_data")).expanduser()
        raw = os.getenv("NUBIOS_ALLOWED_DIRECTORIES", "")
        allowed = tuple(Path(p).expanduser().resolve() for p in raw.split(";") if p.strip())
        provider = os.getenv("NUBIOS_AI_PROVIDER", "mock").strip().lower()
        mock = _env_bool("NUBIOS_MOCK_AI", provider == "mock")
        return cls(
            data_dir=data_dir.resolve(),
            allowed_directories=allowed,
            mock_ai=mock,
            log_level=os.getenv("NUBIOS_LOG_LEVEL", "INFO"),
            ai_provider=provider,
            openai_api_key=os.getenv("OPENAI_API_KEY", ""),
            openai_model=os.getenv("NUBIOS_OPENAI_MODEL", "gpt-4o-mini"),
            openai_base_url=os.getenv("NUBIOS_OPENAI_BASE_URL", "https://api.openai.com/v1").rstrip("/"),
            voice_enabled=_env_bool("NUBIOS_VOICE_ENABLED", False),
            whisper_model=os.getenv("NUBIOS_WHISPER_MODEL", "tiny"),
            tts_provider=os.getenv("NUBIOS_TTS_PROVIDER", "none").strip().lower(),
            elevenlabs_api_key=os.getenv("ELEVENLABS_API_KEY", ""),
            elevenlabs_voice_id=os.getenv("ELEVENLABS_VOICE_ID", ""),
        )
