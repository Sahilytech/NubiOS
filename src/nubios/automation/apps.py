from __future__ import annotations

from dataclasses import dataclass
import shutil


@dataclass(frozen=True)
class Application:
    name: str
    executable: str
    source: str = "PATH"


def discover_applications(names: tuple[str, ...] = ("code", "chrome", "firefox", "godot", "discord")) -> list[Application]:
    """Discover safe executable names available on PATH without assuming fixed install paths."""
    found: list[Application] = []
    for name in names:
        executable = shutil.which(name)
        if executable:
            found.append(Application(name, executable))
    return found
