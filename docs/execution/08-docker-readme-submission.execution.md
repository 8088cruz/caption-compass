# Execution: C8 - Runnable Submission Artifact

## Goal

Prepare Caption Compass for hackathon submission with a runnable container, honest README, demo materials, and a concrete readiness artifact.

C8 is complete only when a judge can clone the public repo, follow the README, run the app, and understand what is implemented.

## Why This Exists

The hackathon requires a public repo, runnable instructions, containerization, demo URL or app platform details, video presentation, and slide presentation. C8 turns the implementation into a submission artifact without adding new core behavior.

This gate should prove:

```text
public repo -> install/run instructions -> Docker/container run -> demo trace -> submission checklist
```

The final README must be accurate, not aspirational.

## Source-of-Truth References

- `SKILL.md`
- `docs/README_GATE_POLICY.md`
- `docs/implementation-prompts/gate-c8.prompt.md`
- `docs/implementation-prompts/todos/c8-t01-docker-readme-submission.prompt.md`
- C7 demo proof from `docs/execution/07-ui-demo-path.execution.md`
- Current public repository: `8088cruz/caption-compass`

## Scope

- Add or verify `Dockerfile`.
- Add or verify `.dockerignore` when useful.
- Add or verify `.env.example`.
- Add or verify `LICENSE` for MIT compliance.
- Make README describe only implemented behavior.
- Include working local run command.
- Include working Docker build/run commands.
- Include Fireworks/Gemma setup instructions honestly.
- Include stub/test mode instructions.
- Include demo URL status or deployment notes.
- Add concise demo video script.
- Add concise slide deck outline.
- Add final submission checklist.
- Produce `docs/artifacts/c8-submission-readiness.md`.

## Out of Scope

- New captioning features
- New evaluator or repair behavior
- New provider abstractions
- Fine-tuning unless already implemented and verified
- Major UI redesign
- Auth, database, multi-user features
- Benchmark superiority claims
- Claims that evaluator scores prove truth
- Post-hackathon roadmap beyond a concise planned section

## Prerequisites

- C7 demo path exists or a blocker is documented.
- Tests or smoke checks exist.
- README gate policy has been read.
- Stub/test mode works without network or its blocker is explicit.
- Provider mode has clear environment variable instructions.

## Files/Packages Likely Touched

```text
Dockerfile
.dockerignore
.env.example
LICENSE
README.md
docs/submission/demo-video-script.md
docs/submission/slide-deck-outline.md
docs/artifacts/c8-submission-readiness.md
tests/
```

Exact paths may differ if the repo has established equivalents. Keep changes minimal.

## Commands or UI Actions Added

Expected local run:

```bash
streamlit run app/main.py
```

Expected tests:

```bash
python -m pytest
```

Expected Docker build:

```bash
docker build -t caption-compass .
```

Expected Docker run:

```bash
docker run --env-file .env -p 8501:8501 caption-compass
```

If `.env` is not required for stub mode, provide a stub-mode Docker command as well.

## Data Contracts

C8 does not change data contracts. It must preserve and document the existing contracts:

- C2 frame evidence packet
- C3 factual scene core
- C4 four-tone caption set
- C5 evaluation result
- C6 repair result
- C7 trace view model

README examples should use committed, public-safe sample artifacts where possible.

## Service Boundary

- C8 packages and documents the existing app.
- C8 must not move core logic into Docker or README scripts.
- C8 must not bypass tests.
- C8 must not hide known provider/API requirements.
- C8 must not use private assets or local-only paths in submission materials.

## Provider/API Boundary

README and `.env.example` must state:

- `FIREWORKS_API_KEY` is required for real provider mode.
- Stub/test mode can run without network if implemented.
- API keys must not be committed.
- Provider behavior is model-assisted and may vary.
- Gemma usage should be described only if actually implemented and visible.

Do not claim Gemma prize alignment unless Gemma is meaningfully used in captioning, evaluation, repair, or a clearly documented provider mode.

## Prompt Contracts

C8 should not introduce new prompt behavior.

Submission docs may summarize:

- factual scene core separation
- four tone generation
- evaluator issue taxonomy
- one repair pass

They must not include private references, hidden context, source-book quotes, or internal system names.

## Tests

Add or verify:

- `python -m pytest`
- Docker build succeeds or blocker is documented
- Docker run command is documented and smoke-tested when practical
- README command examples match actual commands
- `.env.example` exists if provider mode exists
- public artifacts contain no secrets, absolute local paths, or private references
- C8 readiness artifact exists

If Docker cannot run in the current environment, document the exact command attempted and blocker in `docs/artifacts/c8-submission-readiness.md`.

## README Update Requirements

Update README.md to reflect this gate's actual completed behavior. Do not document future gates as implemented.

README must include:

- project summary
- current implementation status
- local setup
- local run command
- test command
- Docker build/run command
- Fireworks/Gemma setup
- stub mode instructions
- demo URL or deployment status
- known limitations
- artifact list
- license
- submission materials links

README must not:

- claim unimplemented provider mode
- claim Docker works if it was not verified or a blocker is not documented
- claim evaluator proof of correctness
- claim fine-tuning if not implemented
- include private references or local-only paths

## Acceptance Criteria

- README is accurate and runnable.
- Dockerfile exists and build/run status is documented.
- `.env.example` exists if provider mode needs environment variables.
- MIT license exists or is explicitly confirmed.
- Demo video script exists.
- Slide deck outline exists.
- C8 submission readiness artifact exists.
- Known limitations are listed.
- No private references, secrets, absolute local paths, or unsupported claims appear in public docs.

## Implementation Steps

1. Read `SKILL.md`.
2. Read `docs/README_GATE_POLICY.md`.
3. Read this execution document.
4. Inspect C7 proof artifact and current README.
5. Verify local test command.
6. Add or update Dockerfile and `.dockerignore`.
7. Add or update `.env.example`.
8. Add or verify MIT `LICENSE`.
9. Add demo video script.
10. Add slide deck outline.
11. Run Docker build/run checks where practical.
12. Create `docs/artifacts/c8-submission-readiness.md`.
13. Update README from verified behavior only.
14. Report changed files, test results, Docker status, artifact path, and submission gaps.

## Reviewer Confidence Signal

A reviewer should be able to see:

- exact commands to run
- whether commands were verified
- Docker readiness
- provider/stub mode status
- demo materials
- submission checklist
- known limitations
- no public/private boundary leakage

## Benchmark / Evidence Artifact

This gate must leave behind:

```text
docs/artifacts/c8-submission-readiness.md
```

It must include:

- local run command and status
- test command and status
- Docker build command and status
- Docker run command and status
- demo URL status or deployment notes
- Fireworks/Gemma status
- README status
- license status
- demo video script path
- slide deck outline path
- known limitations
- final submission checklist
- unresolved blockers

## Demo Commands

```bash
python -m pytest
docker build -t caption-compass .
docker run --env-file .env -p 8501:8501 caption-compass
test -f docs/artifacts/c8-submission-readiness.md
```

Use an alternate documented stub-mode Docker command if `.env` is unnecessary for stub mode.

## Expected Output

A public, MIT-compliant, runnable hackathon submission package with accurate README and submission materials.

## Failure Cases

- Docker build fails and blocker is not documented
- README commands do not work
- README claims future behavior
- Demo script claims unimplemented features
- Gemma usage is claimed but not implemented
- API key guidance is missing
- Known limitations are hidden
- Public files leak local paths, secrets, or private references

## Stop/Gate Criteria

Stop if Docker/readiness cannot be honestly documented, if README starts making unsupported claims, if private references appear, or if implementation starts adding new product features instead of packaging the app.

## Suggested Conventional Commit

```text
docs(submission): add runnable submission artifact
```
