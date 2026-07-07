# Coding Prompt: C8-T01 - Docker README Submission

You are implementing exactly one Caption Compass todo.

## Non-Negotiable Constraints

- Do not expose private research material, private repo paths, unreleased architecture, or long-term strategy.
- Do not mention private research systems, internal project names, private repo paths, unpublished architecture, or long-term product strategy in public repo content.
- Do not quote copyrighted source material.
- Do not add features outside the current gate.
- Do not claim the project is complete before C8.
- Do not implement future todos.
- Keep the project optimized for Track 2 factual accuracy and tone judging.
- Keep factual scene core separate from tone generation.
- Keep all generated outputs LLM-judge-friendly.
- Use Gemma/Fireworks meaningfully only where this gate requires provider behavior.
- Prefer a one-day runnable implementation over clever architecture.
- Keep README synchronized with actual completed behavior.
- Produce the concrete artifact required by this prompt before calling the todo complete.
- README updates must cite only working behavior proven by the concrete artifact, passing tests, or verified command output.

## Execution Todo

Docker README Submission

## Execution Source

`docs/execution/08-docker-readme-submission.execution.md`

Read this execution source before editing files. Treat it as the source of truth for scope, contracts, acceptance criteria, and stop criteria.

## Current Repo Files to Include

```text
Dockerfile
README.md
submission docs
slides/video script optional
tests
```

Also include current test output, if any.

If the repo is still empty, include:

```text
git status
find . -maxdepth 3 -type f | sort
```

## Context Summary

Caption Compass is a public hackathon project for `8088cruz/caption-compass`.

Product flow:

```text
video clip -> timestamped evidence -> factual scene core -> four tonal bearings -> accuracy/tone evaluator -> one bounded repair pass -> demo UI
```

Required tones:

```text
formal
sarcastic
humorous-tech
humorous-non-tech
```

This todo must improve the project while preserving public-safe boundaries, judge-visible evidence, and README gate sync.

## Goal

Make the project runnable and submission-ready without overstating capability.

## Required Behavior

- Add or verify Docker/container instructions.
- Ensure README includes only working local and container commands.
- Add concise demo/video script and slide outline if required by the execution doc.
- Include limitations, API key requirements, and current artifact evidence.
- Keep all public text free of private references.

## Concrete Artifact Requirement

Produce a submission readiness artifact:

```text
docs/artifacts/c8-submission-readiness.md
```

It must include:

- local run command and status
- Docker build/run command and status
- test command and status
- demo URL status or deployment notes
- README status
- known limitations
- final submission checklist

The artifact must be committed when it is small, deterministic, public-safe, and useful for review. If the artifact is generated and should not be committed, commit a small markdown pointer that explains exactly how to reproduce it and where it is written locally.

## README Sync Evidence Rule

Update README.md to reflect this gate's actual completed behavior. Do not document future gates as implemented.

README claims must be backed by at least one of:

- the concrete artifact from this prompt
- a passing test command
- a verified run command
- a committed sample fixture or schema

README must include:

- current gate status
- working commands only
- known limitations
- planned gates clearly marked as planned
- artifact path or verification command for this gate

If the artifact cannot be produced, do not mark the gate complete in README.

## Design Constraints

- Optimize for a judge reading output quickly.
- Prefer explicit JSON contracts over loose prose between pipeline stages.
- Prefer boring, testable services over broad abstractions.
- Keep provider prompts short, direct, and tied to the current data contract.
- Keep fallback/stub behavior available so tests can run without network.
- Keep artifacts small enough to inspect in a review.
- Do not make README claims that cannot be reproduced from the current repo.

## Suggested CLI or UI Behavior

Use the simplest behavior that proves the gate. Prefer explicit local commands, JSON outputs, and Streamlit UI states that judges can understand quickly.

## Tests to Add

- Add deterministic tests for this gate where practical.
- Test malformed or missing inputs.
- Test public-safe output shape.
- Test that future-gate behavior is not claimed or required.
- Test or verify that the concrete artifact is produced, valid, and public-safe.

Suggested command:

```bash
python -m pytest
```

## Acceptance Criteria

- This todo is complete and no future todo is implemented.
- The concrete artifact exists or a committed reproduction note exists.
- Tests or verification command pass, or a concrete blocker is reported.
- README is updated conservatively and references only verified behavior.
- Public-safe boundary is preserved.
- Output remains optimized for factual accuracy and tone separation.
- No private references, local-only private paths, or unsupported claims are introduced.

## README Update Requirement

Update README.md to reflect this gate's actual completed behavior. Do not document future gates as implemented.

Use conservative language:

- say `implemented` only for behavior proven by this gate
- say `planned` for future behavior
- include known limitations
- include only commands that actually work
- include the concrete artifact path or verification command

## Out of Scope

New core features
Architecture rewrites
Fine-tuning unless already implemented
Claims about winning or benchmark superiority

## Expected Files Changed

```text
Dockerfile/container config, README update, submission docs, tests or smoke command, docs/artifacts/c8-submission-readiness.md
```

Infer exact paths from the current repo structure. Keep changes minimal.

## Implementation Instructions

1. Inspect current files.
2. Read `SKILL.md` and `docs/README_GATE_POLICY.md`.
3. Read `docs/execution/08-docker-readme-submission.execution.md`.
4. Add or update tests/verification for this todo.
5. Implement only this todo.
6. Produce the concrete artifact.
7. Update README conservatively from artifact/test evidence.
8. Run the suggested command.
9. Report risks and any deferred work.

## Commands to Run

```bash
python -m pytest
```

Also run a focused artifact check, such as:

```bash
test -f <artifact-path>
```

Replace `<artifact-path>` with the path required by this prompt.

## Expected Output

Tests pass or the blocker is clearly reported. The concrete artifact is present, valid, public-safe, judge-friendly, and free of secrets or private references.

## Failure Cases

- Missing dependency
- Missing Fireworks key
- Invalid video input
- Malformed model JSON
- Caption invents facts
- Tone separation is weak
- README gets ahead of implementation
- Scope drifts into future gates
- Concrete artifact is missing, stale, or not reproducible
- Artifact contains private references, local-only paths, or unsupported claims

## Required Response Format

Return:

1. changed files
2. patch/full contents
3. concrete artifact produced
4. README sync summary
5. tests added
6. tests to run
7. expected output
8. architecture violations found
9. deferred work or blockers
10. suggested conventional commit: `docs(submission): prepare runnable hackathon submission`
