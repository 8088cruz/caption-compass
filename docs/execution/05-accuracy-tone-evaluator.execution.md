# Execution: C5 - Accuracy/tone evaluator

    ## Goal

    Add a judge-like evaluator that scores factual accuracy, tone match, and clarity for each caption.

    ## Why This Exists

    Caption Compass is being built for AMD Developer Hackathon: ACT II Track 2. The judging surface is factual accuracy and tone match across four required styles. This gate keeps implementation focused on the smallest useful slice that improves judge-readiness without leaking private research or overbuilding.

    ## Source-of-Truth References

    - Public repository: `8088cruz/caption-compass`
    - Repository URL: https://github.com/8088cruz/caption-compass
    - Track 2 target: Video Captioning
    - Product thesis: one factual scene core, four tonal bearings, built-in accuracy and tone checks
    - Required tones: formal, sarcastic, humorous-tech, humorous-non-tech
    - Preferred stack: Python, Streamlit, ffmpeg, Fireworks AI API, Gemma when available, Docker
    - README gate policy: `docs/README_GATE_POLICY.md`
    - Current gate prompt: `docs/implementation-prompts/gate-c5.prompt.md`
    - Current todo prompt: `docs/implementation-prompts/todos/c5-t01-accuracy-tone-evaluator.prompt.md`

    ## Scope

    - Score each caption for factual accuracy, tone match, and clarity.
- Flag invented details, missing facts, tone bleed, and unclear jokes.
- Return actionable rewrite hints.
- Work in stub/test mode without network.

    ## Out of Scope

    - Automated repair
- Leaderboard claims
- Human preference UI
- Model fine-tuning

    ## Prerequisites

    - Complete prior gates in order unless explicitly running C0.
    - Keep repository public-safe and MIT-compatible.
    - Keep future work under planned/roadmap language only.
    - Use stub or deterministic behavior when real Fireworks credentials are unavailable.
    - Read `SKILL.md` before implementing.
    - Read `docs/README_GATE_POLICY.md` before editing README.

    ## Files/Packages Likely Touched

    ```text
    evaluator schema
evaluator prompt templates
scoring service
tests
    ```

    ## Commands or UI Actions Added

    Gate-specific commands or UI controls should be minimal. Prefer a working local command, test, or Streamlit interaction over broad architecture.

    Suggested verification command:

    ```bash
    python -m pytest -k 'evaluator or scoring or accuracy or tone'
    ```

    ## Data Contracts

    The final project should converge on these public JSON contracts. This gate should implement only the relevant subset:

    ```json
    {
      "scene_core": {
        "summary": "factual, style-free scene description",
        "observed_entities": [],
        "observed_actions": [],
        "setting": null,
        "visible_text": [],
        "uncertainties": []
      },
      "captions": {
        "formal": "...",
        "sarcastic": "...",
        "humorous_tech": "...",
        "humorous_non_tech": "..."
      },
      "evaluation": {
        "formal": {"factual_accuracy": 1, "tone_match": 1, "clarity": 1, "issues": []}
      }
    }
    ```

    This gate should implement only the pieces required by its scope.

    ### Scene Core Contract

    The scene core is style-free. It should contain observed or cautiously inferred facts only:

    ```json
    {
      "summary": "short factual description",
      "observed_entities": ["person", "object"],
      "observed_actions": ["walks", "points"],
      "setting": "visible setting or null",
      "visible_text": [],
      "audio_notes": [],
      "uncertainties": ["what is unclear"],
      "frame_evidence": []
    }
    ```

    ### Caption Contract

    Captions must preserve the same factual core while changing only presentation style:

    ```json
    {
      "formal": "neutral professional caption",
      "sarcastic": "dry but fact-preserving caption",
      "humorous_tech": "developer/tech humor caption",
      "humorous_non_tech": "general audience humorous caption"
    }
    ```

    ### Evaluation Contract

    Evaluator output must be judge-legible:

    ```json
    {
      "caption_key": {
        "factual_accuracy": 1,
        "tone_match": 1,
        "clarity": 1,
        "issues": [],
        "rewrite_hint": null
      }
    }
    ```

    ## Service Boundary

    - Keep UI thin.
    - Keep provider calls behind a small adapter or service.
    - Keep prompt construction separate from Streamlit widgets.
    - Keep data contracts testable without network.
    - Keep local file paths out of public JSON and screenshots.
    - Keep frame extraction separate from scene reasoning.
    - Keep scene reasoning separate from tone rendering.
    - Keep evaluation separate from generation.

    ## Provider/API Boundary

    - Fireworks/Gemma calls require explicit `FIREWORKS_API_KEY`.
    - Stub/test mode must work without network.
    - Do not send secrets, private repo content, private docs, or local paths as model context.
    - Provider outputs are draft until evaluated or shown as generated outputs.

    ## Prompt Contracts

    Prompts should:

    - preserve factual core before style rendering
    - make uncertainty explicit
    - avoid invented details
    - produce judge-friendly JSON
    - keep humor accessible and non-obscure
    - return strict JSON when a service expects JSON
    - avoid internal project jargon in model-facing instructions

    ## Tests

    Add or preserve tests appropriate to this gate. Prefer deterministic tests for schemas, service behavior, and public-safe output.

    Suggested command:

    ```bash
    python -m pytest -k 'evaluator or scoring or accuracy or tone'
    ```

    ### Direct Service Tests

    Add direct tests for the smallest service involved in this gate. Tests should not require network unless the gate explicitly covers real provider integration.

    ### Contract Tests

    Validate JSON shape, required keys, and failure handling for malformed inputs.

    ### Public-Safety Tests

    Where practical, assert outputs do not include local filesystem paths, secrets, private repo names, or private research terms.

    ### README Sync Test/Check

    Manually inspect README after the gate. The README must not claim future gates are implemented.

    ## README Update Requirements

    Update README.md to reflect this gate's actual completed behavior. Do not document future gates as implemented.

    The README must include current gate status, working commands only, known limitations, and planned gates as future work.

    ## Acceptance Criteria

    - Gate scope is complete.
    - Tests or verification command pass, or blockers are documented.
    - README is updated conservatively.
    - No private or proprietary content is introduced.
    - The project remains optimized for Track 2 accuracy and tone judging.
    - The implementation can be explained in one minute to a hackathon judge.
    - The next gate remains clearly separate.

    ## Implementation Steps

    1. Read `SKILL.md`.
    2. Read `docs/README_GATE_POLICY.md`.
    3. Read this execution document.
    4. Inspect the current repo tree.
    5. Identify the smallest files needed for this gate.
    6. Add or update tests first when practical.
    7. Implement only this gate.
    8. Run the suggested verification command.
    9. Update README with actual completed behavior only.
    10. Report changed files, test results, risks, and next gate.

    ## Reviewer Confidence Signal

    A reviewer should be able to see exactly what changed, why it matters for Track 2 judging, how it was verified, and what remains planned.

    ## Benchmark / Evidence Artifact

    Each gate should leave behind at least one useful artifact: passing tests, a working command, sample JSON, screenshot-ready UI state, or README instructions.

    ## Demo Commands

    Use the simplest command that proves this gate. If no command exists yet, use `true` and document why.

    ```bash
    python -m pytest -k 'evaluator or scoring or accuracy or tone'
    ```

    ## Expected Output

    Public-safe project files and/or demo behavior that prove this gate only. Outputs should not include secrets, private repo paths, or private research references.

    ## Failure Cases

    - Missing Fireworks key
    - Missing ffmpeg
    - Invalid video input
    - Model output is malformed JSON
    - Caption invents facts
    - Tone is ambiguous
    - README claims future work is done

    ## Stop/Gate Criteria

    Stop if implementation broadens beyond this gate, weakens public-safe boundaries, removes README synchronization, or claims completion before the behavior works.

    ## Suggested Conventional Commit

    ```text
    feat(eval): score caption accuracy and tone
    ```
