"""Command line boundary for Caption Compass gates."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .captions import (
    CaptionGenerationError,
    generate_four_tone_captions,
    load_scene_core_json,
    write_captions_json,
)
from .evaluator import EvaluationError, evaluate_captions, load_captions_json, write_evaluation_json
from .scaffold import build_scaffold_status
from .scene_core import (
    SceneCoreError,
    build_scene_core,
    load_frame_evidence_json,
    write_scene_core_json,
)
from .video_ingestion import VideoIngestionError, extract_frame_evidence, write_evidence_json


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="caption-compass")
    subparsers = parser.add_subparsers(dest="command")

    sample_frames = subparsers.add_parser(
        "sample-frames",
        help="sample timestamped frame evidence from a local video",
    )
    sample_frames.add_argument("--video", required=True, help="local video file to sample")
    sample_frames.add_argument("--output", default="-", help="output JSON path, or '-' for stdout")
    sample_frames.add_argument("--frame-count", type=int, default=4, help="number of frame anchors to sample")
    sample_frames.add_argument("--source-id", default=None, help="optional public-safe source identifier for JSON output")

    scene_core = subparsers.add_parser(
        "build-scene-core",
        help="build a deterministic factual scene core contract from C2 evidence",
    )
    scene_core.add_argument("--evidence", required=True, help="C2 frame evidence JSON")
    scene_core.add_argument("--output", default="-", help="output JSON path, or '-' for stdout")

    captions = subparsers.add_parser(
        "generate-captions",
        help="generate the deterministic four-tone caption contract from a C3 scene core",
    )
    captions.add_argument("--scene-core", required=True, help="C3 scene core JSON")
    captions.add_argument("--output", default="-", help="output JSON path, or '-' for stdout")

    evaluation = subparsers.add_parser(
        "evaluate-captions",
        help="score C4 captions against a C3 scene core without repairing them",
    )
    evaluation.add_argument("--scene-core", required=True, help="C3 scene core JSON")
    evaluation.add_argument("--captions", required=True, help="C4 four-tone captions JSON")
    evaluation.add_argument("--output", default="-", help="output JSON path, or '-' for stdout")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command is None:
        print(json.dumps(build_scaffold_status(), indent=2, sort_keys=True))
        return 0

    if args.command == "sample-frames":
        try:
            evidence = extract_frame_evidence(
                Path(args.video),
                frame_count=args.frame_count,
                source_identifier=args.source_id,
            )
        except (ValueError, VideoIngestionError) as exc:
            print(f"caption-compass: {exc}", file=sys.stderr)
            return 2

        if args.output == "-":
            print(json.dumps(evidence, indent=2, sort_keys=True))
        else:
            write_evidence_json(evidence, args.output)
        return 0

    if args.command == "build-scene-core":
        try:
            frame_evidence = load_frame_evidence_json(args.evidence)
            scene_core = build_scene_core(frame_evidence)
        except SceneCoreError as exc:
            print(f"caption-compass: {exc}", file=sys.stderr)
            return 2

        if args.output == "-":
            print(json.dumps(scene_core, indent=2, sort_keys=True))
        else:
            write_scene_core_json(scene_core, args.output)
        return 0

    if args.command == "generate-captions":
        try:
            scene_core = load_scene_core_json(args.scene_core)
            captions = generate_four_tone_captions(scene_core)
        except CaptionGenerationError as exc:
            print(f"caption-compass: {exc}", file=sys.stderr)
            return 2

        if args.output == "-":
            print(json.dumps(captions, indent=2, sort_keys=True))
        else:
            write_captions_json(captions, args.output)
        return 0

    if args.command == "evaluate-captions":
        try:
            scene_core = load_scene_core_json(args.scene_core)
            captions = load_captions_json(args.captions)
            evaluation = evaluate_captions(scene_core, captions)
        except (CaptionGenerationError, EvaluationError) as exc:
            print(f"caption-compass: {exc}", file=sys.stderr)
            return 2

        if args.output == "-":
            print(json.dumps(evaluation, indent=2, sort_keys=True))
        else:
            write_evaluation_json(evaluation, args.output)
        return 0

    parser.error(f"unknown command: {args.command}")
    return 2
