# Roadmap: C3 - Factual scene core JSON contract

    ## Execution Source

    `docs/execution/03-factual-scene-core.execution.md`

    ## Implementation Todos

    ### TODO C3-T01: Factual Scene Core Contract

    **Goal**  
    Define and implement the factual scene core contract that separates observed facts from style, jokes, and interpretation.

    **Source files to include in coding chat**  
    ```text
    scene core schema
Fireworks/Gemma adapter or stub
prompt templates
tests
    ```

    **Suggested test command**  
    ```bash
    python -m pytest -k 'scene_core or factual or schema'
    ```

    **Suggested conventional commit**  
    ```text
    feat(scene): add factual scene core contract
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
