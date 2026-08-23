"""Integration manager bridging the Bundle Loader and the Overlay Window."""

from pathlib import Path

from PySide6.QtWidgets import QWidget

from hud.bundle.loader import HudBundleLoader
from hud.errors import WidgetTypeError
from hud.events.bus import HudEventBus
from hud.events.definitions import HUD_BUNDLE_MOUNTED, HUD_BUNDLE_UNMOUNTED, HUD_WIDGET_ERROR
from hud.events.types import HudEvent
from hud.overlay.engine import HudOverlayWindow
from hud.overlay.layout import calculate_absolute_position


class HudOverlayManager:
    """Manages the lifecycle of dynamic widgets on the PySide6 overlay."""

    def __init__(
        self,
        overlay: HudOverlayWindow,
        bundle_loader: HudBundleLoader,
        event_bus: HudEventBus,
    ) -> None:
        self._overlay = overlay
        self._loader = bundle_loader
        self._event_bus = event_bus
        self._registered_bundles: dict[str, tuple[QWidget, Any]] = {}

    def get_registered(self) -> list[str]:
        """Return a list of all registered bundle IDs."""
        return list(self._registered_bundles.keys())

    def get_mounted(self) -> list[str]:
        """Return a list of all currently mounted bundle IDs."""
        return list(self._overlay._mounted_widgets.keys())

    def register(self, file_path: Path) -> str:
        """Parse and load a widget into memory without mounting it.

        Args:
            file_path: Absolute path to the .py widget file.

        Returns:
            The loaded bundle ID.
            
        Raises:
            WidgetLoadError: If loading fails.
            WidgetTypeError: If the bundle does not export a QWidget.
            ManifestValidationError: If the manifest is invalid.
        """
        widget_instance, manifest = self._loader.load_bundle(file_path)

        if not isinstance(widget_instance, QWidget):
            raise WidgetTypeError(
                bundle_id=manifest.id,
                found_type=type(widget_instance).__name__
            )

        self._registered_bundles[manifest.id] = (widget_instance, manifest)
        return manifest.id

    def mount(self, bundle_id: str) -> None:
        """Mount a registered widget to the overlay.

        Args:
            bundle_id: The ID of the registered widget to mount.
            
        Raises:
            WidgetLoadError: If the bundle is not registered.
            WidgetPlacementError: If the default placement anchor is invalid.
        """
        if bundle_id not in self._registered_bundles:
            raise WidgetLoadError(bundle_id=bundle_id, reason="Widget not registered.")
            
        widget_instance, manifest = self._registered_bundles[bundle_id]
        
        if bundle_id in self._overlay._mounted_widgets:
            return  # Already mounted

        # Handle optional placement gracefully
        placement = manifest.default_placement
        if not placement:
            # Fallback to center if not specified
            from hud.api.models import WidgetPlacement
            placement = WidgetPlacement(anchor="center")

        # Mount to Qt Window
        self._overlay.mount_widget(
            widget=widget_instance,
            placement=placement,
            bundle_id=manifest.id
        )

        # Trigger internal protocol hook if present
        if hasattr(widget_instance, "mount") and callable(widget_instance.mount):
            try:
                widget_instance.mount()
            except Exception as exc:
                self._event_bus.publish(
                    HudEvent(
                        name="HUD_WIDGET_ERROR",
                        payload={"bundle_id": manifest.id, "error": str(exc)},
                        source="hud.overlay.manager"
                    )
                )

        # Broadcast success
        self._event_bus.publish(
            HudEvent(
                name="HUD_BUNDLE_MOUNTED",
                payload={"bundle_id": manifest.id},
                source="hud.overlay.manager"
            )
        )

    def unmount(self, bundle_id: str) -> None:
        """Unmount and destroy a loaded bundle."""
        self._overlay.unmount_widget(bundle_id)
        
        self._event_bus.publish(
            HudEvent(
                name=HUD_BUNDLE_UNMOUNTED,
                payload={"bundle_id": bundle_id},
                source="hud.overlay.manager"
            )
        )
