# Execution: C7 - Judge-Visible Trace UI

## Goal

Build the smallest Streamlit demo UI that makes the Caption Compass quality path visible to a hackathon judge:

```text
video input -> timestamped evidence -> factual scene core -> four tonal bearings -> evaluator scores -> one bounded repair trace
```

The UI is not a general product dashboard. It is a trace viewer for the exact Track 2 judging surface.

## Why This Exists

Track 2 is judged on factual accuracy and tone match. C7 must make those qualities inspectable in under one minute. A judge should not need to infer that the system is careful; the UI should show the evidence chain, the stable factual core, the four style renderings, the evaluator result, and any one-pass repair.

C7 is where Caption Compass becomes visibly more credible than a basic caption generator.

## Source-of-Truth References

- `SKILL.md`
- `docs/README_GATE_POLICY.md`
- `docs/implementation-prompts/gate-c7.prompt.md`
- `docs/implementation-prompts/todos/c7-t01-streamlit-demo-ui.prompt.md`
- C2 frame evidence from `docs/execution/02-video-frame-ingestion.execution.md`
- C3 factual scene core from `docs/execution/03-factual-scene-core.execution.md`
- C4 four-tone captions from `docs/execution/04-four-tone-caption-generation.execution.md`
- C5 evaluator from `docs/execution/05-accuracy-tone-evaluator.execution.md`
- C6 repair trace from `docs/execution/06-retry-repair-loop.execution.md`

## Scope

- Add a minimal Streamlit UI or equivalent thin demo entrypoint.
- Let a user upload/select a video or run a safe sample fixture.
- Show timestamped frame evidence anchors.
- Show the style-free factual scene core.
- Show four captions side by side.
- Show evaluator scores and issue codes.
- Show one bounded repair trace when a repair occurs.
- Show provider/stub mode clearly.
- Surface missing API key, missing ffmpeg, invalid video, and malformed model output states clearly.
- Keep local paths, secrets, and private references out of public UI output and screenshots.
- Produce a screenshot/golden-path proof artifact.

## Out of Scope

- Auth
- User accounts
- Database-backed history
- Complex theming
- Analytics
- Multi-user review
- Human preference ranking
- New provider abstractions
- New captioning behavior beyond displaying prior gates
- Claims that the app is complete before C8

## Prerequisites

- C1 scaffold exists.
- C2-C6 service contracts exist or the UI can read deterministic sample artifacts for missing live provider behavior.
- `streamlit` or chosen UI dependency is available.
- Stub/test mode works without network.
- `SKILL.md` has been read.
- `docs/README_GATE_POLICY.md` has been read before README edits.

## Files/Packages Likely Touched

```text
app/main.py
app/ui.py
app/pipeline.py
app/contracts.py
app/providers.py
tests/test_ui.py
tests/test_pipeline_smoke.py
docs/artifacts/c7-demo-proof.md
README.md
```

Exact paths may differ if the C1 scaffold uses a different package layout. Keep the UI thin and align with the existing repo structure.

## Commands or UI Actions Added

Expected local UI command:

```bash
streamlit run app/main.py
```

Suggested verification command:

```bash
python -m pytest -k "ui or smoke or app or pipeline"
```

Suggested artifact check:

```bash
test -f docs/artifacts/c7-demo-proof.md
```

If a screenshot is captured, store it in a public-safe relative path such as:

```text
docs/artifacts/c7-demo-screenshot.png
```

Do not commit screenshots that reveal private files, local paths, secrets, unrelated browser tabs, or private work.

## Data Contracts

C7 should display existing contracts, not invent new semantics.

### Judge Trace View Model

The UI may assemble a view model equivalent to:

```json
{
  "mode": "stub-or-provider",
  "source_video_id": "stable-video-id",
  "trace_status": "complete",
  "evidence": {
    "sample_strategy": "bounded_uniform",
    "frames": [
      {
        "frame_id": "f001",
        "timestamp_seconds": 0.0,
        "image_ref": "artifacts/frames/f001.jpg"
      }
    ]
  },
  "scene_core": {
    "scene_core_id": "stable-scene-core-id",
    "summary": "style-free factual summary",
    "observed_entities": [],
    "observed_actions": [],
    "uncertainties": [],
    "unsupported_inferences": []
  },
  "captions": {
    "formal": {"text": "...", "tone": "formal"},
    "sarcastic": {"text": "...", "tone": "sarcastic"},
    "humorous_tech": {"text": "...", "tone": "humorous-tech"},
    "humorous_non_tech": {"text": "...", "tone": "humorous-non-tech"}
  },
  "evaluation": {
    "overall": {"passed": true, "repair_recommended": false},
    "evaluation": {}
  },
  "repair": {
    "max_repair_attempts": 1,
    "repair_history": [],
    "final_captions": {}
  },
  "warnings": []
}
```

### UI Section Requirements

The visible UI should have these sections, in this order unless there is a strong local design reason:

1. Input and mode status
2. Timestamped evidence
3. Factual scene core
4. Four tonal bearings
5. Accuracy/tone evaluation
6. Repair trace
7. Known limitations or warnings

## Service Boundary

- UI reads or invokes services from C2-C6.
- UI does not own video extraction, scene reasoning, caption generation, evaluation, or repair logic.
- UI does not mutate the factual scene core.
- UI does not hide provider errors.
- UI does not send secrets or private repo content to providers.
- UI may render sample artifacts in stub mode.

## Provider/API Boundary

- Real provider mode requires `FIREWORKS_API_KEY`.
- Stub mode must run without network.
- Missing key should be visible as a clear UI state, not a crash.
- Provider output remains draft until evaluation is displayed.
- The UI must not expose API keys, absolute local paths, private research material, or implementation-pack internals.

## Prompt Contracts

C7 should not introduce new core prompts. If a UI action calls provider-backed services, it must use existing C3-C6 prompt contracts.

Do not add UI-only prompt instructions that bypass:

- factual scene core separation
- unsupported inference handling
- tone rubrics
- evaluator issue taxonomy
- one-repair-pass discipline

## Tests

Add deterministic tests or smoke checks for:

- UI entrypoint imports without provider credentials
- sample fixture or stub trace renders/assembles successfully
- visible trace model includes evidence, scene core, captions, evaluation, and repair keys
- missing API key produces an explicit status or warning
- public UI output does not include secrets, absolute local paths, or private references
- README does not claim deployment/Docker readiness before C8

When full UI automation is too costly, test the view-model or pipeline function directly and document manual UI verification in `docs/artifacts/c7-demo-proof.md`.

## README Update Requirements

Update README.md to reflect this gate's actual completed behavior. Do not document future gates as implemented.

README claims must be backed by:

- `docs/artifacts/c7-demo-proof.md`
- a passing test or smoke command
- a working local UI command
- a public-safe screenshot only if captured

README must include:

- current gate status
- working UI command only if it works
- provider/stub mode limitations
- known UI limitations
- planned C8 Docker/submission work as planned, not implemented

## Acceptance Criteria

- A judge-visible trace can be rendered in stub mode.
- The UI shows evidence, factual core, four tones, evaluator scores, and repair trace or no-repair state.
- The UI makes provider/stub status clear.
- The UI stays thin and delegates behavior to services.
- A C7 demo proof artifact exists.
- README describes only verified C7 behavior.
- No private references, secrets, or absolute local paths appear in public artifacts.

## Implementation Steps

1. Read `SKILL.md`.
2. Read `docs/README_GATE_POLICY.md`.
3. Read this execution document.
4. Inspect C2-C6 contracts and sample artifacts.
5. Define the minimal trace view model if one does not already exist.
6. Add or update tests for trace assembly and public-safe output.
7. Implement the Streamlit UI as a thin layer.
8. Run the suggested verification command.
9. Run the UI locally if practical.
10. Create `docs/artifacts/c7-demo-proof.md`.
11. Capture a screenshot only if it is public-safe.
12. Update README conservatively.
13. Report changed files, test results, artifact path, and next gate.

## Reviewer Confidence Signal

A reviewer should be able to open the UI or artifact and understand:

- what video/sample was used
- which frame anchors were sampled
- what factual core was generated
- how the same facts became four tones
- how the evaluator scored accuracy and tone
- whether repair happened
- what command proves the gate
- what remains for C8

## Benchmark / Evidence Artifact

This gate must leave behind:

```text
docs/artifacts/c7-demo-proof.md
```

It must include:

- exact UI run command
- exact test/smoke command and status
- sample input used
- provider/stub mode used
- visible UI sections
- screenshot path if captured
- known UI limitations
- README sync summary

Optional artifact:

```text
docs/artifacts/c7-demo-screenshot.png
```

Only commit the screenshot if it is safe, small, and useful.

## Demo Commands

```bash
streamlit run app/main.py
python -m pytest -k "ui or smoke or app or pipeline"
test -f docs/artifacts/c7-demo-proof.md
```

## Expected Output

A public-safe demo UI and proof artifact that show the Caption Compass trace from input to evaluation/repair.

## Failure Cases

- UI hides evaluator or repair output
- UI only shows final captions
- UI crashes without Fireworks credentials
- UI leaks absolute local paths
- UI screenshots expose private files or browser tabs
- UI implies Docker/deployment readiness before C8
- UI adds new captioning behavior instead of displaying service outputs
- README claims future work as implemented

## Stop/Gate Criteria

Stop if the UI cannot show the trace, if the proof artifact cannot be produced, if public-safe boundaries weaken, or if implementation starts C8 submission/Docker work.

## Suggested Conventional Commit

```text
feat(ui): add judge-visible trace demo
```
