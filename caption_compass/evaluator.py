"""C5 deterministic accuracy and tone evaluator.

This module scores a C4 four-tone caption contract against a C3 factual scene
core. It emits issue codes and rewrite hints only; it does not mutate or repair
captions, call providers, inspect pixels, or claim objective truth.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from .captions import CAPTION_SCHEMA_VERSION, TONE_KEYS
from .scene_core import SCENE_CORE_SCHEMA_VERSION
from .video_ingestion import sanitize_source_identifier

EVALUATION_SCHEMA_VERSION = "c5.evaluation.v1"
DETERMINISTIC_STUB_MODE = "deterministic_stub"

THRESHOLDS = {
    "factual_accuracy_min": 0.85,
    "tone_match_min": 0.75,
    "clarity_min": 0.70,
}

ISSUE_TAXONOMY = {
    "invented_fact": {"meaning": "Caption adds a fact absent from the factual scene core.", "repair_eligible": True},
    "missing_core_fact": {"meaning": "Caption omits a key fact needed to preserve the scene core.", "repair_eligible": True},
    "unsupported_inference_used": {"meaning": "Caption uses a C3 unsupported inference as if true.", "repair_eligible": True},
    "uncertainty_overclaimed": {"meaning": "Caption turns uncertainty into certainty.", "repair_eligible": True},
    "tone_mismatch": {"meaning": "Caption does not match its required tone.", "repair_eligible": True},
    "tone_bleed": {"meaning": "Caption overlaps too much with another tone.", "repair_eligible": True},
    "unclear_joke": {"meaning": "Humor is ambiguous, obscure, or hard to score.", "repair_eligible": True},
    "unsafe_or_private_reference": {"meaning": "Output contains private/system/internal references or unsafe content.", "repair_eligible": False},
    "malformed_output": {"meaning": "Provider output is invalid JSON or missing required fields.", "repair_eligible": False},
    "scene_core_mismatch": {"meaning": "Caption output references a different scene_core_id.", "repair_eligible": False},
}

_LOCAL_PATH_PATTERN = re.compile(
    r"(^|[\s\"'])/(?:home|root|tmp|workspace|Users|var|private)/|[A-Za-z]:\\|file://"
)
_SECRET_PATTERN = re.compile(r"(?i)(api[_-]?key|secret|token|sk-[A-Za-z0-9_-]{8,})")
_PRIVATE_REFERENCE_PATTERN = re.compile(r"(?i)(private repo|internal-only|unpublished architecture|private research|private system)")
_WORD_PATTERN = re.compile(r"[a-z0-9]+")

_ALLOWED_NO_FACT_WORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "available",
    "bookmarks",
    "but",
    "compiled",
    "confirmed",
    "contains",
    "core",
    "describe",
    "details",
    "did",
    "empty",
    "evidence",
    "facts",
    "frame",
    "has",
    "is",
    "list",
    "loaded",
    "no",
    "not",
    "scene",
    "showed",
    "successfully",
    "the",
    "there",
    "timestamped",
    "up",
    "verified",
    "video",
    "visual",
    "with",
    "yet",
    "returned",
}

_UNSUPPORTED_KEYWORDS_BY_TYPE = {
    "observed_entities": {"person", "people", "object", "objects", "brand", "brands", "logo", "text", "chef", "table"},
    "visible_actions": {"cook", "cooks", "cooking", "moves", "movement", "interacts", "interaction", "stands", "stirring", "cuts"},
    "setting_or_context": {"kitchen", "location", "restaurant", "home", "mood", "intent", "causes", "because", "happy", "angry"},
    "audio_or_speech": {"audio", "speech", "spoken", "says", "soundtrack", "music", "voice", "heard"},
}

_OBSCURE_JOKE_MARKERS = {
    "monad",
    "kubernetes",
    "sigterm",
    "segfault",
    "kernel",
    "rfc",
    "inside baseball",
    "lambda calculus",
}

_TECH_TONE_MARKERS = {"compiled", "loaded", "empty list", "frame anchors", "debug", "system", "returned", "core"}
_SARCASM_MARKERS = {"showed up", "did not", "naturally", "apparently", "doing the work", "sure", "of course"}
_NON_TECH_HUMOR_MARKERS = {"bookmarks", "lighter", "light", "not much to describe", "yet"}


class EvaluationError(RuntimeError):
    """Base error for public-safe C5 evaluation failures."""


class InvalidEvaluationInputError(EvaluationError, ValueError):
    """Raised when C3 or C4 JSON cannot be evaluated."""


def load_captions_json(input_path: str | Path) -> dict[str, Any]:
    """Load C4 captions JSON without leaking local paths in errors."""

    path = Path(input_path)
    safe_name = sanitize_source_identifier(path.name or "captions.json")
    try:
        raw_text = path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise InvalidEvaluationInputError(f"Captions file not found: {safe_name}") from exc
    except OSError as exc:
        raise InvalidEvaluationInputError(f"Captions file is not readable: {safe_name}") from exc

    try:
        payload = json.loads(raw_text)
    except json.JSONDecodeError as exc:
        raise InvalidEvaluationInputError(
            f"Captions JSON is malformed in {safe_name} at line {exc.lineno}, column {exc.colno}"
        ) from exc

    if not isinstance(payload, dict):
        raise InvalidEvaluationInputError("Captions JSON must be an object.")
    return payload


def evaluate_captions(
    scene_core: dict[str, Any],
    captions: dict[str, Any],
    *,
    mode: str = DETERMINISTIC_STUB_MODE,
) -> dict[str, Any]:
    """Evaluate C4 captions against a C3 factual scene core without repairing them."""

    if mode != DETERMINISTIC_STUB_MODE:
        raise EvaluationError("C5 currently supports deterministic_stub mode only.")

    scene_core_id = _require_scene_core(scene_core)
    _require_caption_contract(captions)
    expected_anchor_ids = _safe_string_list(scene_core.get("evidence_anchor_ids"))
    supported_claims = _safe_supported_claims(captions.get("fact_lock"))
    unsupported_inferences = _safe_unsupported_inferences(scene_core.get("unsupported_inferences"))

    contract_level_issues: list[dict[str, Any]] = []
    if captions.get("scene_core_id") != scene_core_id:
        contract_level_issues.append(
            _issue("scene_core_mismatch", "high", "Caption contract scene_core_id does not match the C3 scene core.")
        )

    source_scene_core = captions.get("source_scene_core")
    if isinstance(source_scene_core, dict):
        if _safe_string_list(source_scene_core.get("evidence_anchor_ids")) != expected_anchor_ids:
            contract_level_issues.append(
                _issue("malformed_output", "high", "Caption contract evidence anchors do not match the C3 scene core.")
            )

    caption_map = captions.get("captions")
    evaluation = {
        tone: _evaluate_one_tone(
            tone=tone,
            entry=caption_map.get(tone) if isinstance(caption_map, dict) else None,
            scene_core_id=scene_core_id,
            expected_anchor_ids=expected_anchor_ids,
            supported_claims=supported_claims,
            unsupported_inferences=unsupported_inferences,
            sibling_entries=caption_map if isinstance(caption_map, dict) else {},
            contract_level_issues=contract_level_issues,
        )
        for tone in TONE_KEYS
    }

    failed_caption_keys = [tone for tone, result in evaluation.items() if not result["passed"]]
    repair_recommended = any(result["repair_eligible"] for result in evaluation.values())
    payload = {
        "schema_version": EVALUATION_SCHEMA_VERSION,
        "gate": "C5",
        "scene_core_id": scene_core_id,
        "source_video_id": _source_video_id(scene_core),
        "thresholds": THRESHOLDS,
        "tone_order": list(TONE_KEYS),
        "issue_taxonomy": ISSUE_TAXONOMY,
        "evaluation": evaluation,
        "overall": {
            "passed": not failed_caption_keys,
            "repair_recommended": repair_recommended,
            "failed_caption_keys": failed_caption_keys,
            "contract_issue_count": len(contract_level_issues),
        },
        "generation": {
            "mode": mode,
            "network_used": False,
            "provider": None,
            "input_contracts": [SCENE_CORE_SCHEMA_VERSION, CAPTION_SCHEMA_VERSION],
            "output_contract": EVALUATION_SCHEMA_VERSION,
        },
        "contract_boundary": {
            "does_not_include": [
                "automated repair",
                "caption rewriting",
                "repair loop",
                "provider calls",
                "leaderboard claims",
                "objective truth proof",
            ],
            "local_paths_included": False,
            "scores_are_heuristic": True,
            "captions_mutated": False,
        },
    }
    _ensure_public_safe_payload(payload)
    return payload


def write_evaluation_json(evaluation: dict[str, Any], output_path: str | Path) -> None:
    """Write C5 evaluation JSON deterministically."""

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(evaluation, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _require_scene_core(scene_core: dict[str, Any]) -> str:
    if scene_core.get("schema_version") != SCENE_CORE_SCHEMA_VERSION:
        raise InvalidEvaluationInputError("Expected c3.scene_core.v1 scene core.")
    scene_core_id = scene_core.get("scene_core_id")
    if not isinstance(scene_core_id, str) or not scene_core_id.strip():
        raise InvalidEvaluationInputError("Scene core must include scene_core_id.")
    contract_boundary = scene_core.get("contract_boundary")
    if isinstance(contract_boundary, dict) and contract_boundary.get("local_paths_included") is True:
        raise InvalidEvaluationInputError("Scene core with local paths cannot be evaluated.")
    return scene_core_id.strip()


def _require_caption_contract(captions: dict[str, Any]) -> None:
    if captions.get("schema_version") != CAPTION_SCHEMA_VERSION:
        raise InvalidEvaluationInputError("Expected c4.four_tone_captions.v1 captions.")
    contract_boundary = captions.get("contract_boundary")
    if isinstance(contract_boundary, dict) and contract_boundary.get("local_paths_included") is True:
        raise InvalidEvaluationInputError("Caption contract with local paths cannot be evaluated.")


def _evaluate_one_tone(
    *,
    tone: str,
    entry: Any,
    scene_core_id: str,
    expected_anchor_ids: list[str],
    supported_claims: list[dict[str, Any]],
    unsupported_inferences: list[dict[str, Any]],
    sibling_entries: dict[str, Any],
    contract_level_issues: list[dict[str, Any]],
) -> dict[str, Any]:
    issues = [dict(issue) for issue in contract_level_issues]

    if not isinstance(entry, dict):
        issues.append(_issue("malformed_output", "high", f"Missing caption entry for tone '{tone}'."))
        return _result(tone, 0.0, 0.0, 0.0, issues)

    caption_text = _clean_text(entry.get("caption"))
    if caption_text is None:
        issues.append(_issue("malformed_output", "high", "Caption entry is missing a non-empty caption string."))
        return _result(tone, 0.0, 0.0, 0.0, issues)

    if entry.get("scene_core_id") != scene_core_id:
        issues.append(_issue("scene_core_mismatch", "high", "Caption entry scene_core_id does not match the C3 scene core."))
    if _safe_string_list(entry.get("evidence_anchor_ids")) != expected_anchor_ids:
        issues.append(_issue("malformed_output", "medium", "Caption evidence anchors do not preserve the C3 anchor list."))
    if entry.get("tone") != tone:
        issues.append(_issue("malformed_output", "medium", "Caption entry tone label does not match its key."))

    issues.extend(_factual_issues(caption_text, supported_claims, unsupported_inferences))
    issues.extend(_tone_issues(tone, caption_text, sibling_entries))
    if _has_private_or_unsafe_reference(caption_text):
        issues.append(_issue("unsafe_or_private_reference", "high", "Caption contains local path, secret-like, or private-reference content."))

    factual_accuracy = _score(
        1.0,
        issues,
        {
            "invented_fact": 0.35,
            "missing_core_fact": 0.25,
            "unsupported_inference_used": 0.30,
            "uncertainty_overclaimed": 0.20,
            "scene_core_mismatch": 1.0,
            "malformed_output": 0.60,
            "unsafe_or_private_reference": 1.0,
        },
    )
    tone_match = _score(
        1.0,
        issues,
        {
            "tone_mismatch": 0.35,
            "tone_bleed": 0.25,
            "unclear_joke": 0.15,
            "malformed_output": 0.60,
            "scene_core_mismatch": 0.50,
            "unsafe_or_private_reference": 0.50,
        },
    )
    clarity = _score(
        1.0,
        issues,
        {
            "unclear_joke": 0.35,
            "malformed_output": 0.60,
            "unsafe_or_private_reference": 0.50,
            "uncertainty_overclaimed": 0.15,
        },
    )
    return _result(tone, factual_accuracy, tone_match, clarity, issues)


def _factual_issues(
    caption_text: str,
    supported_claims: list[dict[str, Any]],
    unsupported_inferences: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    text = caption_text.lower()
    issues: list[dict[str, Any]] = []

    for claim in supported_claims:
        claim_text = _clean_text(claim.get("text")) or ""
        important_words = [word for word in _words(claim_text) if len(word) > 3]
        if important_words and not all(word in text for word in important_words[:3]):
            issues.append(
                _issue("missing_core_fact", "medium", f"Caption omits supported scene-core fact: {claim_text[:96]}")
            )

    unsupported_types = {item.get("claim_type") for item in unsupported_inferences if isinstance(item, dict)}
    supported_words = {word for claim in supported_claims for word in _words(str(claim.get("text", "")))}
    for claim_type, keywords in _UNSUPPORTED_KEYWORDS_BY_TYPE.items():
        matched = sorted(
            keyword
            for keyword in keywords
            if _contains_word_or_phrase(text, keyword) and keyword not in supported_words
        )
        if matched and (claim_type in unsupported_types or not supported_claims):
            issues.append(
                _issue(
                    "unsupported_inference_used",
                    "high",
                    f"Caption treats unsupported {claim_type} as established: {', '.join(matched[:3])}.",
                )
            )
            break

    if not supported_claims and _looks_like_scene_fact(text):
        issues.append(
            _issue(
                "invented_fact",
                "high",
                "Caption describes scene content even though the scene core has no supported visual facts.",
            )
        )
    elif supported_claims:
        supported_words = {word for claim in supported_claims for word in _words(str(claim.get("text", "")))}
        extra_scene_words = _scene_words(text) - supported_words
        if extra_scene_words:
            issues.append(
                _issue("invented_fact", "medium", f"Caption includes scene words not present in supported claims: {', '.join(sorted(extra_scene_words)[:4])}.")
            )

    if _overclaims_uncertainty(text):
        issues.append(
            _issue("uncertainty_overclaimed", "medium", "Caption states uncertain or unsupported details with excessive certainty.")
        )
    return _dedupe_issues(issues)


def _tone_issues(tone: str, caption_text: str, sibling_entries: dict[str, Any]) -> list[dict[str, Any]]:
    text = caption_text.lower()
    issues: list[dict[str, Any]] = []

    if tone == "formal":
        if any(marker in text for marker in _SARCASM_MARKERS) or _contains_any(text, {"lol", "haha", "joke", "compiled"}):
            issues.append(_issue("tone_mismatch", "medium", "Formal caption contains humor, sarcasm, or software-styled phrasing."))
    elif tone == "sarcastic":
        if not any(marker in text for marker in _SARCASM_MARKERS):
            issues.append(_issue("tone_mismatch", "medium", "Sarcastic caption lacks clear dry understatement or irony."))
    elif tone == "humorous-tech":
        if not any(marker in text for marker in _TECH_TONE_MARKERS):
            issues.append(_issue("tone_mismatch", "medium", "Humorous-tech caption lacks an obvious common software-oriented cue."))
        if _contains_any(text, _OBSCURE_JOKE_MARKERS):
            issues.append(_issue("unclear_joke", "medium", "Humorous-tech caption uses an obscure or hard-to-score technical reference."))
    elif tone == "humorous-non-tech":
        if any(marker in text for marker in _TECH_TONE_MARKERS if marker not in {"frame anchors"}):
            issues.append(_issue("tone_bleed", "medium", "Humorous-non-tech caption borrows technical phrasing from the tech tone."))
        if not any(marker in text for marker in _NON_TECH_HUMOR_MARKERS):
            issues.append(_issue("tone_mismatch", "medium", "Humorous-non-tech caption lacks a clear general-audience light-humor cue."))
        if _contains_any(text, _OBSCURE_JOKE_MARKERS):
            issues.append(_issue("unclear_joke", "medium", "Humorous-non-tech caption uses an obscure reference."))

    for other_tone, other_entry in sibling_entries.items():
        if other_tone == tone or not isinstance(other_entry, dict):
            continue
        other_text = _clean_text(other_entry.get("caption"))
        if other_text and _normalized_for_overlap(other_text) == _normalized_for_overlap(caption_text):
            issues.append(_issue("tone_bleed", "medium", f"Caption text is indistinguishable from the {other_tone} tone."))
            break
    return _dedupe_issues(issues)


def _result(tone: str, factual_accuracy: float, tone_match: float, clarity: float, issues: list[dict[str, Any]]) -> dict[str, Any]:
    passed = (
        factual_accuracy >= THRESHOLDS["factual_accuracy_min"]
        and tone_match >= THRESHOLDS["tone_match_min"]
        and clarity >= THRESHOLDS["clarity_min"]
        and not issues
    )
    repair_eligible = bool(issues) and all(bool(issue.get("repair_eligible")) for issue in issues)
    return {
        "factual_accuracy": factual_accuracy,
        "tone_match": tone_match,
        "clarity": clarity,
        "passed": passed,
        "repair_eligible": repair_eligible,
        "issues": issues,
        "rewrite_hint": _rewrite_hint(tone, issues) if issues and repair_eligible else None,
    }


def _issue(code: str, severity: str, detail: str) -> dict[str, Any]:
    taxonomy = ISSUE_TAXONOMY[code]
    return {
        "code": code,
        "severity": severity,
        "detail": detail,
        "repair_eligible": bool(taxonomy["repair_eligible"]),
    }


def _rewrite_hint(tone: str, issues: list[dict[str, Any]]) -> str:
    codes = {issue["code"] for issue in issues}
    parts: list[str] = ["Keep the same scene_core_id and evidence anchors."]
    if {"invented_fact", "unsupported_inference_used", "uncertainty_overclaimed"} & codes:
        parts.append("Remove unsupported scene, emotion, intent, location, or audio claims.")
    if "missing_core_fact" in codes:
        parts.append("Include every supported scene-core fact without adding new facts.")
    if {"tone_mismatch", "tone_bleed", "unclear_joke"} & codes:
        parts.append(f"Make the tone clearly {tone} using simple, judge-legible language.")
    return " ".join(parts)


def _score(base: float, issues: list[dict[str, Any]], penalties: dict[str, float]) -> float:
    value = base
    for issue in issues:
        value -= penalties.get(str(issue.get("code")), 0.0)
    return round(max(0.0, min(1.0, value)), 2)


def _safe_supported_claims(raw_fact_lock: Any) -> list[dict[str, Any]]:
    if not isinstance(raw_fact_lock, dict):
        return []
    raw_claims = raw_fact_lock.get("supported_claims")
    if not isinstance(raw_claims, list):
        return []
    claims: list[dict[str, Any]] = []
    for item in raw_claims:
        if isinstance(item, dict):
            claim_id = _clean_text(item.get("claim_id")) or f"claim_{len(claims) + 1:04d}"
            claim_type = _clean_text(item.get("claim_type")) or "fact"
            text = _clean_text(item.get("text"))
            if text:
                claims.append({"claim_id": claim_id, "claim_type": claim_type, "text": text})
    return claims


def _safe_unsupported_inferences(raw_items: Any) -> list[dict[str, Any]]:
    return [item for item in raw_items if isinstance(item, dict)] if isinstance(raw_items, list) else []


def _safe_string_list(raw_items: Any) -> list[str]:
    return [item for item in raw_items if isinstance(item, str)] if isinstance(raw_items, list) else []


def _source_video_id(scene_core: dict[str, Any]) -> str | None:
    source_video = scene_core.get("source_video")
    if isinstance(source_video, dict):
        identifier = source_video.get("identifier")
        if isinstance(identifier, str) and identifier:
            return sanitize_source_identifier(identifier)
    return None


def _clean_text(raw_value: Any) -> str | None:
    if not isinstance(raw_value, str):
        return None
    text = " ".join(raw_value.strip().split())
    return text[:500] if text else None


def _words(text: str) -> list[str]:
    return _WORD_PATTERN.findall(text.lower())


def _contains_word_or_phrase(text: str, phrase: str) -> bool:
    if " " in phrase:
        return phrase in text
    return re.search(rf"\b{re.escape(phrase)}\b", text) is not None


def _contains_any(text: str, markers: set[str]) -> bool:
    return any(_contains_word_or_phrase(text, marker) for marker in markers)


def _scene_words(text: str) -> set[str]:
    scene_vocab = set().union(*_UNSUPPORTED_KEYWORDS_BY_TYPE.values())
    return {word for word in _words(text) if word in scene_vocab}


def _looks_like_scene_fact(text: str) -> bool:
    return bool(_scene_words(text))


def _overclaims_uncertainty(text: str) -> bool:
    overclaim_markers = {"clearly", "clearly shows", "definitely", "proves", "confirmed that", "obviously"}
    return any(marker in text for marker in overclaim_markers)


def _normalized_for_overlap(text: str) -> str:
    return " ".join(_words(text))


def _dedupe_issues(issues: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set[tuple[str, str]] = set()
    deduped: list[dict[str, Any]] = []
    for issue in issues:
        key = (str(issue.get("code")), str(issue.get("detail")))
        if key not in seen:
            seen.add(key)
            deduped.append(issue)
    return deduped


def _has_private_or_unsafe_reference(text: str) -> bool:
    return bool(_LOCAL_PATH_PATTERN.search(text) or _SECRET_PATTERN.search(text) or _PRIVATE_REFERENCE_PATTERN.search(text))


def _ensure_public_safe_payload(payload: dict[str, Any]) -> None:
    serialized = json.dumps(payload, sort_keys=True)
    if _LOCAL_PATH_PATTERN.search(serialized) or _SECRET_PATTERN.search(serialized) or _PRIVATE_REFERENCE_PATTERN.search(serialized):
        raise EvaluationError("C5 evaluation output contains local path-like, secret-like, or private-reference content.")
