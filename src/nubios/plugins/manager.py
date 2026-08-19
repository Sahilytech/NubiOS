from __future__ import annotations

from pathlib import Path

from ..core.permissions import PermissionManager
from .manifest import PluginManifest


class PluginManager:
    def __init__(self, directory: Path, permissions: PermissionManager) -> None:
        self.directory = directory
        self.permissions = permissions
        self.manifests: dict[str, PluginManifest] = {}

    def discover(self) -> list[PluginManifest]:
        self.manifests.clear()
        if not self.directory.exists():
            return []
        for manifest_path in self.directory.glob("*/plugin.json"):
            try:
                manifest = PluginManifest.load(manifest_path)
            except (OSError, ValueError):
                continue
            self.manifests[manifest.name] = manifest
        return list(self.manifests.values())

    def can_load(self, name: str) -> bool:
        manifest = self.manifests[name]
        return all(self.permissions.check(permission) for permission in manifest.permissions)
