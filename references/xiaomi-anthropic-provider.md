# Xiaomi-Anthropic Paid Provider

## Overview

OpenAI-compatible endpoint that proxies a Claude-class model (mimo-v2.5-pro). 
Returns `reasoning_content` (thinking tokens) similar to Anthropic's Claude Sonnet 4.

## Configuration

```yaml
providers:
  xiaomi-anthropic:
    api: https://token-plan-sgp.xiaomimimo.com/v1
    default_model: mimo-v2.5-pro
    models:
    - mimo-v2.5-pro
    name: Xiaomi Anthropic
    api_key: <key-here>
```

## Key Differences from Standard Xiaomi

| Aspect | Standard Xiaomi (mimo-2.5-pro) | Xiaomi-Anthropic (mimo-v2.5-pro) |
|--------|-------------------------------|-----------------------------------|
| Base URL | `api.xiaomimimo.com` (default) | `token-plan-sgp.xiaomimimo.com` |
| Key type | Regular API key | Paid key (requires specific plan) |
| Reasoning | No `reasoning_content` | Returns `reasoning_content` |
| Thinking tokens | Not supported | Supported (`completion_tokens_details.reasoning_tokens`) |
| Cached tokens | No | Yes (`prompt_tokens_details.cached_tokens`) |

## Known Quirks

1. **Cannot use `hermes auth add xiaomi`** — the default Xiaomi credential stores base URL
   `https://api.xiaomimimo.com/v1` which gives 401 for this key. Must add as a custom
   provider in config.yaml with explicit `api:` and `api_key:` fields.

2. **Model naming** — The model is `mimo-v2.5-pro` (with hyphen), NOT `mimo-v2.5_pro` or
   `mimo-2.5-pro`. Check the list endpoint to confirm:
   ```
   curl -s https://token-plan-sgp.xiaomimimo.com/v1/models \
     -H "Authorization: Bearer <key>" | jq '.data[].id'
   ```

3. **API endpoint is `/v1` not `/anthropic/v1`** — Despite proxying Claude, the endpoint
   is OpenAI-compatible at `token-plan-sgp.xiaomimimo.com/v1`. The `/anthropic` path
   uses the Anthropic-native protocol (POST `/anthropic/v1/messages`).

4. **Cached tokens are automatic** — The API reports `prompt_tokens_details.cached_tokens`
   which can be >0 even on first request. This is server-side caching, not client-controlled.

5. **Rate limiting** — Paid endpoint with no observed daily cap. Tested at ~1 req/s
   without throttling.

## Anthropic-Native Protocol (Alternative)

The same key also works on the Anthropic-native endpoint:
```
POST https://token-plan-sgp.xiaomimimo.com/anthropic/v1/messages
x-api-key: <key>
anthropic-version: 2023-06-01
Content-Type: application/json

{"model":"mimo-v2.5-pro","max_tokens":50,"messages":[{"role":"user","content":"Hi"}]}
```

This returns an Anthropic-format response with `type: message`, `thinking` content blocks,
and `stop_reason: end_turn`. Useful if Hermes ever supports native Anthropic protocol.
