import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from caption_compass.captions import InvalidSceneCoreError, generate_four_tone_captions


SAMPLE_SCENE_CORE_PATH = Path("docs/artifacts/c3-scene-core.sample.json")
EXPECTED_TONES = ["formal", "sarcastic", "humorous-tech", "humorous-non-tech"]


def _load_sample_scene_core() -> dict:
    return json.loads(SAMPLE_SCENE_CORE_PATH.read_text(encoding="utf-8"))


class FourToneCaptionContractTests(unittest.TestCase):
    def test_caption_generation_produces_exactly_four_required_tones(self) -> None:
        captions = generate_four_tone_captions(_load_sample_scene_core())

        self.assertEqual(captions["schema_version"], "c4.four_tone_captions.v1")
        self.assertEqual(captions["gate"], "C4")
        self.assertEqual(captions["tone_order"], EXPECTED_TONES)
        self.assertEqual(list(captions["captions"].keys()), EXPECTED_TONES)
        self.assertEqual(set(captions["captions"].keys()), set(EXPECTED_TONES))

    def test_all_tone_captions_share_same_scene_core_and_fact_lock(self) -> None:
        captions = generate_four_tone_captions(_load_sample_scene_core())
        scene_core_id = captions["scene_core_id"]
        fact_lock_id = captions["fact_lock"]["fact_lock_id"]

        for caption in captions["captions"].values():
            self.assertEqual(caption["scene_core_id"], scene_core_id)
            self.assertEqual(caption["fact_lock_id"], fact_lock_id)
            self.assertEqual(caption["factual_claim_ids"], [])
            self.assertEqual(
                caption["evidence_anchor_ids"],
                captions["source_scene_core"]["evidence_anchor_ids"],
            )

    def test_unsupported_inferences_are_excluded_from_caption_claims(self) -> None:
        captions = generate_four_tone_captions(_load_sample_scene_core())

        self.assertEqual(captions["fact_lock"]["supported_claims"], [])
        self.assertGreaterEqual(len(captions["unsupported_inferences"]), 4)
        self.assertTrue(
            all(
                item["caption_policy"] == "excluded_from_caption_claims"
                for item in captions["unsupported_inferences"]
            )
        )
        caption_text = " ".join(item["caption"] for item in captions["captions"].values())
        self.assertNotIn("person", caption_text.lower())
        self.assertNotIn("kitchen", caption_text.lower())
        self.assertNotIn("cooking", caption_text.lower())

    def test_tone_rubrics_are_judge_legible_and_distinct(self) -> None:
        captions = generate_four_tone_captions(_load_sample_scene_core())

        rubrics = [captions["captions"][tone]["tone_rubric"] for tone in EXPECTED_TONES]
        self.assertEqual(len(set(rubrics)), 4)
        self.assertIn("professional", captions["captions"]["formal"]["tone_rubric"])
        self.assertIn("Dry understatement", captions["captions"]["sarcastic"]["tone_rubric"])
        self.assertIn("software-oriented humor", captions["captions"]["humorous-tech"]["tone_rubric"])
        self.assertIn("General-audience", captions["captions"]["humorous-non-tech"]["tone_rubric"])

    def test_supported_claims_are_preserved_across_caption_tones(self) -> None:
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
        supported_claims = captions["fact_lock"]["supported_claims"]
        claim_ids = [claim["claim_id"] for claim in supported_claims]

        self.assertEqual(len(supported_claims), 5)
        for caption in captions["captions"].values():
            self.assertEqual(caption["factual_claim_ids"], claim_ids)
            self.assertIn("person", caption["caption"])
            self.assertIn("stands", caption["caption"])
            self.assertIn("indoor room", caption["caption"])

    def test_caption_output_is_public_safe_and_excludes_future_gate_payloads(self) -> None:
        captions = generate_four_tone_captions(_load_sample_scene_core())
        payload = json.dumps(captions, sort_keys=True)

        self.assertFalse(captions["contract_boundary"]["local_paths_included"])
        self.assertNotIn("/workspace", payload)
        self.assertNotIn("/tmp", payload)
        self.assertNotIn("/home", payload)
        self.assertNotIn("SECRET_VALUE", payload)
        self.assertNotIn("evaluation", captions)
        self.assertNotIn("repair", captions)

    def test_malformed_scene_core_is_rejected(self) -> None:
        with self.assertRaises(InvalidSceneCoreError):
            generate_four_tone_captions({"schema_version": "c2.frame_evidence.v1"})

    def test_cli_generate_captions_writes_contract_json(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "captions.json"
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "caption_compass",
                    "generate-captions",
                    "--scene-core",
                    str(SAMPLE_SCENE_CORE_PATH),
                    "--output",
                    str(output_path),
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            captions = json.loads(output_path.read_text(encoding="utf-8"))

        self.assertEqual(result.stdout, "")
        self.assertEqual(captions["gate"], "C4")
        self.assertEqual(captions["scene_core_id"], _load_sample_scene_core()["scene_core_id"])
        self.assertEqual(len(captions["captions"]), 4)


if __name__ == "__main__":
    unittest.main()
