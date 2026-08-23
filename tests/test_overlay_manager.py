"""Tests for the HUD Overlay Manager."""

import pytest
from PySide6.QtWidgets import QWidget

from hud.overlay.manager import HudOverlayManager
from hud.overlay.engine import HudOverlayWindow
from hud.bundle.loader import HudBundleLoader
from hud.events.bus import HudEventBus
from hud.errors import WidgetAlreadyMountedError, WidgetNotRegisteredError, WidgetTypeError


def test_overlay_manager_valid_widget(qtbot) -> None:
    code = (
        "from PySide6.QtWidgets import QWidget\n"
        "MANIFEST = {\n"
        "    'id': 'jarvis.hud.test',\n"
        "    'name': 'Test',\n"
        "    'default_placement': {'anchor': 'top_left'}\n"
        "}\n"
        "class Widget(QWidget):\n"
        "    pass\n"
    )

    overlay = HudOverlayWindow()
    loader = HudBundleLoader()
    bus = HudEventBus()
    
    manager = HudOverlayManager(overlay, loader, bus)
    
    bundle_id = manager.register_code(code)
    assert bundle_id == "jarvis.hud.test"
    
    manager.mount(bundle_id)
    assert bundle_id in manager.get_mounted()
    
    with pytest.raises(WidgetAlreadyMountedError):
        manager.mount(bundle_id)
        
    manager.unmount(bundle_id)
    assert bundle_id not in manager.get_mounted()


def test_overlay_manager_invalid_widget_type(qtbot) -> None:
    # Not a QWidget
    code = (
        "MANIFEST = {\n"
        "    'id': 'jarvis.hud.bad',\n"
        "    'name': 'Bad'\n"
        "}\n"
        "class Widget:\n"
        "    pass\n"
    )

    overlay = HudOverlayWindow()
    loader = HudBundleLoader()
    bus = HudEventBus()
    
    manager = HudOverlayManager(overlay, loader, bus)
    
    with pytest.raises(WidgetTypeError):
        manager.register_code(code)
