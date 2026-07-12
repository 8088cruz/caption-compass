"""C6 bounded caption repair trace.

This module runs at most one deterministic repair attempt for C5 repair-eligible
failed captions. It uses the existing C4 caption contract generator as the
stub repair source, re-evaluates with C5, and records before/after scores. It
does not mutate the C3 factual scene core, call providers, implement UI, or run
an unbounded loop.
"""

from __future__ import annotations

import copy
import json
import re
from pathlib import Path
from typing import Any

from .captions import CAPTION_SCHEMA_VERSION, TONE_KEYS, generate_four_tone_captions
from .evaluator import (
    EVALUATION_SCHEMA_VERSION,
    THRESHOLDS,
    EvaluationError,
    evaluate_captions,
)
from .scene_core import SCENE_CORE_SCHEMA_VERSION
from .video_ingestion import sanitize_source_identifier

REPAIR_SCHEMA_VERSION = "c6.repair_trace.v1"
DETERMINISTIC_STUB_MODE = "deterministic_stub"
MAX_REPAIR_ATTEMPTS = 1

REPAIRABLE_ISSUE_CODES = {
    "invented_fact",
    "missing_core_fact",
    "unsupported_inference_used",
    "uncertainty_overclaimed",
    "tone_mismatch",
    "tone_bleed",
    "unclear_joke",
}

NON_REPAIRABLE_ISSUE_CODES = {
    "scene_core_mismatch",
    "malformed_output",
    "unsafe_or_private_reference",
}

_LOCAL_PATH_PATTERN = re.compile(
    r"(^|[\s\"'])/(?:home|root|tmp|workspace|Users|var|private)/|[A-Za-z]:\\|file://"
)
_SECRET_PATTERN = re.compile(r"(?i)(api[_-]?key|secret|token|sk-[A-Za-z0-9_-]{8,})")
_PRIVATE_REFERENCE_PATTERN = re.compile(r"(?i)(private repo|internal-only|unpublished architecture|private research|private system)")


class RepairError(RuntimeError):
    """Base error for public-safe C6 repair failures."""


class InvalidRepairInputError(RepairError, ValueError):
    """Raised when C3/C4/C5 inputs cannot be used for repair."""


def load_evaluation_json(input_path: str | Path) -> dict[str, Any]:
    """Load C5 evaluation JSON without leaking local paths in errors."""

    path = Path(input_path)
    safe_name = sanitize_source_identifier(path.name or "evaluation.json")
    try:
        raw_text = path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise InvalidRepairInputError(f"Evaluation file not found: {safe_name}") from exc
    except OSError as exc:
        raise InvalidRepairInputError(f"Evaluation file is not readable: {safe_name}") from exc

    try:
        payload = json.loads(raw_text)
    except json.JSONDecodeError as exc:
        raise InvalidRepairInputError(
            f"Evaluation JSON is malformed in {safe_name} at line {exc.lineno}, column {exc.colno}"
        ) from exc

    if not isinstance(payload, dict):
        raise InvalidRepairInputError("Evaluation JSON must be an object.")
    return payload


def repair_captions(
    scene_core: dict[str, Any],
    captions: dict[str, Any],
    evaluation: dict[str, Any],
    *,
    mode: str = DETERMINISTIC_STUB_MODE,
) -> dict[str, Any]:
    """Run one bounded deterministic repair pass for C5 repair-eligible captions."""

    if mode != DETERMINISTIC_STUB_MODE:
        raise RepairError("C6 currently supports deterministic_stub mode only.")

    scene_core_id = _require_scene_core(scene_core)
    _require_caption_contract(captions, scene_core_id)
    _require_evaluation_contract(evaluation, scene_core_id)

    thresholds = _thresholds(evaluation)
    original_captions = copy.deepcopy(captions)
    final_caption_contract = copy.deepcopy(captions)
    canonical_repair_contract = generate_four_tone_captions(scene_core)

    repair_history: list[dict[str, Any]] = []
    hard_stops: list[dict[str, Any]] = []

    for tone in TONE_KEYS:
        before_eval = _tone_evaluation(evaluation, tone)
        if before_eval.get("passed") is True:
            continue

        before_issue_codes = _issue_codes(before_eval)
        if before_issue_codes & NON_REPAIRABLE_ISSUE_CODES:
            hard_stops.append(
                {
                    "caption_key": tone,
                    "reason": "non_repairable_issue",
                    "issue_codes": sorted(before_issue_codes & NON_REPAIRABLE_ISSUE_CODES),
                    "repair_attempted": False,
                }
            )
            continue

        if not bool(before_eval.get("repair_eligible")) or not _should_attempt_repair(before_eval, thresholds):
            hard_stops.append(
                {
                    "caption_key": tone,
                    "reason": "not_repair_eligible",
                    "issue_codes": sorted(before_issue_codes),
                    "repair_attempted": False,
                }
            )
            continue

        candidate_contract = copy.deepcopy(final_caption_contract)
        candidate_entry = copy.deepcopy(canonical_repair_contract["captions"][tone])
        candidate_contract["captions"][tone] = candidate_entry
        candidate_evaluation = evaluate_captions(scene_core, candidate_contract)
        after_eval = _tone_evaluation(candidate_evaluation, tone)
        accepted, acceptance_reason = _accepted_repair(before_eval, after_eval, thresholds)

        before_text = _caption_text(final_caption_contract, tone)
        after_text = _caption_text(candidate_contract, tone)
        history_entry = {
            "caption_key": tone,
            "attempt": 1,
            "repair_reason_codes": sorted(before_issue_codes),
            "rewrite_hint_used": before_eval.get("rewrite_hint"),
            "before": {
                "text": before_text,
                "scores": _scores(before_eval),
                "issues": sorted(before_issue_codes),
            },
            "after": {
                "text": after_text,
                "scores": _scores(after_eval),
                "issues": sorted(_issue_codes(after_eval)),
            },
            "accepted": accepted,
            "status": "accepted" if accepted else "rejected",
            "acceptance_reason": acceptance_reason,
        }
        repair_history.append(history_entry)

        if accepted:
            final_caption_contract = candidate_contract

    final_evaluation = evaluate_captions(scene_core, final_caption_contract)
    payload = {
        "schema_version": REPAIR_SCHEMA_VERSION,
        "gate": "C6",
        "scene_core_id": scene_core_id,
        "source_video_id": _source_video_id(scene_core),
        "max_repair_attempts": MAX_REPAIR_ATTEMPTS,
        "repair_thresholds": thresholds,
        "repairable_issue_codes": sorted(REPAIRABLE_ISSUE_CODES),
        "non_repairable_issue_codes": sorted(NON_REPAIRABLE_ISSUE_CODES),
        "repair_history": repair_history,
        "hard_stops": hard_stops,
        "final_captions": _final_caption_texts(final_caption_contract),
        "final_evaluation_summary": {
            "passed": bool(final_evaluation["overall"]["passed"]),
            "failed_caption_keys": final_evaluation["overall"]["failed_caption_keys"],
            "repair_recommended": bool(final_evaluation["overall"]["repair_recommended"]),
        },
        "overall": {
            "repair_attempted_count": len(repair_history),
            "accepted_count": sum(1 for item in repair_history if item["accepted"]),
            "rejected_count": sum(1 for item in repair_history if not item["accepted"]),
            "hard_stop_count": len(hard_stops),
            "max_attempts_per_caption_observed": max([item["attempt"] for item in repair_history], default=0),
            "passed_after_repair": bool(final_evaluation["overall"]["passed"]),
            "final_failed_caption_keys": final_evaluation["overall"]["failed_caption_keys"],
        },
        "generation": {
            "mode": mode,
            "network_used": False,
            "provider": None,
            "input_contracts": [SCENE_CORE_SCHEMA_VERSION, CAPTION_SCHEMA_VERSION, EVALUATION_SCHEMA_VERSION],
            "output_contract": REPAIR_SCHEMA_VERSION,
        },
        "contract_boundary": {
            "does_not_include": [
                "multiple repair loops",
                "human review workflow",
                "Streamlit UI",
                "Docker submission work",
                "fine tuning",
                "audio transcription",
                "provider calls",
                "leaderboard claims",
                "objective truth proof",
            ],
            "local_paths_included": False,
            "scores_are_heuristic": True,
            "source_captions_mutated": original_captions != captions,
            "factual_scene_core_mutated": False,
            "max_one_attempt_per_failed_caption": True,
        },
    }
    _ensure_public_safe_payload(payload)
    return payload


def write_repair_trace_json(repair_trace: dict[str, Any], output_path: str | Path) -> None:
    """Write C6 repair trace JSON deterministically."""

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(repair_trace, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _require_scene_core(scene_core: dict[str, Any]) -> str:
    if scene_core.get("schema_version") != SCENE_CORE_SCHEMA_VERSION:
        raise InvalidRepairInputError("Expected c3.scene_core.v1 scene core.")
    scene_core_id = scene_core.get("scene_core_id")
    if not isinstance(scene_core_id, str) or not scene_core_id.strip():
        raise InvalidRepairInputError("Scene core must include scene_core_id.")
    contract_boundary = scene_core.get("contract_boundary")
    if isinstance(contract_boundary, dict) and contract_boundary.get("local_paths_included") is True:
        raise InvalidRepairInputError("Scene core with local paths cannot be repaired against.")
    return scene_core_id.strip()


def _require_caption_contract(captions: dict[str, Any], scene_core_id: str) -> None:
    if captions.get("schema_version") != CAPTION_SCHEMA_VERSION:
        raise InvalidRepairInputError("Expected c4.four_tone_captions.v1 captions.")
    if captions.get("scene_core_id") != scene_core_id:
        raise InvalidRepairInputError("Caption contract scene_core_id must match the C3 scene core.")
    caption_map = captions.get("captions")
    if not isinstance(caption_map, dict):
        raise InvalidRepairInputError("Caption contract must include captions object.")
    missing = [tone for tone in TONE_KEYS if tone not in caption_map]
    if missing:
        raise InvalidRepairInputError(f"Caption contract is missing required tones: {', '.join(missing)}")
    contract_boundary = captions.get("contract_boundary")
    if isinstance(contract_boundary, dict) and contract_boundary.get("local_paths_included") is True:
        raise InvalidRepairInputError("Caption contract with local paths cannot be repaired.")


def _require_evaluation_contract(evaluation: dict[str, Any], scene_core_id: str) -> None:
    if evaluation.get("schema_version") != EVALUATION_SCHEMA_VERSION:
        raise InvalidRepairInputError("Expected c5.evaluation.v1 evaluation.")
    if evaluation.get("scene_core_id") != scene_core_id:
        raise InvalidRepairInputError("Evaluation scene_core_id must match the C3 scene core.")
    eval_map = evaluation.get("evaluation")
    if not isinstance(eval_map, dict):
        raise InvalidRepairInputError("Evaluation must include per-tone evaluation object.")


def _thresholds(evaluation: dict[str, Any]) -> dict[str, float]:
    raw_thresholds = evaluation.get("thresholds") if isinstance(evaluation.get("thresholds"), dict) else {}
    return {
        "factual_accuracy_min": _threshold(raw_thresholds.get("factual_accuracy_min"), THRESHOLDS["factual_accuracy_min"]),
        "tone_match_min": _threshold(raw_thresholds.get("tone_match_min"), THRESHOLDS["tone_match_min"]),
        "clarity_min": _threshold(raw_thresholds.get("clarity_min"), THRESHOLDS["clarity_min"]),
    }


def _threshold(raw_value: Any, default: float) -> float:
    if isinstance(raw_value, (int, float)) and 0 <= float(raw_value) <= 1:
        return round(float(raw_value), 2)
    return float(default)


def _tone_evaluation(evaluation: dict[str, Any], tone: str) -> dict[str, Any]:
    eval_map = evaluation.get("evaluation")
    if isinstance(eval_map, dict) and isinstance(eval_map.get(tone), dict):
        return eval_map[tone]
    return {
        "factual_accuracy": 0.0,
        "tone_match": 0.0,
        "clarity": 0.0,
        "passed": False,
        "repair_eligible": False,
        "issues": [
            {
                "code": "malformed_output",
                "severity": "high",
                "detail": "Missing per-tone evaluation.",
                "repair_eligible": False,
            }
        ],
        "rewrite_hint": None,
    }


def _issue_codes(tone_evaluation: dict[str, Any]) -> set[str]:
    issues = tone_evaluation.get("issues")
    if not isinstance(issues, list):
        return set()
    return {str(issue.get("code")) for issue in issues if isinstance(issue, dict) and issue.get("code")}


def _should_attempt_repair(tone_evaluation: dict[str, Any], thresholds: dict[str, float]) -> bool:
    codes = _issue_codes(tone_evaluation)
    if codes & REPAIRABLE_ISSUE_CODES:
        return True
    scores = _scores(tone_evaluation)
    return (
        scores["factual_accuracy"] < thresholds["factual_accuracy_min"]
        or scores["tone_match"] < thresholds["tone_match_min"]
        or scores["clarity"] < thresholds["clarity_min"]
    )


def _scores(tone_evaluation: dict[str, Any]) -> dict[str, float]:
    return {
        "factual_accuracy": _score_value(tone_evaluation.get("factual_accuracy")),
        "tone_match": _score_value(tone_evaluation.get("tone_match")),
        "clarity": _score_value(tone_evaluation.get("clarity")),
    }


def _score_value(raw_value: Any) -> float:
    if isinstance(raw_value, (int, float)):
        return round(max(0.0, min(1.0, float(raw_value))), 2)
    return 0.0


def _accepted_repair(
    before_eval: dict[str, Any],
    after_eval: dict[str, Any],
    thresholds: dict[str, float],
) -> tuple[bool, str]:
    before_scores = _scores(before_eval)
    after_scores = _scores(after_eval)
    after_codes = _issue_codes(after_eval)

    if after_codes & NON_REPAIRABLE_ISSUE_CODES:
        return False, "rejected_non_repairable_issue_after_repair"
    if _passes_thresholds(after_scores, thresholds) and not after_codes:
        return True, "accepted_all_thresholds_passed"

    no_metric_worse = all(after_scores[metric] >= before_scores[metric] for metric in before_scores)
    total_improved = sum(after_scores.values()) > sum(before_scores.values())
    issue_count_improved = len(after_codes) < len(_issue_codes(before_eval))
    if no_metric_worse and (total_improved or issue_count_improved):
        return True, "accepted_scores_or_issues_improved"
    return False, "rejected_no_threshold_or_score_improvement"


def _passes_thresholds(scores: dict[str, float], thresholds: dict[str, float]) -> bool:
    return (
        scores["factual_accuracy"] >= thresholds["factual_accuracy_min"]
        and scores["tone_match"] >= thresholds["tone_match_min"]
        and scores["clarity"] >= thresholds["clarity_min"]
    )


def _caption_text(captions: dict[str, Any], tone: str) -> str:
    caption_map = captions.get("captions")
    if not isinstance(caption_map, dict):
        return ""
    entry = caption_map.get(tone)
    if not isinstance(entry, dict):
        return ""
    value = entry.get("caption")
    return " ".join(value.split())[:500] if isinstance(value, str) else ""


def _final_caption_texts(captions: dict[str, Any]) -> dict[str, str]:
    return {tone: _caption_text(captions, tone) for tone in TONE_KEYS}


def _source_video_id(scene_core: dict[str, Any]) -> str | None:
    source_video = scene_core.get("source_video")
    if isinstance(source_video, dict):
        identifier = source_video.get("identifier")
        if isinstance(identifier, str) and identifier:
            return sanitize_source_identifier(identifier)
    return None


def _ensure_public_safe_payload(payload: dict[str, Any]) -> None:
    serialized = json.dumps(payload, sort_keys=True)
    if _LOCAL_PATH_PATTERN.search(serialized) or _SECRET_PATTERN.search(serialized) or _PRIVATE_REFERENCE_PATTERN.search(serialized):
        raise RepairError("C6 repair trace contains local path-like, secret-like, or private-reference content.")
