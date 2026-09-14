# Free Model Rotator - v3.0

## Overview

The **Free Model Rotator** is a Hermes skill that provides intelligent model rotation for Hermes, automatically cycling through free LLM API providers and falling back to paid providers when all free options are exhausted.

**Version:** 3.0 (Free-First with Paid Fallback Strategy)

## Key Features

### 🚀 Free-First Strategy
- **Zero-cost steady state**: Primary model is `cohere/north-mini-code:free` (verified 0.47s TTFT, 194 t/s)
- **8 verified free models**: Carefully tested and ranked by performance
- **Automatic fallback**: Paid DeepSeek as last resort when all free options are exhausted

### 🛡️ Clean Provider Pool
- **No dead keys**: Removed all auth-failed credentials and problematic entries
- **Credential hygiene**: Weekly health sweep to prevent drift
- **Verified performance**: Each free model tested and ranked by real-world metrics

### 📊 Smart Rotation
- **Measured performance**: Real-world TTFT and throughput testing
- **Intelligent fallback**: Moves to next provider on rate limits/auth failures
- **State persistence**: Tracks exhausted providers and rotation state

### 🔧 Gateway Integration
- **Built-in fallback**: Hermes's native `hermes fallback` integration
- **Two-layer rotation**: Agent-level + gateway-level for comprehensive coverage
- **Seamless switching**: No user intervention required

## Current Provider Pool (Priority Order)

| Index | Provider | Model | Measured Performance |
|-------|----------|-------|---------------------|
| 0 | OpenRouter | cohere/north-mini-code:free | 0.31s TTFT / 194 t/s |
| 1 | OpenRouter | dots-studio/dots-3-note-preview:free | 0.71s TTFT / 65 t/s |
| 2 | OpenRouter | nvidia/nemotron-3-super-120b-a12b:free | 1.02s TTFT / 46 t/s (best large model) |
| 3 | OpenRouter | inclusionai/ling-3.0-flash-vl:free | 0.91s TTFT / 157 t/s (multimodal) |
| 4 | OpenRouter | inclusionai/ling-3.0-flash-fin:free | 1.27s TTFT / 452 t/s |
| 5 | OpenRouter | inclusionai/ling-3.0-flash-sante:free | 1.09s TTFT / 296 t/s |
| 6 | OpenRouter | nex-agi/nex-n2.5-mini:free | 0.94s TTFT |
| 7 | OpenRouter | liquid/lfm-2.5-2.6b:free | 0.85s TTFT / 425 t/s (2.6B) |
| 8 | DeepSeek | deepseek-chat | 2.60s median real, 115 t/s (paid fallback) |

## Quick Start

### Prerequisites
- Hermes installed
- Valid OpenRouter API key (for free models)
- DeepSeek API key (optional, for paid fallback)

### Installation

1. **Load the skill** (if not already loaded):
   ```bash
   hermes skills load free-model-rotator
   ```

2. **Configure credentials**:
   ```bash
   hermes auth add openrouter --api-key "sk-or-your-key-here"
   ```

3. **Optional**: Add paid fallback (DeepSeek):
   ```bash
   hermes auth add deepseek --api-key "sk-your-deepseek-key"
   ```

4. **Update fallback chain** (for gateway/Telegram):
   ```bash
   hermes fallback add   # Interactive setup
   ```

5. **Verify configuration**:
   ```bash
   hermes config show
   hermes auth list
   hermes fallback list
   hermes skills run free-model-rotator /rotator status
   ```

### Usage

#### For CLI Sessions
```bash
hermes chat  # Uses free-first rotation
hermes -z "Your prompt here"  # One-shot free model
```

#### For Gateway (Telegram/WhatsApp)
```bash
hermes fallback list  # View the configured fallback chain
hermes fallback add   # Add fallback providers
```

## Commands

### Core Rotator Commands

#### `/rotator status`
Display current rotator state:
- Current provider and index
- List of exhausted providers
- Timestamp of last updates

#### `/rotator reset`
Reset the rotation state:
- Clears exhausted list
- Returns to index 0 (`cohere/north-mini-code:free`)
- Updates config.yaml
- Restarts gateway for changes to take effect

#### `/rotator skip`
Manually mark current provider as exhausted:
- Adds current index to exhausted list
- Rotates to next viable provider
- Logs the action

#### `/rotator paid`
Force switch to paid provider:
- Skips remaining free providers
- Switches to DeepSeek paid model
- Prefixes responses with cost warning

### Verification Commands

```bash
# Check rotator state
hermes skills run free-model-rotator /rotator status

# Check current provider
hermes config show

# Check configured credentials
hermes auth list

# Check gateway fallback chain
hermes fallback list

# Check credential health (weekly)
python3 ~/.hermes/scripts/credential_health_sweep.py
```

## Configuration

### Skill Autoload

To auto-load the skill on every session start, add to `~/.hermes/config.yaml`:

```yaml
skills:
  autoload:
    - free-model-rotator
```

### Provider Registration

**Supported providers for `hermes auth add`**:
- `openrouter` - OpenRouter (primary free tier)
- `deepseek` - DeepSeek API
- `gemini` - Google Gemini
- `xiaomi` - Xiaomi/MiMo API
- `copilot` - GitHub Copilot

**NOT supported**:
- `cerebras`, `groq`, `mistral`, `openai`, `google`, `gemini_pro`

### Troubleshooting

#### If falling back to paid too early:
1. Check `hermes fallback list` - ensure free models are present
2. Verify `hermes auth list` for OpenRouter credentials
3. Run credential health sweep: `python3 ~/.hermes/scripts/credential_health_sweep.py`

#### If stuck on a free model:
1. Check provider status: `hermes skills run free-model-rotator /rotator status`
2. Verify model is still available: `hermes auth list`
3. Consider manual reset: `hermes skills run free-model-rotator /rotator reset`

## Technical Details

### State Management

The rotator persists state in `state.json`:

```json
{
  "current_index": 0,
  "exhausted": [8],
  "last_reset": "2026-09-14T11:55:58.708723+00:00",
  "session_start": "2026-09-14T11:55:58.708723+00:00",
  "gateway_primary": "openrouter",
  "gateway_model": "cohere/north-mini-code:free",
  "fallback_providers": [
    { "provider": "openrouter", "model": "nex-agi/nex-n2.5-mini:free" },
    // ... more providers
  ],
  "last_updated": "2026-09-14T11:55:58.708723+00:00",
  "policy": "free-first with paid fallback (deepseek last)"
}
```

### Provider Detection

Only providers listed in `hermes auth list` are used by the rotator. Any provider not registered via `hermes auth add` will be skipped regardless of its index.

### Performance Monitoring

The rotator tracks provider performance in logs (`~/.hermes/logs/agent.log`):
- API call timing (latency, tokens per second)
- Cache hit rates
- Provider switches and exhaustion events

## Usage Examples

### Example 1: Basic Free Model Rotation

```bash
# Start Hermes with free model rotation
hermes chat

# Hermes automatically uses cohere/north-mini-code:free
# Falls back through verified free models
# Uses deepseek-chat only when all free options exhausted
```

### Example 2: Cron Job Integration

```bash
# Weekly credential health sweep
0 3 * * 0 python3 ~/.hermes/scripts/credential_health_sweep.py

# This ensures clean credentials for optimal rotation
```

### Example 3: Debugging Provider Issues

```bash
# Check current rotator state
hermes skills run free-model-rotator /rotator status

# Verify provider credentials
hermes auth list

# Check gateway fallback chain
hermes fallback list

# If a provider is failing, manually skip to next
hermes skills run free-model-rotator /rotator skip
```

## Known Issues & Solutions

### Issue: Provider Not Working

**Problem**: Provider registered but not working
**Solution**: 
1. Verify credentials: `hermes auth list`
2. Check for `auth failed` status
3. Remove and re-add credentials if needed
4. Reset rotator: `hermes skills run free-model-rotator /rotator reset`

### Issue: Paid Fallback Too Early

**Problem**: Switching to paid provider prematurely
**Solution**:
1. Check free model availability in fallback chain
2. Verify provider credentials are valid
3. Ensure free models are properly ranked by performance
4. Consider adding more free providers to the pool

### Issue: Gateway Not Using Fallback

**Problem**: Telegram/WhatsApp not rotating through fallbacks
**Solution**:
1. Set up gateway fallback chain: `hermes fallback add`
2. Verify gateway configuration
3. Restart gateway: `systemctl --user restart hermes-gateway.service`

## License

This skill is part of the Hermes Agent ecosystem. Use responsibly and respect provider terms of service.

## Support

For issues with the Free Model Rotator:
1. Check logs: `journalctl --user -u hermes-gateway.service`
2. Run credential health sweep: `python3 ~/.hermes/scripts/credential_health_sweep.py`
3. Verify provider credentials: `hermes auth list`
4. Reset rotator if needed: `hermes skills run free-model-rotator /rotator reset`

---

*Last updated: September 14, 2026 - v3.0 (Free-First with Paid Fallback)*