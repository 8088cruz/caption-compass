"""C4 four-tone caption contract boundary.

This module renders exactly the four required Track 2 caption tones from a C3
scene core. It preserves the same factual claim set across tones, excludes
unsupported inferences, and does not call model providers or evaluators.
"""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any

from .scene_core import SCENE_CORE_SCHEMA_VERSION
from .video_ingestion import sanitize_source_identifier

CAPTION_SCHEMA_VERSION = "c4.four_tone_captions.v1"
DETERMINISTIC_STUB_MODE = "deterministic_stub"
TONE_KEYS = ("formal", "sarcastic", "humorous-tech", "humorous-non-tech")

TONE_RUBRICS = {
    "formal": "Neutral, professional, concise, and fact-preserving.",
    "sarcastic": "Dry understatement without hostility, ridicule, or new facts.",
    "humorous-tech": "Light software-oriented humor using common terms only, with no new facts.",
    "humorous-non-tech": "General-audience light humor with no niche references and no new facts.",
}

_LOCAL_PATH_PATTERN = re.compile(
    r"(^|[\s\"'])/(?:home|root|tmp|workspace|Users|var|private)/|[A-Za-z]:\\|file://"
)


class CaptionGenerationError(RuntimeError):
    """Base error for public-safe caption generation failures."""


class InvalidSceneCoreError(CaptionGenerationError, ValueError):
    """Raised when C3 scene core JSON cannot be rendered into C4 captions."""


def load_scene_core_json(input_path: str | Path) -> dict[str, Any]:
    """Load C3 scene core JSON without leaking local paths in errors."""

    path = Path(input_path)
    safe_name = sanitize_source_identifier(path.name or "scene-core.json")
    try:
        raw_text = path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise InvalidSceneCoreError(f"Scene core file not found: {safe_name}") from exc
    except OSError as exc:
        raise InvalidSceneCoreError(f"Scene core file is not readable: {safe_name}") from exc

    try:
        payload = json.loads(raw_text)
    except json.JSONDecodeError as exc:
        raise InvalidSceneCoreError(
            f"Scene core JSON is malformed in {safe_name} at line {exc.lineno}, column {exc.colno}"
        ) from exc

    if not isinstance(payload, dict):
        raise InvalidSceneCoreError("Scene core JSON must be an object.")
    return payload


def generate_four_tone_captions(
    scene_core: dict[str, Any],
    *,
    mode: str = DETERMINISTIC_STUB_MODE,
) -> dict[str, Any]:
    """Generate a deterministic four-tone caption contract from a C3 scene core."""

    if mode != DETERMINISTIC_STUB_MODE:
        raise CaptionGenerationError("C4 currently supports deterministic_stub mode only.")

    scene_core_id = _require_scene_core_id(scene_core)
    evidence_anchor_ids = _safe_string_list(scene_core.get("evidence_anchor_ids"))
    supported_claims = _extract_supported_claims(scene_core, evidence_anchor_ids)
    unsupported_inferences = _excluded_unsupported_inferences(scene_core.get("unsupported_inferences"))
    fact_lock_id = _stable_fact_lock_id(scene_core_id, supported_claims, unsupported_inferences)

    captions = {
        tone_key: _caption_entry(
            tone_key=tone_key,
            scene_core_id=scene_core_id,
            fact_lock_id=fact_lock_id,
            evidence_anchor_ids=evidence_anchor_ids,
            supported_claims=supported_claims,
        )
        for tone_key in TONE_KEYS
    }

    payload = {
        "schema_version": CAPTION_SCHEMA_VERSION,
        "gate": "C4",
        "scene_core_id": scene_core_id,
        "source_scene_core": {
            "schema_version": scene_core.get("schema_version"),
            "gate": scene_core.get("gate"),
            "evidence_anchor_ids": evidence_anchor_ids,
        },
        "tone_order": list(TONE_KEYS),
        "captions": captions,
        "fact_lock": {
            "fact_lock_id": fact_lock_id,
            "scene_core_id": scene_core_id,
            "supported_claims": supported_claims,
            "caption_claim_policy": "all tones use the same supported_claims list",
        },
        "unsupported_inferences": unsupported_inferences,
        "generation": {
            "mode": mode,
            "network_used": False,
            "provider": None,
            "input_contract": SCENE_CORE_SCHEMA_VERSION,
            "output_contract": CAPTION_SCHEMA_VERSION,
        },
        "contract_boundary": {
            "exactly_four_tones": True,
            "tone_keys": list(TONE_KEYS),
            "local_paths_included": False,
            "does_not_include": [
                "evaluator scoring",
                "repair loop",
                "fine tuning",
                "leaderboard claims",
                "provider calls",
                "new factual claims outside the scene core",
            ],
        },
    }
    _ensure_public_safe_payload(payload)
    return payload


def write_captions_json(captions: dict[str, Any], output_path: str | Path) -> None:
    """Write four-tone captions JSON deterministically."""

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(captions, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _require_scene_core_id(scene_core: dict[str, Any]) -> str:
    if scene_core.get("schema_version") != SCENE_CORE_SCHEMA_VERSION:
        raise InvalidSceneCoreError("Expected c3.scene_core.v1 scene core.")
    if scene_core.get("gate") not in (None, "C3"):
        raise InvalidSceneCoreError("Expected C3 scene core.")
    contract_boundary = scene_core.get("contract_boundary")
    if isinstance(contract_boundary, dict) and contract_boundary.get("local_paths_included") is True:
        raise InvalidSceneCoreError("Scene core with local paths cannot be used for C4 output.")

    scene_core_id = scene_core.get("scene_core_id")
    if not isinstance(scene_core_id, str) or not scene_core_id.strip():
        raise InvalidSceneCoreError("Scene core must include scene_core_id.")
    return scene_core_id.strip()


def _extract_supported_claims(
    scene_core: dict[str, Any],
    fallback_anchor_ids: list[str],
) -> list[dict[str, Any]]:
    claims: list[dict[str, Any]] = []

    summary = _clean_text(scene_core.get("summary"))
    if summary:
        claims.append(_claim("summary", summary, fallback_anchor_ids))

    claims.extend(
        _claims_from_items(
            "observed_entities",
            scene_core.get("observed_entities"),
            fallback_anchor_ids,
        )
    )
    claims.extend(
        _claims_from_items(
            "visible_actions",
            scene_core.get("visible_actions"),
            fallback_anchor_ids,
        )
    )

    setting = scene_core.get("setting_or_context")
    if isinstance(setting, dict) and not _is_unsupported_support(setting.get("support")):
        value = _clean_text(setting.get("value"))
        if value:
            claims.append(
                _claim(
                    "setting_or_context",
                    value,
                    _safe_string_list(setting.get("evidence_anchor_ids")) or fallback_anchor_ids,
                )
            )

    claims.extend(_claims_from_items("visible_text", scene_core.get("visible_text"), fallback_anchor_ids))
    claims.extend(_claims_from_items("audio_notes", scene_core.get("audio_notes"), fallback_anchor_ids))

    return [
        {"claim_id": f"claim_{index:04d}", **claim}
        for index, claim in enumerate(claims, start=1)
    ]


def _claims_from_items(
    claim_type: str,
    raw_items: Any,
    fallback_anchor_ids: list[str],
) -> list[dict[str, Any]]:
    if not isinstance(raw_items, list):
        return []

    claims: list[dict[str, Any]] = []
    for item in raw_items:
        text: str | None = None
        evidence_anchor_ids = fallback_anchor_ids

        if isinstance(item, str):
            text = _clean_text(item)
        elif isinstance(item, dict):
            text = (
                _clean_text(item.get("text"))
                or _clean_text(item.get("label"))
                or _clean_text(item.get("value"))
                or _clean_text(item.get("description"))
            )
            item_anchor_ids = _safe_string_list(item.get("evidence_anchor_ids"))
            if item_anchor_ids:
                evidence_anchor_ids = item_anchor_ids

        if text:
            claims.append(_claim(claim_type, text, evidence_anchor_ids))
    return claims


def _claim(claim_type: str, text: str, evidence_anchor_ids: list[str]) -> dict[str, Any]:
    return {
        "claim_type": claim_type,
        "text": text,
        "evidence_anchor_ids": evidence_anchor_ids,
    }


def _excluded_unsupported_inferences(raw_items: Any) -> list[dict[str, Any]]:
    if not isinstance(raw_items, list):
        return []

    excluded: list[dict[str, Any]] = []
    for item in raw_items:
        if not isinstance(item, dict):
            continue
        claim_type = _clean_text(item.get("claim_type")) or "unsupported"
        claim = _clean_text(item.get("claim")) or "unsupported inference"
        excluded.append(
            {
                "claim_type": claim_type,
                "claim": claim,
                "caption_policy": "excluded_from_caption_claims",
                "evidence_anchor_ids": _safe_string_list(item.get("evidence_anchor_ids")),
            }
        )
    return excluded


def _caption_entry(
    *,
    tone_key: str,
    scene_core_id: str,
    fact_lock_id: str,
    evidence_anchor_ids: list[str],
    supported_claims: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "scene_core_id": scene_core_id,
        "tone": tone_key,
        "caption": _caption_text(tone_key, supported_claims),
        "tone_rubric": TONE_RUBRICS[tone_key],
        "fact_lock_id": fact_lock_id,
        "factual_claim_ids": [claim["claim_id"] for claim in supported_claims],
        "evidence_anchor_ids": evidence_anchor_ids,
    }


def _caption_text(tone_key: str, supported_claims: list[dict[str, Any]]) -> str:
    if not supported_claims:
        no_fact_captions = {
            "formal": (
                "Timestamped video evidence is available, but the scene core contains "
                "no supported visual facts to describe."
            ),
            "sarcastic": "The frame anchors showed up; the verified scene details did not.",
            "humorous-tech": "Frame anchors compiled successfully; visual facts returned an empty list.",
            "humorous-non-tech": "The video has bookmarks, but no confirmed scene details yet.",
        }
        return no_fact_captions[tone_key]

    factual_sentence = _factual_sentence(supported_claims)
    captions = {
        "formal": factual_sentence,
        "sarcastic": f"The verified facts are doing the work here: {factual_sentence}",
        "humorous-tech": f"Stable scene core loaded: {factual_sentence}",
        "humorous-non-tech": f"Same facts, lighter delivery: {factual_sentence}",
    }
    return captions[tone_key]


def _factual_sentence(supported_claims: list[dict[str, Any]]) -> str:
    grouped: dict[str, list[str]] = {}
    for claim in supported_claims:
        grouped.setdefault(claim["claim_type"], []).append(claim["text"])

    parts: list[str] = []
    if grouped.get("summary"):
        parts.append(_join_values("Summary", grouped["summary"]))
    if grouped.get("observed_entities"):
        parts.append(_join_values("Observed entities", grouped["observed_entities"]))
    if grouped.get("visible_actions"):
        parts.append(_join_values("Visible actions", grouped["visible_actions"]))
    if grouped.get("setting_or_context"):
        parts.append(_join_values("Setting/context", grouped["setting_or_context"]))
    if grouped.get("visible_text"):
        parts.append(_join_values("Visible text", grouped["visible_text"]))
    if grouped.get("audio_notes"):
        parts.append(_join_values("Audio notes", grouped["audio_notes"]))

    return "; ".join(parts) + "."


def _join_values(label: str, values: list[str]) -> str:
    return f"{label}: {', '.join(values)}"


def _stable_fact_lock_id(
    scene_core_id: str,
    supported_claims: list[dict[str, Any]],
    unsupported_inferences: list[dict[str, Any]],
) -> str:
    canonical = json.dumps(
        {
            "scene_core_id": scene_core_id,
            "supported_claims": supported_claims,
            "unsupported_inferences": unsupported_inferences,
        },
        sort_keys=True,
        separators=(",", ":"),
    )
    digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    return f"fact_lock_{digest[:16]}"


def _clean_text(raw_value: Any) -> str | None:
    if not isinstance(raw_value, str):
        return None
    text = " ".join(raw_value.strip().split())
    if not text:
        return None
    return text[:240]


def _safe_string_list(raw_items: Any) -> list[str]:
    if not isinstance(raw_items, list):
        return []
    safe_items: list[str] = []
    for item in raw_items:
        if not isinstance(item, str):
            continue
        value = re.sub(r"[^A-Za-z0-9_.:-]+", "_", item.strip()).strip("_")
        if value:
            safe_items.append(value[:96])
    return safe_items


def _is_unsupported_support(raw_value: Any) -> bool:
    value = _clean_text(raw_value)
    return value is None or value.startswith("unsupported")


def _ensure_public_safe_payload(payload: dict[str, Any]) -> None:
    serialized = json.dumps(payload, sort_keys=True)
    if _LOCAL_PATH_PATTERN.search(serialized):
        raise CaptionGenerationError("C4 caption output contains local path-like content.")
