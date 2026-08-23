"""Unit tests for the HUD Studio Controller single-file logic."""

from pathlib import Path

import pytest

from hud.events.bus import HudEventBus
from hud.bundle.loader import HudBundleLoader
from hud.overlay.engine import HudOverlayWindow
from hud.overlay.manager import HudOverlayManager
from hud.studio.controller import StudioController
from hud.studio.panels.editor import WorkspaceEditor
from hud.studio.panels.explorer import BundleExplorer
from hud.studio.panels.preview_control import ControlPanel


def test_studio_controller_dry_run_validation(qtbot, tmp_path: Path) -> None:
    """Ensure the controller handles saving and mounting valid/invalid code properly."""
    bundles_dir = tmp_path / "bundles"
    bundles_dir.mkdir()
    
    loader = HudBundleLoader()
    bus = HudEventBus()
    overlay = HudOverlayWindow()
    qtbot.addWidget(overlay)
    
    manager = HudOverlayManager(overlay=overlay, bundle_loader=loader, event_bus=bus)
    
    explorer = BundleExplorer(bundles_dir)
    editor = WorkspaceEditor()
    control = ControlPanel()
    
    qtbot.addWidget(explorer)
    qtbot.addWidget(editor)
    qtbot.addWidget(control)
    
    controller = StudioController(
        overlay_manager=manager,
        explorer=explorer,
        editor=editor,
        control=control,
        bundles_dir=bundles_dir,
    )
    
    active_file = bundles_dir / "test_widget.py"
    controller._active_file_path = active_file
    
    # 1. Test deploying empty / invalid files
    editor.code_editor.setPlainText("invalid python code!!!")
    controller.deploy_active_bundle()
    
    # Ensure logs reflect errors (dry run failed, didn't mount)
    logs = control.log_console.toPlainText()
    assert "Erreur de Validation" in logs
    assert controller._active_bundle_id is None
    
    # 2. Test deploying valid files
    editor.code_editor.setPlainText(
        "MANIFEST = {'id': 'test.widget', 'name': 'T'}\n"
        "from PySide6.QtWidgets import QWidget\n"
        "class Widget(QWidget):\n"
        "    pass"
    )
    
    controller.deploy_active_bundle()
    
    logs = control.log_console.toPlainText()
    assert "Hot-Reload Réussi" in logs
    assert controller._active_bundle_id == "test.widget"
