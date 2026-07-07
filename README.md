# Caption Compass

One factual scene core. Four tonal bearings. Built-in accuracy checks.

Caption Compass is a public AMD Developer Hackathon: ACT II Track 2 video-captioning project. The project is scoped to preserve one style-free factual scene core and render exactly four required caption tones: formal, sarcastic, humorous-tech, and humorous-non-tech.

At the current gate, this repository locks the public-safe project boundary before application behavior starts.

## Current Status

Gate status: **C0 implemented**

C0 artifact: [`docs/artifacts/c0-scope-boundary.md`](docs/artifacts/c0-scope-boundary.md)

Implemented now:

- Public-safe Track 2 scope boundary
- README gate policy
- Gate visual map for the C0-C8 artifact chain
- MIT license

Not implemented yet:

- Application scaffold
- Video upload or frame extraction
- Fireworks/Gemma provider calls
- Factual scene core generation
- Four-tone caption generation
- Accuracy/tone evaluator
- Retry/repair loop
- Streamlit UI
- Docker runtime

## C0 Verification

The current gate is documentation-only. Verify the C0 artifact exists with:

```bash
true
test -f docs/artifacts/c0-scope-boundary.md
```

No application run command exists yet. Add one during C1.

## Planned Product Behavior

1. Sample timestamped frames from a short video clip.
2. Build a style-free factual scene core from visible evidence.
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

## Implementation Gates

| Gate | Status | Purpose |
| --- | --- | --- |
| C0 | Implemented | Scope, public-safe boundary, judging target |
| C1 | Planned | Public repo/app scaffold |
| C2 | Planned | Video upload and frame extraction |
| C3 | Planned | Factual scene core JSON contract |
| C4 | Planned | Four-tone caption generation |
| C5 | Planned | Accuracy/tone evaluator |
| C6 | Planned | Retry/repair loop |
| C7 | Planned | Demo UI and golden path |
| C8 | Planned | Docker, README, slides/video script, submission readiness |

## Docs

- [`docs/README_GATE_POLICY.md`](docs/README_GATE_POLICY.md) - README truthfulness rules for every gate.
- [`docs/GATE_VISUAL_MAPS.md`](docs/GATE_VISUAL_MAPS.md) - visual overview of the gate system, artifacts, and judge-visible trace.

## Known Limitations

- This repo is not yet a runnable app.
- No video processing exists yet.
- Live model behavior is not implemented yet.
- No evaluator or repair behavior exists yet.
- Docker support is planned for C8.
- The future evaluator will be a model-assisted quality check, not a proof of correctness.

## README Discipline

After each gate, update this README to describe only behavior that actually exists. Future gates must remain planned until backed by a gate artifact, passing command, fixture, or schema.

## License

MIT
