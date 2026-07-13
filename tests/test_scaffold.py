import json
import subprocess
import sys
import unittest

from caption_compass import build_scaffold_status


class ScaffoldStatusTests(unittest.TestCase):
    def test_project_status_reports_c6b(self) -> None:
        status = build_scaffold_status()

        self.assertEqual(status["project"], "Caption Compass")
        self.assertEqual(status["gate"], "C6B")
        self.assertEqual(status["status"], "persisted-frames-ready")
        self.assertIn("timestamped frame evidence sampling", status["implemented"])
        self.assertIn("persisted local frame artifacts for provider use", status["implemented"])
        self.assertIn("sanitized provider configuration boundary", status["implemented"])

    def test_future_gate_behavior_is_not_implemented(self) -> None:
        status = build_scaffold_status()
        future_behavior = " ".join(status["not_implemented"])

        self.assertIn("provider calls", future_behavior)
        self.assertIn("scene interpretation", future_behavior)
        self.assertIn("provider-backed caption generation", future_behavior)
        self.assertIn("audio extraction", future_behavior)
        self.assertIn("audio transcription", future_behavior)
        self.assertIn("demo UI", future_behavior)
        self.assertIn("Docker runtime", future_behavior)

    def test_command_outputs_json_status(self) -> None:
        result = subprocess.run(
            [sys.executable, "-m", "caption_compass"],
            check=True,
            capture_output=True,
            text=True,
        )

        status = json.loads(result.stdout)
        self.assertEqual(status["gate"], "C6B")
        self.assertEqual(status["status"], "persisted-frames-ready")
        self.assertIn("demo UI", status["not_implemented"])


if __name__ == "__main__":
    unittest.main()
