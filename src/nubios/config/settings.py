from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    data_dir: Path
    allowed_directories: tuple[Path, ...]
    mock_ai: bool = True
    ai_provider: str = "mock"
    ai_model: str = "llama3.2"
    log_level: str = "INFO"
    theme: str = "dark"
    tts_enabled: bool = False
    startup_enabled: bool = False

    @classmethod
    def from_env(cls) -> "Settings":
        data_dir = Path(os.getenv("NUBIOS_DATA_DIR", "./nubios_data")).expanduser().resolve()
        raw = os.getenv("NUBIOS_ALLOWED_DIRECTORIES", "")
        allowed = tuple(Path(p).expanduser().resolve() for p in raw.split(";") if p.strip())
        mock = os.getenv("NUBIOS_MOCK_AI", "true").lower() in {"1", "true", "yes", "on"}
        return cls(
            data_dir=data_dir,
            allowed_directories=allowed,
            mock_ai=mock,
            ai_provider=os.getenv("NUBIOS_AI_PROVIDER", "mock" if mock else "ollama"),
            ai_model=os.getenv("NUBIOS_AI_MODEL", "llama3.2"),
            log_level=os.getenv("NUBIOS_LOG_LEVEL", "INFO"),
            theme=os.getenv("NUBIOS_THEME", "dark"),
            tts_enabled=os.getenv("NUBIOS_TTS", "false").lower() in {"1", "true", "yes", "on"},
            startup_enabled=os.getenv("NUBIOS_STARTUP", "false").lower() in {"1", "true", "yes", "on"},
        )
