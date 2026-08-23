"""Tests for HudHookRegistry and UI hook interception pipeline."""

import pytest
from typing import Any
from hud import (
    HudClient,
    HudHookCancelledError,
    HudHookContext,
    HudHookPoint,
    HudHookRegistry,
    Priority,
)

class MockBackend:
    @property
    def status(self) -> str:
        return "RUNNING"
        
    def submit(self, prompt: str, request_id: str, context: dict[str, Any] | None = None) -> dict[str, Any]:
        return {"request_id": request_id, "output": f"ACK: {prompt}"}


def test_hud_hook_priority_and_mutation() -> None:
    order: list[str] = []

    def normal_handler(ctx: HudHookContext) -> None:
        order.append("normal")
        ctx.data["prompt"] = "mutated command"

    def high_handler(ctx: HudHookContext) -> None:
        order.append("high")

    registry = HudHookRegistry()
    registry.register(HudHookPoint.PRE_VIEW_RENDER, normal_handler, priority=Priority.NORMAL)
    registry.register(HudHookPoint.PRE_VIEW_RENDER, high_handler, priority=Priority.HIGH)

    backend = MockBackend()
    client = HudClient(backend=backend, hook_registry=registry)
    resp = client.submit_command("initial command", request_id="hud-h1")

    assert order == ["high", "normal"]
    assert "ACK: mutated command" in resp["output"]


def test_hud_hook_cancellation() -> None:
    def block_hook(ctx: HudHookContext) -> None:
        ctx.cancel("UI action blocked by security policy.")

    registry = HudHookRegistry()
    registry.register(HudHookPoint.PRE_VIEW_RENDER, block_hook)

    backend = MockBackend()
    client = HudClient(backend=backend, hook_registry=registry)

    with pytest.raises(HudHookCancelledError) as exc_info:
        client.submit_command("valid command", request_id="hud-h2")

    assert exc_info.value.code == "hud.hook.cancelled"
    assert exc_info.value.hook_point == "PRE_VIEW_RENDER"
