from __future__ import annotations

from enum import StrEnum


class Permission(StrEnum):
    TASKS_READ = "tasks.read"
    TASKS_WRITE = "tasks.write"
    MEMORY_READ = "memory.read"
    MEMORY_WRITE = "memory.write"
    FILESYSTEM_READ = "filesystem.read"
    FILESYSTEM_WRITE = "filesystem.write"
    APPLICATIONS_LAUNCH = "applications.launch"
    WEB_ACCESS = "web.access"
    MICROPHONE = "microphone"
    CAMERA = "camera"
    SCREEN_CAPTURE = "screen.capture"


class PermissionManager:
    """In-memory permission boundary; persistence can be layered through Settings."""

    def __init__(self, granted: set[str] | None = None) -> None:
        defaults = {
            Permission.TASKS_READ, Permission.TASKS_WRITE,
            Permission.MEMORY_READ, Permission.MEMORY_WRITE,
            Permission.FILESYSTEM_READ, Permission.APPLICATIONS_LAUNCH,
        }
        self._granted = set(granted if granted is not None else defaults)
        self._pending: set[str] = set()

    def check(self, permission: str) -> bool:
        return permission in self._granted

    def request(self, permission: str) -> bool:
        self._pending.add(permission)
        return self.check(permission)

    def grant(self, permission: str) -> None:
        self._pending.discard(permission)
        self._granted.add(permission)

    def revoke(self, permission: str) -> None:
        self._granted.discard(permission)

    def all(self) -> set[str]:
        return set(self._granted)

    def pending(self) -> set[str]:
        return set(self._pending)
