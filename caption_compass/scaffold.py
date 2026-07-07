"""Deterministic project status for Caption Compass.

This module reports verified gate status without claiming future behavior.
"""

from __future__ import annotations

import json
from typing import Any


def build_scaffold_status() -> dict[str, Any]:
    """Return the public project status through C3."""

    return {
        "project": "Caption Compass",
        "gate": "C3",
        "status": "scene-core-contract-ready",
        "implemented": [
            "minimal Python package",
            "deterministic scaffold status command",
            "basic scaffold tests",
            "timestamped frame evidence sampling",
            "deterministic factual scene core contract",
        ],
        "not_implemented": [
            "provider calls",
            "scene interpretation",
            "caption generation",
            "accuracy or tone evaluation",
            "repair loop",
            "demo UI",
            "Docker runtime",
        ],
        "next_gate": "C4 planned: four-tone caption generation",
    }


def main() -> int:
    """Print scaffold status as judge-readable JSON."""

    print(json.dumps(build_scaffold_status(), indent=2, sort_keys=True))
    return 0
