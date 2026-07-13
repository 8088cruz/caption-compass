import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from caption_compass.video_ingestion import (
    InvalidVideoError,
    MissingVideoToolError,
    extract_frame_evidence,
    sample_timestamps,
    sanitize_source_identifier,
)


def _require_ffmpeg() -> None:
    if shutil.which("ffmpeg") is None or shutil.which("ffprobe") is None:
        raise unittest.SkipTest("ffmpeg and ffprobe are required for C2/C6B video tests")


def _write_synthetic_video(path: Path) -> None:
    _require_ffmpeg()
    command = [
        "ffmpeg",
        "-nostdin",
        "-y",
        "-loglevel",
        "error",
        "-f",
        "lavfi",
        "-i",
        "testsrc=duration=2:size=64x48:rate=10",
        "-c:v",
        "mpeg4",
        str(path),
    ]
    subprocess.run(command, check=True)


class VideoIngestionTests(unittest.TestCase):
    def test_sample_timestamps_are_deterministic(self) -> None:
        self.assertEqual(sample_timestamps(2.0, frame_count=4), [0.25, 0.75, 1.25, 1.75])

    def test_sanitize_source_identifier_removes_paths_and_spaces(self) -> None:
        self.assertEqual(
            sanitize_source_identifier("nested/local videos/my sample!.mp4"),
            "my-sample.mp4",
        )

    def test_extract_frame_evidence_is_public_safe_json(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            video_path = Path(temp_dir) / "fixture.mp4"
            _write_synthetic_video(video_path)

            evidence = extract_frame_evidence(
                video_path,
                frame_count=3,
                source_identifier="synthetic c2 fixture.mp4",
            )

        payload = json.dumps(evidence, sort_keys=True)
        self.assertEqual(evidence["gate"], "C2")
        self.assertEqual(evidence["schema_version"], "c2.frame_evidence.v1")
        self.assertEqual(evidence["source_video"]["identifier"], "synthetic-c2-fixture.mp4")
        self.assertEqual(evidence["sampling"]["sampled_frame_count"], 3)
        self.assertEqual(evidence["extraction"]["status"], "ok")
        self.assertFalse(evidence["extraction"]["local_paths_included"])
        self.assertFalse(evidence["persistence"]["frames_persisted"])
        self.assertFalse(evidence["persistence"]["local_paths_included"])
        self.assertNotIn(temp_dir, payload)
        self.assertEqual(
            [frame["frame_id"] for frame in evidence["frames"]],
            ["frame_0001", "frame_0002", "frame_0003"],
        )
        self.assertTrue(all(frame["frame_ref"].startswith("frame://") for frame in evidence["frames"]))

    def test_persisted_frames_are_written_but_not_exposed_as_absolute_paths(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            video_path = root / "fixture.mp4"
            output_dir = root / "local_test_outputs" / "manual-run"
            _write_synthetic_video(video_path)

            evidence = extract_frame_evidence(
                video_path,
                frame_count=2,
                source_identifier="manual fixture.mp4",
                persist_frames=True,
                output_dir=output_dir,
            )

            expected_files = [
                output_dir / "frames" / "frame_0001.jpg",
                output_dir / "frames" / "frame_0002.jpg",
            ]
            for frame_path in expected_files:
                self.assertTrue(frame_path.is_file(), frame_path)
                self.assertGreater(frame_path.stat().st_size, 0)

            payload = json.dumps(evidence, sort_keys=True)

        self.assertTrue(evidence["persistence"]["frames_persisted"])
        self.assertEqual(evidence["persistence"]["output_ref"], "local-output://manual-run/frames")
        self.assertFalse(evidence["persistence"]["local_paths_included"])
        self.assertNotIn(temp_dir, payload)
        self.assertTrue(
            all(frame["persisted_frame_ref"].startswith("local-output://manual-run/frames/") for frame in evidence["frames"])
        )

    def test_cli_can_persist_frames_to_ignored_local_output(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            video_path = root / "fixture.mp4"
            output_dir = root / "local_test_outputs" / "cli-run"
            _write_synthetic_video(video_path)
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "caption_compass",
                    "sample-frames",
                    "--video",
                    str(video_path),
                    "--frame-count",
                    "2",
                    "--source-id",
                    "cli fixture.mp4",
                    "--persist-frames",
                    "--output-dir",
                    str(output_dir),
                ],
                check=True,
                capture_output=True,
                text=True,
            )

            self.assertTrue((output_dir / "frames" / "frame_0001.jpg").is_file())
            self.assertTrue((output_dir / "frames" / "frame_0002.jpg").is_file())

        evidence = json.loads(result.stdout)
        self.assertEqual(evidence["gate"], "C2")
        self.assertEqual(evidence["source_video"]["identifier"], "cli-fixture.mp4")
        self.assertEqual(evidence["sampling"]["sampled_frame_count"], 2)
        self.assertTrue(evidence["persistence"]["frames_persisted"])
        self.assertEqual(evidence["persistence"]["output_ref"], "local-output://cli-run/frames")
        self.assertNotIn(temp_dir, result.stdout)

    def test_invalid_video_error_is_clear_without_absolute_path(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            invalid_path = Path(temp_dir) / "not-a-video.mp4"
            invalid_path.write_text("not a video", encoding="utf-8")

            with self.assertRaises(InvalidVideoError) as raised:
                extract_frame_evidence(invalid_path)

        message = str(raised.exception)
        self.assertIn("not-a-video.mp4", message)
        self.assertNotIn(temp_dir, message)

    def test_missing_ffmpeg_error_is_clear(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            video_path = Path(temp_dir) / "fixture.mp4"
            video_path.write_bytes(b"placeholder")

            with self.assertRaises(MissingVideoToolError):
                extract_frame_evidence(video_path, ffmpeg_bin="missing-ffmpeg-for-c2-test")

    def test_cli_sample_frames_outputs_json(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            video_path = Path(temp_dir) / "fixture.mp4"
            _write_synthetic_video(video_path)
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "caption_compass",
                    "sample-frames",
                    "--video",
                    str(video_path),
                    "--frame-count",
                    "2",
                    "--source-id",
                    "cli fixture.mp4",
                ],
                check=True,
                capture_output=True,
                text=True,
            )

        evidence = json.loads(result.stdout)
        self.assertEqual(evidence["gate"], "C2")
        self.assertEqual(evidence["source_video"]["identifier"], "cli-fixture.mp4")
        self.assertEqual(evidence["sampling"]["sampled_frame_count"], 2)
        self.assertFalse(evidence["persistence"]["frames_persisted"])
        self.assertNotIn(temp_dir, result.stdout)


if __name__ == "__main__":
    unittest.main()
