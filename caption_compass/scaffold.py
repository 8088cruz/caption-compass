"""Deterministic project status for Caption Compass.

This module reports verified gate status without claiming future behavior.
"""

from __future__ import annotations

import json
from typing import Any


def build_scaffold_status() -> dict[str, Any]:
    """Return the public project status through C2."""

    return {
        "project": "Caption Compass",
        "gate": "C2",
        "status": "frame-sampling-ready",
        "implemented": [
            "minimal Python package",
            "deterministic scaffold status command",
            "basic scaffold tests",
            "timestamped frame evidence sampling",
        ],
        "not_implemented": [
            "provider calls",
            "scene interpretation",
            "factual scene core",
            "caption generation",
            "accuracy or tone evaluation",
            "repair loop",
            "demo UI",
            "Docker runtime",
        ],
        "next_gate": "C3 planned: factual scene core JSON contract",
    }


def main() -> int:
    """Print scaffold status as judge-readable JSON."""

    print(json.dumps(build_scaffold_status(), indent=2, sort_keys=True))
    return 0
