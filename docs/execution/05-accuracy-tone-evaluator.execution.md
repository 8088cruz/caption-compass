# Execution: C5 - Accuracy/Tone Evaluator

## Goal

Add a judge-like evaluator that scores each caption for factual accuracy, tone match, and clarity, then returns issue codes and actionable rewrite hints.

## Why This Exists

Track 2 is judged on accuracy and tone. C5 makes the project more than a four-caption generator by showing the same kind of checks a judge will care about:

```text
factual scene core + four captions -> score report + issue taxonomy + rewrite hints
```

The evaluator should be visible enough to impress judges, but honest enough not to claim it proves truth.

## Source-of-Truth References

- `SKILL.md`
- `docs/README_GATE_POLICY.md`
- `docs/implementation-prompts/gate-c5.prompt.md`
- `docs/implementation-prompts/todos/c5-t01-accuracy-tone-evaluator.prompt.md`
- C3 factual scene core from `docs/execution/03-factual-scene-core.execution.md`
- C4 four-tone caption contract from `docs/execution/04-four-tone-caption-generation.execution.md`

## Scope

- Score each caption for factual accuracy, tone match, and clarity.
- Compare each caption against the C3 factual scene core.
- Verify that all captions preserve the same `scene_core_id`.
- Flag invented facts, missing core facts, unsupported inference use, tone mismatch, tone bleed, unclear jokes, malformed output, and unsafe/private-reference leakage.
- Return actionable rewrite hints.
- Mark repair eligibility for C6.
- Work in stub/test mode without network.

## Out of Scope

- Automated repair
- Rewriting captions
- Leaderboard claims
- Human preference UI
- Model fine-tuning
- Claims that evaluator scores prove objective truth

## Prerequisites

- C3 factual scene core contract exists.
- C4 four-tone caption contract exists.
- Provider adapter or deterministic stub exists.
- README gate policy has been read before README edits.

## Files/Packages Likely Touched

```text
app/contracts.py
app/evaluator.py
app/providers.py
app/prompts/
tests/test_evaluator.py
README.md
```

## Commands or UI Actions Added

Suggested verification command:

```bash
python -m pytest -k "evaluator or scoring or accuracy or tone"
```

## Data Contracts

### Evaluation Result

C5 should implement this contract or a clearly equivalent typed model:

```json
{
  "scene_core_id": "stable-scene-core-id",
  "source_video_id": "stable-video-id",
  "thresholds": {
    "factual_accuracy_min": 0.85,
    "tone_match_min": 0.75,
    "clarity_min": 0.70
  },
  "evaluation": {
    "formal": {
      "factual_accuracy": 0.95,
      "tone_match": 0.92,
      "clarity": 0.96,
      "passed": true,
      "repair_eligible": false,
      "issues": [],
      "rewrite_hint": null
    },
    "sarcastic": {
      "factual_accuracy": 0.90,
      "tone_match": 0.55,
      "clarity": 0.82,
      "passed": false,
      "repair_eligible": true,
      "issues": [
        {
          "code": "tone_mismatch",
          "severity": "medium",
          "detail": "Caption is playful but not recognizably sarcastic."
        }
      ],
      "rewrite_hint": "Keep the same facts but add mild dry irony without adding new claims."
    }
  },
  "overall": {
    "passed": false,
    "repair_recommended": true,
    "failed_caption_keys": ["sarcastic"]
  }
}
```

### Score Scale

Scores are floats from `0.0` to `1.0`.

Recommended default thresholds:

| Metric | Default threshold | Why |
| --- | ---: | --- |
| `factual_accuracy` | `0.85` | Accuracy is the highest-priority judging surface. |
| `tone_match` | `0.75` | Tones must be obvious but not overfit. |
| `clarity` | `0.70` | Captions must be easy for an LLM judge to score. |

These thresholds should be constants/config, not magic numbers scattered across code.

## Issue Taxonomy

Use these issue codes exactly unless a later gate explicitly revises the taxonomy:

| Code | Meaning | Repair eligible |
| --- | --- | --- |
| `invented_fact` | Caption adds a fact absent from the factual scene core. | yes, if removable |
| `missing_core_fact` | Caption omits a key fact needed to preserve the scene core. | yes |
| `unsupported_inference_used` | Caption uses a C3 unsupported inference as if true. | yes, if removable |
| `uncertainty_overclaimed` | Caption turns uncertainty into certainty. | yes |
| `tone_mismatch` | Caption does not match its required tone. | yes |
| `tone_bleed` | Caption overlaps too much with another tone. | yes |
| `unclear_joke` | Humor is ambiguous, obscure, or hard to score. | yes |
| `unsafe_or_private_reference` | Output contains private/system/internal references or unsafe content. | no until removed by guardrail |
| `malformed_output` | Provider output is invalid JSON or missing required fields. | no; regenerate or fail safely |
| `scene_core_mismatch` | Caption output references a different `scene_core_id`. | no; fail contract |

## Service Boundary

- Evaluation consumes the C3 factual scene core and C4 captions.
- Evaluation does not mutate captions.
- Evaluation does not repair captions; C6 handles repair.
- Evaluation does not inspect raw private docs or implementation-pack content.
- UI may display evaluation later, but C5 should be usable as a service with tests.

## Provider/API Boundary

If using Fireworks/Gemma, send only public-safe factual scene core, captions, tone labels, and evaluator instructions. Never send secrets, private docs, local paths, implementation pack contents, or private research material as model context.

Evaluator output must be described as model-assisted or heuristic. Do not claim it proves correctness.

## Prompt Contracts

The evaluator prompt must:

- require strict JSON
- compare each caption against the factual scene core
- score factual accuracy, tone match, and clarity
- use the exact issue taxonomy
- include concise issue details
- include actionable rewrite hints only when useful
- mark `repair_eligible`
- reject mismatched `scene_core_id`
- avoid hidden or private project context

## Tests

Add deterministic tests for:

- passing fixture returns `passed: true`
- invented fact fixture returns `invented_fact`
- unsupported inference fixture returns `unsupported_inference_used`
- uncertainty overclaim fixture returns `uncertainty_overclaimed`
- wrong tone fixture returns `tone_mismatch`
- tone overlap fixture returns `tone_bleed`
- obscure joke fixture returns `unclear_joke`
- mismatched `scene_core_id` returns `scene_core_mismatch`
- malformed provider JSON fails safely
- scores are bounded from `0.0` to `1.0`
- public output contains no local paths, secrets, or private research terms

## README Update Requirements

Update README.md to reflect this gate's actual completed behavior. Do not document future gates as implemented.

The README must include current gate status, working commands only, known limitations, and planned gates as future work. If implemented, describe evaluator output as model-assisted or heuristic, not proof.

## Acceptance Criteria

- Evaluator returns judge-readable scores and issue codes.
- Failed captions include actionable rewrite hints where repair is possible.
- Repair eligibility is explicit for C6.
- Same `scene_core_id` is enforced.
- README does not overclaim evaluator correctness.

## Implementation Steps

1. Read `SKILL.md`.
2. Read `docs/README_GATE_POLICY.md`.
3. Read this execution document.
4. Inspect C3 and C4 contracts.
5. Define or update evaluator contract.
6. Add deterministic issue-taxonomy fixtures.
7. Implement only C5 evaluation behavior.
8. Run the suggested verification command.
9. Update README with actual completed behavior only.
10. Report changed files, test results, risks, and next gate.

## Reviewer Confidence Signal

A reviewer should be able to see exactly how each caption was scored, why any caption failed, which issue codes were assigned, what repair hint was produced, and what remains deferred to C6 repair.

## Benchmark / Evidence Artifact

This gate should leave behind at least one concrete artifact:

- passing evaluator contract tests
- a sample evaluator JSON fixture
- an issue-taxonomy fixture set
- a malformed-provider-output failure fixture
- a README note describing evaluator limitations
- a documented blocker with exact provider, schema, or fixture issue

## Demo Commands

```bash
python -m pytest -k "evaluator or scoring or accuracy or tone"
```

## Expected Output

A public-safe evaluation JSON object that can drive C6 repair and C7 UI display.

## Failure Cases

- Evaluator accepts invented facts
- Evaluator misses unsupported inference use
- Evaluator confuses tone categories
- Evaluator gives vague rewrite hints
- Evaluator output is malformed JSON
- Evaluator claims proof instead of score
- README claims repair exists before C6

## Stop/Gate Criteria

Stop if evaluator cannot explain why a caption failed, if issue codes are not stable, if repair is implemented inside C5, or if evaluator claims objective truth.

## Suggested Conventional Commit

```text
feat(eval): score caption accuracy and tone
```
