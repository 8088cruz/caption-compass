import json
import subprocess
import sys
import unittest

from caption_compass import build_scaffold_status


class ScaffoldStatusTests(unittest.TestCase):
    def test_project_status_reports_c5(self) -> None:
        status = build_scaffold_status()

        self.assertEqual(status["project"], "Caption Compass")
        self.assertEqual(status["gate"], "C5")
        self.assertEqual(status["status"], "accuracy-tone-evaluator-ready")
        self.assertIn("minimal Python package", status["implemented"])
        self.assertIn("timestamped frame evidence sampling", status["implemented"])
        self.assertIn("deterministic factual scene core contract", status["implemented"])
        self.assertIn("deterministic four-tone caption contract", status["implemented"])
        self.assertIn("deterministic accuracy and tone evaluator", status["implemented"])

    def test_future_gate_behavior_is_not_implemented(self) -> None:
        status = build_scaffold_status()
        future_behavior = " ".join(status["not_implemented"])

        self.assertIn("provider calls", future_behavior)
        self.assertIn("scene interpretation", future_behavior)
        self.assertIn("provider-backed caption generation", future_behavior)
        self.assertIn("automated caption repair", future_behavior)
        self.assertIn("repair loop", future_behavior)

    def test_command_outputs_json_status(self) -> None:
        result = subprocess.run(
            [sys.executable, "-m", "caption_compass"],
            check=True,
            capture_output=True,
            text=True,
        )

        status = json.loads(result.stdout)
        self.assertEqual(status["gate"], "C5")
        self.assertEqual(status["status"], "accuracy-tone-evaluator-ready")
        self.assertIn("demo UI", status["not_implemented"])


if __name__ == "__main__":
    unittest.main()
