import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from caption_compass.evaluator import evaluate_captions
from caption_compass.repair import InvalidRepairInputError, repair_captions

SAMPLE_SCENE_CORE_PATH = Path("docs/artifacts/c3-scene-core.sample.json")
SAMPLE_CAPTIONS_PATH = Path("docs/artifacts/c4-four-tone-captions.sample.json")
SAMPLE_EVALUATION_PATH = Path("docs/artifacts/c5-evaluation.sample.json")
EXPECTED_TONES = ["formal", "sarcastic", "humorous-tech", "humorous-non-tech"]


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _load_sample_scene_core() -> dict:
    return _load_json(SAMPLE_SCENE_CORE_PATH)


def _load_sample_captions() -> dict:
    return _load_json(SAMPLE_CAPTIONS_PATH)


def _load_sample_evaluation() -> dict:
    return _load_json(SAMPLE_EVALUATION_PATH)


def _failed_sarcastic_fixture() -> tuple[dict, dict, dict]:
    scene_core = _load_sample_scene_core()
    captions = _load_sample_captions()
    captions["captions"]["sarcastic"]["caption"] = "Timestamped video evidence is available, but no verified scene details are available."
    evaluation = evaluate_captions(scene_core, captions)
    return scene_core, captions, evaluation


class BoundedRepairTests(unittest.TestCase):
    def test_passing_captions_are_not_repaired(self) -> None:
        scene_core = _load_sample_scene_core()
        captions = _load_sample_captions()
        evaluation = _load_sample_evaluation()

        trace = repair_captions(scene_core, captions, evaluation)

        self.assertEqual(trace["schema_version"], "c6.repair_trace.v1")
        self.assertEqual(trace["gate"], "C6")
        self.assertEqual(trace["max_repair_attempts"], 1)
        self.assertEqual(trace["repair_history"], [])
        self.assertEqual(trace["hard_stops"], [])
        self.assertEqual(trace["overall"]["repair_attempted_count"], 0)
        self.assertTrue(trace["overall"]["passed_after_repair"])

    def test_failed_repair_eligible_caption_is_repaired_exactly_once(self) -> None:
        scene_core, captions, evaluation = _failed_sarcastic_fixture()

        trace = repair_captions(scene_core, captions, evaluation)

        self.assertEqual(len(trace["repair_history"]), 1)
        history = trace["repair_history"][0]
        self.assertEqual(history["caption_key"], "sarcastic")
        self.assertEqual(history["attempt"], 1)
        self.assertIn("tone_mismatch", history["repair_reason_codes"])
        self.assertTrue(history["accepted"])
        self.assertEqual(history["status"], "accepted")
        self.assertNotEqual(history["before"]["text"], history["after"]["text"])
        self.assertIn("factual_accuracy", history["before"]["scores"])
        self.assertIn("tone_match", history["after"]["scores"])
        self.assertLessEqual(trace["overall"]["max_attempts_per_caption_observed"], 1)

    def test_repair_preserves_scene_core_id_and_original_scene_core(self) -> None:
        scene_core, captions, evaluation = _failed_sarcastic_fixture()
        original_scene_core = copy.deepcopy(scene_core)

        trace = repair_captions(scene_core, captions, evaluation)

        self.assertEqual(scene_core, original_scene_core)
        self.assertEqual(trace["scene_core_id"], scene_core["scene_core_id"])
        self.assertFalse(trace["contract_boundary"]["factual_scene_core_mutated"])
        self.assertTrue(trace["contract_boundary"]["max_one_attempt_per_failed_caption"])

    def test_repaired_caption_is_reevaluated_and_final_captions_are_accepted(self) -> None:
        scene_core, captions, evaluation = _failed_sarcastic_fixture()

        trace = repair_captions(scene_core, captions, evaluation)
        history = trace["repair_history"][0]

        self.assertGreaterEqual(history["after"]["scores"]["tone_match"], history["before"]["scores"]["tone_match"])
        self.assertEqual(history["after"]["issues"], [])
        self.assertEqual(trace["final_captions"]["sarcastic"], history["after"]["text"])
        self.assertTrue(trace["final_evaluation_summary"]["passed"])

    def test_non_repairable_issue_codes_stop_repair(self) -> None:
        scene_core = _load_sample_scene_core()
        captions = _load_sample_captions()
        captions["captions"]["formal"]["scene_core_id"] = "scene_core_wrong"
        evaluation = evaluate_captions(scene_core, captions)

        trace = repair_captions(scene_core, captions, evaluation)

        self.assertEqual(trace["repair_history"], [])
        self.assertEqual(len(trace["hard_stops"]), 1)
        self.assertEqual(trace["hard_stops"][0]["caption_key"], "formal")
        self.assertIn("scene_core_mismatch", trace["hard_stops"][0]["issue_codes"])
        self.assertFalse(trace["hard_stops"][0]["repair_attempted"])

    def test_rejected_repair_does_not_replace_original_caption(self) -> None:
        scene_core, captions, evaluation = _failed_sarcastic_fixture()
        original_text = captions["captions"]["sarcastic"]["caption"]
        bad_repair_contract = copy.deepcopy(captions)
        bad_repair_contract["captions"]["sarcastic"]["caption"] = "A chef cooks pasta in a kitchen."

        with patch("caption_compass.repair.generate_four_tone_captions", return_value=bad_repair_contract):
            trace = repair_captions(scene_core, captions, evaluation)

        self.assertEqual(len(trace["repair_history"]), 1)
        history = trace["repair_history"][0]
        self.assertFalse(history["accepted"])
        self.assertEqual(history["status"], "rejected")
        self.assertEqual(trace["final_captions"]["sarcastic"], original_text)

    def test_repair_does_not_use_c3_unsupported_inferences(self) -> None:
        scene_core, captions, evaluation = _failed_sarcastic_fixture()

        trace = repair_captions(scene_core, captions, evaluation)
        repaired_text = trace["repair_history"][0]["after"]["text"].lower()

        self.assertNotIn("person", repaired_text)
        self.assertNotIn("kitchen", repaired_text)
        self.assertNotIn("cooking", repaired_text)
        self.assertNotIn("soundtrack", repaired_text)

    def test_public_safe_output_excludes_future_gate_payloads(self) -> None:
        scene_core, captions, evaluation = _failed_sarcastic_fixture()

        trace = repair_captions(scene_core, captions, evaluation)
        payload = json.dumps(trace, sort_keys=True)

        self.assertFalse(trace["contract_boundary"]["local_paths_included"])
        self.assertNotIn("/workspace", payload)
        self.assertNotIn("/tmp", payload)
        self.assertNotIn("/home", payload)
        self.assertNotIn("SECRET_VALUE", payload)
        self.assertNotIn("Streamlit", json.dumps(trace.get("final_captions", {})))
        self.assertIn("Streamlit UI", trace["contract_boundary"]["does_not_include"])

    def test_invalid_evaluation_schema_is_rejected(self) -> None:
        with self.assertRaises(InvalidRepairInputError):
            repair_captions(_load_sample_scene_core(), _load_sample_captions(), {"schema_version": "c4.four_tone_captions.v1"})

    def test_cli_repair_captions_writes_trace_json(self) -> None:
        scene_core, captions, evaluation = _failed_sarcastic_fixture()
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            captions_path = temp_path / "captions.json"
            evaluation_path = temp_path / "evaluation.json"
            output_path = temp_path / "repair-trace.json"
            captions_path.write_text(json.dumps(captions), encoding="utf-8")
            evaluation_path.write_text(json.dumps(evaluation), encoding="utf-8")

            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "caption_compass",
                    "repair-captions",
                    "--scene-core",
                    str(SAMPLE_SCENE_CORE_PATH),
                    "--captions",
                    str(captions_path),
                    "--evaluation",
                    str(evaluation_path),
                    "--output",
                    str(output_path),
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            trace = json.loads(output_path.read_text(encoding="utf-8"))

        self.assertEqual(result.stdout, "")
        self.assertEqual(trace["gate"], "C6")
        self.assertEqual(trace["scene_core_id"], _load_sample_scene_core()["scene_core_id"])
        self.assertEqual(len(trace["repair_history"]), 1)


if __name__ == "__main__":
    unittest.main()
