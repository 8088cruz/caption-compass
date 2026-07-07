# Coding Prompt: C2-T01 - Video Upload and Frame Sampling

    You are implementing exactly one Caption Compass todo.

    ## Non-Negotiable Constraints

    - Do not expose private research material, private repo paths, unreleased architecture, or long-term strategy.
- Do not mention private Corpus, Signal, CGS, KGL, or Arachne internals in public repo content.
- Do not quote copyrighted source material.
- Do not add features outside the current gate.
- Do not claim the project is complete before C8.
    - Do not implement future todos.
    - Keep the project optimized for Track 2 factual accuracy and tone judging.
    - Keep factual scene core separate from tone generation.
    - Keep all generated outputs LLM-judge-friendly.
    - Use Gemma/Fireworks meaningfully only where this gate requires provider behavior.
    - Prefer a one-day runnable implementation over clever architecture.
    - Keep README synchronized with actual completed behavior.

    ## Execution Todo

    Video Upload and Frame Sampling

    ## Execution Source

    `docs/execution/02-video-frame-ingestion.execution.md`

    ## Current Repo Files to Include

    ```text
    app video modules
ffmpeg wrapper
sample fixtures
tests
    ```

    Also include current test output, if any.

    If the repo is still empty, include:

    ```text
    git status
    find . -maxdepth 3 -type f | sort
    ```

    ## Context Summary

    Caption Compass is a public hackathon project for `8088cruz/caption-compass`.

    Product flow:

    ```text
    video clip -> factual scene core -> four tonal bearings -> accuracy/tone evaluator -> optional repair -> demo UI
    ```

    Required tones:

    ```text
    formal
    sarcastic
    humorous-tech
    humorous-non-tech
    ```

    This todo must improve the project while preserving public-safe boundaries and README gate sync.

    ## Goal

    Implement local video file acceptance and deterministic frame sampling suitable for 30 second to 2 minute clips.

    ## Required Behavior

    - Accept a local video path or uploaded file.
- Sample a bounded number of frames deterministically.
- Return frame metadata without leaking local paths in public outputs.
- Fail with clear errors when ffmpeg is unavailable or input is invalid.

    ## Design Constraints

    - Optimize for a judge reading output quickly.
    - Prefer explicit JSON contracts over loose prose between pipeline stages.
    - Prefer boring, testable services over broad abstractions.
    - Keep provider prompts short, direct, and tied to the current data contract.
    - Keep fallback/stub behavior available so tests can run without network.

    ## Suggested CLI or UI Behavior

    Use the simplest behavior that proves the gate. Prefer explicit local commands, JSON outputs, and Streamlit UI states that judges can understand quickly.

    ## Tests to Add

    - Add deterministic tests for this gate where practical.
    - Test malformed or missing inputs.
    - Test public-safe output shape.
    - Test that future-gate behavior is not claimed or required.

    Suggested command:

    ```bash
    python -m pytest -k 'video or frame or sampling'
    ```

    ## Acceptance Criteria

    - This todo is complete and no future todo is implemented.
    - Tests or verification command pass, or a concrete blocker is reported.
    - README is updated conservatively.
    - Public-safe boundary is preserved.
    - Output remains optimized for factual accuracy and tone separation.

    ## README Update Requirement

    Update README.md to reflect this gate's actual completed behavior. Do not document future gates as implemented.

    README must include:

    - current gate status
    - working commands only
    - known limitations
    - planned gates clearly marked as planned

    ## Out of Scope

    - Scene understanding
- Caption generation
- Audio transcription unless clips force it
- Cloud storage

    ## Expected Files Changed

    ```text
    video/frame extraction service, sample fixture or fixture builder, tests, README update
    ```

    Infer exact paths from the current repo structure. Keep changes minimal.

    ## Implementation Instructions

    1. Inspect current files.
    2. Read `SKILL.md` and `docs/README_GATE_POLICY.md`.
    3. Add tests or verification where practical.
    4. Implement only this todo.
    5. Update README conservatively.
    6. Run the suggested command.
    7. Report risks and any deferred work.

    ## Commands to Run

    ```bash
    python -m pytest -k 'video or frame or sampling'
    ```

    ## Expected Output

    Tests pass or the blocker is clearly reported. Any generated output must be public-safe, judge-friendly, and free of secrets or private references.

    ## Failure Cases

    - Missing dependency
    - Missing Fireworks key
    - Invalid video input
    - Malformed model JSON
    - Caption invents facts
    - Tone separation is weak
    - README gets ahead of implementation
    - Scope drifts into future gates

    ## Required Response Format

    Return:

    1. changed files
    2. patch/full contents
    3. tests added
    4. tests to run
    5. expected output
    6. architecture violations found
    7. suggested conventional commit
