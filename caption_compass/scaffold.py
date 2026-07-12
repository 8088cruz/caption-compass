"""Deterministic project status for Caption Compass.

This module reports verified gate status without claiming future behavior.
"""

from __future__ import annotations

import json
from typing import Any


def build_scaffold_status() -> dict[str, Any]:
    """Return the public project status through C4."""

    return {
        "project": "Caption Compass",
        "gate": "C4",
        "status": "four-tone-caption-contract-ready",
        "implemented": [
            "minimal Python package",
            "deterministic scaffold status command",
            "basic scaffold tests",
            "timestamped frame evidence sampling",
            "deterministic factual scene core contract",
            "deterministic four-tone caption contract",
        ],
        "not_implemented": [
            "provider calls",
            "scene interpretation",
            "provider-backed caption generation",
            "accuracy or tone evaluation",
            "repair loop",
            "demo UI",
            "Docker runtime",
        ],
        "next_gate": "C5 planned: accuracy and tone evaluator",
    }


def main() -> int:
    """Print scaffold status as judge-readable JSON."""

    print(json.dumps(build_scaffold_status(), indent=2, sort_keys=True))
    return 0
