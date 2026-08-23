"""HUD UI client implementation interacting with JarvisEngine via public API."""

from __future__ import annotations

import time
from typing import Any

from hud.api.models import HudViewState
from hud.errors import (
    HudHookCancelledError,
    ViewRenderError,
)
from hud.events.bus import HudEventBus
from hud.events.definitions import (
    STATE_SYNCHRONIZED,
    VIEW_RENDERED,
)
from hud.events.types import HudEvent
from hud.hooks.registry import HudHookRegistry
from hud.hooks.types import HudHookContext, HudHookPoint
from hud.api.protocols import BackendProtocol


class HudClient:
    """Monitoring, debugging and execution UI interface client."""

    def __init__(
        self,
        backend: BackendProtocol,
        event_bus: HudEventBus | None = None,
        hook_registry: HudHookRegistry | None = None,
    ) -> None:
        self._backend = backend
        self._event_bus = event_bus or HudEventBus()
        self._hook_registry = hook_registry or HudHookRegistry()
        self._last_request_id: str | None = None
        self._last_updated = time.time()
        self._view_data: dict[str, Any] = {}

    @property
    def event_bus(self) -> HudEventBus:
        """Access the HUD client's event bus."""
        return self._event_bus

    @property
    def hook_registry(self) -> HudHookRegistry:
        """Access the HUD client's hook registry."""
        return self._hook_registry

    def poll_backend_status(self) -> str:
        """Poll the current status of the backend and emit state synchronization event."""
        # Trigger pre-sync hook
        pre_ctx = HudHookContext(
            hook_point=HudHookPoint.PRE_STATE_SYNC,
            data={"timestamp": time.time()},
        )
        self._hook_registry.trigger(HudHookPoint.PRE_STATE_SYNC, pre_ctx)

        current_status = self._backend.status
        self._last_updated = time.time()

        # Trigger post-sync hook
        post_ctx = HudHookContext(
            hook_point=HudHookPoint.POST_STATE_SYNC,
            data={"backend_status": current_status, "timestamp": self._last_updated},
        )
        self._hook_registry.trigger(HudHookPoint.POST_STATE_SYNC, post_ctx)

        self._event_bus.publish(
            HudEvent(
                name=STATE_SYNCHRONIZED,
                payload={"synced_keys": ["status"], "backend_status": current_status},
                source="hud.ui.client",
            )
        )
        return current_status

    def submit_command(
        self,
        prompt: str,
        request_id: str,
        context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Submit a user/operator command to the backend public API."""
        if not prompt.strip():
            raise ViewRenderError(
                view_id="hud.command_prompt",
                reason="Cannot submit empty command string to engine",
            )

        # Trigger pre-render / pre-dispatch hook
        pre_ctx = HudHookContext(
            hook_point=HudHookPoint.PRE_VIEW_RENDER,
            data={"prompt": prompt, "request_id": request_id},
        )
        pre_res = self._hook_registry.trigger(HudHookPoint.PRE_VIEW_RENDER, pre_ctx)
        if pre_res.cancelled:
            raise HudHookCancelledError(
                hook_point=HudHookPoint.PRE_VIEW_RENDER.value,
                reason=pre_res.cancel_reason or "Cancelled by HUD hook interceptor",
            )

        effective_prompt = str(pre_ctx.data.get("prompt", prompt))

        response = self._backend.submit(prompt=effective_prompt, request_id=request_id, context=context)
        
        self._last_request_id = response.get("request_id", request_id)
        self._last_updated = time.time()
        self._view_data["last_output"] = response.get("output", "")

        self._event_bus.publish(
            HudEvent(
                name=VIEW_RENDERED,
                payload={"view_id": "main_hud_dashboard", "timestamp": self._last_updated},
                source="hud.ui.client",
            )
        )

        return response

    def get_view_state(self) -> HudViewState:
        """Return the current immutable HUD view state."""
        return HudViewState(
            backend_status=self._backend.status,
            last_request_id=self._last_request_id,
            last_updated=self._last_updated,
            view_data=dict(self._view_data),
        )
