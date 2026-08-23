"""Tests for HUD event bus and lifecycle event dispatching."""

from hud import (
    STATE_SYNCHRONIZED,
    VIEW_RENDERED,
    HudEvent,
    HudEventBus,
)


def test_hud_event_bus_publish() -> None:
    received: list[HudEvent] = []

    bus = HudEventBus()
    bus.subscribe(VIEW_RENDERED, lambda e: received.append(e))

    event = HudEvent(name=VIEW_RENDERED, payload={"view_id": "dashboard", "timestamp": 12345.0})
    bus.publish(event)

    assert len(received) == 1
    assert received[0].name == VIEW_RENDERED
    assert received[0].payload["view_id"] == "dashboard"


def test_hud_event_bus_unsubscribe() -> None:
    received: list[HudEvent] = []

    def handler(e: HudEvent) -> None:
        received.append(e)

    bus = HudEventBus()
    bus.subscribe(STATE_SYNCHRONIZED, handler)
    bus.unsubscribe(STATE_SYNCHRONIZED, handler)

    bus.publish(HudEvent(name=STATE_SYNCHRONIZED, payload={"synced_keys": ["k1"]}))
    assert len(received) == 0
