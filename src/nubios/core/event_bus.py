from __future__ import annotations

from collections import defaultdict
from collections.abc import Callable
from typing import Any


EventHandler = Callable[[dict[str, Any]], None]


class EventBus:
    """Small synchronous event bus used to decouple NubiOS services."""

    def __init__(self) -> None:
        self._handlers: dict[str, list[EventHandler]] = defaultdict(list)

    def subscribe(self, event: str, handler: EventHandler) -> None:
        if handler not in self._handlers[event]:
            self._handlers[event].append(handler)

    def unsubscribe(self, event: str, handler: EventHandler) -> None:
        if handler in self._handlers[event]:
            self._handlers[event].remove(handler)

    def publish(self, event: str, **data: Any) -> None:
        for handler in tuple(self._handlers.get(event, ())):
            handler(data)
