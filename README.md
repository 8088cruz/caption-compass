# Caption Compass

One factual scene core. Four tonal bearings. Built-in accuracy checks.

Caption Compass is a public AMD Developer Hackathon: ACT II Track 2 video-captioning project. The target behavior is simple: sample a short video, build a style-free factual scene core, generate the four required caption styles, evaluate accuracy and tone, and repair weak captions once when possible.

## Current Status

Gate status: **C0 pending**

This repository currently contains the research and implementation prompt pack. Application implementation has not started yet.

Implemented now:

- Public-safe project boundary documentation
- Gate-based execution docs
- Implementation prompts for C0-C8
- README gate policy
- Builder skill instructions
- Gate visual maps

Not implemented yet:

- Video upload or frame extraction
- Fireworks/Gemma provider calls
- Factual scene core generation
- Four-tone caption generation
- Accuracy/tone evaluator
- Retry/repair loop
- Streamlit UI
- Docker runtime

## Planned Product Behavior

1. Sample timestamped frames from a short video clip.
2. Build a factual scene core from visible evidence.
3. Generate exactly four captions from the same factual core:
   - formal
   - sarcastic
   - humorous-tech
   - humorous-non-tech
4. Score each caption for factual accuracy, tone match, and clarity.
5. Repair failed captions once using evaluator feedback.
6. Show a judge-readable trace from evidence to captions to scores.

## Planned Stack

- Python
- Streamlit
- ffmpeg
- Fireworks AI API
- Gemma through Fireworks when available
- JSON contracts for scene core, captions, evaluation, and repair
- Docker

## Run Commands

No application run command exists yet. Add one during C1.

## Test Commands

No test command exists yet. Add one during C1.

## Known Limitations

- This repo is not yet a runnable app.
- Live model behavior is not implemented yet.
- Docker support is planned for C8.
- The evaluator, once implemented, will be a model-assisted quality check, not a proof of correctness.
- Audio transcription is deferred unless the challenge clips require it.

## Implementation Gates

| Gate | Status | Purpose |
| --- | --- | --- |
| C0 | Pending | Scope, public-safe boundary, judging target |
| C1 | Planned | Public repo/app scaffold |
| C2 | Planned | Video upload and frame extraction |
| C3 | Planned | Factual scene core JSON contract |
| C4 | Planned | Four-tone caption generation |
| C5 | Planned | Accuracy/tone evaluator |
| C6 | Planned | Retry/repair loop |
| C7 | Planned | Demo UI and golden path |
| C8 | Planned | Docker, README, slides/video script, submission readiness |

Docs:

- [Gate Visual Maps](docs/GATE_VISUAL_MAPS.md) - visual overview of the C0-C8 gate system, artifacts, and judge-visible trace.

## README Discipline

After each gate, update this README to describe only behavior that actually works. Future gates must remain under planned or roadmap language until implemented.

## License

MIT license planned. Add `LICENSE` during C0 or C1 before implementation work expands.
