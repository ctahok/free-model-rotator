# Free Model Rotator State Management

The free model rotator persists its state in `~/.hermes/skills/free-model-rotator/state.json`. This file contains:

```json
{
  "current_index": 0,          // Index into the ordered provider list
  "exhausted": [],             // List of provider indices that are exhausted
  "last_reset": "ISO timestamp", // Last time the exhausted list was cleared
  "session_start": "ISO timestamp", // When the current session started
  "gateway_primary": "provider-name", // Primary provider for gateway
  "gateway_model": "model-name", // Model for primary provider
  "fallback_providers": [      // Ordered list of fallback providers
    { "provider": "provider-name", "model": "model-name" },
    // ... more providers
  ],
  "last_updated": "ISO timestamp" // When state was last updated
}
```

## Provider Order

The provider order used by the rotator is:
1. The provider specified by `gateway_primary`/`gateway_model`
2. Followed by providers in the `fallback_providers` array (in order)

## How HERMES_HOME Affects State

The state file is located relative to your Hermes home directory. If you run multiple Hermes instances with different `HERMES_HOME` values, each will have its own independent free model rotator state.

Example:
- `HERMES_HOME=/root/.hermes` → Uses `/root/.hermes/skills/free-model-rotator/state.json`
- `HERMES_HOME=/home/iliko/.hermes` → Uses `/home/iliko/.hermes/skills/free-model-rotator/state.json`

## Best Practices

1. **Consistent Configuration**: Ensure all Hermes instances (CLI, gateway, etc.) that should share model rotation use the same `HERMES_HOME`.

2. **Gateway Synchronization**: If you want your Telegram bot to use the same model rotation as your CLI, start the gateway with:
   ```bash
   HERMES_HOME=/home/iliko/.hermes hermes gateway run &
   ```

3. **State Inspection**: Check current state with:
   ```bash
   hermes skills run free-model-rotator /rotator status
   # Or directly:
   cat ~/.hermes/skills/free-model-rotator/state.json
   ```

4. **Manual Reset**: To reset to the first provider:
   ```bash
   hermes skills run free-model-rotator /rotator reset
   ```