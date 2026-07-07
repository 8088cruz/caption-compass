"""C3 factual scene core contract boundary.

This module converts C2 timestamped frame evidence into a deterministic JSON
contract. It does not inspect pixels, interpret scenes, generate captions,
evaluate tone, repair output, transcribe audio, or call model providers.
"""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any

from .video_ingestion import sanitize_source_identifier

SCENE_CORE_SCHEMA_VERSION = "c3.scene_core.v1"
FRAME_EVIDENCE_SCHEMA_VERSION = "c2.frame_evidence.v1"
DETERMINISTIC_STUB_MODE = "deterministic_stub"

_LOCAL_PATH_PATTERN = re.compile(
    r"(^|[\s\"'])/(?:home|root|tmp|workspace|Users|var|private)/|[A-Za-z]:\\|file://"
)


class SceneCoreError(RuntimeError):
    """Base error for public-safe scene core failures."""


class InvalidSceneEvidenceError(SceneCoreError, ValueError):
    """Raised when C2 evidence cannot be converted into a C3 contract."""


def load_frame_evidence_json(input_path: str | Path) -> dict[str, Any]:
    """Load C2 evidence JSON without leaking local paths in errors."""

    path = Path(input_path)
    safe_name = sanitize_source_identifier(path.name or "frame-evidence.json")
    try:
        raw_text = path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise InvalidSceneEvidenceError(f"Evidence file not found: {safe_name}") from exc
    except OSError as exc:
        raise InvalidSceneEvidenceError(f"Evidence file is not readable: {safe_name}") from exc

    try:
        payload = json.loads(raw_text)
    except json.JSONDecodeError as exc:
        raise InvalidSceneEvidenceError(
            f"Evidence JSON is malformed in {safe_name} at line {exc.lineno}, column {exc.colno}"
        ) from exc

    if not isinstance(payload, dict):
        raise InvalidSceneEvidenceError("Evidence JSON must be an object.")
    return payload


def build_scene_core(
    frame_evidence: dict[str, Any],
    *,
    mode: str = DETERMINISTIC_STUB_MODE,
) -> dict[str, Any]:
    """Build a stable C3 scene core contract from C2 frame evidence."""

    if mode != DETERMINISTIC_STUB_MODE:
        raise SceneCoreError("C3 currently supports deterministic_stub mode only.")

    anchors, warnings = _extract_evidence_anchors(frame_evidence)
    source_video = _safe_source_video(frame_evidence.get("source_video"))
    anchor_ids = [anchor["anchor_id"] for anchor in anchors]

    id_basis = {
        "schema_version": SCENE_CORE_SCHEMA_VERSION,
        "source_video_identifier": source_video["identifier"],
        "evidence_anchors": anchors,
    }
    scene_core_id = _stable_scene_core_id(id_basis)

    payload = {
        "schema_version": SCENE_CORE_SCHEMA_VERSION,
        "gate": "C3",
        "scene_core_id": scene_core_id,
        "source_evidence": {
            "schema_version": frame_evidence.get("schema_version"),
            "gate": frame_evidence.get("gate"),
            "source_video_identifier": source_video["identifier"],
            "evidence_anchor_count": len(anchors),
        },
        "source_video": source_video,
        "evidence_anchor_ids": anchor_ids,
        "evidence_anchors": anchors,
        "summary": None,
        "observed_entities": [],
        "visible_actions": [],
        "setting_or_context": {
            "value": None,
            "support": "unsupported_from_c2_frame_metadata_only",
            "evidence_anchor_ids": [],
        },
        "visible_text": [],
        "audio_notes": [],
        "unsupported_inferences": _unsupported_inferences(anchor_ids),
        "uncertainty_notes": _uncertainty_notes(anchor_ids, warnings),
        "generation": {
            "mode": mode,
            "network_used": False,
            "provider": None,
            "input_contract": FRAME_EVIDENCE_SCHEMA_VERSION,
            "output_contract": SCENE_CORE_SCHEMA_VERSION,
        },
        "contract_boundary": {
            "style_free": True,
            "local_paths_included": False,
            "does_not_include": [
                "tone generation",
                "caption generation",
                "evaluator scoring",
                "repair loop",
                "audio transcription",
                "provider calls",
            ],
        },
    }
    _ensure_public_safe_payload(payload)
    return payload


def write_scene_core_json(scene_core: dict[str, Any], output_path: str | Path) -> None:
    """Write scene core JSON deterministically."""

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(scene_core, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _extract_evidence_anchors(frame_evidence: dict[str, Any]) -> tuple[list[dict[str, Any]], list[str]]:
    if frame_evidence.get("schema_version") != FRAME_EVIDENCE_SCHEMA_VERSION:
        raise InvalidSceneEvidenceError("Expected c2.frame_evidence.v1 evidence.")
    if frame_evidence.get("gate") not in (None, "C2"):
        raise InvalidSceneEvidenceError("Expected C2 frame evidence.")

    extraction = frame_evidence.get("extraction")
    if isinstance(extraction, dict) and extraction.get("local_paths_included") is True:
        raise InvalidSceneEvidenceError("C2 evidence with local paths cannot be used for C3 output.")

    frames = frame_evidence.get("frames")
    if not isinstance(frames, list) or not frames:
        raise InvalidSceneEvidenceError("C2 evidence must include at least one frame anchor.")

    source_video = _safe_source_video(frame_evidence.get("source_video"))
    source_slug = _slug_from_identifier(source_video["identifier"])

    warnings: list[str] = []
    anchors: list[dict[str, Any]] = []
    for index, frame in enumerate(frames, start=1):
        if not isinstance(frame, dict):
            raise InvalidSceneEvidenceError("Each frame anchor must be an object.")

        anchor_id = _safe_anchor_id(frame.get("frame_id"), index)
        timestamp_seconds = _safe_timestamp(frame.get("timestamp_seconds"), anchor_id)
        frame_ref = _safe_frame_ref(frame.get("frame_ref"), source_slug, anchor_id, warnings)
        timestamp_label = str(frame.get("timestamp_label") or _format_timestamp(timestamp_seconds))

        anchors.append(
            {
                "anchor_id": anchor_id,
                "frame_id": anchor_id,
                "frame_ref": frame_ref,
                "timestamp_seconds": timestamp_seconds,
                "timestamp_label": timestamp_label,
            }
        )

    return anchors, warnings


def _safe_source_video(raw_source_video: Any) -> dict[str, Any]:
    source_video = raw_source_video if isinstance(raw_source_video, dict) else {}
    source_id = sanitize_source_identifier(str(source_video.get("identifier") or "video"))
    return {
        "identifier": source_id,
        "duration_seconds": _optional_number(source_video.get("duration_seconds")),
        "width": _optional_int(source_video.get("width")),
        "height": _optional_int(source_video.get("height")),
        "frame_rate": _optional_number(source_video.get("frame_rate")),
    }


def _safe_anchor_id(raw_anchor_id: Any, index: int) -> str:
    candidate = str(raw_anchor_id or f"frame_{index:04d}").strip()
    safe = re.sub(r"[^A-Za-z0-9_-]+", "_", candidate).strip("_")
    return safe[:64] or f"frame_{index:04d}"


def _safe_timestamp(raw_timestamp: Any, anchor_id: str) -> float:
    if not isinstance(raw_timestamp, (int, float)):
        raise InvalidSceneEvidenceError(f"Frame anchor {anchor_id} must include timestamp_seconds.")
    timestamp = round(float(raw_timestamp), 3)
    if timestamp < 0:
        raise InvalidSceneEvidenceError(f"Frame anchor {anchor_id} timestamp_seconds cannot be negative.")
    return timestamp


def _safe_frame_ref(
    raw_frame_ref: Any,
    source_slug: str,
    anchor_id: str,
    warnings: list[str],
) -> str:
    candidate = str(raw_frame_ref or "").strip()
    if candidate.startswith("frame://") and not _LOCAL_PATH_PATTERN.search(candidate):
        return candidate

    warnings.append(f"Frame ref for {anchor_id} was regenerated as a stable public ref.")
    return f"frame://{source_slug}/{anchor_id}"


def _optional_number(raw_value: Any) -> float | None:
    if raw_value is None:
        return None
    if not isinstance(raw_value, (int, float)):
        return None
    return round(float(raw_value), 3)


def _optional_int(raw_value: Any) -> int | None:
    if isinstance(raw_value, bool):
        return None
    if not isinstance(raw_value, int):
        return None
    return raw_value


def _slug_from_identifier(identifier: str) -> str:
    stem = Path(identifier).stem or identifier
    slug = re.sub(r"[^A-Za-z0-9_-]+", "-", stem).strip("-").lower()
    return slug[:64] or "video"


def _stable_scene_core_id(id_basis: dict[str, Any]) -> str:
    canonical = json.dumps(id_basis, sort_keys=True, separators=(",", ":"))
    digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    return f"scene_core_{digest[:16]}"


def _unsupported_inferences(anchor_ids: list[str]) -> list[dict[str, Any]]:
    reason = (
        "C2 evidence supplies timestamped frame anchors only; deterministic C3 mode does not "
        "inspect image pixels or call a model provider."
    )
    return [
        {
            "claim_type": "observed_entities",
            "claim": "specific visible people, objects, brands, or text",
            "reason": reason,
            "evidence_anchor_ids": anchor_ids,
        },
        {
            "claim_type": "visible_actions",
            "claim": "specific movements, interactions, or events",
            "reason": reason,
            "evidence_anchor_ids": anchor_ids,
        },
        {
            "claim_type": "setting_or_context",
            "claim": "location, event context, mood, intent, or causality",
            "reason": reason,
            "evidence_anchor_ids": anchor_ids,
        },
        {
            "claim_type": "audio_or_speech",
            "claim": "spoken words, soundtrack content, or audio cues",
            "reason": "C2 evidence does not include audio transcription.",
            "evidence_anchor_ids": anchor_ids,
        },
    ]


def _uncertainty_notes(anchor_ids: list[str], warnings: list[str]) -> list[dict[str, Any]]:
    notes = [
        {
            "note": "Frame anchors establish sampling times and stable refs, not visual-semantic facts.",
            "evidence_anchor_ids": anchor_ids,
        },
        {
            "note": "Observed entities, visible actions, and setting remain unknown until supported by explicit evidence.",
            "evidence_anchor_ids": anchor_ids,
        },
    ]
    notes.extend({"note": warning, "evidence_anchor_ids": anchor_ids} for warning in warnings)
    return notes


def _format_timestamp(seconds: float) -> str:
    total_milliseconds = int(round(seconds * 1000))
    total_seconds, milliseconds = divmod(total_milliseconds, 1000)
    minutes, seconds_only = divmod(total_seconds, 60)
    return f"{minutes:02d}:{seconds_only:02d}.{milliseconds:03d}"


def _ensure_public_safe_payload(payload: dict[str, Any]) -> None:
    serialized = json.dumps(payload, sort_keys=True)
    if _LOCAL_PATH_PATTERN.search(serialized):
        raise SceneCoreError("C3 scene core output contains local path-like content.")
