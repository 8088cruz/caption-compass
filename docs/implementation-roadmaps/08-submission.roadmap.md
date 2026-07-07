# Roadmap: C8 - Runnable Submission Artifact

## Execution Source

`docs/execution/08-docker-readme-submission.execution.md`

## Implementation Todos

### TODO C8-T01: Docker README Submission

**Goal**  
Prepare the public repo for hackathon submission with verified local commands, Docker/container instructions, README accuracy, demo video script, slide outline, and a readiness checklist.

**Concrete artifact**  

```text
docs/artifacts/c8-submission-readiness.md
```

**Source files to include in coding chat**  

```text
SKILL.md
docs/README_GATE_POLICY.md
docs/execution/08-docker-readme-submission.execution.md
docs/implementation-prompts/todos/c8-t01-docker-readme-submission.prompt.md
docs/artifacts/c7-demo-proof.md
Dockerfile optional
.dockerignore optional
.env.example optional
LICENSE optional
README.md
docs/submission/ optional
tests/ optional
```

**Suggested test command**  

```bash
python -m pytest
```

**Suggested Docker commands**  

```bash
docker build -t caption-compass .
docker run --env-file .env -p 8501:8501 caption-compass
```

Use a documented stub-mode Docker command if `.env` is not required.

**Suggested artifact check**  

```bash
test -f docs/artifacts/c8-submission-readiness.md
```

**Suggested conventional commit**  

```text
docs(submission): add runnable submission artifact
```

## Architecture Guardrails

- C8 packages and documents existing behavior.
- Do not add new captioning, evaluator, repair, or UI features.
- README must lag implementation, never lead it.
- Docker commands must be verified or blockers must be documented.
- Provider/API requirements must be explicit.
- Stub/test mode instructions must be honest.
- Gemma usage must only be claimed if implemented and visible.
- Public files must not expose secrets, absolute local paths, private references, or implementation-pack internals.
- Known limitations must be visible.

## README Sync Requirement

Update README.md to reflect this gate's actual completed behavior. Do not document future gates as implemented.

README must include:

- project summary
- current implementation status
- local setup/run commands
- test command
- Docker build/run command and status
- Fireworks/Gemma setup
- stub mode instructions
- demo URL or deployment status
- known limitations
- artifact list
- license
- submission material links

If C8 readiness artifact is missing, do not mark C8 complete.

## Stop/Defer Rules

Stop if:

- Docker readiness cannot be honestly documented
- README commands do not match working commands
- private references or local-only paths appear
- submission docs overclaim implementation
- implementation starts new product work instead of packaging
