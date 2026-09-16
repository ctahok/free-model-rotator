# Free Model Rotator - Modern Multi-Key Rotation System

## Overview

The Free Model Rotator is an advanced Hermes skill that provides intelligent model rotation with multi-key support, automatic key retirement, and enhanced quota monitoring. This system goes beyond basic provider rotation to offer sophisticated credential management, performance optimization, and comprehensive discovery capabilities.

**Version**: 3.1.0 (Free-First with Paid Fallback Strategy)

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

3. **Configure credentials**:
   ```bash
   hermes auth add openrouter --api-key "sk-or-your-key"
   hermes auth add gemini --api-key "$GEMINI_API_KEY"
   hermes auth add deepseek --api-key "sk-your-deepseek-key"
   ```

4. **Set up configuration**:
   ```bash
   # Create config.json with your preferred settings
   cp config.json ~/.hermes/config.json
   ```

5. **Verify installation**:
   ```bash
   hermes skills run free-model-rotator /rotator status
   ```

## Usage

### Basic Commands

#### Status and Monitoring
```bash
# View current rotation status
hermes skills run free-model-rotcome /rotator status

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
hermes skills run free-model-rotator /rotator reset

# Skip current provider (mark as exhausted)
hermes skills run free-model-rotator /rotator skip

# Force switch to paid provider
hermes skills run free-model-rotator /rotator paid
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
```bash
# Run discovery to find available models
hermes skills run free-model-rotator /discovery run

# View discovered models
hermes skills run free-model-rotator /models list
```

### Monitoring and Reporting
```bash
# View usage statistics
hermes skills run free-model-rotator /usage report

# Check quota status
hermes skills run free-model-rotator /quota status

# Generate performance report
hermes skills run free-model-rotator /report generate
```

## Configuration Options

### config.json
The main configuration file for the Free Model Rotator skill.

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

#### /rotator status
Display current rotation status:
```bash
hermes skills run free-model-rotator /rotator status
```

#### /rotator reset
Reset rotation state (clears exhausted keys):
```bash
hermes skills run free-model-rotator /rotator reset
```

#### /rotator skip
Mark current provider as exhausted:
```bash
hermes skills run free-model-rotator /rotator skip
```

#### /rotator paid
Force switch to paid provider:
```bash
hermes skills run free-model-rotator /rotator paid
```

#### /discovery run
Run provider discovery:
```bash
hermes skills run free-model-rotator /discovery run
```

#### /models list
List discovered models:
```bash
hermes skills run free-model-rotator /models list
```

#### /usage report
Generate usage report:
```bash
hermes skills run free-model-rotator /usage report
```

#### /quota status
Check quota status:
```bash
hermens skills run free-model-rotator /quota status
```

#### /report generate
Generate performance report:
```bash
hermes skills run free-model-rotator /report generate
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
- Reset rotation if needed: `hermes skills run free-model-rotator /rotator reset`

#### 3. Quota Exceeded
**Problem**: API quota limits reached.
**Solution**:
- Monitor quota usage: `hermes skills run free-model-rotator /usage report`
- Add more keys for the same provider
- Implement key cooldown periods

#### `hermes auth list` Shows No Keys
**Problem**: No credentials found.
**Solution**:
- Register keys: `hermes auth add <provider> --api-key "<key>"`
- Verify provider names: `hermes auth list`
- Check for typos in provider names

#### Key Retirement
**Problem**: Keys are being retired after failures.
**Solution**:
- Check failure counts: `hermes auth list`
- Manually remove retired keys
- Add new valid keys
- Reset rotation: `hermes skills run free-model-rotator /rotator reset`

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
  "version": "3.1.0",
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

For issues with the Free Model Rotator:
1. Check logs: `journalctl --user -u hermes-gateway.service`
2. Run credential health sweep: `hermes skills run free-model-rotator /usage report`
3. Verify provider credentials: `hermes auth list`
4. Reset rotator if needed: `hermes skills run free-model-rotator /rotator reset`

---

*Last updated: September 16, 2026 - v3.1.0 (Free-First with Paid Fallback)*