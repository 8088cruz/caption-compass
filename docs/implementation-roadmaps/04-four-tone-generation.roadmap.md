# Roadmap: C4 - Four-tone caption generation

    ## Execution Source

    `docs/execution/04-four-tone-caption-generation.execution.md`

    ## Implementation Todos

    ### TODO C4-T01: Four-Tone Caption Contract

    **Goal**  
    Generate exactly four captions from the same factual scene core: formal, sarcastic, humorous-tech, and humorous-non-tech.

    **Source files to include in coding chat**  
    ```text
    caption schema
caption prompt templates
Fireworks/Gemma adapter or stub
tests
    ```

    **Suggested test command**  
    ```bash
    python -m pytest -k 'caption or tone or style'
    ```

    **Suggested conventional commit**  
    ```text
    feat(captions): generate four judged tones
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
