# Execution: C6 - Retry/Repair Loop

## Goal

Implement one bounded repair pass for captions that fail C5 factual accuracy, tone match, or clarity thresholds.

## Why This Exists

C6 turns C5 evaluation into visible product behavior while staying feasible for a one-day solo build:

```text
failed caption + factual scene core + evaluator issue codes -> one repaired caption -> before/after score artifact
```

The repair loop should demonstrate quality control, not become an unbounded agent system.

## Source-of-Truth References

- `SKILL.md`
- `docs/README_GATE_POLICY.md`
- `docs/implementation-prompts/gate-c6.prompt.md`
- `docs/implementation-prompts/todos/c6-t01-retry-repair-loop.prompt.md`
- C3 factual scene core from `docs/execution/03-factual-scene-core.execution.md`
- C4 four-tone caption contract from `docs/execution/04-four-tone-caption-generation.execution.md`
- C5 evaluator contract from `docs/execution/05-accuracy-tone-evaluator.execution.md`

## Scope

- Retry only captions marked `repair_eligible: true` by C5.
- Use C5 issue codes and rewrite hints to repair failed captions.
- Preserve the same `scene_core_id`.
- Preserve factual content from the C3 scene core.
- Exclude C3 `unsupported_inferences` from repaired caption facts.
- Bound repair to exactly one pass per failed caption.
- Re-evaluate repaired captions.
- Expose before/after captions and before/after scores for demo clarity.

## Out of Scope

- Multi-agent loops
- Unbounded self-improvement
- More than one repair attempt
- Automatic fine-tuning
- Complex caching
- Human preference ranking UI
- Repairing malformed scene cores

## Prerequisites

- C3 factual scene core contract exists.
- C4 four-caption output exists.
- C5 evaluator returns issue codes, thresholds, rewrite hints, and `repair_eligible`.
- Provider adapter or deterministic stub exists.
- README gate policy has been read before README edits.

## Files/Packages Likely Touched

```text
app/contracts.py
app/repair.py
app/evaluator.py
app/captions.py
app/providers.py
app/prompts/
tests/test_repair.py
README.md
```

## Commands or UI Actions Added

Suggested verification command:

```bash
python -m pytest -k "repair or retry or evaluator or caption"
```

## Data Contracts

### Repair Result

C6 should implement this contract or a clearly equivalent typed model:

```json
{
  "scene_core_id": "stable-scene-core-id",
  "source_video_id": "stable-video-id",
  "max_repair_attempts": 1,
  "repair_thresholds": {
    "factual_accuracy_min": 0.85,
    "tone_match_min": 0.75,
    "clarity_min": 0.70
  },
  "repair_history": [
    {
      "caption_key": "sarcastic",
      "attempt": 1,
      "repair_reason_codes": ["tone_mismatch"],
      "rewrite_hint_used": "Keep the same facts but add mild dry irony without adding new claims.",
      "before": {
        "text": "Original failed caption.",
        "scores": {
          "factual_accuracy": 0.90,
          "tone_match": 0.55,
          "clarity": 0.82
        },
        "issues": ["tone_mismatch"]
      },
      "after": {
        "text": "Repaired caption.",
        "scores": {
          "factual_accuracy": 0.90,
          "tone_match": 0.82,
          "clarity": 0.86
        },
        "issues": []
      },
      "accepted": true
    }
  ],
  "final_captions": {
    "formal": "unchanged passing caption",
    "sarcastic": "repaired caption",
    "humorous_tech": "unchanged passing caption",
    "humorous_non_tech": "unchanged passing caption"
  }
}
```

### Before/After Score Artifact

The demo should be able to show:

| Field | Meaning |
| --- | --- |
| `caption_key` | Which tone was repaired. |
| `attempt` | Always `1` unless scope changes later. |
| `repair_reason_codes` | C5 issue codes that triggered repair. |
| `before.text` | Original failed caption. |
| `before.scores` | C5 scores before repair. |
| `after.text` | Repaired caption. |
| `after.scores` | C5 scores after repair. |
| `accepted` | Whether repaired caption meets thresholds and does not introduce worse issues. |

## Repair Thresholds

Use C5 thresholds by default:

| Metric | Default threshold |
| --- | ---: |
| `factual_accuracy` | `0.85` |
| `tone_match` | `0.75` |
| `clarity` | `0.70` |

Repair is triggered when:

- C5 sets `repair_eligible: true`, and
- one or more scores are below threshold, or
- one or more repairable issue codes are present.

Repair should not run when:

- `scene_core_mismatch` is present
- `malformed_output` prevents reliable parsing
- `unsafe_or_private_reference` requires hard failure instead of rewrite
- the factual scene core itself is missing or malformed
- the caption already passes thresholds

## Repairable Issue Codes

Repair may target:

- `invented_fact`
- `missing_core_fact`
- `unsupported_inference_used`
- `uncertainty_overclaimed`
- `tone_mismatch`
- `tone_bleed`
- `unclear_joke`

Repair must not hide or bypass:

- `scene_core_mismatch`
- `malformed_output`
- `unsafe_or_private_reference`

## Service Boundary

- Repair consumes C3 factual scene core, C4 captions, and C5 evaluation.
- Repair does not mutate the factual scene core.
- Repair does not invent new facts.
- Repair does not run more than once per failed caption.
- Repair does not implement UI; C7 displays repair results later.

## Provider/API Boundary

If using Fireworks/Gemma, send only the failed caption, target tone, factual scene core, issue codes, and rewrite hint. Never send secrets, private docs, local paths, implementation pack contents, or private research material as model context.

Provider output is still draft text until re-evaluated.

## Prompt Contracts

The repair prompt must:

- require strict JSON or a single repaired caption field
- preserve the same `scene_core_id`
- preserve factual scene core
- target only the supplied issue codes
- use the supplied rewrite hint
- avoid new facts
- exclude unsupported inferences
- preserve uncertainty
- keep tone judge-friendly
- avoid private references and internal project jargon

## Tests

Add deterministic tests for:

- passing captions are not repaired
- failed repair-eligible captions are repaired exactly once
- `max_repair_attempts` is enforced
- repaired caption preserves `scene_core_id`
- repair history includes before/after text and scores
- repaired caption is re-evaluated
- accepted repair meets thresholds
- rejected repair does not replace the original unless policy explicitly allows it
- non-repairable issue codes stop repair
- repair does not use C3 `unsupported_inferences`
- public output contains no local paths, secrets, or private research terms

## README Update Requirements

Update README.md to reflect this gate's actual completed behavior. Do not document future gates as implemented.

The README must include current gate status, working commands only, known limitations, and planned gates as future work. If implemented, describe repair as one bounded repair pass, not a self-improving or autonomous loop.

## Acceptance Criteria

- Repair loop is bounded to one pass.
- Only repair-eligible captions are retried.
- Before/after scores are visible in structured output.
- Repaired captions are re-evaluated.
- Repair never changes the factual scene core.
- README does not overclaim autonomous improvement.

## Implementation Steps

1. Read `SKILL.md`.
2. Read `docs/README_GATE_POLICY.md`.
3. Read this execution document.
4. Inspect C3, C4, and C5 contracts.
5. Define or update repair history contract.
6. Add deterministic repair fixtures.
7. Implement only C6 repair behavior.
8. Run the suggested verification command.
9. Update README with actual completed behavior only.
10. Report changed files, test results, risks, and next gate.

## Reviewer Confidence Signal

A reviewer should be able to see which captions failed, why they failed, which repair hint was used, what changed, whether scores improved, and whether the repaired caption was accepted without any hidden loop.

## Benchmark / Evidence Artifact

This gate should leave behind at least one concrete artifact:

- passing repair-loop tests
- a sample repair history JSON fixture
- a before/after score fixture
- a rejected-repair fixture
- a no-repair-needed fixture
- a README note describing the one-pass repair limitation
- a documented blocker with exact provider, schema, or fixture issue

## Demo Commands

```bash
python -m pytest -k "repair or retry or evaluator or caption"
```

## Expected Output

A public-safe repair result JSON object that can drive C7 UI display.

## Failure Cases

- Repair invents new details
- Repair ignores evaluator issue codes
- Repair loops more than once
- Repair changes scene core
- Repair uses unsupported inferences
- Repair worsens factual accuracy
- Re-evaluation is skipped
- README claims autonomous self-improvement

## Stop/Gate Criteria

Stop if repair cannot be bounded, if before/after artifacts are absent, if scene core mutates, if repair starts handling UI, or if the loop becomes multi-agent/unbounded.

## Suggested Conventional Commit

```text
feat(captions): add bounded repair loop
```
