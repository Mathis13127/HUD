"""Typed hook data structures and interception contracts for hud (Rule L4)."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from enum import Enum, IntEnum
from typing import Any


class Priority(IntEnum):
    """Hook handler execution priority."""

    HIGHEST = 100
    HIGH = 75
    NORMAL = 50
    LOW = 25
    LOWEST = 0


class HudHookPoint(str, Enum):
    """Named lifecycle interception points for HUD UI."""

    PRE_STATE_SYNC = "PRE_STATE_SYNC"
    POST_STATE_SYNC = "POST_STATE_SYNC"
    PRE_VIEW_RENDER = "PRE_VIEW_RENDER"
    PRE_BUNDLE_LOAD = "PRE_BUNDLE_LOAD"
    POST_BUNDLE_LOAD = "POST_BUNDLE_LOAD"


@dataclass
class HudHookContext:
    """Mutable execution context passed through a HUD hook pipeline."""

    hook_point: HudHookPoint
    data: dict[str, Any] = field(default_factory=dict)
    _cancelled: bool = False
    _cancel_reason: str | None = None

    @property
    def is_cancelled(self) -> bool:
        """Check if execution was cancelled by an interceptor."""
        return self._cancelled

    @property
    def cancel_reason(self) -> str | None:
        """Get cancellation rationale."""
        return self._cancel_reason

    def cancel(self, reason: str) -> None:
        """Cancel subsequent hook execution and UI dispatch."""
        self._cancelled = True
        self._cancel_reason = reason


@dataclass(frozen=True)
class HudHookResult:
    """Outcome of running a HUD hook interception chain."""

    hook_point: HudHookPoint
    success: bool
    cancelled: bool
    cancel_reason: str | None = None
    data: dict[str, Any] = field(default_factory=dict)


HudHookHandler = Callable[[HudHookContext], None]
