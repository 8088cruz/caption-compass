"""Deterministic scaffold status for Caption Compass.

This module proves the project can run without implementing video processing,
provider calls, caption generation, evaluation, repair, or UI behavior.
"""

from __future__ import annotations

import json
from typing import Any


def build_scaffold_status() -> dict[str, Any]:
    """Return the public C1 scaffold status."""

    return {
        "project": "Caption Compass",
        "gate": "C1",
        "status": "scaffold-ready",
        "implemented": [
            "minimal Python package",
            "deterministic scaffold status command",
            "basic offline verification tests",
        ],
        "not_implemented": [
            "video processing",
            "provider calls",
            "caption generation",
            "accuracy or tone evaluation",
            "repair loop",
            "demo UI",
            "Docker runtime",
        ],
        "next_gate": "C2 planned: video upload and frame extraction",
    }


def main() -> int:
    """Print scaffold status as judge-readable JSON."""

    print(json.dumps(build_scaffold_status(), indent=2, sort_keys=True))
    return 0
