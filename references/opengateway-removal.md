# OpenGateway Removal — Migration Record (2026-06-02)

## What Changed

OpenGateway (MiMo v2.5-pro at `opengateway.gitlawb.com`) was removed from Hermes and the free model rotator.

## Files Modified

| File | Change |
|------|--------|
| `~/.hermes/config.yaml` | Cleared `model.api_key` (was ogw key), cleared `model.name` (was mimo-v2.5-pro), removed `opengateway` provider block, removed trailing `opengateway:` remnant |
| `~/.hermes/.env` | Removed `OPENGATEWAY_API_KEY` |
| `SKILL.md` | Removed from priority table, index mapping, prerequisites, daily reset text; re-indexed pool |
| `state.json` | Reset to `current_index: 0`, empty exhausted |

## Removal Procedure

1. Clear the main model section's api_key and name: `sed -i 's/.../'"''"'/' config.yaml`
2. Delete the provider block: `sed -i '/^  opengateway:/,/^  [a-z]/ { /^  opengateway:/! { /^  [a-z]/!d }; /^  opengateway:/d }' config.yaml`
3. Remove trailing remnant: `sed -i '648,650d' config.yaml`
4. Remove .env entry: `sed -i '/^OPENGATEWAY_API_KEY=/d' .env`
5. In SKILL.md: remove table row, update index mapping, update exhaustion threshold, update daily reset text
6. Reset state.json to index 0

## Post-removal Provider Pool (before subsequent additions)

| Index | Provider | Model |
|-------|----------|-------|
| 0 | OpenRouter | nvidia/nemotron-3-super-120b-a12b:free |
| 1 | Cerebras | qwen3-235b |
| 2 | OpenRouter | openrouter/owl-alpha:free |
| 3 | Groq | llama-3.3-70b-versatile |
| 4 | Gemini | gemini-2.5-flash |
| 5 | Mistral | mistral-small-latest |
| 6 | OpenRouter | qwen/qwen3-coder:free |
