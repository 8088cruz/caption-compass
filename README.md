# Caption Compass

One factual scene core. Four tonal bearings. Built-in accuracy checks and one bounded repair pass.

Caption Compass is a public AMD Developer Hackathon: ACT II Track 2 video-captioning project. The project is scoped to preserve one style-free factual scene core and render exactly four required caption tones: formal, sarcastic, humorous-tech, and humorous-non-tech.

At the current gate, this repository can sample timestamped frame evidence from a local video file, optionally persist sampled frame JPGs under ignored local outputs for future provider use, convert frame anchors into a deterministic factual scene core contract, render exactly four caption tones from that same core, score those captions with a deterministic evaluator, run one bounded repair pass for eligible failed captions, and report sanitized provider configuration. It does not identify scene content from pixels; unsupported facts are marked unknown or excluded from caption claims. Evaluator scores and repair decisions are heuristic checks, not proof of objective truth. Provider-backed vision/audio is not implemented yet.

## Current Status

Gate status: **C6B implemented**

C0 artifact: [`docs/artifacts/c0-scope-boundary.md`](docs/artifacts/c0-scope-boundary.md)
C1 artifact: [`docs/artifacts/c1-scaffold-proof.md`](docs/artifacts/c1-scaffold-proof.md)
C2 artifact: [`docs/artifacts/c2-frame-evidence.sample.json`](docs/artifacts/c2-frame-evidence.sample.json)
C3 artifact: [`docs/artifacts/c3-scene-core.sample.json`](docs/artifacts/c3-scene-core.sample.json)
C4 artifact: [`docs/artifacts/c4-four-tone-captions.sample.json`](docs/artifacts/c4-four-tone-captions.sample.json)
C5 artifact: [`docs/artifacts/c5-evaluation.sample.json`](docs/artifacts/c5-evaluation.sample.json)
C6 artifact: [`docs/artifacts/c6-repair-trace.sample.json`](docs/artifacts/c6-repair-trace.sample.json)
C6A artifact: [`docs/artifacts/c6a-provider-config.sample.json`](docs/artifacts/c6a-provider-config.sample.json)
C6B artifact: [`docs/artifacts/c6b-persisted-frames.sample.json`](docs/artifacts/c6b-persisted-frames.sample.json)

Implemented now:

- Public-safe Track 2 scope boundary
- README gate policy
- Gate visual map for the C0-C8 artifact chain
- MIT license
- Minimal Python package scaffold
- Timestamped frame evidence sampling from a local video file
- Optional persisted sampled frame JPGs under ignored `local_test_outputs/`
- Public-safe frame metadata JSON with stable frame refs and no absolute local paths
- Deterministic factual scene core contract from C2 evidence anchors
- Deterministic four-tone caption contract from a C3 scene core
- Exactly four tone outputs: formal, sarcastic, humorous-tech, and humorous-non-tech
- Shared `scene_core_id` and fact lock across all four captions
- Deterministic accuracy/tone evaluator for C3 scene core plus C4 captions
- One bounded deterministic repair pass for failed repair-eligible captions
- Sanitized provider configuration boundary for `stub` and `fireworks`
- `.env.example` placeholders and local secret/output ignore rules

Not implemented yet:

- Fireworks/Gemma provider calls
- Visual scene interpretation/provider-generated observations
- Provider-backed caption generation
- Audio extraction or transcription
- Streamlit UI
- Docker runtime

## Provider Configuration

Default mode is deterministic stub mode and does not use the network:

```bash
uv run caption-compass provider-status
```

For local provider experiments, copy `.env.example` to `.env` and set local values. `.env` is ignored and must not be committed.

Credentials alone are not enough for pixel/audio understanding. C6A only adds the provider configuration boundary, and C6B only persists local frame JPGs for future provider use. Vision observations, audio extraction, and transcription remain future work.

## Run Command

Install the project environment with:

```bash
uv sync
```

Run the current scaffold with:

```bash
uv run caption-compass
```

Expected output: JSON reporting `gate` as `C6B` and `status` as `persisted-frames-ready`.

Sample timestamped frame evidence from a local video file without persisting frames:

```bash
uv run caption-compass sample-frames --video local_test_videos/sample.mp4 --output frame-evidence.json
```

Persist sampled frame JPGs for future provider use:

```bash
uv run caption-compass sample-frames --video local_test_videos/sample.mp4 --output frame-evidence.json --persist-frames --output-dir local_test_outputs/manual-run
```

Expected output: public-safe JSON metadata with sanitized source identifier, sampled frame timestamps, stable `frame://...` refs, ignored local output refs such as `local-output://manual-run/frames/frame_0001.jpg`, extraction status, and warnings. The JSON must not include absolute local paths.

Build scene core, generate the four required caption tones, evaluate them, and run one bounded repair pass with the existing commands:

```bash
uv run caption-compass build-scene-core --evidence docs/artifacts/c2-frame-evidence.sample.json --output scene-core.json
uv run caption-compass generate-captions --scene-core docs/artifacts/c3-scene-core.sample.json --output captions.json
uv run caption-compass evaluate-captions --scene-core docs/artifacts/c3-scene-core.sample.json --captions docs/artifacts/c4-four-tone-captions.sample.json --output evaluation.json
uv run caption-compass repair-captions --scene-core docs/artifacts/c3-scene-core.sample.json --captions docs/artifacts/c4-four-tone-captions.sample.json --evaluation docs/artifacts/c5-evaluation.sample.json --output repair-trace.json
```

## Test And Verification Commands

```bash
uv run pytest
uv run pytest -k 'frame or persist or output'
uv run pytest -k 'provider or config or fireworks'
test -f docs/artifacts/c6a-provider-config.sample.json
test -f docs/artifacts/c6b-persisted-frames.sample.json
```

Manual smoke test:

```bash
uv run caption-compass sample-frames \
  --video local_test_videos/sample.mp4 \
  --output frame-evidence.json \
  --persist-frames \
  --output-dir local_test_outputs/manual-run
find local_test_outputs/manual-run/frames -maxdepth 1 -type f | sort
rg -n "/home|/tmp|/workspace" frame-evidence.json
```

The `rg` command should return no matches.

## Planned Product Behavior

1. Sample timestamped frames from a short video clip.
2. Persist frame JPGs locally when provider inspection is needed.
3. Build a style-free factual scene core from visible evidence.
4. Generate exactly four captions from the same factual core:
  - formal
  - sarcastic
  - humorous-tech
  - humorous-non-tech
5. Score each caption for factual accuracy, tone match, and clarity.
6. Repair failed captions once using evaluator feedback.
7. Show a judge-readable trace from evidence to captions to scores.

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
| C6 | Implemented | One bounded repair pass |
| C6A | Implemented | Provider configuration boundary |
| C6B | Implemented | Persisted frame artifacts for provider use |
| C6C | Planned | Vision observations from sampled frames |
| C6D | Planned | Scene core fusion from visual observations |
| C7 | Planned | Demo UI and golden path |
| C8 | Planned | Docker, README, slides/video script, submission readiness |

## Docs

- [`docs/README_GATE_POLICY.md`](docs/README_GATE_POLICY.md) - README truthfulness rules for every gate.
- [`docs/GATE_VISUAL_MAPS.md`](docs/GATE_VISUAL_MAPS.md) - visual overview of the gate system, artifacts, and judge-visible trace.

## Known Limitations

- This repo currently produces frame evidence metadata, optional local persisted frame JPGs, a deterministic factual scene core contract, deterministic four-tone caption contract output, deterministic evaluator output, a deterministic one-pass repair trace, and sanitized provider configuration status.
- `uv sync` is the supported setup path.
- Manual test videos should stay outside git, for example under ignored `local_test_videos/`.
- Local provider outputs should stay outside git, for example under ignored `local_test_outputs/`.
- Persisted frames are local files for future provider use and should not be committed.
- `.env` is ignored and must not be committed.
- C6A/C6B do not make Fireworks/Gemma calls.
- C6B does not add pixel/audio understanding.
- Public JSON does not include absolute local paths.
- C3 deterministic mode does not inspect image pixels or identify entities, actions, settings, emotions, or intent.
- Live model behavior is not implemented yet.
- No visual observation provider call exists yet.
- No demo UI exists yet.
- Docker support is planned for C8.

## README Discipline

After each gate, update this README to describe only behavior that actually exists. Future gates must remain planned until backed by a gate artifact, passing command, fixture, or schema.

## License

MIT
