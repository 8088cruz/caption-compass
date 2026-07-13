import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from caption_compass.vision_observations import VisionObservationError, observe_frames


def _sample_evidence() -> dict[str, object]:
    return {
        "schema_version": "c2.frame_evidence.v1",
        "gate": "C2",
        "source_video": {
            "identifier": "sample-video.mp4",
            "duration_seconds": 2.0,
            "width": 64,
            "height": 48,
            "frame_rate": 10.0,
        },
        "sampling": {
            "requested_frame_count": 2,
            "sampled_frame_count": 2,
            "strategy": "center-of-equal-time-segments",
        },
        "frames": [
            {
                "frame_id": "frame_0001",
                "frame_ref": "frame://sample-video/frame_0001",
                "timestamp_seconds": 0.25,
                "timestamp_label": "00:00.250",
                "persisted_frame_ref": "local-output://manual-run/frames/frame_0001.jpg",
            },
            {
                "frame_id": "frame_0002",
                "frame_ref": "frame://sample-video/frame_0002",
                "timestamp_seconds": 0.75,
                "timestamp_label": "00:00.750",
                "persisted_frame_ref": "local-output://manual-run/frames/frame_0002.jpg",
            },
        ],
        "persistence": {
            "frames_persisted": True,
            "output_ref": "local-output://manual-run/frames",
            "local_paths_included": False,
        },
        "extraction": {"status": "ok", "tooling": "ffmpeg/ffprobe", "warnings": [], "local_paths_included": False},
    }


class VisionObservationTests(unittest.TestCase):
    def test_stub_observations_are_public_safe_and_network_free(self) -> None:
        observations = observe_frames(_sample_evidence(), env={"CAPTION_COMPASS_PROVIDER": "stub"})

        payload = json.dumps(observations, sort_keys=True)
        self.assertEqual(observations["gate"], "C6C")
        self.assertEqual(observations["schema_version"], "c6c.frame_observations.v1")
        self.assertEqual(observations["provider"]["name"], "stub")
        self.assertFalse(observations["provider"]["network_used"])
        self.assertFalse(observations["local_paths_included"])
        self.assertEqual(len(observations["frames"]), 2)
        self.assertIn("Stub provider mode does not inspect pixels", observations["frames"][0]["uncertainty_notes"][0])
        self.assertNotIn("/tmp", payload)
        self.assertNotIn("/home", payload)
        self.assertNotIn("FIREWORKS_API_KEY", payload)

    def test_fireworks_mode_requires_frames_dir(self) -> None:
        with self.assertRaises(VisionObservationError) as raised:
            observe_frames(
                _sample_evidence(),
                env={
                    "CAPTION_COMPASS_PROVIDER": "fireworks",
                    "FIREWORKS_API_KEY": "super-secret-test-key",
                    "CAPTION_COMPASS_VISION_MODEL": "vision-model",
                },
            )

        self.assertIn("--frames-dir", str(raised.exception))
        self.assertNotIn("super-secret-test-key", str(raised.exception))

    def test_fireworks_mode_reports_missing_frame_without_absolute_path(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            frames_dir = Path(temp_dir) / "frames"
            frames_dir.mkdir()
            with self.assertRaises(VisionObservationError) as raised:
                observe_frames(
                    _sample_evidence(),
                    frames_dir=frames_dir,
                    env={
                        "CAPTION_COMPASS_PROVIDER": "fireworks",
                        "FIREWORKS_API_KEY": "super-secret-test-key",
                        "CAPTION_COMPASS_VISION_MODEL": "vision-model",
                    },
                )

        message = str(raised.exception)
        self.assertIn("frame_0001", message)
        self.assertNotIn(temp_dir, message)
        self.assertNotIn("super-secret-test-key", message)

    def test_fireworks_mode_uses_provider_payload_without_leaking_paths(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            frames_dir = Path(temp_dir) / "frames"
            frames_dir.mkdir()
            (frames_dir / "frame_0001.jpg").write_bytes(b"fake-jpeg-1")
            (frames_dir / "frame_0002.jpg").write_bytes(b"fake-jpeg-2")

            with patch("caption_compass.vision_observations._call_fireworks_vision") as call:
                call.return_value = {
                    "observed_entities": ["person", "pan"],
                    "visible_actions": ["stirs food"],
                    "visible_text": [],
                    "setting_or_context": "kitchen",
                    "uncertainty_notes": ["exact ingredients unclear"],
                    "unsupported_inferences": ["taste cannot be determined"],
                }
                observations = observe_frames(
                    _sample_evidence(),
                    frames_dir=frames_dir,
                    env={
                        "CAPTION_COMPASS_PROVIDER": "fireworks",
                        "FIREWORKS_API_KEY": "super-secret-test-key",
                        "CAPTION_COMPASS_VISION_MODEL": "vision-model",
                    },
                )

            payload = json.dumps(observations, sort_keys=True)

        self.assertTrue(observations["provider"]["network_used"])
        self.assertEqual(observations["provider"]["name"], "fireworks")
        self.assertEqual(observations["frames"][0]["observed_entities"], ["person", "pan"])
        self.assertEqual(observations["frames"][0]["setting_or_context"], "kitchen")
        self.assertNotIn(temp_dir, payload)
        self.assertNotIn("super-secret-test-key", payload)

    def test_cli_observe_frames_outputs_stub_json(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            evidence_path = Path(temp_dir) / "frame-evidence.json"
            evidence_path.write_text(json.dumps(_sample_evidence()), encoding="utf-8")
            env = os.environ.copy()
            env["CAPTION_COMPASS_PROVIDER"] = "stub"
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "caption_compass",
                    "observe-frames",
                    "--evidence",
                    str(evidence_path),
                ],
                check=True,
                capture_output=True,
                env=env,
                text=True,
            )

        observations = json.loads(result.stdout)
        self.assertEqual(observations["gate"], "C6C")
        self.assertEqual(observations["provider"]["name"], "stub")
        self.assertFalse(observations["provider"]["network_used"])
        self.assertNotIn(temp_dir, result.stdout)


if __name__ == "__main__":
    unittest.main()
