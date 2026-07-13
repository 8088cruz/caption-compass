"""Public-safe provider configuration boundary for Caption Compass.

C6A adds configuration and validation only. It does not make provider calls.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Mapping

SUPPORTED_PROVIDERS = {"stub", "fireworks"}
DEFAULT_PROVIDER = "stub"
DEFAULT_TIMEOUT_SECONDS = 60


class ProviderConfigError(ValueError):
    """Raised when provider configuration is malformed or not ready."""


@dataclass(frozen=True)
class ProviderConfig:
    """Sanitized provider configuration.

    The raw API key is intentionally not stored on this object so it cannot
    leak through repr(), JSON artifacts, test failures, or CLI status output.
    """

    provider: str
    api_key_present: bool
    vision_model: str | None
    text_model: str | None
    audio_model: str | None
    timeout_seconds: int

    @property
    def network_enabled(self) -> bool:
        """Return whether this provider mode may use the network."""

        return self.provider == "fireworks"

    def to_public_dict(self) -> dict[str, object]:
        """Return provider status safe for artifacts, logs, and README examples."""

        warnings: list[str] = []
        if self.provider == "fireworks" and not self.api_key_present:
            warnings.append("FIREWORKS_API_KEY is required before Fireworks provider calls.")
        if self.provider == "fireworks" and not self.vision_model:
            warnings.append("CAPTION_COMPASS_VISION_MODEL is required before vision provider calls.")
        if self.provider == "fireworks" and not self.text_model:
            warnings.append("CAPTION_COMPASS_TEXT_MODEL is required before text provider calls.")
        if self.provider == "fireworks" and not self.audio_model:
            warnings.append("CAPTION_COMPASS_AUDIO_MODEL is required before audio provider calls.")

        return {
            "provider": self.provider,
            "network_enabled": self.network_enabled,
            "network_used": False,
            "api_key_present": self.api_key_present,
            "configured_models": {
                "vision": self.vision_model,
                "text": self.text_model,
                "audio": self.audio_model,
            },
            "timeout_seconds": self.timeout_seconds,
            "provider_ready": not warnings,
            "local_paths_included": False,
            "warnings": warnings,
        }


def _clean_env_value(value: str | None) -> str | None:
    if value is None:
        return None
    cleaned = value.strip()
    return cleaned or None


def _parse_timeout(raw_value: str | None) -> int:
    if raw_value is None or not raw_value.strip():
        return DEFAULT_TIMEOUT_SECONDS
    try:
        timeout = int(raw_value)
    except ValueError as exc:
        raise ProviderConfigError("CAPTION_COMPASS_PROVIDER_TIMEOUT_SECONDS must be an integer.") from exc
    if timeout <= 0:
        raise ProviderConfigError("CAPTION_COMPASS_PROVIDER_TIMEOUT_SECONDS must be greater than zero.")
    return timeout


def load_provider_config(env: Mapping[str, str] | None = None) -> ProviderConfig:
    """Load sanitized provider configuration from environment variables."""

    source: Mapping[str, str] = os.environ if env is None else env
    provider = _clean_env_value(source.get("CAPTION_COMPASS_PROVIDER")) or DEFAULT_PROVIDER
    provider = provider.lower()

    if provider not in SUPPORTED_PROVIDERS:
        supported = ", ".join(sorted(SUPPORTED_PROVIDERS))
        raise ProviderConfigError(f"Unsupported CAPTION_COMPASS_PROVIDER '{provider}'. Expected one of: {supported}.")

    api_key_present = bool(_clean_env_value(source.get("FIREWORKS_API_KEY")))

    return ProviderConfig(
        provider=provider,
        api_key_present=api_key_present,
        vision_model=_clean_env_value(source.get("CAPTION_COMPASS_VISION_MODEL")),
        text_model=_clean_env_value(source.get("CAPTION_COMPASS_TEXT_MODEL")),
        audio_model=_clean_env_value(source.get("CAPTION_COMPASS_AUDIO_MODEL")),
        timeout_seconds=_parse_timeout(source.get("CAPTION_COMPASS_PROVIDER_TIMEOUT_SECONDS")),
    )


def validate_provider_ready(config: ProviderConfig, capability: str) -> None:
    """Validate provider readiness before a future provider call.

    C6A does not call providers. Future gates should call this function before
    making a provider-backed vision, text, or audio request.
    """

    capability = capability.strip().lower()
    if capability not in {"vision", "text", "audio"}:
        raise ProviderConfigError("Provider capability must be one of: vision, text, audio.")

    if config.provider == "stub":
        return

    if config.provider == "fireworks" and not config.api_key_present:
        raise ProviderConfigError("CAPTION_COMPASS_PROVIDER=fireworks requires FIREWORKS_API_KEY before provider calls.")

    model_by_capability = {
        "vision": config.vision_model,
        "text": config.text_model,
        "audio": config.audio_model,
    }
    if config.provider == "fireworks" and not model_by_capability[capability]:
        env_name = {
            "vision": "CAPTION_COMPASS_VISION_MODEL",
            "text": "CAPTION_COMPASS_TEXT_MODEL",
            "audio": "CAPTION_COMPASS_AUDIO_MODEL",
        }[capability]
        raise ProviderConfigError(
            f"CAPTION_COMPASS_PROVIDER=fireworks requires {env_name} before {capability} provider calls."
        )


def build_provider_status(env: Mapping[str, str] | None = None) -> dict[str, object]:
    """Build a public-safe provider status artifact."""

    config = load_provider_config(env)
    return {
        "gate": "C6A",
        "schema_version": "c6a.provider_config.v1",
        **config.to_public_dict(),
    }


def get_fireworks_api_key(env: Mapping[str, str] | None = None) -> str:
    """Return the raw Fireworks API key for future provider clients only.

    Do not put this value in artifacts, logs, exceptions, or README examples.
    """

    source: Mapping[str, str] = os.environ if env is None else env
    api_key = _clean_env_value(source.get("FIREWORKS_API_KEY"))
    if not api_key:
        raise ProviderConfigError("FIREWORKS_API_KEY is required before Fireworks provider calls.")
    return api_key
