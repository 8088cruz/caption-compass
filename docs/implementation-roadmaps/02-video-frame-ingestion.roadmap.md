# Roadmap: C2 - Video upload and frame extraction

    ## Execution Source

    `docs/execution/02-video-frame-ingestion.execution.md`

    ## Implementation Todos

    ### TODO C2-T01: Video Upload and Frame Sampling

    **Goal**  
    Implement local video file acceptance and deterministic frame sampling suitable for 30 second to 2 minute clips.

    **Source files to include in coding chat**  
    ```text
    app video modules
ffmpeg wrapper
sample fixtures
tests
    ```

    **Suggested test command**  
    ```bash
    python -m pytest -k 'video or frame or sampling'
    ```

    **Suggested conventional commit**  
    ```text
    feat(video): add frame sampling pipeline
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
