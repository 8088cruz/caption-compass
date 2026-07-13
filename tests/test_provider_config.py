import json
import os
import subprocess
import sys
import unittest

from caption_compass.provider_config import (
    ProviderConfigError,
    build_provider_status,
    get_fireworks_api_key,
    load_provider_config,
    validate_provider_ready,
)


class ProviderConfigTests(unittest.TestCase):
    def test_default_stub_status_is_public_safe(self) -> None:
        status = build_provider_status({})

        self.assertEqual(status["gate"], "C6A")
        self.assertEqual(status["provider"], "stub")
        self.assertFalse(status["network_enabled"])
        self.assertFalse(status["network_used"])
        self.assertFalse(status["api_key_present"])
        self.assertTrue(status["provider_ready"])
        self.assertFalse(status["local_paths_included"])
        self.assertEqual(status["warnings"], [])

    def test_fireworks_missing_key_is_not_ready_without_leaking_secret(self) -> None:
        status = build_provider_status(
            {
                "CAPTION_COMPASS_PROVIDER": "fireworks",
                "CAPTION_COMPASS_VISION_MODEL": "vision-model",
                "CAPTION_COMPASS_TEXT_MODEL": "text-model",
                "CAPTION_COMPASS_AUDIO_MODEL": "audio-model",
            }
        )

        self.assertEqual(status["provider"], "fireworks")
        self.assertTrue(status["network_enabled"])
        self.assertFalse(status["network_used"])
        self.assertFalse(status["api_key_present"])
        self.assertFalse(status["provider_ready"])
        self.assertIn("FIREWORKS_API_KEY", " ".join(status["warnings"]))

    def test_validate_fireworks_ready_requires_capability_model(self) -> None:
        config = load_provider_config(
            {
                "CAPTION_COMPASS_PROVIDER": "fireworks",
                "FIREWORKS_API_KEY": "super-secret-test-key",
                "CAPTION_COMPASS_TEXT_MODEL": "text-model",
                "CAPTION_COMPASS_AUDIO_MODEL": "audio-model",
            }
        )

        with self.assertRaises(ProviderConfigError) as raised:
            validate_provider_ready(config, "vision")

        message = str(raised.exception)
        self.assertIn("CAPTION_COMPASS_VISION_MODEL", message)
        self.assertNotIn("super-secret-test-key", message)

    def test_validate_fireworks_ready_accepts_configured_vision(self) -> None:
        config = load_provider_config(
            {
                "CAPTION_COMPASS_PROVIDER": "fireworks",
                "FIREWORKS_API_KEY": "super-secret-test-key",
                "CAPTION_COMPASS_VISION_MODEL": "vision-model",
            }
        )

        validate_provider_ready(config, "vision")

    def test_get_fireworks_api_key_is_explicit_and_not_in_public_status(self) -> None:
        env = {
            "CAPTION_COMPASS_PROVIDER": "fireworks",
            "FIREWORKS_API_KEY": "super-secret-test-key",
            "CAPTION_COMPASS_VISION_MODEL": "vision-model",
        }

        self.assertEqual(get_fireworks_api_key(env), "super-secret-test-key")
        status_json = json.dumps(build_provider_status(env))
        self.assertNotIn("super-secret-test-key", status_json)

    def test_invalid_provider_fails_clearly(self) -> None:
        with self.assertRaises(ProviderConfigError) as raised:
            load_provider_config({"CAPTION_COMPASS_PROVIDER": "not-a-provider"})

        self.assertIn("Unsupported CAPTION_COMPASS_PROVIDER", str(raised.exception))

    def test_invalid_timeout_fails_clearly(self) -> None:
        with self.assertRaises(ProviderConfigError) as raised:
            load_provider_config({"CAPTION_COMPASS_PROVIDER_TIMEOUT_SECONDS": "zero"})

        self.assertIn("CAPTION_COMPASS_PROVIDER_TIMEOUT_SECONDS", str(raised.exception))

    def test_provider_status_cli_outputs_sanitized_json(self) -> None:
        env = os.environ.copy()
        env.update(
            {
                "CAPTION_COMPASS_PROVIDER": "fireworks",
                "FIREWORKS_API_KEY": "super-secret-test-key",
                "CAPTION_COMPASS_VISION_MODEL": "vision-model",
            }
        )

        result = subprocess.run(
            [sys.executable, "-m", "caption_compass", "provider-status"],
            check=True,
            capture_output=True,
            env=env,
            text=True,
        )

        status = json.loads(result.stdout)
        self.assertEqual(status["gate"], "C6A")
        self.assertEqual(status["provider"], "fireworks")
        self.assertTrue(status["api_key_present"])
        self.assertNotIn("super-secret-test-key", result.stdout)

    def test_stub_provider_is_ready_for_future_stub_calls(self) -> None:
        config = load_provider_config({"CAPTION_COMPASS_PROVIDER": "stub"})

        validate_provider_ready(config, "vision")
        validate_provider_ready(config, "text")
        validate_provider_ready(config, "audio")


if __name__ == "__main__":
    unittest.main()
