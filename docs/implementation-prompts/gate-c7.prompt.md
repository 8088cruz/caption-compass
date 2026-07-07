# Gate Prompt: C7

## Purpose

Implement Gate C7 only: Judge-Visible Trace UI.

C7 must make the Caption Compass pipeline inspectable for judges:

```text
video input -> timestamped evidence -> factual scene core -> four tonal bearings -> evaluator scores -> one bounded repair trace
```

## Todos Included

- C7-T01: Streamlit Demo UI

## Strict Non-Scope

- Do not expose private research material, private repo paths, unreleased architecture, or long-term strategy.
- Do not mention private research systems, internal project names, private repo paths, unpublished architecture, or long-term product strategy in public repo content.
- Do not quote copyrighted source material.
- Do not add features outside the current gate.
- Do not claim the project is complete before C8.
- Do not implement future gates.
- Do not add Docker/submission work; that belongs to C8.
- Do not add optional audio/transcription unless already implemented and required by prior gates.
- Do not add auth, database, history, analytics, or multi-user behavior.
- Do not move core pipeline logic into Streamlit widgets.

## Concrete Artifact Requirement

C7 must produce:

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

Optional screenshot:

```text
docs/artifacts/c7-demo-screenshot.png
```

Only commit a screenshot if it is public-safe, useful, and does not expose private browser tabs, local paths, secrets, or unrelated work.

## README Sync Evidence Rule

Update README.md to reflect this gate's actual completed behavior. Do not document future gates as implemented.

README claims must be backed by at least one of:

- `docs/artifacts/c7-demo-proof.md`
- a passing test/smoke command
- a working UI command
- a committed public-safe screenshot or trace fixture

If the C7 proof artifact cannot be produced, do not mark C7 complete in README.

## Implementation Sequence

1. Read `SKILL.md`.
2. Read `docs/README_GATE_POLICY.md`.
3. Read `docs/execution/07-ui-demo-path.execution.md`.
4. Read `docs/implementation-prompts/todos/c7-t01-streamlit-demo-ui.prompt.md`.
5. Inspect current repo state and C2-C6 artifacts/contracts.
6. Add or update trace-view tests before UI work where practical.
7. Implement only the thin C7 UI path.
8. Run the suggested command.
9. Run the UI command if practical.
10. Produce `docs/artifacts/c7-demo-proof.md`.
11. Capture a screenshot only if safe and useful.
12. Update README from verified behavior only.
13. Report changed files, tests, artifact, README sync, risks, and commit suggestion.

## Commit Sequence

- `feat(ui): add judge-visible trace demo`

## Stop Criteria

Stop if:

- the UI cannot show the trace sections
- implementation crosses into C8
- core behavior is moved into UI widgets
- public-safe boundaries weaken
- a required artifact cannot be produced
- README claims behavior not proven by an artifact, test, or working command
