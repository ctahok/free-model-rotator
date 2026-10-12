# FMR - Modern Multi-Key Rotation System

## Overview

FMR is an advanced Hermes skill that provides intelligent model rotation with multi-key support, automatic key retirement, and enhanced quota monitoring. This system goes beyond basic provider rotation to offer sophisticated credential management, performance optimization, and comprehensive discovery capabilities.

**Version**: 3.2.0 (FMR branding and documentation update)

## What's new in 3.2.0
- Standardised the user-facing name as **FMR**.
- Synchronised the repository skill with the latest FMR provider, credential-recovery, and state-management guidance.
- Corrected command examples and clarified the `hermes fallback` versus `config.yaml` distinction.
- Added the multi-key Gemini credential-recovery reference.

## Key Features

### 🔑 Multi-Key Provider Support
- **Automatic key rotation**: Seamless switching between multiple API keys for the same provider
- **Key retirement**: Automatic retirement of keys that exceed failure thresholds
- **Cooldown periods**: Per-key cooldown periods to prevent abuse and ensure fair usage
- **Weighted selection**: Intelligent selection based on key performance and availability

### 🚀 Groq Support
- **Custom provider**: Groq offers an OpenAI-compatible API at `https://api.groq.com/openai/v1` and can be configured as a custom provider in `config.yaml`.

### ⚙️ Enhanced Configuration System
- **Two-tier configuration**: Local (`.env`) and global (`config.json`) settings
- **Deep merge strategy**: Objects merge by key, arrays replace entirely
- **Tombstone system**: Persistent deletions via tombstone tracking
- **Discovery mechanism**: Automatic provider and model discovery

### 📊 Advanced Quota Monitoring
- **Real-time quota tracking**: Per-provider and per-key quota usage
- **Violation detection**: Automatic detection of quota violations
- **Learning system**: Adaptive quota learning from API responses
- **Usage reporting**: Detailed usage statistics and reports

### 🔍 Comprehensive Model Discovery
- **Multi-source discovery**: Discover models from various provider APIs
- **Automatic cataloging**: Build comprehensive model catalogs
- **Quota-aware discovery**: Discover models respecting current quota constraints
- **Dynamic updates**: Real-time updates to model availability

## Installation and Setup

### Prerequisites
- Hermes v2.0 or later
- Python 3.8 or higher
- Git 2.0 or higher

### Quick Start

1. **Clone the repository**:
   ```bash
   git clone https://github.com/ctahok/free-model-rotator.git
   cd free-model-rotator
   ```

2. **Initialize the skill**:
   ```bash
   hermes skills load free-model-rotator
   ```

3. **Configure credentials safely**:
   ```bash
   read -rsp "OpenRouter API Key: " OR_KEY; echo
   hermes auth add openrouter --api-key "$OR_KEY"
   unset OR_KEY

   read -rsp "Gemini API Key: " GEM_KEY; echo
   hermes auth add gemini --api-key "$GEM_KEY"
   unset GEM_KEY

   read -rsp "DeepSeek API Key: " DS_KEY; echo
   hermes auth add deepseek --api-key "$DS_KEY"
   unset DS_KEY
   ```

4. **Verify installation & rotator status**:
   ```bash
   python update_state.py status
   ```

## Usage

### Basic Commands

#### Status and Monitoring
```bash
# View current rotation status via CLI
python update_state.py status

# Or check state.json directly
cat ~/.hermes/skills/free-model-rotator/state.json

# Check provider configuration
hermes config show

# List available providers
hermes auth list

# Check fallback chain
hermes fallback list
```

#### Rotation Control
```bash
# Reset rotation (clears exhausted keys)
python update_state.py reset

# Skip current provider (mark as exhausted and rotate)
python update_state.py skip

# Force switch to paid provider
python update_state.py paid
```

#### Configuration
```bash
# View current configuration
hermes config show

# Update provider configuration
hermes config set model.provider openrouter
hermes config set model.default cohere/north-mini-code:free
```

### Advanced Usage

#### Custom Configuration
Create a custom `config.json` with your preferred settings:

```json
{
  "providers": {
    "openrouter": {
      "keys": ["sk-or-1", "sk-or-2", "sk-or-3"],
      "base_urls": ["https://openrouter.ai/api/v1", "https://openrouter.ai/api/v1", "https://openrouter.ai/api/v1"],
      "current_key_index": 0,
      "key_weights": [1.0, 1.0, 1.0],
      "cooldowns": {},
      "retired_keys": [],
      "max_failures": 3,
      "failure_reset_time": 3600
    },
    "gemini": {
      "keys": ["$GEMINI_API_KEY_1", "$GEMINI_API_KEY_2"],
      "base_urls": ["https://generativelanguage.googleapis.com/v1", "https://generativelanguage.googleapis.com/v1"],
      "current_key_index": 0,
      "key_weights": [1.0, 1.0],
      "cooldowns": {},
      "retired_keys": [],
      "max_failures": 3,
      "failure_reset_time": 3600
    }
  },
  "discovery": {
    "enabled": true,
    "providers": ["openrouter", "gemini", "deepseek"],
    "intervals": {"openrouter": 86400000},
    "exclude_patterns": ["*-tts", "*-image"],
    "include_patterns": ["*-flash", "*-free"]
  },
  "rotation": {
    "max_failures_before_retirement": 5,
    "cooldown_base_seconds": 300
  }
}
```

### Model Discovery
Dynamic model availability is updated according to provider capabilities and status:

- **Automatic Scanning**: Periodically queries provider APIs for available models
- **Quota-Aware**: Respects quota constraints while discovering
- **Dynamic Updates**: Updates model availability in real-time
- **Performance Tracking**: Tracks model performance metrics

## Configuration Options

### config.json
The main configuration file for the FMR skill.

**Providers Section**:
```json
"providers": {
  "openrouter": {
    "keys": ["sk-or-1", "sk-or-2"],
    "base_urls": ["https://openrouter.ai/api/v1", "https://openrouter.ai/api/v1"],
    "current_key_index": 0,
    "key_weights": [1.0, 1.0],
    "cooldowns": {},
    "retired_keys": [],
    "max_failures": 3,
    "failure_reset_time": 3600,
    "usage_tracking": true,
    "quota_enforcement": true
  },
  "gemini": {
    "keys": ["$GEMINI_API_KEY_1", "$GEMINI_API_KEY_2"],
    "base_urls": ["https://generativelanguage.googleapis.com/v1", "https://generativelanguage.googleapis.com/v1"],
    "current_key_index": 0,
    "key_weights": [1.0, 1.0],
    "cooldowns": {},
    "retired_keys": [],
    "max_failures": 3,
    "failure_reset_time": 3600,
    "usage_tracking": true,
    "quota_enforcement": true
  }
}
```

**Discovery Section**:
```json
"discovery": {
  "enabled": true,
  "providers": ["openrouter", "gemini", "deepseek"],
  "intervals": {"openrouter": 86400000},
  "exclude_patterns": ["*-tts", "*-image"],
  "include_patterns": ["*-flash", "*-free"]
}
```

**Rotation Section**:
```json
"rotation": {
  "max_failures_before_retirement": 5,
  "cooldown_base_seconds": 300,
  "load_balance_algorithm": "weighted_random",
  "health_check_endpoint": "/api/v1/models"
}
```

## API Reference

### Skill Commands

Within a Hermes Agent session, these commands can be sent as text instructions to the agent:

#### `/rotator status`
Instructs the agent to display the current rotation state and active model.

#### `/rotator reset`
Instructs the agent to reset rotation state (clearing exhausted keys back to slot 0).

#### `/rotator skip`
Instructs the agent to mark the current provider as exhausted and switch immediately.

#### `/rotator paid`
Instructs the agent to switch immediately to the configured paid fallback.

### CLI Management (`update_state.py`)

Outside agent sessions, manage rotation state with:
```bash
python update_state.py status
python update_state.py rotate
python update_state.py reset
python update_state.py skip
python update_state.py paid
```

## Troubleshooting

### Common Issues and Solutions

#### 1. No Keys Available
**Problem**: No API keys are available for use.
**Solution**:
- Check if keys are registered: `hermes auth list`
- Ensure keys are not retired: `hermes auth remove <provider> <key-id>`
- Add new keys: `hermes auth add <provider> --api-key "<new-key>"`

#### 2. All Keys Retired
**Problem**: All keys for a provider have been retired.
**Solution**:
- Manually remove retired keys: `hermes auth remove <provider> <key-id>`
- Add replacement keys
- Reset rotation if needed: `python update_state.py reset`

#### 3. Quota Exceeded
**Problem**: API quota limits reached.
**Solution**:
- Monitor quota usage: `hermes auth list`
- Add more keys for the same provider
- Implement key cooldown periods

#### `hermes auth list` Shows No Keys
**Problem**: No credentials found.
**Solution**:
- Register keys:
  ```bash
  read -rsp "API Key: " KEY; echo
  hermes auth add <provider> --api-key "$KEY"
  unset KEY
  ```
- Verify provider names: `hermes auth list`
- Check for typos in provider names

#### Key Retirement
**Problem**: Keys are being retired after failures.
**Solution**:
- Check failure counts: `hermes auth list`
- Manually remove retired keys
- Add new valid keys
- Reset rotation: `python update_state.py reset`

### Error Messages

#### "No keys available"
**Cause**: No valid API keys for the selected provider.
**Solution**: Add new keys or check existing keys.

#### "Provider not found"
**Cause**: Provider not registered.
**Solution**: Register the provider: `hermes auth add <provider> --api-key "<key>"`

#### "Quota exceeded"
**Cause**: API quota limits reached.
**Solution**: Add more keys, wait for quota reset, or use paid fallback.

## Advanced Features

### Model Discovery
The discovery feature automatically scans provider APIs to discover available models:

- **Automatic Scanning**: Periodically queries provider APIs for available models
- **Quota-Aware**: Respects quota constraints while discovering
- **Dynamic Updates**: Updates model availability in real-time
- **Performance Tracking**: Tracks model performance metrics

### Quota Monitoring
Enhanced quota monitoring provides:
- **Real-time Usage**: Track API key usage in real-time
- **Violation Detection**: Automatic detection of quota violations
- **Learning System**: Learn from API responses to optimize quota usage
- **Reporting**: Detailed quota reports and analytics

### Advanced Rotation
Smart rotation strategies:
- **Weighted Selection**: Select keys based on performance and availability
- **Cooldown Management**: Prevent abuse of keys during high usage
- **Key Retirement**: Automatically retire underperforming keys
- **Load Balancing**: Distribute requests across available keys

## API Reference

### Configuration Schema
```json
{
  "$schema": "https://hermes-agent.nousresearch.com/schemas/free-model-rotator.json",
  "version": "3.2.0",
  "providers": {
    "provider_name": {
      "keys": ["key1", "key2"],
      "base_urls": ["https://api.provider1.com/v1", "https://api.provider2.com/v1"],
      "current_key_index": 0,
      "key_weights": [1.0, 1.0],
      "cooldowns": {},
      "retired_keys": [],
      "max_failures": 3,
      "failure_reset_time": 3600,
      "usage_tracking": true,
      "quota_enforcement": true
    }
  },
  "discovery": {
    "enabled": true,
    "providers": ["openrouter", "gemini", "deepseek"],
    "intervals": {"openrouter": 86400000},
    "exclude_patterns": ["*-tts", "*-image"],
    "include_patterns": ["*-flash", "*-free"]
  },
  "rotation": {
    "max_failures_before_retirement": 5,
    "cooldown_base_seconds": 300,
    "load_balance_algorithm": "weighted_random",
    "health_check_endpoint": "/api/v1/models"
  },
  "monitoring": {
    "quota_logging": true,
    "quota_report_interval": 3600,
    "performance_tracking": true,
    "failure_logging": true
  }
}
```

## License

This project is part of the Hermes Agent ecosystem. Use responsibly and respect provider terms of service.

## Support

For issues with FMR:
1. Check logs: `journalctl --user -u hermes-gateway.service`
2. Verify provider credentials: `hermes auth list`
3. Inspect current rotator state: `python update_state.py status`
4. Reset rotator if needed: `python update_state.py reset`

---

*Last updated: September 20, 2026 - v3.2.0 (FMR branding and documentation update)*