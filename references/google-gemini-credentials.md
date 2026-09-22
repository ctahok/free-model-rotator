# Google Gemini credential pool and rotator indexing

Use this reference when a user wants two Google API keys for Gemini or wants Gemini at rotator index `0`.

## Core distinction

- `current_index` selects a **provider/model slot** in the free-model rotator. It is not an API-key index.
- API-key priority is managed by Hermes' credential store and inspected with `hermes auth list <provider>`.
- A provider entry's `api_key` is a scalar. Two real keys must be registered as separate credentials; do not put a YAML list in `api_key`.
- `google`, `google-gemini`, and `gemini_pro` are not substitutes for the Hermes provider ID `gemini`.

## Register two keys safely

Run locally and never paste real keys into chat. Prefer an interactive secret prompt or a local secret manager. Do not place keys in shell history, repository files, logs, or Telegram messages.

```bash
read -rsp 'Google API key 1: ' GEMINI_API_KEY_1; echo
read -rsp 'Google API key 2: ' GEMINI_API_KEY_2; echo

# Use the syntax exposed by the installed Hermes CLI.
hermes auth add gemini --api-key "$GEMINI_API_KEY_1"
hermes auth add gemini --api-key "$GEMINI_API_KEY_2"

unset GEMINI_API_KEY_1 GEMINI_API_KEY_2
hermes auth list gemini
```

If the installed CLI exposes credential priority or label options, use the documented syntax, for example:

```bash
hermes auth add gemini --type api-key --label "Google Gemini primary" --priority 0
hermes auth add gemini --type api-key --label "Google Gemini secondary" --priority 1
hermes auth strategy gemini fill_first
```

Verify the result with `hermes auth list gemini` and `hermes auth strategy gemini`. If the installed CLI does not expose those options, add the keys sequentially and verify the displayed priority/order; do not invent an unsupported option name.

## Exhaustion-only index-0 workflow

Use this workflow when the requirement is Gemini first, then key 1 until exhaustion, then key 2, before the existing fallback chain:

1. Register both keys under native provider `gemini` with priorities `0` and `1`.
2. Set `hermes auth strategy gemini fill_first`.
3. Select a model that has been verified against the provider's current model listing.
4. Update the active state file only: `$HERMES_HOME/skills/free-model-rotator/state.json`.
5. Set `current_index: 0`, `gateway_primary: gemini`, and `gateway_model: <verified-model>`.
6. Preserve every existing fallback provider and shift indexes atomically if a slot is inserted.
7. Do not create a daily-reset cron job or run a reset script.
8. Restart the user gateway and verify configuration, credentials, fallback chain, and gateway logs.

A state mutation should use a temporary file plus `os.replace`, not an in-place rewrite of an unrelated JSON file. The active state path is authoritative; do not search the repository for the first JSON file that happens to contain `current_index`.

## YAML shape

For a native Gemini credential pool, keep the provider metadata in YAML but keep secrets out of it:

```yaml
model:
  provider: gemini
  default: gemini-1.5-flash

providers:
  gemini:
    api: https://generativelanguage.googleapis.com/v1beta/openai/
    default_model: gemini-1.5-flash
    models:
      - gemini-1.5-flash
      - gemini-1.5-pro
    name: Google Gemini
```

If a single-key custom-provider configuration is required, use an environment reference such as `key_env: GEMINI_API_KEY` when supported by the installed Hermes version. Do not embed the real key in `api_key`.

## Make Gemini the first rotator slot

Do not set `current_index: 0` merely because Gemini has two credentials. Index `0` is the first provider slot in the current table.

Choose one consistent design:

1. **Keep the existing slot table:** leave Gemini at its documented slot, set `model.provider: gemini`, and make Gemini the gateway primary if that is the desired absolute-first endpoint.
2. **Move Gemini to slot 0:** update the provider table, the state file, `gateway_primary`, `gateway_model`, and every dependent fallback mapping together. Never change only one of those places.

For design 2, the state must describe Gemini as slot `0`, for example:

```json
{
  "current_index": 0,
  "exhausted": [],
  "gateway_primary": "gemini",
  "gateway_model": "gemini-1.5-flash"
}
```

Then verify the complete chain rather than trusting the file alone:

```bash
hermes auth list gemini
hermes config show
hermes fallback list
systemctl --user restart hermes-gateway.service
```

## Pitfalls

- A duplicate `providers.gemini` block does not create a second API key.
- A YAML `api_key` list is not a credential pool in the native provider path.
- `current_index: 0` and credential priority `0` solve different problems; configure both only when the user explicitly requests Gemini-first exhaustion behavior.
- A custom provider can bypass the free-model rotator entirely; add it to the gateway fallback chain when fallback behavior is required.
- `hermes fallback add` is interactive in current Hermes versions; configure and verify the built-in fallback chain separately from `state.json`.
- After changing gateway provider/model configuration, restart the user gateway and inspect its logs for the actual selected provider.
- Do not run a setup script until its Python/JSON syntax, exact state path, secret handling, index shifting, and model availability have been checked.
- Never automatically reset an exhaustion-only Gemini pool; schedule resets only for explicitly requested quota-window mode.
