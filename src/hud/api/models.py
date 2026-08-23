"""Public data models and enums for the hud package."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class HudViewState:
    """Structured view model representing HUD UI state."""

    backend_status: str
    last_request_id: str | None
    last_updated: float
    view_data: dict[str, Any] | None = None


@dataclass(frozen=True)
class WidgetPlacement:
    """Screen coordinate and anchor definitions for a widget."""
    anchor: str
    offset_x: int = 0
    offset_y: int = 0
    width: int | None = None
    height: int | None = None


@dataclass(frozen=True)
class HudWidgetManifest:
    """Declarative metadata and permissions for a dynamic HUD widget bundle."""
    id: str
    name: str
    version: str
    author: str
    entry_point: str
    default_placement: WidgetPlacement | None = None
    subscribed_events: list[str] | None = None
    hooks: dict[str, str] | None = None
    assets: dict[str, str] | None = None
