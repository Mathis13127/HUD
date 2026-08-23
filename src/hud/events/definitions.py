"""Documented standard event names for hud UI package (Rule L4)."""

VIEW_RENDERED: str = "VIEW_RENDERED"
"""Triggered when a HUD viewport or component state is updated and rendered.
Payload schema: {"view_id": str, "timestamp": float}
"""

STATE_SYNCHRONIZED: str = "STATE_SYNCHRONIZED"
"""Triggered when the HUD successfully polls and synchronizes state with the engine.
Payload schema: {"synced_keys": list[str], "engine_status": str}
"""

HUD_BUNDLE_MOUNTED: str = "HUD_BUNDLE_MOUNTED"
"""Triggered when a HUD widget bundle is dynamically loaded and mounted.
Payload schema: {"bundle_id": str, "version": str, "placement": str}
"""

HUD_BUNDLE_UNMOUNTED: str = "HUD_BUNDLE_UNMOUNTED"
"""Triggered when a HUD widget bundle is unmounted and removed from the UI.
Payload schema: {"bundle_id": str}
"""

HUD_WIDGET_ERROR: str = "HUD_WIDGET_ERROR"
"""Triggered when a HUD widget encounters an internal error.
Payload schema: {"bundle_id": str, "error": str}
"""
