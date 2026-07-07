"""Caption Compass public package surface."""

from .scaffold import build_scaffold_status
from .video_ingestion import extract_frame_evidence

__all__ = ["build_scaffold_status", "extract_frame_evidence"]
__version__ = "0.1.0"
