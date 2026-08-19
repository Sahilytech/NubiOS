from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import json


@dataclass(frozen=True)
class PluginManifest:
    name: str
    version: str
    description: str
    author: str
    permissions: tuple[str, ...] = ()

    @classmethod
    def load(cls, path: Path) -> "PluginManifest":
        payload = json.loads(path.read_text(encoding="utf-8"))
        required = {"name", "version", "description", "author"}
        missing = required - payload.keys()
        if missing:
            raise ValueError(f"Plugin manifest missing: {', '.join(sorted(missing))}")
        return cls(payload["name"], payload["version"], payload["description"], payload["author"], tuple(payload.get("permissions", ())))
