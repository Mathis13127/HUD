"""Parser for the HUD Widget Manifest."""

from typing import Any

from hud.api.models import HudWidgetManifest, WidgetPlacement
from hud.errors import ManifestValidationError


def parse_manifest(data: dict[str, Any], file_path: str = "unknown") -> HudWidgetManifest:
    """Parse and validate a Python dictionary into a HudWidgetManifest.

    Args:
        data: The dictionary loaded from the module's MANIFEST attribute.
        file_path: Reference path for error reporting.

    Returns:
        A validated HudWidgetManifest instance.

    Raises:
        ManifestValidationError: If required fields are missing or types are invalid.
    """
    # Note: "entry_point" is no longer strictly necessary since the class is usually 'Widget'
    # but we will keep it for compatibility, or default it. Let's just require id and name.
    required_fields = ["id", "name"]
    missing = [field for field in required_fields if field not in data]

    if missing:
        raise ManifestValidationError(bundle_path=file_path, missing_fields=missing)

    placement = None
    if "default_placement" in data:
        p_data = data["default_placement"]
        # If it's already a WidgetPlacement instance (possible in pure Python!)
        if isinstance(p_data, WidgetPlacement):
            placement = p_data
        else:
            placement = WidgetPlacement(
                anchor=p_data.get("anchor", "center"),
                offset_x=p_data.get("offset_x", 0),
                offset_y=p_data.get("offset_y", 0)
            )

    return HudWidgetManifest(
        id=data["id"],
        name=data["name"],
        version=data.get("version", "1.0"),
        author=data.get("author", "unknown"),
        entry_point=data.get("entry_point", "Widget"), # Default to looking for a 'Widget' class
        default_placement=placement,
    )
