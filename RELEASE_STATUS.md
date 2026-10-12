# FMR v3.2.2 Release Status

Status: **RELEASED**

Prepared: 2026-10-12

## Work completed in v3.2.2

- Made `openrouter/free` the primary default model (`gateway_model: openrouter/free` at index 0).
- Cleared permanent exhaustion on `openrouter/free`, establishing it as the default gateway model.
- Updated documentation and skill definitions to reflect `openrouter/free` as default.
- Updated test suite covering `openrouter/free` state and transitions.

## Work completed in v3.2.1

- Standardised user-facing branding to **FMR**.
- Updated release version to **3.2.1**.
- Fixed `sed` delimiter bug by adopting `#` delimiter to prevent failures with slash-containing model names.
- Complete overhaul of `update_state.py` into a robust CLI utility supporting canonical `state.json` schema, atomic writes, and file permission safety.
- Sanitised credentials setup documentation using non-echoing environment variables.
- Scrubbed leaked private paths and cron IDs from documentation and references.
- Added automated test suite `tests/test_rotator.py` verifying model replacements, schema validation, and state rotation.
- Ran tests and compilation checks successfully.

## Current runtime evidence

`state.json` currently reports:

- `current_index: 0`
- `exhausted: []`
- primary: `openrouter/openrouter/free`
- `last_reset: 2026-10-12T19:20:00.000000+00:00`
