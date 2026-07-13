"""C6C frame observation provider seam.

This module turns sampled frame anchors into structured per-frame observations.
Stub mode is deterministic and network-free. Fireworks mode validates provider
configuration, reads persisted local JPGs, and sends image data without exposing
local paths or API keys in public outputs.
"""

from __future__ import annotations

import base64
import json
import re
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Mapping

from .provider_config import (
    ProviderConfig,
    ProviderConfigError,
    get_fireworks_api_key,
    load_provider_config,
    validate_provider_ready,
)

FIREWORKS_CHAT_COMPLETIONS_URL = "https://api.fireworks.ai/inference/v1/chat/completions"
OBSERVATION_SCHEMA_VERSION = "c6c.frame_observations.v1"


class VisionObservationError(RuntimeError):
    """Raised when frame observations cannot be produced safely."""


def _source_video_id(frame_evidence: Mapping[str, Any]) -> str:
    source_video = frame_evidence.get("source_video") or {}
    identifier = str(source_video.get("identifier") or "video")
    stem = Path(identifier).stem or identifier
    return re.sub(r"[^A-Za-z0-9_-]+", "-", stem).strip("-").lower()[:64] or "video"


def _frames_from_evidence(frame_evidence: Mapping[str, Any]) -> list[Mapping[str, Any]]:
    frames = frame_evidence.get("frames")
    if not isinstance(frames, list) or not frames:
        raise VisionObservationError("Frame evidence must include at least one frame.")
    return frames


def _frame_file_path(frame: Mapping[str, Any], frames_dir: Path | None) -> Path:
    frame_id = str(frame.get("frame_id") or "").strip()
    if not frame_id:
        raise VisionObservationError("Frame evidence contains a frame without frame_id.")
    if frames_dir is None:
        raise VisionObservationError("--frames-dir is required for provider-backed frame observations.")
    return frames_dir / f"{frame_id}.jpg"


def _ensure_frame_file(path: Path, frame_id: str) -> None:
    if not path.is_file() or path.stat().st_size <= 0:
        raise VisionObservationError(f"Persisted frame file is missing or empty for {frame_id}.")


def _base_observation(frame: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "frame_id": frame.get("frame_id"),
        "frame_ref": frame.get("frame_ref"),
        "timestamp_seconds": frame.get("timestamp_seconds"),
        "observed_entities": [],
        "visible_actions": [],
        "visible_text": [],
        "setting_or_context": None,
        "uncertainty_notes": [],
        "unsupported_inferences": [],
    }


def _stub_observation(frame: Mapping[str, Any], *, source_video_id: str) -> dict[str, Any]:
    observation = _base_observation(frame)
    observation["uncertainty_notes"] = [
        "Stub provider mode does not inspect pixels; visual content remains unknown."
    ]
    observation["unsupported_inferences"] = [
        "Any claim about objects, actions, text, setting, emotion, identity, or intent is unsupported until provider vision is used."
    ]
    observation["provider_evidence"] = {
        "mode": "stub",
        "source_video_id": source_video_id,
        "local_paths_included": False,
    }
    return observation


def _json_schema_prompt(frame: Mapping[str, Any]) -> str:
    frame_id = frame.get("frame_id")
    timestamp = frame.get("timestamp_seconds")
    return (
        "You are Caption Compass vision evidence extraction. "
        "Inspect this single video frame and return strict JSON only. "
        "Use only visible evidence. Do not infer identity, private attributes, emotion, motive, or causality. "
        "If uncertain, put the uncertainty in uncertainty_notes. "
        "Schema: {"
        '"observed_entities": ["visible noun phrases"], '
        '"visible_actions": ["visible actions"], '
        '"visible_text": ["exact visible text if any"], '
        '"setting_or_context": "visible setting or null", '
        '"uncertainty_notes": ["uncertainties"], '
        '"unsupported_inferences": ["things not supported"]'
        "}. "
        f"Frame id: {frame_id}. Timestamp seconds: {timestamp}."
    )


def _extract_json_object(text: str) -> dict[str, Any]:
    stripped = text.strip()
    if stripped.startswith("```"):
        stripped = re.sub(r"^```(?:json)?", "", stripped).strip()
        stripped = re.sub(r"```$", "", stripped).strip()
    try:
        payload = json.loads(stripped)
    except json.JSONDecodeError as exc:
        start = stripped.find("{")
        end = stripped.rfind("}")
        if start == -1 or end == -1 or end <= start:
            raise VisionObservationError("Provider returned malformed JSON for frame observation.") from exc
        try:
            payload = json.loads(stripped[start : end + 1])
        except json.JSONDecodeError as nested_exc:
            raise VisionObservationError("Provider returned malformed JSON for frame observation.") from nested_exc
    if not isinstance(payload, dict):
        raise VisionObservationError("Provider frame observation must be a JSON object.")
    return payload


def _coerce_string_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [value] if value.strip() else []
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    return [str(value).strip()] if str(value).strip() else []


def _coerce_provider_observation(frame: Mapping[str, Any], payload: Mapping[str, Any]) -> dict[str, Any]:
    observation = _base_observation(frame)
    observation["observed_entities"] = _coerce_string_list(payload.get("observed_entities"))
    observation["visible_actions"] = _coerce_string_list(payload.get("visible_actions"))
    observation["visible_text"] = _coerce_string_list(payload.get("visible_text"))
    setting = payload.get("setting_or_context")
    observation["setting_or_context"] = str(setting).strip() if setting not in (None, "") else None
    observation["uncertainty_notes"] = _coerce_string_list(payload.get("uncertainty_notes"))
    observation["unsupported_inferences"] = _coerce_string_list(payload.get("unsupported_inferences"))
    return observation


def _image_data_url(path: Path) -> str:
    data = path.read_bytes()
    encoded = base64.b64encode(data).decode("ascii")
    return f"data:image/jpeg;base64,{encoded}"


def _call_fireworks_vision(
    *,
    config: ProviderConfig,
    api_key: str,
    frame: Mapping[str, Any],
    frame_path: Path,
) -> dict[str, Any]:
    if not config.vision_model:
        raise ProviderConfigError("CAPTION_COMPASS_VISION_MODEL is required before vision provider calls.")

    request_payload = {
        "model": config.vision_model,
        "temperature": 0,
        "max_tokens": 700,
        "response_format": {"type": "json_object"},
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": _json_schema_prompt(frame)},
                    {"type": "image_url", "image_url": {"url": _image_data_url(frame_path)}},
                ],
            }
        ],
    }
    body = json.dumps(request_payload).encode("utf-8")
    request = urllib.request.Request(
        FIREWORKS_CHAT_COMPLETIONS_URL,
        data=body,
        method="POST",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=config.timeout_seconds) as response:
            response_payload = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")[:240]
        detail = detail.replace(api_key, "[redacted]")
        raise VisionObservationError(f"Fireworks vision request failed with HTTP {exc.code}. Detail: {detail}") from exc
    except urllib.error.URLError as exc:
        raise VisionObservationError("Fireworks vision request failed before a response was received.") from exc
    except TimeoutError as exc:
        raise VisionObservationError("Fireworks vision request timed out.") from exc

    try:
        content = response_payload["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError) as exc:
        raise VisionObservationError("Fireworks response did not contain a chat completion message.") from exc
    return _extract_json_object(str(content))


def observe_frames(
    frame_evidence: Mapping[str, Any],
    *,
    frames_dir: str | Path | None = None,
    env: Mapping[str, str] | None = None,
) -> dict[str, Any]:
    """Produce public-safe per-frame observations from C2 frame evidence."""

    config = load_provider_config(env)
    source_video_id = _source_video_id(frame_evidence)
    frames = _frames_from_evidence(frame_evidence)
    frames_root = Path(frames_dir) if frames_dir is not None else None

    observations: list[dict[str, Any]] = []
    network_used = False
    warnings: list[str] = []

    if config.provider == "stub":
        observations = [_stub_observation(frame, source_video_id=source_video_id) for frame in frames]
    elif config.provider == "fireworks":
        validate_provider_ready(config, "vision")
        api_key = get_fireworks_api_key(env)
        network_used = True
        for frame in frames:
            frame_id = str(frame.get("frame_id") or "")
            frame_path = _frame_file_path(frame, frames_root)
            _ensure_frame_file(frame_path, frame_id)
            provider_payload = _call_fireworks_vision(
                config=config,
                api_key=api_key,
                frame=frame,
                frame_path=frame_path,
            )
            observation = _coerce_provider_observation(frame, provider_payload)
            observation["provider_evidence"] = {
                "mode": "fireworks",
                "model": config.vision_model,
                "local_paths_included": False,
            }
            observations.append(observation)
    else:
        raise VisionObservationError(f"Unsupported provider for frame observations: {config.provider}")

    return {
        "schema_version": OBSERVATION_SCHEMA_VERSION,
        "gate": "C6C",
        "source_video_id": source_video_id,
        "provider": {
            "name": config.provider,
            "model": config.vision_model if config.provider == "fireworks" else "stub",
            "network_used": network_used,
            "local_paths_included": False,
        },
        "frames": observations,
        "warnings": warnings,
        "local_paths_included": False,
    }


def write_frame_observations_json(observations: Mapping[str, Any], output_path: str | Path) -> None:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(observations, indent=2, sort_keys=True) + "\n", encoding="utf-8")
