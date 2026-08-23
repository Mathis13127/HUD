"""Layout and coordinate calculation for HUD widgets."""

from hud.errors import WidgetPlacementError


def calculate_absolute_position(
    anchor: str,
    offset_x: int,
    offset_y: int,
    widget_width: int,
    widget_height: int,
    screen_width: int,
    screen_height: int,
) -> tuple[int, int]:
    """Calculate the absolute screen (x, y) coordinates for a widget based on its placement.

    Args:
        anchor: The string identifier for the anchor point (e.g., 'top_left', 'center').
        offset_x: Horizontal shift from the anchor point.
        offset_y: Vertical shift from the anchor point.
        widget_width: Computed width of the widget.
        widget_height: Computed height of the widget.
        screen_width: Available width of the target screen.
        screen_height: Available height of the target screen.

    Returns:
        (x, y) coordinates for the top-left corner of the widget.

    Raises:
        WidgetPlacementError: If the anchor string is unrecognized.
    """
    anchor_norm = anchor.lower().strip()

    # Base X coordinate calculation
    if "left" in anchor_norm:
        base_x = 0
    elif "right" in anchor_norm:
        base_x = screen_width - widget_width
    elif "center" in anchor_norm or anchor_norm in ("top", "bottom"):
        base_x = (screen_width - widget_width) // 2
    else:
        raise WidgetPlacementError(anchor=anchor)

    # Base Y coordinate calculation
    if "top" in anchor_norm:
        base_y = 0
    elif "bottom" in anchor_norm:
        base_y = screen_height - widget_height
    elif "center" in anchor_norm or anchor_norm in ("left", "right"):
        base_y = (screen_height - widget_height) // 2
    else:
        # We already checked for valid strings in X calculation but for safety:
        raise WidgetPlacementError(anchor=anchor)

    # Combine with offsets
    return (base_x + offset_x, base_y + offset_y)
