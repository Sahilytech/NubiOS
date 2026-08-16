from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    data_dir: Path
    allowed_directories: tuple[Path, ...]
    mock_ai: bool = True
    log_level: str = "INFO"

    @classmethod
    def from_env(cls) -> "Settings":
        data_dir = Path(os.getenv("NUBIOS_DATA_DIR", "./nubios_data")).expanduser()
        raw = os.getenv("NUBIOS_ALLOWED_DIRECTORIES", "")
        allowed = tuple(Path(p).expanduser().resolve() for p in raw.split(";") if p.strip())
        mock = os.getenv("NUBIOS_MOCK_AI", "true").lower() in {"1", "true", "yes", "on"}
        return cls(data_dir.resolve(), allowed, mock, os.getenv("NUBIOS_LOG_LEVEL", "INFO"))
