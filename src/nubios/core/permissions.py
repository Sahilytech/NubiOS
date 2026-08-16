from __future__ import annotations

from enum import StrEnum


class Permission(StrEnum):
    FILESYSTEM_READ = "filesystem.read"
    FILESYSTEM_WRITE = "filesystem.write"
    APPLICATIONS_LAUNCH = "applications.launch"
    MEMORY_READ = "memory.read"
    MEMORY_WRITE = "memory.write"
    TASKS_READ = "tasks.read"
    TASKS_WRITE = "tasks.write"


class PermissionManager:
    def __init__(self, granted: set[str] | None = None) -> None:
        self._granted = set(granted or {Permission.TASKS_READ, Permission.TASKS_WRITE, Permission.MEMORY_READ, Permission.MEMORY_WRITE, Permission.FILESYSTEM_READ, Permission.APPLICATIONS_LAUNCH})

    def check(self, permission: str) -> bool:
        return permission in self._granted

    def grant(self, permission: str) -> None:
        self._granted.add(permission)

    def revoke(self, permission: str) -> None:
        self._granted.discard(permission)

    def all(self) -> set[str]:
        return set(self._granted)
