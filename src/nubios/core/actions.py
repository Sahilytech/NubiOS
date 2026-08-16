from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

from .permissions import Permission, PermissionManager


@dataclass(frozen=True)
class ActionResult:
    success: bool
    message: str
    data: dict[str, Any] = field(default_factory=dict)


class Action(ABC):
    name: str
    description: str
    required_permission: str | None = None
    destructive: bool = False

    def __init__(self, parameters: dict[str, Any] | None = None) -> None:
        self.parameters = parameters or {}

    def preview(self) -> str:
        return f"{self.name}: {self.description}"

    @abstractmethod
    def execute(self) -> ActionResult:
        """Execute the already validated action."""


class ActionExecutor:
    """Single enforcement point for action permissions and confirmation."""

    def __init__(self, permissions: PermissionManager) -> None:
        self.permissions = permissions

    def run(self, action: Action, *, confirmed: bool = False) -> ActionResult:
        if action.required_permission and not self.permissions.check(action.required_permission):
            return ActionResult(False, f"Permission denied: {action.required_permission}")
        if action.destructive and not confirmed:
            return ActionResult(False, action.preview(), {"confirmation_required": True})
        try:
            return action.execute()
        except Exception as exc:
            return ActionResult(False, f"Action failed: {exc}")
