"""Tests for HudClient interacting with Backend via public API."""

import pytest
from typing import Any
from hud import (
    HudClient,
    HudEvent,
    HudEventBus,
    ViewRenderError,
)

class MockBackend:
    @property
    def status(self) -> str:
        return "RUNNING"
        
    def submit(self, prompt: str, request_id: str, context: dict[str, Any] | None = None) -> dict[str, Any]:
        return {"request_id": request_id, "output": f"ACK: {prompt}"}


def test_hud_client_status_poll_and_submit() -> None:
    backend = MockBackend()
    events_received: list[HudEvent] = []
    bus = HudEventBus()
    bus.subscribe("STATE_SYNCHRONIZED", lambda e: events_received.append(e))

    hud = HudClient(backend=backend, event_bus=bus)
    status = hud.poll_backend_status()
    assert status == "RUNNING"

    response = hud.submit_command("Display diagnostics", request_id="hud-cmd-1")
    assert response["request_id"] == "hud-cmd-1"
    assert "ACK: Display diagnostics" in response["output"]

    state = hud.get_view_state()
    assert state.backend_status == "RUNNING"
    assert state.last_request_id == "hud-cmd-1"
    assert len(events_received) >= 1


def test_hud_client_empty_command_raises_typed_error() -> None:
    backend = MockBackend()
    hud = HudClient(backend=backend)

    with pytest.raises(ViewRenderError) as exc_info:
        hud.submit_command("", request_id="hud-empty")

    assert exc_info.value.code == "hud.view.render_failed"
    assert exc_info.value.view_id == "hud.command_prompt"
