# Xiaomi/MiMo Model Setup for Free Model Rotator

## Credential Setup (Done)

Two Xiaomi credentials registered in `~/.hermes/auth.json`:

1. **XIAOMI_API_KEY** (env, priority 0) — old key, base_url: `https://token-plan-sgp.xiaomimimo.com/v1`
2. **Mimo-2.5-pro** (manual, priority 1) — new paid key, base_url: `https://token-plan-sgp.xiaomimimo.com/v1`

Both share the same base URL. The rotator uses the first non-exhausted credential in priority order.

## Model

- **Model name:** `mimo-2.5-pro`
- **Base URL:** `https://token-plan-sgp.xiaomimimo.com/v1`
- **Rotator priority:** Index 6 (free tier), Index 99 (paid fallback)

## Verification

The provider is included in the rotator's fallback_providers in state.json:

```json
{
  "provider": "xiaomi",
  "model": "mimo-2.5-pro"
}
```

To test directly:
```bash
curl -X POST "https://token-plan-sgp.xiaomimimo.com/v1/chat/completions" \
  -H "Authorization: Bearer tp-sbt1b80c43zy5vgxptlbtbaz31lhnnm56jj2hxujnwflt998" \
  -H "Content-Type: application/json" \
  -d '{"model":"mimo-2.5-pro","messages":[{"role":"user","content":"hello"}]}'
```

## Notes

- The free tier and paid tier use the **same model** (mimo-2.5-pro). The difference is the credential's daily quota allocation.
- Both credentials point to `https://token-plan-sgp.xiaomimimo.com/v1` — NOT the default `https://api.xiaomimimo.com/v1`.
- The base URL was manually corrected in auth.json after `hermes auth add` assigned the default.
- When the rotater reaches index 99 (paid fallback), it uses the first xiaomi credential not in `exhausted` (ideally the Mimo-2.5-pro credential if the env one was exhausted first).
