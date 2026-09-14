# Provider Compatibility Reference

## `hermes auth add` — Supported Provider Names

Only these provider names work with `hermes auth add <name> --api-key <key>`:

| Provider     | `hermes auth add` works? | Notes |
|-------------|--------------------------|-------|
| `gemini`    | ✅ Yes                   | Google Gemini (OpenAI-compatible) |
| `deepseek`  | ✅ Yes                   | DeepSeek API |
| `openrouter`| ✅ Yes                   | OpenRouter.ai |
| `xiaomi`    | ✅ Yes                   | Xiaomi/MiMo API |
| `copilot`   | ✅ Yes                   | GitHub Copilot |

**NOT supported** (returns "Unknown provider"):
`cerebras`, `groq`, `mistral`, `openai`, `google`, `anthropic`,
`gemini_pro`, `ollama`

## `hermes fallback add` — Supported Providers

Same supported names as `hermes auth add`. Command is interactive (requires TTY).

## Gateway Fallback Chain

The gateway uses Hermes's built-in fallback mechanism, NOT the
`fallback_providers:` section in config.yaml. Configure via:

```bash
hermes fallback add  # Interactive — run in real terminal
hermes fallback list # Verify
```

The built-in fallback chain auto-retries with the next provider when the
primary returns auth/rate-limit errors. No agent intervention needed.

## How to Test a Provider

```bash
# 1. Register the credential
hermes auth add <provider> --api-key <key>

# 2. Verify it shows up
hermes auth list

# 3. Set as primary (requires sed, config.yaml is protected)
sed -i 's/^  provider: .*/  provider: <provider>/' ~/.hermes/config.yaml
sed -i 's/^  default: .*/  default: <model>/' ~/.hermes/config.yaml

# 4. Restart gateway
systemctl --user restart hermes-gateway.service

# 5. Watch the logs for auth success/failure
journalctl --user -u hermes-gateway.service --no-pager -n 20 -f
```

## Config.yaml Traps

- Setting `model.api_key` or `model.base_url` manually is UNNECESSARY when
  the provider is registered via `hermes auth add`. These values can conflict
  with the auth system's credential resolution.
- The `fallback_providers:` section in config.yaml is NOT used by Hermes
  for the gateway fallback chain. It's a custom section that Hermes ignores.
- `model.api_mode: chat_completions` is the default and doesn't need to be set
  explicitly unless using a non-standard API format.

## Restart Methods

| Method | Effect | Correct? |
|--------|--------|----------|
| `systemctl --user restart hermes-gateway.service` | Clean restart via systemd | ✅ Always use this |
| `pkill -f "hermes gateway run"` | Kills process, may leave orphans | ❌ Orphaned MCP/child processes |
| `kill -9 <PID>` | Force kill, no cleanup | ❌ Dangerous |
