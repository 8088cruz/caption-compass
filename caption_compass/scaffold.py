"""Deterministic project status for Caption Compass.

This module reports verified gate status without claiming future behavior.
"""

from __future__ import annotations

import json
from typing import Any


def build_scaffold_status() -> dict[str, Any]:
    """Return the public project status through C6C."""

    return {
        "project": "Caption Compass",
        "gate": "C6C",
        "status": "vision-observation-ready",
        "implemented": [
            "minimal Python package",
            "deterministic scaffold status command",
            "basic scaffold tests",
            "timestamped frame evidence sampling",
            "persisted local frame artifacts for provider use",
            "structured frame observation contract",
            "stub vision observation mode",
            "Fireworks vision provider seam",
            "deterministic factual scene core contract",
            "deterministic four-tone caption contract",
            "deterministic accuracy and tone evaluator",
            "one bounded deterministic repair pass",
            "sanitized provider configuration boundary",
        ],
        "not_implemented": [
            "scene-core fusion from visual observations",
            "provider-backed caption generation",
            "audio extraction",
            "audio transcription",
            "demo UI",
            "Docker runtime",
        ],
        "next_gate": "C6D planned: scene core fusion from visual observations",
    }


def main() -> int:
    """Print scaffold status as judge-readable JSON."""

    print(json.dumps(build_scaffold_status(), indent=2, sort_keys=True))
    return 0
