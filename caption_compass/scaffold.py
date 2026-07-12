"""Deterministic project status for Caption Compass.

This module reports verified gate status without claiming future behavior.
"""

from __future__ import annotations

import json
from typing import Any


def build_scaffold_status() -> dict[str, Any]:
    """Return the public project status through C5."""

    return {
        "project": "Caption Compass",
        "gate": "C5",
        "status": "accuracy-tone-evaluator-ready",
        "implemented": [
            "minimal Python package",
            "deterministic scaffold status command",
            "basic scaffold tests",
            "timestamped frame evidence sampling",
            "deterministic factual scene core contract",
            "deterministic four-tone caption contract",
            "deterministic accuracy and tone evaluator",
        ],
        "not_implemented": [
            "provider calls",
            "scene interpretation",
            "provider-backed caption generation",
            "automated caption repair",
            "repair loop",
            "demo UI",
            "Docker runtime",
        ],
        "next_gate": "C6 planned: one bounded repair pass",
    }


def main() -> int:
    """Print scaffold status as judge-readable JSON."""

    print(json.dumps(build_scaffold_status(), indent=2, sort_keys=True))
    return 0
