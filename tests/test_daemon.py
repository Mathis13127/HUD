"""Unit tests for the HUD Production Daemon."""

import json
from pathlib import Path

from hud.daemon.config import load_daemon_config


def test_load_daemon_config_empty(tmp_path: Path) -> None:
    config_path = tmp_path / "missing.json"
    config = load_daemon_config(config_path)
    assert config.autostart_widgets == []


def test_load_daemon_config_valid(tmp_path: Path) -> None:
    config_path = tmp_path / "valid.json"
    config_path.write_text(json.dumps({"autostart_widgets": ["test1.py", "test2.py"]}))
    
    config = load_daemon_config(config_path)
    assert config.autostart_widgets == ["test1.py", "test2.py"]


def test_load_daemon_config_invalid_json(tmp_path: Path) -> None:
    config_path = tmp_path / "invalid.json"
    config_path.write_text("not json at all")
    
    config = load_daemon_config(config_path)
    assert config.autostart_widgets == []
