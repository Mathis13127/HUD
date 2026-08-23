"""Configuration loader for the HUD Production Daemon."""

import json
from pathlib import Path
from dataclasses import dataclass, field


@dataclass
class DaemonConfig:
    """Daemon configuration structure."""
    autostart_widgets: list[str] = field(default_factory=list)


def load_daemon_config(config_path: Path) -> DaemonConfig:
    """Load configuration from a JSON file. Returns empty defaults if missing."""
    if not config_path.is_file():
        return DaemonConfig()
        
    try:
        data = json.loads(config_path.read_text(encoding="utf-8"))
        widgets = data.get("autostart_widgets", [])
        return DaemonConfig(autostart_widgets=widgets)
    except Exception:
        return DaemonConfig()
