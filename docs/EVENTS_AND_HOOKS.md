# packages/hud Events and Hooks

## Events (`hud.events`)

- `VIEW_RENDERED`: Triggered when HUD viewport state is updated and rendered. Payload: `{"view_id": str, "timestamp": float}`.
- `STATE_SYNCHRONIZED`: Triggered when HUD polls and updates its cached engine state. Payload: `{"synced_keys": list[str], "engine_status": str}`.

## Hooks (`hud.hooks`)

- `PRE_STATE_SYNC`: Intercepts state polling cycle prior to contacting the engine.
- `POST_STATE_SYNC`: Intercepts state payload before updating internal view models.
- `PRE_VIEW_RENDER`: Intercepts rendering pipeline prior to drawing components.
