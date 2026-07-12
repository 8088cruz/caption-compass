# Caption Compass

One factual scene core. Four tonal bearings. Built-in accuracy checks.

Caption Compass is a public AMD Developer Hackathon: ACT II Track 2 video-captioning project. The project is scoped to preserve one style-free factual scene core and render exactly four required caption tones: formal, sarcastic, humorous-tech, and humorous-non-tech.

At the current gate, this repository can sample timestamped frame evidence from a local video file, convert those anchors into a deterministic factual scene core contract, render exactly four caption tones from that same core, and score those captions with a deterministic evaluator. It does not identify scene content from pixels; unsupported facts are marked unknown or excluded from caption claims. Evaluator scores are heuristic checks, not proof of objective truth.

## Current Status

Gate status: **C5 implemented**

C0 artifact: [`docs/artifacts/c0-scope-boundary.md`](docs/artifacts/c0-scope-boundary.md)
C1 artifact: [`docs/artifacts/c1-scaffold-proof.md`](docs/artifacts/c1-scaffold-proof.md)
C2 artifact: [`docs/artifacts/c2-frame-evidence.sample.json`](docs/artifacts/c2-frame-evidence.sample.json)
C3 artifact: [`docs/artifacts/c3-scene-core.sample.json`](docs/artifacts/c3-scene-core.sample.json)
C4 artifact: [`docs/artifacts/c4-four-tone-captions.sample.json`](docs/artifacts/c4-four-tone-captions.sample.json)
C5 artifact: [`docs/artifacts/c5-evaluation.sample.json`](docs/artifacts/c5-evaluation.sample.json)

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
- Deterministic four-tone caption contract from a C3 scene core
- Exactly four tone outputs: formal, sarcastic, humorous-tech, and humorous-non-tech
- Shared `scene_core_id` and fact lock across all four captions
- Deterministic accuracy/tone evaluator for C3 scene core plus C4 captions
- Per-tone factual accuracy, tone match, and clarity scores with issue codes, repair eligibility, and rewrite hints

Not implemented yet:

- Fireworks/Gemma provider calls
- Visual scene interpretation/provider-generated observations
- Provider-backed caption generation
- Automated caption repair
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

Expected output: JSON reporting `gate` as `C5` and `status` as `accuracy-tone-evaluator-ready`.

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

Generate exactly four deterministic captions from a C3 scene core:

```bash
uv run caption-compass generate-captions --scene-core docs/artifacts/c3-scene-core.sample.json --output captions.json
```

Expected output: public-safe JSON with `scene_core_id`, four required tones, tone rubrics, a shared fact lock, and unsupported inferences excluded from caption claims.

Evaluate C4 captions against a C3 scene core:

```bash
uv run caption-compass evaluate-captions --scene-core docs/artifacts/c3-scene-core.sample.json --captions docs/artifacts/c4-four-tone-captions.sample.json --output evaluation.json
```

Expected output: public-safe JSON with `scene_core_id`, thresholds, per-tone factual accuracy/tone match/clarity scores, issue codes, repair eligibility flags, and rewrite hints where applicable. The evaluator does not repair captions.

## Test And Verification Commands

Run the full tests with:

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

Run the focused C4 tests with:

```bash
uv run pytest -k 'caption or tone or generation'
```

Run the focused C5 tests with:

```bash
uv run pytest -k 'evaluator or scoring or accuracy or tone'
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

Verify the C4 artifact exists with:

```bash
test -f docs/artifacts/c4-four-tone-captions.sample.json
```

Verify the C5 artifact exists with:

```bash
test -f docs/artifacts/c5-evaluation.sample.json
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
| C4 | Implemented | Four-tone caption generation |
| C5 | Implemented | Accuracy/tone evaluator |
| C6 | Planned | Retry/repair loop |
| C7 | Planned | Demo UI and golden path |
| C8 | Planned | Docker, README, slides/video script, submission readiness |

## Docs

- [`docs/README_GATE_POLICY.md`](docs/README_GATE_POLICY.md) - README truthfulness rules for every gate.
- [`docs/GATE_VISUAL_MAPS.md`](docs/GATE_VISUAL_MAPS.md) - visual overview of the gate system, artifacts, and judge-visible trace.

## Known Limitations

- This repo currently produces frame evidence metadata, a deterministic factual scene core contract, deterministic four-tone caption contract output, and deterministic evaluator output.
- `uv sync` is the supported setup path.
- Manual test videos should stay outside git, for example under ignored `local_test_videos/`.
- Frame evidence output does not include absolute local paths.
- C2 does not interpret scene content.
- C3 deterministic mode does not inspect image pixels or identify entities, actions, settings, emotions, or intent.
- C3 marks unsupported facts as unknown or unsupported instead of guessing.
- C4 deterministic mode changes tone only; it does not add facts outside the C3 scene core.
- If the C3 scene core has no supported visual facts, C4 captions state that limitation instead of inventing a scene.
- C5 deterministic mode is a heuristic evaluator. Its scores help catch obvious accuracy, tone, and clarity issues but do not prove objective truth.
- C5 does not rewrite or repair captions.
- Live model behavior is not implemented yet.
- No repair behavior exists yet.
- No demo UI exists yet.
- Docker support is planned for C8.

## README Discipline

After each gate, update this README to describe only behavior that actually exists. Future gates must remain planned until backed by a gate artifact, passing command, fixture, or schema.

## License

MIT
