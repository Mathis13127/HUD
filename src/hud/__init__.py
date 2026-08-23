"""J.A.R.V.I.S - HUD Monitoring, Debugging and UI Interface.

Public API exports for the hud package (Rule L3).
"""

from hud.api.models import HudViewState
from hud.api.protocols import (
    HudClientProtocol,
    HudRendererProtocol,
    StateSyncProtocol,
)
from hud.client import HudClient
from hud.errors import (
    HudError,
    HudHookCancelledError,
    InvalidUiStateError,
    StateSyncError,
    ViewRenderError,
)
from hud.events.bus import HudEventBus
from hud.events.definitions import (
    STATE_SYNCHRONIZED,
    VIEW_RENDERED,
)
from hud.events.types import (
    HudEvent,
    HudEventHandler,
)
from hud.hooks.registry import HudHookRegistry
from hud.hooks.types import (
    HudHookContext,
    HudHookHandler,
    HudHookPoint,
    HudHookResult,
    Priority,
)

__version__ = "0.1.0"

__all__ = [
    # Client & Core
    "HudClient",
    "HudViewState",
    "HudRendererProtocol",
    "StateSyncProtocol",
    "HudClientProtocol",
    # Errors
    "HudError",
    "ViewRenderError",
    "StateSyncError",
    "InvalidUiStateError",
    "HudHookCancelledError",
    # Events
    "HudEvent",
    "HudEventBus",
    "HudEventHandler",
    "VIEW_RENDERED",
    "STATE_SYNCHRONIZED",
    # Hooks
    "HudHookPoint",
    "Priority",
    "HudHookContext",
    "HudHookResult",
    "HudHookHandler",
    "HudHookRegistry",
]
