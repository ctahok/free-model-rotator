#!/usr/bin/env python3
"""
FMR State Manager - Multi-Provider Rotation Management for Hermes Agent

This module manages state and rotation for the Free Model Rotator (FMR) skill.
It operates on the canonical state.json schema used by Hermes Agent, supporting
safe inspection, atomic updates, and fallback rotation.

Canonical Schema:
- current_index: int (0-19: free pool, 99: paid fallback)
- exhausted: list of int (indices marked 429/error/exhausted)
- last_reset: ISO timestamp
- session_start: ISO timestamp
- gateway_primary: string (e.g. "openrouter")
- gateway_model: string (e.g. "openrouter/free")
- fallback_providers: list of dicts [{"provider": str, "model": str}, ...]
- last_updated: ISO timestamp
- policy: string
"""

import os
import sys
import json
import argparse
import tempfile
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any

# Ordered provider pool mapping matching SKILL.md
FREE_PROVIDER_POOL = [
    {"index": 0, "provider": "openrouter", "model": "openrouter/free"},
    {"index": 1, "provider": "openrouter", "model": "dots-studio/dots-3-note-preview:free"},
    {"index": 2, "provider": "openrouter", "model": "nvidia/nemotron-3-super-120b-a12b:free"},
    {"index": 3, "provider": "openrouter", "model": "inclusionai/ling-3.0-flash-vl:free"},
    {"index": 4, "provider": "openrouter", "model": "inclusionai/ling-3.0-flash-fin:free"},
    {"index": 5, "provider": "openrouter", "model": "inclusionai/ling-3.0-flash-sante:free"},
    {"index": 6, "provider": "openrouter", "model": "nex-agi/nex-n2.5-mini:free"},
    {"index": 7, "provider": "openrouter", "model": "liquid/lfm-2.5-2.6b:free"},
    {"index": 8, "provider": "openrouter", "model": "poolside/laguna-xs-2.1:free"},
    {"index": 9, "provider": "openrouter", "model": "poolside/laguna-s-2.1:free"},
    {"index": 10, "provider": "openrouter", "model": "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free"},
    {"index": 11, "provider": "openrouter", "model": "nex-agi/nex-n2.5-pro:free"},
    {"index": 12, "provider": "openrouter", "model": "nvidia/nemotron-3.5-lightning:free"},
    {"index": 13, "provider": "openrouter", "model": "nvidia/nemotron-3-ultra-550b-a55b:free"},
    {"index": 14, "provider": "deepseek", "model": "deepseek-chat"},
    {"index": 15, "provider": "zai", "model": "glm-5.2:free"},
    {"index": 16, "provider": "gemini", "model": "gemini-1.5-flash"},
    {"index": 17, "provider": "xiaomi", "model": "mimo-2.5-pro"},
    {"index": 18, "provider": "copilot", "model": "gpt-4o-mini"},
]

PAID_FALLBACK_INDEX = 99
TOTAL_FREE_SLOTS = 19  # indices 0 through 18


def get_default_state_path() -> str:
    """Resolve state file location from HERMES_HOME or default home."""
    hermes_home = os.environ.get("HERMES_HOME", os.path.expanduser("~/.hermes"))
    return os.path.join(hermes_home, "skills", "free-model-rotator", "state.json")


class RotatorStateManager:
    """Manages reading, rotating, and atomically saving the canonical state.json."""

    def __init__(self, state_path: Optional[str] = None):
        self.state_path = state_path or get_default_state_path()
        self.state = self.load_state()

    def _get_default_state(self) -> Dict[str, Any]:
        now = datetime.now(timezone.utc).isoformat()
        return {
            "current_index": 0,
            "exhausted": [],
            "last_reset": now,
            "session_start": now,
            "gateway_primary": "openrouter",
            "gateway_model": "openrouter/free",
            "fallback_providers": [
                {"provider": "openrouter", "model": "nex-agi/nex-n2.5-mini:free"},
                {"provider": "openrouter", "model": "nvidia/nemotron-3-super-120b-a12b:free"},
                {"provider": "openrouter", "model": "dots-studio/dots-3-note-preview:free"},
                {"provider": "openrouter", "model": "inclusionai/ling-3.0-flash-fin:free"},
                {"provider": "openrouter", "model": "inclusionai/ling-3.0-flash-vl:free"},
                {"provider": "openrouter", "model": "inclusionai/ling-3.0-flash-sante:free"},
                {"provider": "nvidia", "model": "nvidia/nemotron-3-super-120b-a12b"},
                {"provider": "zai", "model": "glm-4.5-flash"},
                {"provider": "deepseek", "model": "deepseek-chat"},
            ],
            "last_updated": now,
            "policy": "free-first with paid fallback (deepseek last); openrouter/free default",
        }

    def load_state(self) -> Dict[str, Any]:
        """Load state from JSON or return default state."""
        if os.path.exists(self.state_path):
            try:
                with open(self.state_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except (json.JSONDecodeError, OSError):
                return self._get_default_state()
        return self._get_default_state()

    def save_state(self) -> None:
        """Atomically save state with restricted permissions."""
        os.makedirs(os.path.dirname(os.path.abspath(self.state_path)), exist_ok=True)
        dir_name = os.path.dirname(os.path.abspath(self.state_path))
        self.state["last_updated"] = datetime.now(timezone.utc).isoformat()

        # Write to temporary file in the same directory for atomic replace
        with tempfile.NamedTemporaryFile("w", dir=dir_name, delete=False, encoding="utf-8") as tmp:
            json.dump(self.state, tmp, indent=2)
            tmp_name = tmp.name

        try:
            # Set owner read/write (0600) where supported
            if hasattr(os, "chmod"):
                try:
                    os.chmod(tmp_name, 0o600)
                except OSError:
                    pass
            os.replace(tmp_name, self.state_path)
        except Exception:
            if os.path.exists(tmp_name):
                os.remove(tmp_name)
            raise

    def get_state(self) -> Dict[str, Any]:
        return self.state

    def get_slot_info(self, index: int) -> Optional[Dict[str, Any]]:
        """Look up provider info for a given slot index."""
        if index == PAID_FALLBACK_INDEX:
            return {"index": PAID_FALLBACK_INDEX, "provider": "deepseek (paid)", "model": "deepseek-chat"}
        for item in FREE_PROVIDER_POOL:
            if item["index"] == index:
                return item
        return None

    def rotate(self, exhaust_current: bool = True) -> int:
        """
        Advance to the next non-exhausted provider.
        If all free providers are exhausted, switches to paid sentinel (99).
        """
        current_idx = self.state.get("current_index", 0)
        exhausted = set(self.state.get("exhausted", []))

        if exhaust_current and current_idx < TOTAL_FREE_SLOTS:
            exhausted.add(current_idx)

        # Find next available index >= current_idx + 1 up to TOTAL_FREE_SLOTS - 1
        next_idx = None
        for i in range(current_idx + 1, TOTAL_FREE_SLOTS):
            if i not in exhausted:
                next_idx = i
                break

        # If not found after current_idx, check from 0 up to current_idx
        if next_idx is None:
            for i in range(0, current_idx):
                if i not in exhausted:
                    next_idx = i
                    break

        if next_idx is None:
            # All free slots exhausted -> switch to paid fallback sentinel
            next_idx = PAID_FALLBACK_INDEX

        self.state["current_index"] = next_idx
        self.state["exhausted"] = sorted(list(exhausted))

        info = self.get_slot_info(next_idx)
        if info:
            self.state["gateway_primary"] = info["provider"]
            self.state["gateway_model"] = info["model"]

        self.save_state()
        return next_idx

    def reset(self) -> None:
        """Reset rotator state: clear exhausted list and return to index 0."""
        now = datetime.now(timezone.utc).isoformat()
        self.state["current_index"] = 0
        self.state["exhausted"] = []
        self.state["last_reset"] = now
        info = self.get_slot_info(0)
        if info:
            self.state["gateway_primary"] = info["provider"]
            self.state["gateway_model"] = info["model"]
        self.save_state()

    def skip(self) -> int:
        """Mark current provider as exhausted and rotate immediately."""
        return self.rotate(exhaust_current=True)


def main():
    parser = argparse.ArgumentParser(description="FMR State Management CLI")
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # Status
    subparsers.add_parser("status", help="Show current rotator status")

    # Rotate
    rotate_parser = subparsers.add_parser("rotate", help="Rotate to next provider")
    rotate_parser.add_argument("--exhaust-current", action="store_true", default=True, help="Mark current index exhausted")

    # Skip
    subparsers.add_parser("skip", help="Mark current provider exhausted and rotate")

    # Reset
    subparsers.add_parser("reset", help="Reset exhausted list and return to slot 0")

    # Paid
    subparsers.add_parser("paid", help="Force switch to paid fallback provider")

    args = parser.parse_args()
    mgr = RotatorStateManager()

    if args.command == "status" or not args.command:
        state = mgr.get_state()
        curr_idx = state.get("current_index", 0)
        slot = mgr.get_slot_info(curr_idx)
        print("FMR State Status")
        print("================")
        print(f"Current Index   : {curr_idx}")
        print(f"Current Provider: {state.get('gateway_primary')}")
        print(f"Current Model   : {state.get('gateway_model')}")
        print(f"Exhausted Slots : {state.get('exhausted', [])}")
        print(f"Last Reset      : {state.get('last_reset')}")
        print(f"Last Updated    : {state.get('last_updated')}")
        if slot:
            print(f"Slot Mapping    : {slot['provider']} -> {slot['model']}")
    elif args.command == "rotate" or args.command == "skip":
        new_idx = mgr.rotate(exhaust_current=True)
        slot = mgr.get_slot_info(new_idx)
        print(f"Rotated to slot {new_idx}: {slot['provider'] if slot else 'unknown'} ({slot['model'] if slot else 'unknown'})")
    elif args.command == "reset":
        mgr.reset()
        print("FMR reset complete: current_index=0, exhausted list cleared.")
    elif args.command == "paid":
        mgr.state["current_index"] = PAID_FALLBACK_INDEX
        mgr.state["gateway_primary"] = "deepseek"
        mgr.state["gateway_model"] = "deepseek-chat"
        mgr.save_state()
        print(f"Switched to PAID fallback: index {PAID_FALLBACK_INDEX} (deepseek/deepseek-chat)")


if __name__ == "__main__":
    main()
