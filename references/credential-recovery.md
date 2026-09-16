# Free Model Rotator Reference Documentation

This documentation provides comprehensive information about the Free Model Rotator skill's architecture, configuration, and troubleshooting procedures.

## Overview

The Free Model Rotator is an intelligent model rotation system designed to automatically cycle through free-tier LLM API providers, with sophisticated multi-key support, automatic key retirement, and enhanced quota monitoring.

## Key Features

### Multi-Key Provider Support
- **Automatic key rotation**: Seamless switching between multiple API keys for the same provider
- **Key retirement**: Automatic retirement of keys that exceed failure thresholds
- **Cooldown periods**: Per-key cooldown periods to prevent abuse
- **Weighted selection**: Intelligent selection based on key performance and availability

### Enhanced Configuration System
- **Two-tier configuration**: Local (`.env`) and global (`config.json`) settings
- **Deep merge strategy**: Objects merge by key, arrays replace entirely
- **Tombstone system**: Persistent deletions via tombstone tracking
- **Discovery mechanism**: Automatic provider and model discovery

### Advanced Quota Monitoring
- **Real-time quota tracking**: Per-provider and per-key quota usage
- **Violation detection**: Automatic detection of quota violations
- **Learning system**: Adaptive quota learning from API responses
- **Usage reporting**: Detailed usage statistics and reports

### Comprehensive Model Discovery
- **Multi-source discovery**: Discover models from various provider APIs
- **Automatic cataloging**: Build comprehensive model catalogs
- **Quota-aware discovery**: Discover models respecting current quota constraints
- **Dynamic updates**: Real-time updates to model availability

## Configuration Files

### config.json
The main configuration file for the Free Model Rotator skill.

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
    },
    "deepseek": {
      "keys": ["sk-your-deepseek-key-1", "sk-your-deepseek-key-2"],
      "base_urls": ["https://api.deepseek.com/v1", "https://api.deepseek.com/v1"],
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
    "providers": ["openrouter", "gemini", "deepseek", "bai", "tokenrouter"],
    "intervals": {"openrouter": 86400000, "gemini": 43200000, "deepseek": 86400000},
    "exclude_patterns": ["*-tts", "*-image", "*-antigravity"],
    "include_patterns": ["*-flash", "*-instruct", "*-lite", "*-free"]
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

### Local Configuration (.env)

Environment variables for overriding configuration values:

```bash
# Provider keys
OPENROUTER_API_KEY_1="sk-or-your-first-key"
OPENROUTER_API_KEY_2="sk-or-your-second-key"
GEMINI_API_KEY_1="$GEMINI_API_KEY_1"
GEMINI_API_KEY_2="$GEMINI_API_KEY_2"
DEEPSEEK_API_KEY_1="sk-your-deepseek-key-1"
DEEPSEEK_API_KEY_2="sk-your-deepseek-key-2"

# Configuration overrides
FREE_ROUTER_CONFIG_PATH="$HOME/.hermes/config.json"
FREE_ROUTER_LOG_LEVEL="info"
FREE_ROUTER_QUOTA_ENFORCEMENT="true"

# Discovery settings
FREE_ROUTER_DISCOVERY_ENABLED="true"
FREE_ROUTER_DISCOVERY_INTERVAL="86400000"
```

## Model Catalog

### OpenRouter Models

| Model | Type | Context Window | TTFT | Throughput | Notes |
|-------|------|---------------|-----|-------------|-------|
| cohere/north-mini-code:free | Code Completion | 4K | 0.31s | 194 t/s | Fastest model |
| dots-studio/dots-3-note-preview:free | Note Taking | 8K | 0.71s | 65 t/s | Multimodal notes |
| nvidia/nemotron-3-super-120b-a12b:free | Large Model | 128K | 1.02s | 46 t/s | Best large model |
| inclusionai/ling-3.0-flash-vl:free | Vision-Language | 128K | 0.91s | 157 t/s | Multimodal |
| inclusionai/ling-3.0-flash-fin:free | Financial | 128K | 1.27s | 452 t/s | Finance specialist |
| inclusionai/ling-3.0-flash-sante:free | Medical | 128K | 1.09s | 296 t/s | Medical specialist |
| nex-agi/nex-n2.5-mini:free | Mini Model | 128K | 0.94s | Various | Alternative family |
| liquid/lfm-2.5-2.6b:free | Small Model | 2.6K | 0.85s | 425 t/s | Efficient |

### Gemini Models

| Model | Type | Context Window | TTFT | Throughput | Notes |
|-------|------|---------------|-----|-------------|-------|
| gemini-1.5-flash | General | 1M | Varies | Varies | Most capable free model |
| gemini-1.5-pro | Advanced | 128K | Varies | Varies | Higher capability |

### DeepSeek Models

| Model | Type | Context Window | TTFT | Throughput | Notes |
|-------|------|---------------|-----|-------------|-------|
| deepseek-chat | Chat | 32K | Varies | Varies | Default choice |
| deepseek-flash | Fast | 32K | Varies | Varies | Faster variant |

## API Rate Limits and Quotas

### OpenRouter Free Tier
- **Daily Limit**: 100 requests per key
- **Concurrent Requests**: 10 requests per second
- **Model Access**: All free models available with rotation
- **Rate Limit Headers**: `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`

### Gemini Free Tier
- **Daily Limit**: 60 requests per key
- **Concurrent Requests**: 1 request per second
- **Model Access**: Limited to specified models
- **Rate Limit Headers**: `x-goog-quota-remaining`, `x-goog-quota-limit`

### DeepSeek Free Tier
- **Daily Limit**: 5 requests per key
- **Concurrent Requests**: 1 request per second
- **Model Access**: deepseek-chat and deepseek-flash
- **Rate Limit Headers**: Various rate limit headers

## Troubleshooting Guide

### Common Issues and Solutions

#### 1. Key Retirement
**Problem**: API keys are being retired after failures.
**Solution**: 
- Check key failure count: `hermes auth list`
- Manually remove retired keys: `hermes auth remove openrouter <key-id>`
- Add new valid keys: `hermes auth add openrouter --api-key "<new-key>"`

#### 2. Quota Exceeded
**Problem**: API quota limits reached.
**Solution**:
- Monitor quota usage: `free-model-rotator --usage`
- Consider adding more keys for the same provider
- Implement key cooldown periods

#### 3
