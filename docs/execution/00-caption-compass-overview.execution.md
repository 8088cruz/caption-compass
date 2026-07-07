# Execution: Caption Compass Overview

## Goal

Define the full gated execution strategy for Caption Compass, a public Track 2 video captioning submission optimized for factual accuracy, four-tone style separation, Gemma/Fireworks usage, and runnable hackathon submission.

## Why This Exists

Caption Compass should be remarkable because it is built for the actual judging surface: an LLM judge evaluating accuracy and tone. The project should be simple enough to ship quickly and clear enough for judges to understand in under a minute.

## Source-of-Truth References

- Public repository: `8088cruz/caption-compass`
- Product thesis: one factual scene core, four tonal bearings, built-in accuracy and tone checks
- Track: AMD Developer Hackathon ACT II, Track 2 Video Captioning
- Required tones: formal, sarcastic, humorous-tech, humorous-non-tech
- README gate policy: `docs/README_GATE_POLICY.md`

## Scope

Gates C0-C8:

| Gate | Purpose |
| --- | --- |
| C0 | Scope, IP boundary, judging target |
| C1 | Public repo/app scaffold |
| C2 | Video upload and frame extraction |
| C3 | Factual scene core JSON contract |
| C4 | Four-tone caption generation |
| C5 | Accuracy/tone evaluator |
| C6 | Retry/repair loop |
| C7 | Demo UI and golden path |
| C8 | Docker, README, slides/video script, submission readiness |

## Out of Scope

- Private research disclosure
- Fine-tuning unless later explicitly required and feasible
- Complex auth, database, or multi-user features
- Audio/transcription unless clips clearly require it
- Unbounded agent loops
- Claims that the app is complete before C8

## Prerequisites

- Empty or nearly empty public repo
- Python environment
- ffmpeg for frame extraction
- Fireworks API key for real provider mode
- Stub/test mode for network-free verification

## Files/Packages Likely Touched

```text
README.md
pyproject.toml
app/
tests/
Dockerfile
.env.example
docs/
```

## Commands or UI Actions Added

The final project should support:

```bash
streamlit run app/main.py
python -m pytest
docker build -t caption-compass .
docker run --env-file .env -p 8501:8501 caption-compass
```

## Data Contracts

See individual execution docs for scene core, captions, evaluator, and repair contracts.

## Service Boundary

- UI calls services.
- Services own video processing, provider calls, generation, evaluation, and repair.
- Provider adapter owns Fireworks/Gemma integration.
- Tests can run without network through stubs.

## Provider/API Boundary

- No API key in repo.
- Use `.env.example`.
- Stub mode must not call network.
- Provider prompts must include only video-derived public-safe context.

## Prompt Contracts

Prompt contracts must preserve factual core before style rendering and return judge-friendly JSON.

## Tests

Add tests gate by gate. Prefer deterministic contract tests and smoke tests.

## README Update Requirements

Update README.md to reflect this gate's actual completed behavior. Do not document future gates as implemented.

## Acceptance Criteria

C8 is complete when a judge can run the app, upload a clip, see the factual core, four captions, evaluator scores, and understand the project from README and demo materials.

## Demo Commands

```bash
streamlit run app/main.py
```

## Expected Output

A public, runnable, judge-friendly Track 2 demo.

## Failure Cases

- Hallucinated scene facts
- Weak tone separation
- Broken Docker build
- README overclaims
- Missing Fireworks setup
- Over-scoped architecture

## Stop/Gate Criteria

Stop if implementation leaks private research, broadens beyond Track 2, or becomes too complex to submit.

## Suggested Conventional Commit

```text
not applicable
```
