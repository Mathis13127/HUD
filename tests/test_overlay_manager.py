"""Unit tests for the Overlay Manager bridging single-file bundles and the PySide6 UI."""

from pathlib import Path

import pytest
from PySide6.QtWidgets import QWidget

from hud.bundle.loader import HudBundleLoader
from hud.errors import WidgetTypeError
from hud.events.bus import HudEventBus
from hud.overlay.engine import HudOverlayWindow
from hud.overlay.manager import HudOverlayManager


def test_overlay_manager_valid_widget(qtbot, tmp_path: Path) -> None:
    # Setup single-file bundle
    widget_file = tmp_path / "valid_widget.py"
    widget_file.write_text(
        "MANIFEST = {\n"
        "    'id': 'test.qt.bundle',\n"
        "    'name': 'Test Qt'\n"
        "}\n"
        "from PySide6.QtWidgets import QWidget\n"
        "class Widget(QWidget):\n"
        "    def mount(self): pass\n",
        encoding="utf-8"
    )

    loader = HudBundleLoader()
    bus = HudEventBus()
    overlay = HudOverlayWindow()
    qtbot.addWidget(overlay)

    manager = HudOverlayManager(overlay=overlay, bundle_loader=loader, event_bus=bus)
    
    events = []
    bus.subscribe("HUD_BUNDLE_MOUNTED", lambda e: events.append(e))

    bundle_id = manager.register(widget_file)
    manager.mount(bundle_id)

    assert bundle_id == "test.qt.bundle"
    assert "test.qt.bundle" in overlay._mounted_widgets
    assert isinstance(overlay._mounted_widgets["test.qt.bundle"], QWidget)
    assert len(events) == 1
    assert events[0].payload["bundle_id"] == "test.qt.bundle"


def test_overlay_manager_invalid_widget_type(tmp_path: Path) -> None:
    # Setup bundle that exports a non-QWidget
    widget_file = tmp_path / "bad_widget.py"
    widget_file.write_text(
        "MANIFEST = {'id': 'bad.bundle', 'name': 'Bad'}\n"
        "class Widget:\n"
        "    def mount(self): pass\n",
        encoding="utf-8"
    )

    loader = HudBundleLoader()
    bus = HudEventBus()
    overlay = HudOverlayWindow()

    manager = HudOverlayManager(overlay=overlay, bundle_loader=loader, event_bus=bus)

    with pytest.raises(WidgetTypeError) as exc:
        manager.register(widget_file)

    assert exc.value.code == "hud.overlay.invalid_widget_type"
    assert exc.value.bundle_id == "bad.bundle"
    assert exc.value.found_type == "Widget"
