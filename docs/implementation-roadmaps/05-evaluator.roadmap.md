# Roadmap: C5 - Accuracy/tone evaluator

    ## Execution Source

    `docs/execution/05-accuracy-tone-evaluator.execution.md`

    ## Implementation Todos

    ### TODO C5-T01: Accuracy and Tone Evaluator

    **Goal**  
    Add a judge-like evaluator that scores factual accuracy, tone match, and clarity for each caption.

    **Source files to include in coding chat**  
    ```text
    evaluator schema
evaluator prompt templates
scoring service
tests
    ```

    **Suggested test command**  
    ```bash
    python -m pytest -k 'evaluator or scoring or accuracy or tone'
    ```

    **Suggested conventional commit**  
    ```text
    feat(eval): score caption accuracy and tone
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
