# Execution: C3 - Factual Scene Core JSON Contract

## Goal

Define and implement the factual scene core contract that separates observed facts from style, jokes, and interpretation.

## Why This Exists

Track 2 rewards factual accuracy and tone match. The safest implementation path is:

```text
timestamped frame evidence -> one style-free factual scene core -> four tone renderings
```

C3 is the boundary where visible evidence becomes a compact factual core. It must preserve uncertainty and block unsupported inference before any humorous or stylistic generation happens.

## Source-of-Truth References

- `SKILL.md`
- `docs/README_GATE_POLICY.md`
- `docs/implementation-prompts/gate-c3.prompt.md`
- `docs/implementation-prompts/todos/c3-t01-factual-scene-core-contract.prompt.md`
- C2 frame evidence packet from `docs/execution/02-video-frame-ingestion.execution.md`

## Scope

- Create a JSON contract for factual scene core.
- Consume timestamped frame evidence from C2.
- Include stable `scene_core_id`.
- Separate observed entities, actions, setting, visible text, optional audio notes, uncertainties, and unsupported inferences.
- Link factual claims to `frame_id` evidence when possible.
- Prevent style words, jokes, sarcasm, emotion inference, motive inference, and unsupported causality from entering the factual core.
- Allow stub/test mode without network.

## Out of Scope

- Four-tone rendering
- Evaluator scoring
- Retry/repair loop
- Fine-tuning
- Broad scene interpretation beyond visible/audible evidence

## Prerequisites

- C2 frame evidence packet exists.
- Provider adapter or deterministic stub exists.
- README gate policy has been read before README edits.

## Files/Packages Likely Touched

```text
app/contracts.py
app/scene_core.py
app/providers.py
tests/test_scene_core.py
README.md
```

## Commands or UI Actions Added

Suggested verification command:

```bash
python -m pytest -k "scene_core or factual or schema"
```

## Data Contracts

### Factual Scene Core

C3 should implement this contract or a clearly equivalent typed model:

```json
{
  "scene_core_id": "stable-scene-core-id",
  "source_video_id": "stable-video-id",
  "summary": "short factual description without style",
  "observed_entities": [
    {
      "label": "person",
      "evidence_frame_ids": ["f001"],
      "confidence": "medium"
    }
  ],
  "observed_actions": [
    {
      "label": "walks across the room",
      "evidence_frame_ids": ["f001", "f002"],
      "confidence": "medium"
    }
  ],
  "setting": {
    "label": "indoor room",
    "evidence_frame_ids": ["f001"],
    "confidence": "low"
  },
  "visible_text": [
    {
      "text": "visible sign text",
      "evidence_frame_ids": ["f003"],
      "confidence": "medium"
    }
  ],
  "audio_notes": [],
  "uncertainties": [
    {
      "description": "small background object is unclear",
      "evidence_frame_ids": ["f004"]
    }
  ],
  "unsupported_inferences": [
    {
      "claim": "person is frustrated",
      "reason": "emotion is not directly established by the sampled frames",
      "handling": "omit from factual core and captions unless later evidence supports it"
    }
  ]
}
```

### Unsupported Inference Handling

Unsupported inferences are not facts. They are rejected or quarantined claims that should not be used by C4 unless converted into a supported observation.

Examples:

| Unsupported claim | Safer handling |
| --- | --- |
| `the person is angry` | `the person gestures quickly` if visible |
| `the object is expensive` | `a shiny object is visible` if supported |
| `the scene is a failure` | describe visible actions only |
| `the speaker is confused` | use transcript or mark uncertainty |

## Service Boundary

- Scene core construction consumes C2 frame evidence.
- Scene core construction returns facts, uncertainties, and rejected inferences.
- It does not create jokes, tone, marketing language, final captions, evaluator scores, or repair output.
- It must keep local file paths out of public JSON and screenshots.

## Provider/API Boundary

If using Fireworks/Gemma, send only video-derived evidence and public-safe task instructions. Never send secrets, private docs, local paths, implementation pack contents, or private research material as model context.

## Prompt Contracts

The scene-core prompt must:

- request observed facts only
- require strict JSON
- require evidence frame IDs for supported claims when available
- mark ambiguous facts as uncertainty
- place rejected guesses in `unsupported_inferences`
- prohibit style, humor, sarcasm, emotion inference, motive inference, identity inference, and unsupported causality
- avoid internal project jargon in model-facing instructions

## Tests

Add deterministic tests for:

- required keys exist
- `scene_core_id` is stable for the same fixture input
- observed facts can reference C2 `frame_id` values
- unsupported claims are placed in `unsupported_inferences` or omitted
- style/joke language is absent from factual core
- public output does not include absolute local paths, secrets, or private research terms
- malformed provider JSON fails safely

## README Update Requirements

Update README.md to reflect this gate's actual completed behavior. Do not document future gates as implemented.

The README must include current gate status, working commands only, known limitations, and planned gates as future work.

## Acceptance Criteria

- Factual core can be produced in stub mode.
- Factual core is separate from captions.
- Factual claims can point back to frame evidence where possible.
- Unsupported inferences are blocked from becoming caption facts.
- Uncertainty is explicit.

## Reviewer Confidence Signal

A reviewer should be able to see exactly how the factual core was built from frame evidence, which claims are supported, which claims are uncertain or unsupported, how tone/style was excluded, how the gate was verified, and what remains deferred to C4 or later.

## Benchmark / Evidence Artifact

This gate should leave behind at least one concrete artifact:

- passing scene-core contract tests
- a sample factual scene core JSON fixture
- a malformed-provider-output failure fixture
- a sample `unsupported_inferences` case
- a documented blocker with the exact provider, schema, or fixture issue

## Demo Commands

```bash
python -m pytest -k "scene_core or factual or schema"
```

## Expected Output

A style-free factual scene core that downstream caption generation can reuse without inventing facts.

## Failure Cases

- Scene core invents facts
- Scene core includes jokes or sarcasm
- Ambiguous evidence is overclaimed
- Emotion or motive is inferred without support
- Unsupported inferences leak into captions
- Provider output is malformed JSON

## Stop/Gate Criteria

Stop if implementation cannot keep factual core and tone generation separate, or if unsupported inference handling is removed.

## Suggested Conventional Commit

```text
feat(scene): add factual scene core contract
```
