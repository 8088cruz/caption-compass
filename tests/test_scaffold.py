import json
import subprocess
import sys
import unittest

from caption_compass import build_scaffold_status


class ScaffoldStatusTests(unittest.TestCase):
    def test_project_status_reports_c6a(self) -> None:
        status = build_scaffold_status()

        self.assertEqual(status["project"], "Caption Compass")
        self.assertEqual(status["gate"], "C6A")
        self.assertEqual(status["status"], "provider-config-ready")
        self.assertIn("minimal Python package", status["implemented"])
        self.assertIn("timestamped frame evidence sampling", status["implemented"])
        self.assertIn("deterministic factual scene core contract", status["implemented"])
        self.assertIn("deterministic four-tone caption contract", status["implemented"])
        self.assertIn("deterministic accuracy and tone evaluator", status["implemented"])
        self.assertIn("one bounded deterministic repair pass", status["implemented"])
        self.assertIn("sanitized provider configuration boundary", status["implemented"])

    def test_future_gate_behavior_is_not_implemented(self) -> None:
        status = build_scaffold_status()
        future_behavior = " ".join(status["not_implemented"])

        self.assertIn("provider calls", future_behavior)
        self.assertIn("scene interpretation", future_behavior)
        self.assertIn("provider-backed caption generation", future_behavior)
        self.assertIn("persisted frame artifacts", future_behavior)
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
        self.assertEqual(status["gate"], "C6A")
        self.assertEqual(status["status"], "provider-config-ready")
        self.assertIn("demo UI", status["not_implemented"])


if __name__ == "__main__":
    unittest.main()
