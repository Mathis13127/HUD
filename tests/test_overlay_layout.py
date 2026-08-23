"""Unit tests for HUD overlay layout coordinate math."""

import pytest

from hud.errors import WidgetPlacementError
from hud.overlay.layout import calculate_absolute_position


def test_calculate_absolute_position_top_left() -> None:
    x, y = calculate_absolute_position(
        anchor="top_left",
        offset_x=10,
        offset_y=15,
        widget_width=100,
        widget_height=50,
        screen_width=1920,
        screen_height=1080,
    )
    assert x == 10
    assert y == 15


def test_calculate_absolute_position_bottom_right() -> None:
    x, y = calculate_absolute_position(
        anchor="bottom_right",
        offset_x=-10,
        offset_y=-15,
        widget_width=100,
        widget_height=50,
        screen_width=1920,
        screen_height=1080,
    )
    assert x == 1920 - 100 - 10
    assert y == 1080 - 50 - 15


def test_calculate_absolute_position_center() -> None:
    x, y = calculate_absolute_position(
        anchor="center",
        offset_x=0,
        offset_y=0,
        widget_width=200,
        widget_height=100,
        screen_width=1920,
        screen_height=1080,
    )
    assert x == (1920 - 200) // 2
    assert y == (1080 - 100) // 2


def test_calculate_absolute_position_invalid_anchor() -> None:
    with pytest.raises(WidgetPlacementError) as exc:
        calculate_absolute_position(
            anchor="middle_nowhere",
            offset_x=0,
            offset_y=0,
            widget_width=100,
            widget_height=50,
            screen_width=1920,
            screen_height=1080,
        )
    assert "middle_nowhere" in str(exc.value)
