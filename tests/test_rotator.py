import os
import json
import re
import tempfile
import unittest

# Models defined in the rotation table in SKILL.md
MODELS_IN_POOL = [
    ("openrouter", "cohere/north-mini-code:free"),
    ("openrouter", "dots-studio/dots-3-note-preview:free"),
    ("openrouter", "nvidia/nemotron-3-super-120b-a12b:free"),
    ("openrouter", "inclusionai/ling-3.0-flash-vl:free"),
    ("openrouter", "inclusionai/ling-3.0-flash-fin:free"),
    ("openrouter", "inclusionai/ling-3.0-flash-sante:free"),
    ("openrouter", "nex-agi/nex-n2.5-mini:free"),
    ("openrouter", "liquid/lfm-2.5-2.6b:free"),
    ("openrouter", "openrouter/free"),
    ("openrouter", "poolside/laguna-xs-2.1:free"),
    ("openrouter", "poolside/laguna-s-2.1:free"),
    ("openrouter", "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free"),
    ("openrouter", "nex-agi/nex-n2.5-pro:free"),
    ("openrouter", "nvidia/nemotron-3.5-lightning:free"),
    ("openrouter", "nvidia/nemotron-3-ultra-550b-a55b:free"),
    ("deepseek", "deepseek-chat"),
    ("zai", "glm-5.2:free"),
    ("gemini", "gemini-1.5-flash"),
    ("xiaomi", "mimo-2.5-pro"),
    ("copilot", "gpt-4o-mini"),
]

class TestRotator(unittest.TestCase):
    def test_sed_regex_replacement_handles_slashes(self):
        """Verify that using '#' as delimiter in sed-style replacement safely handles model names with '/' and ':'."""
        sample_yaml = """model:
  provider: old-provider
  default: old-model
  name: old-model
"""
        for provider, model in MODELS_IN_POOL:
            sub_provider = re.sub(r"^  provider: .*", f"  provider: {provider}", sample_yaml, flags=re.MULTILINE)
            sub_default = re.sub(r"^  default: .*", f"  default: {model}", sub_provider, flags=re.MULTILINE)
            sub_name = re.sub(r"^  name: .*", f"  name: {model}", sub_default, flags=re.MULTILINE)
            
            self.assertIn(f"  provider: {provider}", sub_name)
            self.assertIn(f"  default: {model}", sub_name)
            self.assertIn(f"  name: {model}", sub_name)

    def test_update_state_cli_and_schema(self):
        """Verify update_state module can load, inspect, rotate, and reset the canonical state.json schema."""
        import update_state

        with tempfile.TemporaryDirectory() as tmpdir:
            state_file = os.path.join(tmpdir, "state.json")
            initial_state = {
                "current_index": 0,
                "exhausted": [8],
                "last_reset": "2026-09-14T11:55:58.708723+00:00",
                "session_start": "2026-09-14T11:55:58.708723+00:00",
                "gateway_primary": "openrouter",
                "gateway_model": "cohere/north-mini-code:free",
                "fallback_providers": [
                    {"provider": "openrouter", "model": "nex-agi/nex-n2.5-mini:free"},
                    {"provider": "deepseek", "model": "deepseek-chat"}
                ],
                "last_updated": "2026-09-14T11:55:58.708723+00:00",
                "policy": "free-first with paid fallback"
            }
            with open(state_file, "w", encoding="utf-8") as f:
                json.dump(initial_state, f)

            mgr = update_state.RotatorStateManager(state_path=state_file)
            state = mgr.get_state()
            self.assertEqual(state["current_index"], 0)
            self.assertIn(8, state["exhausted"])

            # Rotate to next available (skip 8 if current was 7)
            mgr.state["current_index"] = 7
            next_idx = mgr.rotate(exhaust_current=True)
            self.assertEqual(next_idx, 9)
            self.assertIn(7, mgr.state["exhausted"])
            self.assertEqual(mgr.state["current_index"], 9)

            # Exhaust all up to 20 -> should switch to sentinel 99 (paid fallback)
            mgr.state["exhausted"] = list(range(20))
            mgr.state["current_index"] = 19
            paid_idx = mgr.rotate(exhaust_current=True)
            self.assertEqual(paid_idx, 99)
            self.assertEqual(mgr.state["current_index"], 99)

            # Reset
            mgr.reset()
            self.assertEqual(mgr.state["current_index"], 0)
            self.assertEqual(mgr.state["exhausted"], [8])

    def test_cli_subcommands(self):
        """Verify CLI argument commands status, skip, paid work directly."""
        import update_state

        with tempfile.TemporaryDirectory() as tmpdir:
            state_file = os.path.join(tmpdir, "state.json")
            mgr = update_state.RotatorStateManager(state_path=state_file)
            self.assertEqual(mgr.state["current_index"], 0)

            # Skip
            new_idx = mgr.skip()
            self.assertEqual(new_idx, 1)
            self.assertIn(0, mgr.state["exhausted"])

            # Slot info lookup
            slot = mgr.get_slot_info(new_idx)
            self.assertIsNotNone(slot)
            self.assertEqual(slot["provider"], "openrouter")
            self.assertEqual(slot["model"], "dots-studio/dots-3-note-preview:free")

            # Paid lookup
            paid_slot = mgr.get_slot_info(99)
            self.assertEqual(paid_slot["provider"], "deepseek (paid)")

if __name__ == "__main__":
    unittest.main()
