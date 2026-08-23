"""Typed domain exception taxonomy for the hud UI interface package.

Adheres strictly to Rule L2: typed errors with semantic namespaced machine-readable codes.
"""

from __future__ import annotations

from typing import Any


class HudError(Exception):
    """Base exception for all domain errors within hud."""

    def __init__(
        self,
        message: str,
        code: str = "hud.error.generic",
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(f"[{code}] {message}")
        self.message = message
        self.code = code
        self.details = details or {}


class ViewRenderError(HudError):
    """Raised when rendering a HUD visual component or view state fails."""

    def __init__(self, view_id: str, reason: str) -> None:
        self.view_id = view_id
        self.reason = reason
        super().__init__(
            message=f"Failed to render HUD view '{view_id}': {reason}.",
            code="hud.view.render_failed",
            details={"view_id": view_id, "reason": reason},
        )


class StateSyncError(HudError):
    """Raised when state synchronization between HUD UI and backend engines fails."""

    def __init__(self, sync_target: str, reason: str) -> None:
        self.sync_target = sync_target
        self.reason = reason
        super().__init__(
            message=f"HUD state synchronization failed for target '{sync_target}': {reason}.",
            code="hud.state.sync_failed",
            details={"sync_target": sync_target, "reason": reason},
        )


class InvalidUiStateError(HudError):
    """Raised when a UI interaction occurs in an unsupported state."""

    def __init__(self, current_state: str, operation: str) -> None:
        self.current_state = current_state
        self.operation = operation
        super().__init__(
            message=f"Cannot execute UI operation '{operation}' in state '{current_state}'.",
            code="hud.state.invalid",
            details={"current_state": current_state, "operation": operation},
        )


class HudHookCancelledError(HudError):
    """Raised when a HUD UI hook intercepts and intentionally cancels an action."""

    def __init__(self, hook_point: str, reason: str) -> None:
        self.hook_point = hook_point
        self.reason = reason
        super().__init__(
            message=f"HUD interaction cancelled at hook '{hook_point}': {reason}",
            code="hud.hook.cancelled",
            details={"hook_point": hook_point, "reason": reason},
        )


class ManifestValidationError(HudError):
    """Raised when a widget bundle manifest.json is invalid or missing required fields."""

    def __init__(self, bundle_path: str, missing_fields: list[str]) -> None:
        self.bundle_path = bundle_path
        self.missing_fields = missing_fields
        super().__init__(
            message=f"Invalid manifest.json in bundle '{bundle_path}'. Missing: {', '.join(missing_fields)}",
            code="hud.bundle.manifest_invalid",
            details={"bundle_path": bundle_path, "missing_fields": missing_fields},
        )


class WidgetLoadError(HudError):
    """Raised when a widget bundle fails to load or dynamically import."""

    def __init__(self, bundle_id: str, reason: str) -> None:
        self.bundle_id = bundle_id
        self.reason = reason
        super().__init__(
            message=f"Failed to load HUD widget bundle '{bundle_id}': {reason}",
            code="hud.bundle.load_failed",
            details={"bundle_id": bundle_id, "reason": reason},
        )


class WidgetTypeError(HudError):
    """Raised when a dynamically loaded bundle entry point does not inherit from QWidget."""

    def __init__(self, bundle_id: str, found_type: str) -> None:
        self.bundle_id = bundle_id
        self.found_type = found_type
        super().__init__(
            message=f"Widget bundle '{bundle_id}' must export a QWidget, found '{found_type}'.",
            code="hud.overlay.invalid_widget_type",
            details={"bundle_id": bundle_id, "found_type": found_type},
        )


class WidgetPlacementError(HudError):
    """Raised when an invalid anchor is requested for widget placement."""

    def __init__(self, anchor: str) -> None:
        self.anchor = anchor
        super().__init__(
            message=f"Invalid layout anchor '{anchor}'.",
            code="hud.overlay.invalid_anchor",
            details={"anchor": anchor},
        )

class WidgetAlreadyMountedError(HudError):
    def __init__(self, bundle_id: str) -> None:
        super().__init__(
            message=f"Widget '{bundle_id}' is already mounted.",
            code="hud.overlay.already_mounted",
            details={"bundle_id": bundle_id}
        )

class WidgetNotRegisteredError(HudError):
    def __init__(self, bundle_id: str) -> None:
        super().__init__(
            message=f"Widget '{bundle_id}' is not registered.",
            code="hud.overlay.not_registered",
            details={"bundle_id": bundle_id}
        )
