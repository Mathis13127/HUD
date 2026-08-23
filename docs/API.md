# packages/hud Public API Specification

## Module: `hud.api`

### Models (`hud.api.models`)
- `HudViewState`: Dataclass (`engine_status: EngineStatus`, `last_request_id: str | None`, `last_updated: float`).

### Protocols (`hud.api.protocols`)
- `HudRendererProtocol`: Contract for UI components rendering view state.
- `StateSyncProtocol`: Contract for engine state synchronization.
- `HudClientProtocol`: Unified HUD client interface.
