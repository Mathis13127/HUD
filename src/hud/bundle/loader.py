"""Dynamic loader for HUD Widget single-file scripts."""

import importlib.util
import sys
from pathlib import Path
from typing import Any

from hud.api.models import HudWidgetManifest
from hud.api.protocols import HudWidgetProtocol
from hud.bundle.manifest import parse_manifest
from hud.errors import WidgetLoadError, ManifestValidationError
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
        """Load a .py file and return the instantiated widget and its manifest."""
        if not file_path.exists() or not file_path.is_file():
            raise WidgetLoadError(bundle_id="unknown", reason=f"File not found: {file_path}")

        self.hooks.trigger(HudHookPoint.PRE_BUNDLE_LOAD, HudHookContext(hook_point=HudHookPoint.PRE_BUNDLE_LOAD, data={"file_path": str(file_path)}))

        module_name = f"hud_dynamic_widget_{file_path.stem}"
        spec = importlib.util.spec_from_file_location(module_name, str(file_path))
        if spec is None or spec.loader is None:
            raise WidgetLoadError(bundle_id="unknown", reason=f"Could not create module spec for {file_path.name}")

        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module

        try:
            spec.loader.exec_module(module)
        except Exception as e:
            raise WidgetLoadError(bundle_id="unknown", reason=f"Error executing module {file_path.name}: {e}")

        if not hasattr(module, "MANIFEST") or getattr(module, "MANIFEST") is None:
            raise WidgetLoadError(bundle_id=str(file_path), reason="Bundle is missing 'MANIFEST' dictionary.")

        if not hasattr(module, "Widget") or getattr(module, "Widget") is None:
            raise WidgetLoadError(bundle_id=str(file_path), reason="Bundle is missing 'Widget' class.")

        manifest = parse_manifest(module.MANIFEST)
        widget_instance = module.Widget()

        self.hooks.trigger(HudHookPoint.POST_BUNDLE_LOAD, HudHookContext(hook_point=HudHookPoint.POST_BUNDLE_LOAD, data={"manifest": manifest, "instance": widget_instance}))

        return widget_instance, manifest


    def load_bundle_from_source(self, source_code: str) -> tuple[Any, HudWidgetManifest]:
        """Validate, compile, and load a widget directly from a source code string (In-Memory)."""
        from hud.bundle.sandbox import HudAstValidator
        
        # 1. AST Validation
        validator = HudAstValidator()
        validator.validate(source_code)
        
        # 2. Compile to bytecode
        try:
            bytecode = compile(source_code, "<string>", "exec")
        except Exception as e:
            raise WidgetLoadError(bundle_id="<in-memory>", reason=f"Compilation failed: {e}")
            
        # 3. Create isolated module and execute
        import types
        module = types.ModuleType("hud_dynamic_in_memory")
        
        try:
            exec(bytecode, module.__dict__)
        except Exception as e:
            raise WidgetLoadError(bundle_id="<in-memory>", reason=f"Execution failed: {e}")
            
        # 4. Verify attributes
        if not hasattr(module, "MANIFEST") or getattr(module, "MANIFEST") is None:
            raise WidgetLoadError(bundle_id="<in-memory>", reason="In-Memory bundle is missing 'MANIFEST' dictionary.")

        if not hasattr(module, "Widget") or getattr(module, "Widget") is None:
            raise WidgetLoadError(bundle_id="<in-memory>", reason="In-Memory bundle is missing 'Widget' class.")

        # 5. Parse manifest and instantiate
        manifest = parse_manifest(module.MANIFEST)
        widget_instance = module.Widget()

        return widget_instance, manifest
