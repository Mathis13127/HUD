"""Typed event bus and documented lifecycle events for the hud package.

Documented Events (Rule L4):
- VIEW_RENDERED:
    Payload: {"view_id": str, "timestamp": float}
    Trigger: Emitted when a HUD viewport or component state is updated and rendered.
- STATE_SYNCHRONIZED:
    Payload: {"synced_keys": list[str], "engine_status": str}
    Trigger: Emitted when the HUD successfully polls and synchronizes state with the engine.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
import time
from typing import Any

HudEventHandler = Callable[["HudEvent"], None]


@dataclass(frozen=True)
class HudEvent:
    """Immutable event payload published by the HUD interface."""

    name: str
    payload: dict[str, Any]
    source: str = "hud.ui.client"
    timestamp: float = field(default_factory=time.time)


class HudEventBus:
    """Synchronous in-process event bus for HUD lifecycle events."""

    def __init__(self) -> None:
        self._handlers: dict[str, list[HudEventHandler]] = {}

    def subscribe(self, event_name: str, handler: HudEventHandler) -> None:
        """Register a handler for a specific event name."""
        if event_name not in self._handlers:
            self._handlers[event_name] = []
        if handler not in self._handlers[event_name]:
            self._handlers[event_name].append(handler)

    def unsubscribe(self, event_name: str, handler: HudEventHandler) -> None:
        """Remove a registered handler for a specific event name."""
        if event_name in self._handlers and handler in self._handlers[event_name]:
            self._handlers[event_name].remove(handler)

    def publish(self, event: HudEvent) -> None:
        """Dispatch an event synchronously to all registered handlers."""
        handlers = self._handlers.get(event.name, [])
        for handler in handlers:
            handler(event)
