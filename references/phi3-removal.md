# phi3 → qwen3-coder Migration (2026-05-22)

## Context
The `phi3:latest` and `phi3:mini` models were removed from the free-model-rotator and Ollama configuration because the models were no longer installed locally and OpenRouter returned HTTP 400 (`phi3:latest is not a valid model ID`).

## What Broke
- `config.yaml` had `model.default: phi3:latest` and `model.name: phi3:latest`
- Ollama models list in config still included `phi3:mini`
- `context_length_cache.yaml` had a stale `phi3:latest` entry
- The rotator's provider pool had an index 7 Ollama tier pointing to `phi3:latest`
- Running gateway was hitting the dead model, producing 404 errors in `agent.log`

## Fix Applied
1. Removed index 7 (Ollama/phi3) tier from rotator provider pool in `SKILL.md`
2. Changed index 0 model from `nvidia/nemotron-3-super-120b-a12b:free` to `qwen/qwen3-coder:free`
3. Updated `config.yaml`: `model.default` and `model.name` → `qwen/qwen3-coder:free`
4. Removed `phi3:mini` from Ollama models list in `config.yaml`
5. Removed stale `phi3:latest` entry from `context_length_cache.yaml`
6. Reset rotator `state.json` (clean slate, 7 free tiers instead of 8)
7. Adjusted exhaustion threshold: `>= 8` → `>= 7`
8. Updated recommended primary model reference: `phi3:mini` → `qwen3-coder`

## Key Lesson
Changing `model.name` in `config.yaml` does **not** take effect on a running gateway. The gateway must be restarted after model config changes. Created `gateway-watchdog.sh` to auto-detect config changes and restart the gateway.

## Checklist for Future Model Changes
- [ ] Update `config.yaml` model/default/name
- [ ] Update rotator `SKILL.md` provider pool table
- [ ] Update rotator `state.json` if tier count changed
- [ ] Clean `context_length_cache.yaml` if old model is removed
- [ ] Remove model from Ollama `models` list if applicable
- [ ] Restart gateway (`pkill -f "hermes gateway run"` + relaunch)