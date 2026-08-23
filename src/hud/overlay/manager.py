"""Overlay Manager to handle widget lifecycles on the screen."""

from PySide6.QtWidgets import QWidget
from typing import Any

from hud.api.models import HudWidgetManifest
from hud.bundle.loader import HudBundleLoader
from hud.errors import WidgetAlreadyMountedError, WidgetNotRegisteredError, WidgetTypeError
from hud.events.bus import HudEventBus
from hud.overlay.engine import HudOverlayWindow
from hud.overlay.layout import calculate_absolute_position


class HudOverlayManager:
    """Manages the registration and mounting of widgets onto the Overlay."""

    def __init__(self, overlay: HudOverlayWindow, bundle_loader: HudBundleLoader, event_bus: HudEventBus) -> None:
        self.overlay = overlay
        self._loader = bundle_loader
        self._event_bus = event_bus
        
        # bundle_id -> (WidgetInstance, Manifest, source_code)
        self._registered_bundles: dict[str, tuple[QWidget, HudWidgetManifest, str]] = {}
        # bundle_id -> True
        self._mounted_bundles: dict[str, bool] = {}

    def get_code(self, bundle_id: str) -> str | None:
        """Retrieve the source code of a registered widget."""
        if bundle_id in self._registered_bundles:
            return self._registered_bundles[bundle_id][2]
        return None

    def register_code(self, source_code: str) -> str:
        """Parse and load a widget into memory from raw source code (In-Memory).

        Args:
            source_code: Raw Python code string containing MANIFEST and Widget.

        Returns:
            The loaded bundle ID.
            
        Raises:
            WidgetSecurityError: If code violates the AST sandbox.
            WidgetLoadError: If compilation or loading fails.
            WidgetTypeError: If the bundle does not export a QWidget.
            ManifestValidationError: If the manifest is invalid.
        """
        widget_instance, manifest = self._loader.load_bundle_from_source(source_code)

        if not isinstance(widget_instance, QWidget):
            raise WidgetTypeError(
                bundle_id=manifest.id,
                found_type=type(widget_instance).__name__
            )

        if manifest.id in self._registered_bundles:
            self.unregister(manifest.id)

        self._registered_bundles[manifest.id] = (widget_instance, manifest, source_code)
        return manifest.id

    def unregister(self, bundle_id: str) -> None:
        """Remove a widget completely from memory. If mounted, it unmounts it first."""
        if bundle_id in self._registered_bundles:
            self.unmount(bundle_id)
            del self._registered_bundles[bundle_id]

    def mount(self, bundle_id: str) -> None:
        """Mount a registered widget to the overlay."""
        if bundle_id not in self._registered_bundles:
            raise WidgetNotRegisteredError(bundle_id)
            
        if bundle_id in self._mounted_bundles:
            raise WidgetAlreadyMountedError(bundle_id)
            
        widget_instance, manifest, _ = self._registered_bundles[bundle_id]
        
        if hasattr(widget_instance, "mount"):
            widget_instance.mount()

        widget_instance.setParent(self.overlay)
        if manifest.default_placement:
            pos_tuple = calculate_absolute_position(
                manifest.default_placement.anchor,
                manifest.default_placement.offset_x,
                manifest.default_placement.offset_y,
                widget_instance.width(),
                widget_instance.height(),
                self.overlay.width(),
                self.overlay.height()
            )
            widget_instance.move(pos_tuple[0], pos_tuple[1])
            
        widget_instance.show()
        
        self._mounted_bundles[bundle_id] = True

    def unmount(self, bundle_id: str) -> None:
        """Hide and unmount a widget from the overlay."""
        if bundle_id not in self._mounted_bundles:
            return
            
        widget_instance, _, _ = self._registered_bundles[bundle_id]
        
        if hasattr(widget_instance, "unmount"):
            widget_instance.unmount()
            
        widget_instance.hide()
        widget_instance.setParent(None)
        
        del self._mounted_bundles[bundle_id]

    def get_registered(self) -> list[str]:
        """Return a list of all registered bundle IDs."""
        return list(self._registered_bundles.keys())

    def get_mounted(self) -> list[str]:
        """Return a list of all currently mounted bundle IDs."""
        return list(self._mounted_bundles.keys())
