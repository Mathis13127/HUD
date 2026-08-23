"""HUD transparent overlay window and PySide6 engine."""

from typing import Any

from PySide6.QtCore import Qt, QPoint
from PySide6.QtWidgets import QWidget, QApplication

from hud.api.models import WidgetPlacement
from hud.overlay.layout import calculate_absolute_position


class HudOverlayWindow(QWidget):
    """The invisible, full-screen transparent overlay host for HUD widgets."""

    def __init__(self) -> None:
        super().__init__()
        self._mounted_widgets: dict[str, QWidget] = {}

        self.setWindowTitle("JARVIS HUD Overlay")
        self._configure_transparency()

    def _configure_transparency(self) -> None:
        """Set all required PySide6 flags to make the window invisible and click-through."""
        # Frameless, Stays on top, acts as a Tool (doesn't steal focus), click-through
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
            | Qt.WindowType.WindowTransparentForInput
        )
        
        # Make the background fully transparent
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setStyleSheet("background: transparent;")

    def maximize_to_screen(self) -> None:
        """Expand the overlay to fill the primary screen."""
        screen = QApplication.primaryScreen()
        if screen:
            self.setGeometry(screen.geometry())

    def mount_widget(self, widget: QWidget, placement: WidgetPlacement, bundle_id: str) -> None:
        """Place a loaded bundle widget onto the overlay.

        Args:
            widget: The PySide6 QWidget instance loaded from the bundle.
            placement: Anchor and offset definitions.
            bundle_id: Unique identifier for tracking and unmounting.
        """
        # Ensure widget is a child of the overlay
        widget.setParent(self)
        
        # Wait for Qt to calculate hints, or use fixed size
        widget.adjustSize()
        w_width = widget.width()
        w_height = widget.height()

        x, y = calculate_absolute_position(
            anchor=placement.anchor,
            offset_x=placement.offset_x,
            offset_y=placement.offset_y,
            widget_width=w_width,
            widget_height=w_height,
            screen_width=self.width(),
            screen_height=self.height(),
        )

        widget.move(QPoint(x, y))
        
        # Apply fade-in animation
        from PySide6.QtWidgets import QGraphicsOpacityEffect
        from PySide6.QtCore import QPropertyAnimation, QEasingCurve
        
        effect = QGraphicsOpacityEffect(widget)
        widget.setGraphicsEffect(effect)
        
        # We need to keep a reference to the animation so it isn't garbage collected
        if not hasattr(self, "_animations"):
            self._animations = []
            
        animation = QPropertyAnimation(effect, b"opacity")
        animation.setDuration(200)  # 200ms fade-in
        animation.setStartValue(0.0)
        animation.setEndValue(1.0)
        animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
        
        # Clean up reference when done
        animation.finished.connect(lambda: self._animations.remove(animation) if animation in self._animations else None)
        self._animations.append(animation)
        
        widget.show()
        animation.start()
        
        # Store reference
        self._mounted_widgets[bundle_id] = widget

    def unmount_widget(self, bundle_id: str) -> None:
        """Remove a widget from the overlay and destroy it gracefully.

        Args:
            bundle_id: The ID of the mounted widget.
        """
        if bundle_id in self._mounted_widgets:
            widget = self._mounted_widgets.pop(bundle_id)
            
            # Animate fade out
            from PySide6.QtWidgets import QGraphicsOpacityEffect
            from PySide6.QtCore import QPropertyAnimation, QEasingCurve
            
            effect = widget.graphicsEffect()
            if not isinstance(effect, QGraphicsOpacityEffect):
                effect = QGraphicsOpacityEffect(widget)
                widget.setGraphicsEffect(effect)
                
            if not hasattr(self, "_animations"):
                self._animations = []
                
            animation = QPropertyAnimation(effect, b"opacity")
            animation.setDuration(200)
            animation.setStartValue(1.0)
            animation.setEndValue(0.0)
            animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
            
            # Clean up properly after animation
            def _on_finished():
                if animation in self._animations:
                    self._animations.remove(animation)
                widget.hide()
                widget.deleteLater()
                
            animation.finished.connect(_on_finished)
            self._animations.append(animation)
            animation.start()
