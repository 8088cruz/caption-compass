# Gate Prompt: C2

    ## Purpose

    Implement Gate C2 only: Video upload and frame extraction.

    ## Todos Included

    - C2-T01: Video Upload and Frame Sampling

    ## Strict Non-Scope

    - Do not expose private research material, private repo paths, unreleased architecture, or long-term strategy.
- Do not mention private Corpus, Signal, CGS, KGL, or Arachne internals in public repo content.
- Do not quote copyrighted source material.
- Do not add features outside the current gate.
- Do not claim the project is complete before C8.
    - Do not implement future gates.
    - Do not add optional audio/transcription unless this gate explicitly requires it.
    - Do not add complex architecture when a simple hackathon-ready path is enough.

    ## Implementation Sequence

    1. Read the execution source for this gate.
    2. Inspect the current repo state.
    3. Add tests or verification first where practical.
    4. Implement only the current todo.
    5. Run the suggested command.
    6. Update README.md to reflect this gate's actual completed behavior. Do not document future gates as implemented.
    7. Report changed files, tests, risks, and commit suggestion.

    ## Commit Sequence

    - `feat(video): add frame sampling pipeline`

    ## Stop Criteria

    Stop if the implementation crosses future-gate scope, weakens public-safe boundaries, includes private references, or makes README claim behavior that is not implemented.
