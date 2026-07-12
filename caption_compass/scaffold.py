"""Deterministic project status for Caption Compass.

This module reports verified gate status without claiming future behavior.
"""

from __future__ import annotations

import json
from typing import Any


def build_scaffold_status() -> dict[str, Any]:
    """Return the public project status through C6."""

    return {
        "project": "Caption Compass",
        "gate": "C6",
        "status": "bounded-repair-ready",
        "implemented": [
            "minimal Python package",
            "deterministic scaffold status command",
            "basic scaffold tests",
            "timestamped frame evidence sampling",
            "deterministic factual scene core contract",
            "deterministic four-tone caption contract",
            "deterministic accuracy and tone evaluator",
            "one bounded deterministic repair pass",
        ],
        "not_implemented": [
            "provider calls",
            "scene interpretation",
            "provider-backed caption generation",
            "demo UI",
            "Docker runtime",
        ],
        "next_gate": "C7 planned: judge-visible trace UI",
    }


def main() -> int:
    """Print scaffold status as judge-readable JSON."""

    print(json.dumps(build_scaffold_status(), indent=2, sort_keys=True))
    return 0
