# Roadmap: C8 - Docker, README, slides/video script, submission readiness

    ## Execution Source

    `docs/execution/08-docker-readme-submission.execution.md`

    ## Implementation Todos

    ### TODO C8-T01: Docker, README, and Submission Readiness

    **Goal**  
    Prepare the public repo for hackathon submission with Docker, README, demo instructions, slide outline, and video script.

    **Source files to include in coding chat**  
    ```text
    Dockerfile
README.md
LICENSE
.env.example
submission docs
smoke tests
    ```

    **Suggested test command**  
    ```bash
    docker build -t caption-compass . && python -m pytest
    ```

    **Suggested conventional commit**  
    ```text
    docs(submission): prepare Caption Compass hackathon submission
    ```

    ## Architecture Guardrails

    - Factual scene core stays separate from tone rendering.
    - UI stays thin; services own behavior.
    - Provider/API calls stay behind a small adapter.
    - Stub/test mode must work without network where practical.
    - Public outputs must not expose secrets, local paths, or private research references.
    - Do not implement future gates.
    - Tests should be deterministic where possible.
    - Fireworks/Gemma integration must have a stub/test path where practical.
    - README must lag implementation, never lead it.

    ## README Sync Requirement

    Update README.md to reflect this gate's actual completed behavior. Do not document future gates as implemented.

    ## Stop/Defer Rules

    Stop if implementation crosses future-gate scope, adds private/proprietary references, claims unimplemented behavior, or makes the project harder to run for the hackathon judges.
