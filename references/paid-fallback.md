# Using Xiaomi/MiMo as a Paid Fallback

After exhausting all free-tier providers (Gemini, OpenRouter, DeepSeek), the free model rotator can switch to a paid Xiaomi/MiMo model.

## Setup

1. Register your Xiaomi/MiMo API key:
   ```bash
   hermes auth add xiaomi --api-key "<your-key>"
   ```

2. **⚠ Verify base URL in auth.json** — `hermes auth add` assigns the default
   `https://api.xiaomimimo.com/v1`. If your endpoint is different (e.g.
   `https://token-plan-sgp.xiaomimimo.com/v1`), edit `~/.hermes/auth.json`
   and change the `base_url` field for the new credential manually.

3. Ensure the free provider list in `state.json` does NOT include Xiaomi/MiMo
   (priority 6) or mark it as exhausted. The rotator will then use the paid
   fallback.

4. The rotator will automatically switch to the paid Xiaomi/MiMo model when
   `current_index` reaches 99 (the paid fallback sentinel).

## Verification

Check the state:
```bash
cat ~/.hermes/skills/free-model-rotator/state.json
```
Look for `"exhausted": [0,1,2,3,4,5]` and `"current_index": 99`.

## Notes

- The paid model uses the same API key registered via `hermes auth add xiaomi`.
- No additional configuration in `config.yaml` is needed; the rotator uses the auth system.
- To revert to free providers, run `/rotator reset` or manually clear the `exhausted` list and reset `current_index` to 0.
- If the paid model fails with a 401/403 error, check that the base URL in `auth.json` matches the exact endpoint your key was issued for. Regional Xiaomi endpoints differ.
