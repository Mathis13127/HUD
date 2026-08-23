"""Hook interception registry and execution pipeline for HUD (Rule L4)."""

from __future__ import annotations

from dataclasses import dataclass

from hud.hooks.types import (
    HudHookContext,
    HudHookHandler,
    HudHookPoint,
    HudHookResult,
    Priority,
)


@dataclass(frozen=True)
class _RegisteredHudHook:
    handler: HudHookHandler
    priority: int


class HudHookRegistry:
    """Registry managing named interception points for UI lifecycle."""

    def __init__(self) -> None:
        self._hooks: dict[HudHookPoint, list[_RegisteredHudHook]] = {
            point: [] for point in HudHookPoint
        }

    def register(
        self,
        hook_point: HudHookPoint,
        handler: HudHookHandler,
        priority: Priority | int = Priority.NORMAL,
    ) -> None:
        """Register an interceptor for a HUD hook point with priority ordering."""
        p_val = int(priority)
        reg = _RegisteredHudHook(handler=handler, priority=p_val)
        hook_list = self._hooks.setdefault(hook_point, [])
        hook_list.append(reg)
        hook_list.sort(key=lambda item: item.priority, reverse=True)

    def unregister(self, hook_point: HudHookPoint, handler: HudHookHandler) -> None:
        """Remove a registered handler from a HUD hook point."""
        if hook_point in self._hooks:
            self._hooks[hook_point] = [
                h for h in self._hooks[hook_point] if h.handler != handler
            ]

    def trigger(self, hook_point: HudHookPoint, context: HudHookContext) -> HudHookResult:
        """Execute all registered hooks for a HUD hook point sequentially by priority."""
        registered = self._hooks.get(hook_point, [])
        for item in registered:
            if context.is_cancelled:
                break
            item.handler(context)

        return HudHookResult(
            hook_point=hook_point,
            success=not context.is_cancelled,
            cancelled=context.is_cancelled,
            cancel_reason=context.cancel_reason,
            data=context.data,
        )
