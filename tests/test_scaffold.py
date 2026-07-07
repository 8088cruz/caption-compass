import json
import subprocess
import sys
import unittest

from caption_compass import build_scaffold_status


class ScaffoldStatusTests(unittest.TestCase):
    def test_scaffold_status_is_c1_only(self) -> None:
        status = build_scaffold_status()

        self.assertEqual(status["project"], "Caption Compass")
        self.assertEqual(status["gate"], "C1")
        self.assertEqual(status["status"], "scaffold-ready")
        self.assertIn("minimal Python package", status["implemented"])

    def test_future_gate_behavior_is_not_implemented(self) -> None:
        status = build_scaffold_status()
        future_behavior = " ".join(status["not_implemented"])

        self.assertIn("video processing", future_behavior)
        self.assertIn("provider calls", future_behavior)
        self.assertIn("caption generation", future_behavior)
        self.assertIn("accuracy or tone evaluation", future_behavior)
        self.assertIn("repair loop", future_behavior)

    def test_command_outputs_json_status(self) -> None:
        result = subprocess.run(
            [sys.executable, "-m", "caption_compass"],
            check=True,
            capture_output=True,
            text=True,
        )

        status = json.loads(result.stdout)
        self.assertEqual(status["gate"], "C1")
        self.assertEqual(status["status"], "scaffold-ready")
        self.assertIn("demo UI", status["not_implemented"])


if __name__ == "__main__":
    unittest.main()
