# Gate Prompt: C8

## Purpose

Implement Gate C8 only: Runnable Submission Artifact.

C8 packages the app for hackathon submission:

```text
public repo -> install/run instructions -> Docker/container run -> demo trace -> submission checklist
```

## Todos Included

- C8-T01: Docker README Submission

## Strict Non-Scope

- Do not expose private research material, private repo paths, unreleased architecture, or long-term strategy.
- Do not mention private research systems, internal project names, private repo paths, unpublished architecture, or long-term product strategy in public repo content.
- Do not quote copyrighted source material.
- Do not add features outside the current gate.
- Do not claim the project is complete unless C8 acceptance criteria are actually met.
- Do not implement new captioning, evaluator, repair, or UI behavior.
- Do not add fine-tuning unless already implemented and verified.
- Do not claim Gemma usage unless it is implemented and visible.
- Do not claim Docker readiness without a verified command or documented blocker.
- Do not add a broad post-hackathon roadmap.

## Concrete Artifact Requirement

C8 must produce:

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

## README Sync Evidence Rule

Update README.md to reflect this gate's actual completed behavior. Do not document future gates as implemented.

README claims must be backed by at least one of:

- `docs/artifacts/c8-submission-readiness.md`
- a passing test command
- a verified local run command
- a verified Docker build/run command
- a documented blocker with the exact command attempted

If Docker cannot be verified in the environment, README must say so clearly and the readiness artifact must include the blocker.

## Implementation Sequence

1. Read `SKILL.md`.
2. Read `docs/README_GATE_POLICY.md`.
3. Read `docs/execution/08-docker-readme-submission.execution.md`.
4. Read `docs/implementation-prompts/todos/c8-t01-docker-readme-submission.prompt.md`.
5. Inspect C7 proof artifact and current README.
6. Verify tests and local run command.
7. Add or update Dockerfile, `.dockerignore`, and `.env.example`.
8. Add or verify MIT `LICENSE`.
9. Add demo video script and slide deck outline.
10. Run Docker build/run checks where practical.
11. Produce `docs/artifacts/c8-submission-readiness.md`.
12. Update README from verified behavior only.
13. Report changed files, tests, Docker status, artifact, README sync, risks, and commit suggestion.

## Commit Sequence

- `docs(submission): add runnable submission artifact`

## Stop Criteria

Stop if:

- Docker/readiness status cannot be honestly documented
- README commands are unverified or inaccurate
- submission docs claim unimplemented features
- private references or local-only paths appear
- implementation starts adding new product features instead of packaging the app
