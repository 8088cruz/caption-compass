# Roadmap: C7 - Demo UI and golden path

    ## Execution Source

    `docs/execution/07-ui-demo-path.execution.md`

    ## Implementation Todos

    ### TODO C7-T01: Streamlit Demo UI

    **Goal**  
    Build a simple Streamlit golden path that shows upload, factual core, four captions, evaluator scores, and repair state.

    **Source files to include in coding chat**  
    ```text
    streamlit app
app services
sample outputs
tests optional
    ```

    **Suggested test command**  
    ```bash
    python -m pytest -k 'ui or smoke or app'
    ```

    **Suggested conventional commit**  
    ```text
    feat(ui): add Caption Compass demo path
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
