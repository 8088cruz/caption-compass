"""Caption Compass public package surface."""

from .captions import generate_four_tone_captions
from .evaluator import evaluate_captions
from .provider_config import (
    build_provider_status,
    get_fireworks_api_key,
    load_provider_config,
    validate_provider_ready,
)
from .repair import repair_captions
from .scaffold import build_scaffold_status
from .scene_core import build_scene_core
from .video_ingestion import extract_frame_evidence

__all__ = [
    "build_provider_status",
    "build_scaffold_status",
    "build_scene_core",
    "evaluate_captions",
    "extract_frame_evidence",
    "generate_four_tone_captions",
    "get_fireworks_api_key",
    "load_provider_config",
    "repair_captions",
    "validate_provider_ready",
]
__version__ = "0.1.0"
