import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from caption_compass.captions import generate_four_tone_captions
from caption_compass.evaluator import (
    ISSUE_TAXONOMY,
    InvalidEvaluationInputError,
    evaluate_captions,
)


SAMPLE_SCENE_CORE_PATH = Path("docs/artifacts/c3-scene-core.sample.json")
SAMPLE_CAPTIONS_PATH = Path("docs/artifacts/c4-four-tone-captions.sample.json")
EXPECTED_TONES = ["formal", "sarcastic", "humorous-tech", "humorous-non-tech"]


def _load_sample_scene_core() -> dict:
    return json.loads(SAMPLE_SCENE_CORE_PATH.read_text(encoding="utf-8"))


def _load_sample_captions() -> dict:
    return json.loads(SAMPLE_CAPTIONS_PATH.read_text(encoding="utf-8"))


def _codes(result: dict, tone: str) -> set[str]:
    return {issue["code"] for issue in result["evaluation"][tone]["issues"]}


class AccuracyToneEvaluatorTests(unittest.TestCase):
    def test_passing_fixture_scores_all_tones_without_repairing_captions(self) -> None:
        scene_core = _load_sample_scene_core()
        captions = _load_sample_captions()
        before = copy.deepcopy(captions)

        result = evaluate_captions(scene_core, captions)

        self.assertEqual(result["schema_version"], "c5.evaluation.v1")
        self.assertEqual(result["gate"], "C5")
        self.assertEqual(result["scene_core_id"], scene_core["scene_core_id"])
        self.assertEqual(result["tone_order"], EXPECTED_TONES)
        self.assertTrue(result["overall"]["passed"])
        self.assertFalse(result["overall"]["repair_recommended"])
        self.assertEqual(captions, before)
        for tone in EXPECTED_TONES:
            self.assertTrue(result["evaluation"][tone]["passed"])
            self.assertEqual(result["evaluation"][tone]["issues"], [])
            self.assertFalse(result["evaluation"][tone]["repair_eligible"])

    def test_invented_fact_fixture_returns_invented_fact_and_rewrite_hint(self) -> None:
        scene_core = _load_sample_scene_core()
        captions = _load_sample_captions()
        captions["captions"]["formal"]["caption"] = "A chef cooks pasta in a kitchen."

        result = evaluate_captions(scene_core, captions)

        self.assertIn("invented_fact", _codes(result, "formal"))
        self.assertFalse(result["evaluation"]["formal"]["passed"])
        self.assertTrue(result["evaluation"]["formal"]["repair_eligible"])
        self.assertIn("Remove unsupported", result["evaluation"]["formal"]["rewrite_hint"])

    def test_unsupported_inference_fixture_returns_unsupported_inference_used(self) -> None:
        scene_core = _load_sample_scene_core()
        captions = _load_sample_captions()
        captions["captions"]["formal"]["caption"] = "The soundtrack clearly says this is a cooking video."

        result = evaluate_captions(scene_core, captions)

        self.assertIn("unsupported_inference_used", _codes(result, "formal"))
        self.assertIn("uncertainty_overclaimed", _codes(result, "formal"))

    def test_uncertainty_overclaim_fixture_returns_uncertainty_overclaimed(self) -> None:
        scene_core = _load_sample_scene_core()
        captions = _load_sample_captions()
        captions["captions"]["formal"]["caption"] = "The frame anchors clearly shows a happy person."

        result = evaluate_captions(scene_core, captions)

        self.assertIn("uncertainty_overclaimed", _codes(result, "formal"))

    def test_wrong_tone_fixture_returns_tone_mismatch(self) -> None:
        scene_core = _load_sample_scene_core()
        captions = _load_sample_captions()
        captions["captions"]["sarcastic"]["caption"] = captions["captions"]["formal"]["caption"]

        result = evaluate_captions(scene_core, captions)

        self.assertIn("tone_mismatch", _codes(result, "sarcastic"))

    def test_tone_overlap_fixture_returns_tone_bleed(self) -> None:
        scene_core = _load_sample_scene_core()
        captions = _load_sample_captions()
        same = "Frame anchors compiled successfully; visual facts returned an empty list."
        captions["captions"]["humorous-tech"]["caption"] = same
        captions["captions"]["humorous-non-tech"]["caption"] = same

        result = evaluate_captions(scene_core, captions)

        self.assertIn("tone_bleed", _codes(result, "humorous-non-tech"))

    def test_obscure_joke_fixture_returns_unclear_joke(self) -> None:
        scene_core = _load_sample_scene_core()
        captions = _load_sample_captions()
        captions["captions"]["humorous-tech"]["caption"] = "The monad caught a Kubernetes SIGTERM, obviously."

        result = evaluate_captions(scene_core, captions)

        self.assertIn("unclear_joke", _codes(result, "humorous-tech"))

    def test_mismatched_scene_core_returns_scene_core_mismatch(self) -> None:
        scene_core = _load_sample_scene_core()
        captions = _load_sample_captions()
        captions["captions"]["formal"]["scene_core_id"] = "scene_core_wrong"

        result = evaluate_captions(scene_core, captions)

        self.assertIn("scene_core_mismatch", _codes(result, "formal"))
        self.assertFalse(result["evaluation"]["formal"]["repair_eligible"])

    def test_malformed_caption_contract_fails_safely(self) -> None:
        scene_core = _load_sample_scene_core()
        captions = _load_sample_captions()
        del captions["captions"]["formal"]["caption"]

        result = evaluate_captions(scene_core, captions)

        self.assertIn("malformed_output", _codes(result, "formal"))
        self.assertFalse(result["evaluation"]["formal"]["repair_eligible"])
        self.assertIsNone(result["evaluation"]["formal"]["rewrite_hint"])

    def test_invalid_schema_is_rejected(self) -> None:
        with self.assertRaises(InvalidEvaluationInputError):
            evaluate_captions({"schema_version": "c2.frame_evidence.v1"}, _load_sample_captions())

    def test_scores_are_bounded_and_taxonomy_is_complete(self) -> None:
        result = evaluate_captions(_load_sample_scene_core(), _load_sample_captions())

        for issue_code in [
            "invented_fact",
            "missing_core_fact",
            "unsupported_inference_used",
            "uncertainty_overclaimed",
            "tone_mismatch",
            "tone_bleed",
            "unclear_joke",
            "unsafe_or_private_reference",
            "malformed_output",
            "scene_core_mismatch",
        ]:
            self.assertIn(issue_code, ISSUE_TAXONOMY)
            self.assertIn(issue_code, result["issue_taxonomy"])

        for tone in EXPECTED_TONES:
            for metric in ("factual_accuracy", "tone_match", "clarity"):
                self.assertGreaterEqual(result["evaluation"][tone][metric], 0.0)
                self.assertLessEqual(result["evaluation"][tone][metric], 1.0)

    def test_public_safe_output_excludes_future_gate_payloads(self) -> None:
        result = evaluate_captions(_load_sample_scene_core(), _load_sample_captions())
        payload = json.dumps(result, sort_keys=True)

        self.assertFalse(result["contract_boundary"]["local_paths_included"])
        self.assertFalse(result["contract_boundary"]["captions_mutated"])
        self.assertTrue(result["contract_boundary"]["scores_are_heuristic"])
        self.assertNotIn("/workspace", payload)
        self.assertNotIn("/tmp", payload)
        self.assertNotIn("/home", payload)
        self.assertNotIn("SECRET_VALUE", payload)
        self.assertNotIn("repaired_caption", payload)
        self.assertNotIn("repair_trace", payload)

    def test_cli_evaluate_captions_writes_contract_json(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "evaluation.json"
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "caption_compass",
                    "evaluate-captions",
                    "--scene-core",
                    str(SAMPLE_SCENE_CORE_PATH),
                    "--captions",
                    str(SAMPLE_CAPTIONS_PATH),
                    "--output",
                    str(output_path),
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            evaluation = json.loads(output_path.read_text(encoding="utf-8"))

        self.assertEqual(result.stdout, "")
        self.assertEqual(evaluation["gate"], "C5")
        self.assertEqual(evaluation["scene_core_id"], _load_sample_scene_core()["scene_core_id"])
        self.assertEqual(set(evaluation["evaluation"].keys()), set(EXPECTED_TONES))

    def test_supported_claim_omission_returns_missing_core_fact(self) -> None:
        scene_core = _load_sample_scene_core()
        scene_core["summary"] = "A person stands at a table."
        scene_core["observed_entities"] = ["person", "table"]
        scene_core["visible_actions"] = ["stands"]
        scene_core["setting_or_context"] = {
            "value": "indoor room",
            "support": "supported_by_scene_core",
            "evidence_anchor_ids": ["frame_0001"],
        }
        captions = generate_four_tone_captions(scene_core)
        captions["captions"]["formal"]["caption"] = "Observed entities: person."

        result = evaluate_captions(scene_core, captions)

        self.assertIn("missing_core_fact", _codes(result, "formal"))
        self.assertTrue(result["evaluation"]["formal"]["repair_eligible"])


if __name__ == "__main__":
    unittest.main()
