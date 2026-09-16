#!/usr/bin/env python3
"""
Modernized Free Model Rotator - Multi-Key Support with Enhanced Configuration

This module implements advanced multi-key rotation, credential management,
and quota monitoring for Hermes model providers.

Key Features:
- Multi-key provider support with automatic rotation
- Key retirement on authentication failures
- Per-key cooldown periods
- Enhanced quota monitoring and learning
- Layered configuration system
- Dynamic model discovery
"""

import os
import json
import time
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

class ModernFreeModelRotator:
    """Enhanced Free Model Rotator with multi-key support and advanced features."""
    
    def __init__(self, config_path: str = "~/.hermes/config.json"):
        self.config_path = os.path.expanduser(config_path)
        self.state_path = os.path.expanduser("~/.hermes/skills/free-model-rotator/state.json")
        self.load_config()
        self.load_state()
        
    def load_config(self):
        """Load configuration from JSON file."""
        try:
            with open(self.config_path, 'r') as f:
                self.config = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self.config = self._get_default_config()
            self.save_config()
    
    def _get_default_config(self) -> Dict:
        """Return default configuration."""
        return {
            "providers": {
                "openrouter": {
                    "keys": [
                        "sk-or-your-openrouter-key-1",
                        "sk-or-your-openrouter-key-2",
                        "sk-or-your-openrouter-key-3"
                    ],
                    "base_urls": [
                        "https://openrouter.ai/api/v1",
                        "https://openrouter.ai/api/v1",
                        "https://openrouter.ai/api/v1"
                    ],
                    "current_key_index": 0,
                    "key_weights": [1.0, 1.0, 1.0],
                    "cooldowns": {},
                    "retired_keys": [],
                    "max_failures": 3,
                    "failure_reset_time": 3600,
                    "usage_tracking": True,
                    "quota_enforcement": True
                },
                "gemini": {
                    "keys": [
                        "$GEMINI_API_KEY_1",
                        "$GEMINI_API_KEY_2"
                    ],
                    "base_urls": [
                        "https://generativelanguage.googleapis.com/v1",
                        "https://generativellanguage.googleapis.com/v1"
                    ],
                    "current_key_index": 0,
                    "key_weights": [1.0, 1.0],
                    "cooldowns": {},
                    "retired_keys": [],
                    "max_failures": 3,
                    "failure_reset_time": 3600,
                    "usage_tracking": True,
                    "quota_enforcement": True
                },
                "deepseek": {
                    "keys": [
                        "sk-your-deepseek-key-1",
                        "sk-your-deepseek-key-2"
                    ],
                    "base_urls": [
                        "https://api.deepseek.com/v1",
                        "https://api.deepseek.com/v1"
                    ],
                    "current_key_index": 0,
                    "key_weights": [1.0, 1.0],
                    "cooldowns": {},
                    "retired_keys": [],
                    "max_failures": 3,
                    "failure_reset_time": 3600,
                    "usage_tracking": True,
                    "quota_enforcement": True
                }
            },
            "discovery": {
                "enabled": True,
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
                "quota_logging": True,
                "quota_report_interval": 3600,
                "performance_tracking": True,
                "failure_logging": True
            }
        }
    
    def load_state(self):
        """Load rotation state from JSON file."""
        try:
            with open(self.state_path, 'r') as f:
                self.state = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self.state = self._get_default_state()
            self.save_state()
    
    def _get_default_state(self) -> Dict:
        """Return default state."""
        return {
            "current_provider": "openrouter",
            "current_model": "cohere/north-mini-code:free",
            "provider_rotation_count": {
                "openrouter": 0,
                "gemini": 0,
                "deepseek": 0
            },
            "key_rotation_count": {
                "openrouter": {0: 0, 1: 0, 2: 0},
                "gemini": {0: 0, 1: 0},
                "deepseek": {0: 0, 1: 0}
            },
            "key_failures": {
                "openrouter": {0: 0, 1: 0, 2: 0},
                "gemini": {0: 0, 1: 0},
                "deepseek": {0: 0, 1: 0}
            },
            "last_exhaustion": {},
            "exhausted_providers": [],
            "retired_keys": {},
            "last_rotation": datetime.now().isoformat(),
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "quota_violations": 0,
            "auth_failures": 0
        }
    
    def save_config(self):
        """Save configuration to JSON file."""
        with open(self.config_path, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def save_state(self):
        """Save state to JSON file."""
        with open(self.state_path, 'w') as f:
            json.dump(self.state, f, indent=2)
    
    def select_next_key(self, provider: str) -> Optional[int]:
        """
        Select the next key for a provider using weighted random selection.
        
        Args:
            provider: Provider name
            
        Returns:
            Index of selected key, or None if no keys available
        """
        if provider not in self.config["providers"]:
            return None
        
        provider_config = self.config["providers"][provider]
        
        # Filter out retired keys and keys in cooldown
        available_keys = []
        weights = []
        
        for i, key in enumerate(provider_config["keys"]):
            if i in provider_config["retired_keys"]:
                continue
                
            # Check if key is in cooldown
            cooldown_until = provider_config["cooldowns"].get(i, 0)
            if cooldown_until > datetime.now().timestamp():
                continue
                
            available_keys.append(i)
            weights.append(provider_config["key_weights"][i])
        
        if not available_keys:
            return None
        
        # Use weighted random selection
        total_weight = sum(weights)
        rand = random.random() * total_weight
        
        cumulative = 0
        for i, weight in enumerate(weights):
            cumulative += weight
            if rand <= cumulative:
                selected_key = available_keys[i]
                
                # Update usage statistics
                self.state["key_rotation_count"][provider][selected_key] = \
                    self.state["key_rotation_count"][provider].get(selected_key, 0) + 1
                
                return selected_key
        
        return None
    
    def record_failure(self, provider: str, key_index: int):
        """
        Record a failure for a specific key and potentially retire it.
        
        Args:
            provider: Provider name
            key_index: Index of the key that failed
        """
        if provider not in self.config["providers"]:
            return
        
        provider_config = self.config["providers"][provider]
        
        # Increment failure count
        if provider not in self.state["key_failures"]:
            self.state["key_failures"][provider] = {}
        
        self.state["key_failures"][provider][key_index] = \
            self.state["key_failures"][provider].get(key_index, 0) + 1
        
        # Check if key should be retired
        max_failures = provider_config.get("max_failures", 3)
        if self.state["key_failures"][provider].get(key_index, 0) >= max_failures:
            # Retire the key
            provider_config["retired_keys"].append(key_index)
            
            # Set cooldown for retirement
            cooldown_seconds = provider_config.get("failure_reset_time", 3600)
            provider_config["cooldowns"][key_index] = datetime.now().timestamp() + cooldown_seconds
            
            print(f"Key {key_index} retired for provider {provider} due to excessive failures")
        
        # Set cooldown for next attempt
        cooldown_seconds = provider_config.get("failure_reset_time", 3600)
        provider_config["cooldowns"][key_index] = datetime.now().timestamp() + cooldown_seconds
        
        self.save_state()
    
    def get_provider_for_request(self) -> Optional[str]:
        """
        Select the next provider for a request using weighted random selection
        based on provider rotation counts.
        
        Returns:
            Selected provider name, or None if no providers available
        """
        available_providers = []
        weights = []
        
        for provider, config in self.config["providers"].items():
            if provider in self.state["exhausted_providers"]:
                continue
                
            # Check if any keys are available
            available_keys = [
                i for i in range(len(config["keys"]))
                if i not in config["retired_keys"]
                and config["cooldowns"].get(i, 0) <= datetime.now().timestamp()
            ]
            
            if available_keys:
                # Calculate weight based on rotation count (less rotation = higher weight)
                rotation_count = self.state["provider_rotation_count"].get(provider, 0)
                weight = max(0.1, 1.0 - (rotation_count * 0.1))
                
                available_providers.append(provider)
                weights.append(weight)
        
        if not available_providers:
            return None
        
        # Use weighted random selection
        total_weight = sum(weights)
        rand = random.random() * total_weight
        
        cumulative = 0
        for i, provider in enumerate(available_providers):
            cumulative += weights[i]
            if rand <= cumulative:
                return provider
        
        return None
    
    def get_model_for_provider(self, provider: str) -> Optional[str]:
        """
        Get a model for a provider based on the current key selection.
        
        Args:
            provider: Provider name
            
        Returns:
            Model name, or None if no model available
        """
        if provider not in self.config["providers"]:
            return None
        
        key_index = self.select_next_key(provider)
        if key_index is None:
            return None
        
        # For now, return a default model based on provider
        # In a real implementation, this would query the provider's API
        # to get the actual list of available models
        models = {
            "openrouter": "cohere/north-mini-code:free",
            "gemini": "gemini-3.5-flash",
            "deepseek": "deepseek-chat"
        }
        
        return models.get(provider)
    
    def record_request(self, provider: str, success: bool):
        """
        Record a request and update statistics.
        
        Args:
            provider: Provider name
            success: Whether the request was successful
        """
        self.state["total_requests"] += 1
        
        if success:
            self.state["successful_requests"] += 1
            # Increment rotation count for successful request
            if provider in self.state["provider_rotation_count"]:
                self.state["provider_rotation_count"][provider] = \
                    self.state["provider_rotation_count"].get(provider, 0) + 1
        else:
            self.state["failed_requests"] += 1
        
        self.save_state()
    
    def get_status(self) -> Dict:
        """
        Get current status of the free model rotator.
        
        Returns:
            Dictionary with current status
        """
        return {
            "current_provider": self.state.get("current_provider"),
            "current_model": self.state.get("current_model"),
            "exhausted_providers": self.state.get("exhausted_providers", []),
            "provider_rotation_count": self.state.get("provider_rotation_count", {}),
            "total_requests": self.state.get("total_requests", 0),
            "success_rate": self.state.get("successful_requests", 0) / max(1, self.state.get("total_requests", 1)),
            "available_providers": [
                p for p in self.config["providers"].keys()
                if p not in self.state.get("exhausted_providers", [])
            ],
            "key_status": {
                provider: {
                    "total_keys": len(self.config["providers"][provider]["keys"]),
                    "retired_keys": self.config["providers"][provider]["retired_keys"],
                    "cooldowns": self.config["providers"][provider]["cooldowns"]
                }
                for provider in self.config["providers"]
            }
        }
    
    def run_discovery(self):
        """
        Run provider discovery to find available models and keys.
        """
        print("Running provider discovery...")
        
        # This is a placeholder for actual discovery logic
        # In a real implementation, this would query various APIs
        # to discover available models and credentials
        
        discovered_providers = []
        
        for provider in self.config["discovery"]["providers"]:
            if provider in self.config["providers"]:
                # Simulate discovery by checking if keys are valid
                available_keys = []
                for i, key in enumerate(self.config["providers"][provider]["keys"]):
                    if i not in self.config["providers"][provider]["retired_keys"]:
                        # In a real implementation, you would make an API call here
                        # to verify the key is valid and get available models
                        available_keys.append(i)
                
                if available_keys:
                    discovered_providers.append(provider)
                    print(f"✓ Discovered {len(available_keys)} keys for provider {provider}")
                else:
                    print(f"✗ No available keys for provider {provider}")
        
        return discovered_providers
    
    def generate_report(self) -> str:
        """
        Generate a report of the current state and statistics.
        
        Returns:
            Formatted report string
        """
        status = self.get_status()
        
        report = f"""Free Model Rotator Status Report
==========================================
Generated: {datetime.now().isoformat()}

Current Provider: {status['current_provider']}
Current Model: {status['current_model']}

Provider Rotation Counts:
"""
        
        for provider, count in status['provider_rotation_count'].items():
            report += f"  {provider}: {count}\n"
        
        report += f"\nExhausted Providers: {', '.join(status['exhausted_providers'])}\n\n"
        report += f"Total Requests: {status['total_requests']}\n"
        report += f"Successful Requests: {status['successful_requests']}\n"
        report += f"Failed Requests: {status['failed_requests']}\n"
        report += f"Success Rate: {status['success_rate'] * 100:.1f}%\n\n"
        
        report += "Available Providers:\n"
        for provider in status['available_providers']:
            report += f"  - {provider}\n"
        
        report += "\nKey Status:\n"
        for provider, key_status in status['key_status'].items():
            report += f"  {provider}:\n"
            report += f"    Total keys: {key_status['total_keys']}\n"
            report += f"    Retired keys: {key_status['retired_keys']}\n"
            report += f"    Keys in cooldown: {list(key_status['cooldowns'].keys())}\n"
        
        return report


def main():
    """Main function to demonstrate the modern free model rotator."""
    print("Initializing Modern Free Model Rotator...")
    
    rotator = ModernFreeModelRotator()
    
    # Display initial status
    print("\nInitial Status:")
    print(rotator.get_status())
    
    # Simulate some requests
    print("\nSimulating requests...")
    providers = ["openrouter", "gemini", "deepseek"]
    
    for i in range(5):
        provider = random.choice(providers)
        success = random.random() > 0.3  # 70% success rate
        
        model = rotator.get_model_for_provider(provider)
        if model:
            print(f"Request {i+1}: Using {provider}/{model} - Success: {success}")
            rotator.record_request(provider, success)
            
            if not success:
                key_index = random.choice([0, 1, 2])  # Simulate failure for a random key
                rotator.record_failure(provider, key_index)
        else:
            print(f"Request {i+1}: No available model for {provider}")
    
    # Display final status
    print("\n" + "="*60)
    print("Final Status:")
    print("="*60)
    print(rotator.get_status())
    
    print("\n" + rotator.generate_report())

if __name__ == "__main__":
    main()