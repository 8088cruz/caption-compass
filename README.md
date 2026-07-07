# Caption Compass

One factual scene core. Four tonal bearings. Built-in accuracy checks.

Caption Compass is a public AMD Developer Hackathon: ACT II Track 2 video-captioning project. The project is scoped to preserve one style-free factual scene core and render exactly four required caption tones: formal, sarcastic, humorous-tech, and humorous-non-tech.

At the current gate, this repository can sample timestamped frame evidence from a local video file and convert those anchors into a deterministic factual scene core contract. It does not identify scene content from pixels; unsupported facts are marked unknown or unsupported.

## Current Status

Gate status: **C3 implemented**

C0 artifact: [`docs/artifacts/c0-scope-boundary.md`](docs/artifacts/c0-scope-boundary.md)
C1 artifact: [`docs/artifacts/c1-scaffold-proof.md`](docs/artifacts/c1-scaffold-proof.md)
C2 artifact: [`docs/artifacts/c2-frame-evidence.sample.json`](docs/artifacts/c2-frame-evidence.sample.json)
C3 artifact: [`docs/artifacts/c3-scene-core.sample.json`](docs/artifacts/c3-scene-core.sample.json)

Implemented now:

- Public-safe Track 2 scope boundary
- README gate policy
- Gate visual map for the C0-C8 artifact chain
- MIT license
- Minimal Python package scaffold
- Deterministic scaffold status command
- Basic scaffold tests run through `uv`
- Timestamped frame evidence sampling from a local video file
- Public-safe frame metadata JSON with stable frame refs
- Deterministic factual scene core contract from C2 evidence anchors
- Stable `scene_core_id`, preserved evidence anchor IDs, unsupported inferences, and uncertainty notes

Not implemented yet:

- Fireworks/Gemma provider calls
- Visual scene interpretation/provider-generated observations
- Four-tone caption generation
- Accuracy/tone evaluator
- Retry/repair loop
- Streamlit UI
- Docker runtime

## Run Command

Install the project environment with:

```bash
uv sync
```

Run the current scaffold with:

```bash
uv run caption-compass
```

Expected output: JSON reporting `gate` as `C3` and `status` as `scene-core-contract-ready`.

Sample timestamped frame evidence from a local video file:

```bash
uv run caption-compass sample-frames --video local_test_videos/sample.mp4 --output frame-evidence.json
```

Expected output: public-safe JSON metadata with sanitized source identifier, video duration when available, sampled frame timestamps, stable `frame://...` refs, extraction status, and warnings.

Build a deterministic factual scene core contract from C2 frame evidence:

```bash
uv run caption-compass build-scene-core --evidence docs/artifacts/c2-frame-evidence.sample.json --output scene-core.json
```

Expected output: public-safe JSON with a stable `scene_core_id`, preserved evidence anchors, empty observed facts when unsupported, explicit unsupported inferences, and uncertainty notes.

## Test And Verification Commands

Run the scaffold tests with:

```bash
uv run pytest
```

Run the focused C2 tests with:

```bash
uv run pytest -k 'video or frame or ingestion'
```

Run the focused C3 tests with:

```bash
uv run pytest -k 'scene_core or factual or contract'
```

Verify the C1 artifact exists with:

```bash
test -f docs/artifacts/c1-scaffold-proof.md
```

Verify the C2 artifact exists with:

```bash
test -f docs/artifacts/c2-frame-evidence.sample.json
```

Verify the C3 artifact exists with:

```bash
test -f docs/artifacts/c3-scene-core.sample.json
```

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
| C1 | Implemented | Public repo/app scaffold |
| C2 | Implemented | Video upload and frame extraction |
| C3 | Implemented | Factual scene core JSON contract |
| C4 | Planned | Four-tone caption generation |
| C5 | Planned | Accuracy/tone evaluator |
| C6 | Planned | Retry/repair loop |
| C7 | Planned | Demo UI and golden path |
| C8 | Planned | Docker, README, slides/video script, submission readiness |

## Docs

- [`docs/README_GATE_POLICY.md`](docs/README_GATE_POLICY.md) - README truthfulness rules for every gate.
- [`docs/GATE_VISUAL_MAPS.md`](docs/GATE_VISUAL_MAPS.md) - visual overview of the gate system, artifacts, and judge-visible trace.

## Known Limitations

- This repo currently produces frame evidence metadata and a deterministic factual scene core contract only.
- `uv sync` is the supported setup path.
- Manual test videos should stay outside git, for example under ignored `local_test_videos/`.
- Frame evidence output does not include absolute local paths.
- C2 does not interpret scene content.
- C3 deterministic mode does not inspect image pixels or identify entities, actions, settings, emotions, or intent.
- C3 marks unsupported facts as unknown or unsupported instead of guessing.
- Live model behavior is not implemented yet.
- No four-tone captions exist yet.
- No evaluator or repair behavior exists yet.
- No demo UI exists yet.
- Docker support is planned for C8.
- The future evaluator will be a model-assisted quality check, not a proof of correctness.

## README Discipline

After each gate, update this README to describe only behavior that actually exists. Future gates must remain planned until backed by a gate artifact, passing command, fixture, or schema.

## License

MIT
