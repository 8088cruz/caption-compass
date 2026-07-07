import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from caption_compass.scene_core import InvalidSceneEvidenceError, build_scene_core


SAMPLE_EVIDENCE_PATH = Path("docs/artifacts/c2-frame-evidence.sample.json")


def _load_sample_evidence() -> dict:
    return json.loads(SAMPLE_EVIDENCE_PATH.read_text(encoding="utf-8"))


class SceneCoreContractTests(unittest.TestCase):
    def test_scene_core_contract_is_deterministic(self) -> None:
        evidence = _load_sample_evidence()

        first = build_scene_core(evidence)
        second = build_scene_core(evidence)

        self.assertEqual(first["scene_core_id"], second["scene_core_id"])
        self.assertTrue(first["scene_core_id"].startswith("scene_core_"))
        self.assertEqual(first, second)

    def test_factual_scene_core_preserves_evidence_anchors_without_guessing(self) -> None:
        scene_core = build_scene_core(_load_sample_evidence())

        self.assertEqual(scene_core["schema_version"], "c3.scene_core.v1")
        self.assertEqual(scene_core["gate"], "C3")
        self.assertEqual(
            scene_core["evidence_anchor_ids"],
            ["frame_0001", "frame_0002", "frame_0003", "frame_0004"],
        )
        self.assertEqual(scene_core["observed_entities"], [])
        self.assertEqual(scene_core["visible_actions"], [])
        self.assertIsNone(scene_core["setting_or_context"]["value"])
        self.assertEqual(
            scene_core["setting_or_context"]["support"],
            "unsupported_from_c2_frame_metadata_only",
        )

    def test_contract_marks_unsupported_inferences_and_uncertainty(self) -> None:
        scene_core = build_scene_core(_load_sample_evidence())
        unsupported_claim_types = {
            item["claim_type"] for item in scene_core["unsupported_inferences"]
        }

        self.assertIn("observed_entities", unsupported_claim_types)
        self.assertIn("visible_actions", unsupported_claim_types)
        self.assertIn("setting_or_context", unsupported_claim_types)
        self.assertIn("audio_or_speech", unsupported_claim_types)
        self.assertGreaterEqual(len(scene_core["uncertainty_notes"]), 2)
        self.assertFalse(scene_core["generation"]["network_used"])
        self.assertIsNone(scene_core["generation"]["provider"])

    def test_scene_core_output_is_public_safe_and_excludes_future_gate_payloads(self) -> None:
        scene_core = build_scene_core(_load_sample_evidence())
        payload = json.dumps(scene_core, sort_keys=True)

        self.assertFalse(scene_core["contract_boundary"]["local_paths_included"])
        self.assertNotIn("/workspace", payload)
        self.assertNotIn("/tmp", payload)
        self.assertNotIn("/home", payload)
        self.assertNotIn("SECRET_VALUE", payload)
        self.assertNotIn("captions", scene_core)
        self.assertNotIn("evaluation", scene_core)
        self.assertNotIn("repair", scene_core)

    def test_malformed_evidence_is_rejected(self) -> None:
        with self.assertRaises(InvalidSceneEvidenceError):
            build_scene_core({"schema_version": "c2.frame_evidence.v1", "frames": []})

    def test_cli_build_scene_core_writes_contract_json(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "scene-core.json"
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "caption_compass",
                    "build-scene-core",
                    "--evidence",
                    str(SAMPLE_EVIDENCE_PATH),
                    "--output",
                    str(output_path),
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            scene_core = json.loads(output_path.read_text(encoding="utf-8"))

        self.assertEqual(result.stdout, "")
        self.assertEqual(scene_core["gate"], "C3")
        self.assertEqual(scene_core["source_evidence"]["gate"], "C2")
        self.assertEqual(scene_core["source_evidence"]["evidence_anchor_count"], 4)


if __name__ == "__main__":
    unittest.main()
