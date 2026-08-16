from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


DEFAULT_APPS = {
    "vs code": ["code"],
    "visual studio code": ["code"],
    "chrome": ["chrome"],
    "file explorer": ["explorer.exe"],
}


class ApplicationRegistry:
    def __init__(self, custom: dict[str, list[str]] | None = None) -> None:
        self.apps = {**DEFAULT_APPS, **(custom or {})}

    def launch(self, name: str) -> str:
        key = name.strip().lower()
        command = self.apps.get(key)
        if command is None:
            return f"Application '{name}' is not configured."
        try:
            if os.name == "nt":
                subprocess.Popen(command, shell=False)
            elif key == "file explorer":
                subprocess.Popen(["xdg-open", "."], shell=False)
            else:
                subprocess.Popen(command, shell=False)
            return f"Opening {name}."
        except (FileNotFoundError, OSError) as exc:
            return f"Could not open {name}: {exc}"


class FileSearcher:
    def __init__(self, allowed_directories: tuple[Path, ...]) -> None:
        self.allowed = tuple(p.resolve() for p in allowed_directories)

    def search(self, query: str, limit: int = 30) -> list[Path]:
        if not self.allowed:
            return []
        needle = query.lower()
        results: list[Path] = []
        for root in self.allowed:
            if not root.exists():
                continue
            for path in root.rglob("*"):
                if needle in path.name.lower():
                    results.append(path)
                    if len(results) >= limit:
                        return results
        return results
