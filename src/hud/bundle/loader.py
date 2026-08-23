"""Dynamic loader for HUD Widget single-file scripts."""

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
    """Loads a PySide6 widget dynamically from raw source code."""

    def __init__(self) -> None:
        self.hooks = HudHookRegistry()
        self.events = HudEventBus()

    def load_bundle_from_source(self, source_code: str) -> tuple[Any, HudWidgetManifest]:
        """Validate, compile, and load a widget directly from a source code string (In-Memory)."""
        from hud.bundle.sandbox import HudAstValidator
        
        # 1. AST Validation
        validator = HudAstValidator()
        validator.validate(source_code)
        
        self.hooks.trigger(HudHookPoint.PRE_BUNDLE_LOAD, HudHookContext(hook_point=HudHookPoint.PRE_BUNDLE_LOAD, data={"source_length": len(source_code)}))
        
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

        self.hooks.trigger(HudHookPoint.POST_BUNDLE_LOAD, HudHookContext(hook_point=HudHookPoint.POST_BUNDLE_LOAD, data={"manifest": manifest, "instance": widget_instance}))

        return widget_instance, manifest
