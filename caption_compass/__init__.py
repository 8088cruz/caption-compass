"""Caption Compass public package surface."""

from .scaffold import build_scaffold_status
from .scene_core import build_scene_core
from .video_ingestion import extract_frame_evidence

__all__ = ["build_scaffold_status", "build_scene_core", "extract_frame_evidence"]
__version__ = "0.1.0"
