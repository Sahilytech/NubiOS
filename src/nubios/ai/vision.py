from __future__ import annotations

from typing import Protocol

from ..core.permissions import Permission, PermissionManager


class VisionProvider(Protocol):
    def analyze(self, image_bytes: bytes, prompt: str) -> str: ...


class VisionService:
    def __init__(self, permissions: PermissionManager, provider: VisionProvider | None = None) -> None:
        self.permissions = permissions
        self.provider = provider

    def analyze_screenshot(self, image_bytes: bytes, prompt: str = "Describe this screen.") -> str:
        if not self.permissions.check(Permission.SCREEN_CAPTURE):
            raise PermissionError("Permission denied: screen.capture")
        if self.provider is None:
            raise RuntimeError("No vision provider configured")
        return self.provider.analyze(image_bytes, prompt)
