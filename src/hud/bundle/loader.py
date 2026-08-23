"""Dynamic loader for HUD Widget single-file scripts."""

import importlib.util
import sys
from pathlib import Path
from typing import Any

from hud.api.models import HudWidgetManifest
from hud.api.protocols import HudWidgetProtocol
from hud.bundle.manifest import parse_manifest
from hud.errors import WidgetLoadError
from hud.events.bus import HudEventBus
from hud.events.types import HudEvent
from hud.hooks.types import HudHookPoint, HudHookContext
from hud.hooks.registry import HudHookRegistry


class HudBundleLoader:
    """Loads a PySide6 widget dynamically from a single .py file."""

    def __init__(self) -> None:
        self.hooks = HudHookRegistry()
        self.events = HudEventBus()

    def load_bundle(self, file_path: Path) -> tuple[Any, HudWidgetManifest]:
        """Load a .py file and return the instantiated widget and its manifest.

        Args:
            file_path: Absolute path to the .py widget file.

        Returns:
            A tuple of (WidgetInstance, Manifest).

        Raises:
            WidgetLoadError: If the file cannot be found or dynamically imported.
            ManifestValidationError: If the MANIFEST dict is invalid.
        """
        # 1. Verify existence
        if not file_path.exists() or not file_path.is_file():
            raise WidgetLoadError(bundle_id="unknown", reason=f"File not found: {file_path}")

        # Execute PRE_BUNDLE_LOAD hooks
        self.hooks.trigger(HudHookPoint.PRE_BUNDLE_LOAD, HudHookContext(hook_point=HudHookPoint.PRE_BUNDLE_LOAD, data={"file_path": str(file_path)}))

        # 2. Dynamically import the python file
        module_name = f"hud_dynamic_widget_{file_path.stem}"
        spec = importlib.util.spec_from_file_location(module_name, str(file_path))
        if spec is None or spec.loader is None:
            raise WidgetLoadError(bundle_id="unknown", reason=f"Could not create module spec for {file_path.name}")

        module = importlib.util.module_from_spec(spec)
        # sys.modules registration helps with sub-imports but can cause collisions if names match.
        # We use a unique name derived from the file stem.
        sys.modules[module_name] = module

        try:
            spec.loader.exec_module(module)
        except Exception as e:
            raise WidgetLoadError(bundle_id="unknown", reason=f"Error executing module {file_path.name}: {e}")

        # 3. Extract MANIFEST dictionary
        if not hasattr(module, "MANIFEST"):
            raise WidgetLoadError(
                bundle_id="unknown", 
                reason=f"Module {file_path.name} is missing the required 'MANIFEST' dictionary."
            )
            
        manifest_data = getattr(module, "MANIFEST")
        if not isinstance(manifest_data, dict):
            raise WidgetLoadError(
                bundle_id="unknown", 
                reason=f"'MANIFEST' in {file_path.name} must be a dictionary."
            )

        manifest = parse_manifest(manifest_data, str(file_path))

        # 4. Extract Widget Class
        class_name = manifest.entry_point
        if not hasattr(module, class_name):
            raise WidgetLoadError(
                bundle_id=manifest.id,
                reason=f"Module {file_path.name} does not export the class '{class_name}'"
            )

        widget_class = getattr(module, class_name)
        
        try:
            widget_instance = widget_class()
        except Exception as e:
            raise WidgetLoadError(
                bundle_id=manifest.id,
                reason=f"Failed to instantiate {class_name}: {e}"
            )

        # Execute POST_BUNDLE_LOAD hooks
        self.hooks.trigger(HudHookPoint.POST_BUNDLE_LOAD, HudHookContext(hook_point=HudHookPoint.POST_BUNDLE_LOAD, data={"manifest": manifest, "instance": widget_instance}))

        return widget_instance, manifest
