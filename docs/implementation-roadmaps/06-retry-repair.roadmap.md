# Roadmap: C6 - Retry/repair loop

    ## Execution Source

    `docs/execution/06-retry-repair-loop.execution.md`

    ## Implementation Todos

    ### TODO C6-T01: Retry and Repair Loop

    **Goal**  
    Implement one bounded repair pass for captions that fail accuracy, tone, or clarity thresholds.

    **Source files to include in coding chat**  
    ```text
    caption service
evaluator service
repair prompt templates
tests
    ```

    **Suggested test command**  
    ```bash
    python -m pytest -k 'repair or retry or evaluator or caption'
    ```

    **Suggested conventional commit**  
    ```text
    feat(captions): add bounded repair loop
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
