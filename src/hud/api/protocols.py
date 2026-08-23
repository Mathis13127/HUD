"""Public protocol interfaces (PEP 544) for the hud package."""

from __future__ import annotations

from typing import Any, Protocol

from hud.api.models import HudViewState


class BackendProtocol(Protocol):
    """Protocol defining how HUD communicates with its host backend."""
    
    @property
    def status(self) -> str:
        """Get the current backend status as a string."""
        ...
        
    def submit(self, prompt: str, request_id: str, context: dict[str, Any] | None = None) -> dict[str, Any]:
        """Submit a command to the backend."""
        ...


class HudRendererProtocol(Protocol):
    """Protocol for HUD view renderers."""

    def render(self, state: HudViewState) -> None:
        """Render the viewport with updated state."""
        ...


class StateSyncProtocol(Protocol):
    """Protocol for HUD backend state synchronization."""

    def sync(self) -> str:
        """Synchronize with backend status."""
        ...


class HudClientProtocol(Protocol):
    """Protocol for unified HUD client interface."""

    def poll_backend_status(self) -> str:
        """Poll the current status of the backend."""
        ...

    def submit_command(
        self,
        prompt: str,
        request_id: str,
        context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Submit command to backend."""
        ...

    def get_view_state(self) -> HudViewState:
        """Return the current immutable HUD view state."""
        ...


class HudWidgetProtocol(Protocol):
    """Protocol that all dynamic HUD widget bundles must implement."""

    def mount(self) -> None:
        """Called when the widget is loaded and attached to the UI."""
        ...

    def unmount(self) -> None:
        """Called when the widget is removed from the UI."""
        ...

    def render(self, context: dict[str, Any] | None = None) -> None:
        """Called to update the widget's visual state with new context."""
        ...
