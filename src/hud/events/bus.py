"""Synchronous in-process event bus for HUD lifecycle events."""

from __future__ import annotations

from hud.events.types import HudEvent, HudEventHandler


class HudEventBus:
    """Synchronous, typed publish-subscribe event bus for HUD."""

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
        handlers = list(self._handlers.get(event.name, []))
        for handler in handlers:
            handler(event)
