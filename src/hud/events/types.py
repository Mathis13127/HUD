"""Typed event data structures for the hud package."""

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
