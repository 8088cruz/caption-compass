# Roadmap: Caption Compass Overview

    ## Execution Source

    `docs/execution/00-caption-compass-overview.execution.md`

    ## Implementation Todos

    - C0: Scope, IP boundary, judging target -> `c0-t01-project-scope-and-ip-boundary.prompt.md`
- C1: Public repo/app scaffold -> `c1-t01-app-scaffold.prompt.md`
- C2: Video upload and frame extraction -> `c2-t01-video-upload-and-frame-sampling.prompt.md`
- C3: Factual scene core JSON contract -> `c3-t01-factual-scene-core-contract.prompt.md`
- C4: Four-tone caption generation -> `c4-t01-four-tone-caption-contract.prompt.md`
- C5: Accuracy/tone evaluator -> `c5-t01-accuracy-tone-evaluator.prompt.md`
- C6: Retry/repair loop -> `c6-t01-retry-repair-loop.prompt.md`
- C7: Demo UI and golden path -> `c7-t01-streamlit-demo-ui.prompt.md`
- C8: Docker, README, slides/video script, submission readiness -> `c8-t01-docker-readme-submission.prompt.md`

    ## Goal

    Build Caption Compass gate by gate, preserving a simple, runnable, public-safe hackathon submission.

    ## Source Files To Include In Coding Chat

    ```text
    current repo tree
    README.md if present
    relevant execution doc
    relevant todo prompt
    tests for current gate
    ```

    ## Suggested Test Command

    ```bash
    python -m pytest
    ```

    ## Suggested Conventional Commit

    Use the commit suggested by the current gate.

    ## Architecture Guardrails

    - One factual scene core.
    - Four required tones only.
    - Evaluator scores accuracy and tone.
    - README is conservative after every gate.
    - Stub/test mode remains possible.
    - No private research references.

    ## README Sync Requirement

    Update README.md to reflect this gate's actual completed behavior. Do not document future gates as implemented.

    ## Stop/Defer Rules

    Defer anything that does not help Track 2 accuracy, tone, Gemma/Fireworks usage, demo clarity, Docker runnability, or submission readiness.
