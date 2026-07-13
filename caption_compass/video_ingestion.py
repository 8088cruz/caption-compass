"""C2 video ingestion and timestamped frame evidence sampling.

This module extracts evidence anchors only. It does not interpret scene
content, transcribe audio, generate captions, evaluate tone, or call providers.

C6B adds an optional persisted-frame seam for future provider use. Public JSON
still avoids absolute local paths.
"""

from __future__ import annotations

import json
import re
import shutil
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any


class VideoIngestionError(RuntimeError):
    """Base error for public-safe video ingestion failures."""


class MissingVideoToolError(VideoIngestionError):
    """Raised when ffmpeg or ffprobe is unavailable."""


class InvalidVideoError(VideoIngestionError):
    """Raised when input is missing, invalid, or unsupported."""


@dataclass(frozen=True)
class VideoProbe:
    duration_seconds: float | None
    width: int | None
    height: int | None
    frame_rate: float | None


def sanitize_source_identifier(source_name: str) -> str:
    """Return a filename-like identifier without path information."""

    name = Path(source_name).name.strip() or "video"
    safe = re.sub(r"[^A-Za-z0-9._-]+", "-", name).strip(".-")
    safe = re.sub(r"-+", "-", safe)
    safe = safe.replace("-.", ".")
    return safe[:96] or "video"


def _slug_from_identifier(identifier: str) -> str:
    stem = Path(identifier).stem or identifier
    slug = re.sub(r"[^A-Za-z0-9_-]+", "-", stem).strip("-").lower()
    return slug[:64] or "video"


def _public_path_name(path: Path) -> str:
    return sanitize_source_identifier(path.name)


def _ensure_tool(binary: str, label: str) -> None:
    if shutil.which(binary) is None:
        raise MissingVideoToolError(f"{label} is required for C2 frame sampling but was not found.")


def _run(command: list[str], error_message: str) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode != 0:
        detail = (result.stderr or result.stdout or "").strip().splitlines()
        suffix = f" Detail: {_scrub_tool_error(detail[-1])}" if detail else ""
        raise InvalidVideoError(f"{error_message}.{suffix}")
    return result


def _scrub_tool_error(message: str) -> str:
    """Remove local path prefixes from ffmpeg/ffprobe error details."""

    scrubbed = re.sub(r"(/[^\s:]+/)([^/\s:]+)", r"\2", message)
    scrubbed = re.sub(r"([A-Za-z]:\\(?:[^\s:]+\\)+)([^\\\s:]+)", r"\2", scrubbed)
    return scrubbed


def _parse_frame_rate(value: str | None) -> float | None:
    if not value or value == "0/0":
        return None
    if "/" in value:
        numerator, denominator = value.split("/", 1)
        try:
            denominator_float = float(denominator)
            if denominator_float == 0:
                return None
            return round(float(numerator) / denominator_float, 3)
        except ValueError:
            return None
    try:
        return round(float(value), 3)
    except ValueError:
        return None


def probe_video(video_path: str | Path, *, ffprobe_bin: str = "ffprobe") -> VideoProbe:
    """Probe video metadata without returning local paths."""

    path = Path(video_path)
    if not path.is_file():
        raise InvalidVideoError(f"Video file not found or not readable: {_public_path_name(path)}")

    _ensure_tool(ffprobe_bin, "ffprobe")
    command = [
        ffprobe_bin,
        "-v",
        "error",
        "-select_streams",
        "v:0",
        "-show_entries",
        "stream=duration,width,height,avg_frame_rate,r_frame_rate:format=duration",
        "-of",
        "json",
        str(path),
    ]
    result = _run(command, f"Could not read video metadata for {_public_path_name(path)}")
    payload = json.loads(result.stdout)
    streams = payload.get("streams") or []
    if not streams:
        raise InvalidVideoError(f"No video stream found in {_public_path_name(path)}")

    stream = streams[0]
    duration_raw = stream.get("duration") or (payload.get("format") or {}).get("duration")
    duration = None
    if duration_raw not in (None, "N/A"):
        try:
            duration = round(float(duration_raw), 3)
        except ValueError:
            duration = None

    return VideoProbe(
        duration_seconds=duration,
        width=int(stream["width"]) if stream.get("width") else None,
        height=int(stream["height"]) if stream.get("height") else None,
        frame_rate=_parse_frame_rate(stream.get("avg_frame_rate") or stream.get("r_frame_rate")),
    )


def sample_timestamps(duration_seconds: float | None, *, frame_count: int = 4) -> list[float]:
    """Return deterministic center-of-segment timestamps."""

    if frame_count < 1:
        raise ValueError("frame_count must be at least 1")
    if duration_seconds is None or duration_seconds <= 0:
        return [0.0]

    safe_duration = max(duration_seconds, 0.001)
    return [
        round(min(((index + 0.5) * safe_duration) / frame_count, max(safe_duration - 0.001, 0.0)), 3)
        for index in range(frame_count)
    ]


def _local_output_run_id(output_dir: Path) -> str:
    return re.sub(r"[^A-Za-z0-9_-]+", "-", output_dir.name.strip()).strip("-").lower() or "run"


def _default_output_dir(source_slug: str) -> Path:
    return Path("local_test_outputs") / source_slug


def _build_frame_record(
    *,
    source_slug: str,
    index: int,
    timestamp: float,
    persisted: bool,
    run_id: str | None,
) -> dict[str, Any]:
    frame_id = f"frame_{index:04d}"
    frame: dict[str, Any] = {
        "frame_id": frame_id,
        "frame_ref": f"frame://{source_slug}/{frame_id}",
        "timestamp_seconds": timestamp,
        "timestamp_label": _format_timestamp(timestamp),
    }
    if persisted and run_id:
        frame["persisted_frame_ref"] = f"local-output://{run_id}/frames/{frame_id}.jpg"
    return frame


def extract_frame_evidence(
    video_path: str | Path,
    *,
    frame_count: int = 4,
    source_identifier: str | None = None,
    ffmpeg_bin: str = "ffmpeg",
    ffprobe_bin: str = "ffprobe",
    persist_frames: bool = False,
    output_dir: str | Path | None = None,
) -> dict[str, Any]:
    """Extract timestamped frame anchors and return public-safe metadata.

    When ``persist_frames`` is true, sampled JPGs are written under
    ``<output_dir>/frames`` for future provider use. Returned JSON includes
    safe local-output refs, never absolute local paths.
    """

    path = Path(video_path)
    if not path.is_file():
        raise InvalidVideoError(f"Video file not found or not readable: {_public_path_name(path)}")
    _ensure_tool(ffmpeg_bin, "ffmpeg")
    _ensure_tool(ffprobe_bin, "ffprobe")

    source_id = sanitize_source_identifier(source_identifier or path.name)
    source_slug = _slug_from_identifier(source_id)
    probe = probe_video(path, ffprobe_bin=ffprobe_bin)
    timestamps = sample_timestamps(probe.duration_seconds, frame_count=frame_count)

    run_id: str | None = None
    persisted_output_ref: str | None = None

    if persist_frames:
        root_dir = Path(output_dir) if output_dir is not None else _default_output_dir(source_slug)
        frames_dir = root_dir / "frames"
        frames_dir.mkdir(parents=True, exist_ok=True)
        run_id = _local_output_run_id(root_dir)
        persisted_output_ref = f"local-output://{run_id}/frames"
        cleanup_context = None
        extraction_dir = frames_dir
    else:
        cleanup_context = tempfile.TemporaryDirectory(prefix="caption-compass-c2-")
        extraction_dir = Path(cleanup_context.name)

    try:
        for index, timestamp in enumerate(timestamps, start=1):
            frame_path = extraction_dir / f"frame_{index:04d}.jpg"
            command = [
                ffmpeg_bin,
                "-nostdin",
                "-y",
                "-loglevel",
                "error",
                "-ss",
                f"{timestamp:.3f}",
                "-i",
                str(path),
                "-frames:v",
                "1",
                "-an",
                str(frame_path),
            ]
            _run(command, f"Could not extract frame {index} from {source_id}")
            if not frame_path.is_file() or frame_path.stat().st_size == 0:
                raise InvalidVideoError(f"Could not extract frame {index} from {source_id}.")
    finally:
        if cleanup_context is not None:
            cleanup_context.cleanup()

    frames = [
        _build_frame_record(
            source_slug=source_slug,
            index=index,
            timestamp=timestamp,
            persisted=persist_frames,
            run_id=run_id,
        )
        for index, timestamp in enumerate(timestamps, start=1)
    ]

    warnings: list[str] = []
    if probe.duration_seconds is None:
        warnings.append("duration unavailable; sampled first frame only")

    return {
        "schema_version": "c2.frame_evidence.v1",
        "gate": "C2",
        "source_video": {
            "identifier": source_id,
            "duration_seconds": probe.duration_seconds,
            "width": probe.width,
            "height": probe.height,
            "frame_rate": probe.frame_rate,
        },
        "sampling": {
            "requested_frame_count": frame_count,
            "sampled_frame_count": len(frames),
            "strategy": "center-of-equal-time-segments",
        },
        "frames": frames,
        "persistence": {
            "frames_persisted": persist_frames,
            "output_ref": persisted_output_ref,
            "local_paths_included": False,
        },
        "extraction": {
            "status": "ok",
            "tooling": "ffmpeg/ffprobe",
            "warnings": warnings,
            "local_paths_included": False,
        },
    }


def _format_timestamp(seconds: float) -> str:
    total_milliseconds = int(round(seconds * 1000))
    total_seconds, milliseconds = divmod(total_milliseconds, 1000)
    minutes, seconds_only = divmod(total_seconds, 60)
    return f"{minutes:02d}:{seconds_only:02d}.{milliseconds:03d}"


def write_evidence_json(evidence: dict[str, Any], output_path: str | Path) -> None:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")
