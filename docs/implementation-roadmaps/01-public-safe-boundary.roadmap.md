# Roadmap: C0 - Scope, IP boundary, judging target

    ## Execution Source

    `docs/execution/01-public-safe-product-boundary.execution.md`

    ## Implementation Todos

    ### TODO C0-T01: Project Scope and IP Boundary

    **Goal**  
    Lock the public-safe scope, Track 2 judging target, repository assumptions, and README gate policy before coding.

    **Source files to include in coding chat**  
    ```text
    README.md
LICENSE optional
.github optional
docs/README_GATE_POLICY.md optional
    ```

    **Suggested test command**  
    ```bash
    true
    ```

    **Suggested conventional commit**  
    ```text
    docs(scope): lock Caption Compass public-safe boundary
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
