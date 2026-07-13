# Caption Compass

One factual scene core. Four tonal bearings. Built-in accuracy checks and one bounded repair pass.

Caption Compass is a public AMD Developer Hackathon: ACT II Track 2 video-captioning project. The project is scoped to preserve one style-free factual scene core and render exactly four required caption tones: formal, sarcastic, humorous-tech, and humorous-non-tech.

At the current gate, this repository can sample timestamped frame evidence from a local video file, convert those anchors into a deterministic factual scene core contract, render exactly four caption tones from that same core, score those captions with a deterministic evaluator, run one bounded repair pass for eligible failed captions, and report sanitized provider configuration. It does not identify scene content from pixels; unsupported facts are marked unknown or excluded from caption claims. Evaluator scores and repair decisions are heuristic checks, not proof of objective truth. Provider-backed vision/audio is not implemented yet.

## Current Status

Gate status: **C6A implemented**

C0 artifact: [`docs/artifacts/c0-scope-boundary.md`](docs/artifacts/c0-scope-boundary.md)
C1 artifact: [`docs/artifacts/c1-scaffold-proof.md`](docs/artifacts/c1-scaffold-proof.md)
C2 artifact: [`docs/artifacts/c2-frame-evidence.sample.json`](docs/artifacts/c2-frame-evidence.sample.json)
C3 artifact: [`docs/artifacts/c3-scene-core.sample.json`](docs/artifacts/c3-scene-core.sample.json)
C4 artifact: [`docs/artifacts/c4-four-tone-captions.sample.json`](docs/artifacts/c4-four-tone-captions.sample.json)
C5 artifact: [`docs/artifacts/c5-evaluation.sample.json`](docs/artifacts/c5-evaluation.sample.json)
C6 artifact: [`docs/artifacts/c6-repair-trace.sample.json`](docs/artifacts/c6-repair-trace.sample.json)
C6A artifact: [`docs/artifacts/c6a-provider-config.sample.json`](docs/artifacts/c6a-provider-config.sample.json)

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
- One bounded deterministic repair pass for failed repair-eligible captions
- Before/after repair trace with scores, issue codes, accepted/rejected status, and final captions
- Sanitized provider configuration boundary for `stub` and `fireworks`
- `.env.example` placeholders and local secret/output ignore rules

Not implemented yet:

- Fireworks/Gemma provider calls
- Visual scene interpretation/provider-generated observations
- Provider-backed caption generation
- Persisted frame artifacts for provider use
- Audio extraction or transcription
- Streamlit UI
- Docker runtime

## Provider Configuration

Default mode is deterministic stub mode and does not use the network:

```bash
uv run caption-compass provider-status
```

Expected output: public-safe JSON reporting provider mode, configured model names if present, whether an API key is present, readiness warnings, and `network_used: false`.

For local provider experiments, copy `.env.example` to `.env` and set local values:

```bash
cp .env.example .env
```

Required environment variables for future Fireworks provider readiness:

```bash
CAPTION_COMPASS_PROVIDER=fireworks
FIREWORKS_API_KEY=replace-with-your-local-key
CAPTION_COMPASS_VISION_MODEL=replace-with-hackathon-vision-model
CAPTION_COMPASS_TEXT_MODEL=replace-with-hackathon-text-model
CAPTION_COMPASS_AUDIO_MODEL=replace-with-hackathon-audio-model
CAPTION_COMPASS_PROVIDER_TIMEOUT_SECONDS=60
```

`.env` is ignored and must not be committed. Provider status output never includes the raw API key.

Credentials alone are not enough for pixel/audio understanding. C6A only adds the provider configuration boundary. Vision observations, persisted frames for provider use, audio extraction, and transcription remain future work.

## Run Command

Install the project environment with:

```bash
uv sync
```

Run the current scaffold with:

```bash
uv run caption-compass
```

Expected output: JSON reporting `gate` as `C6A` and `status` as `provider-config-ready`.

Sample timestamped frame evidence from a local video file:

```bash
uv run caption-compass sample-frames --video local_test_videos/sample.mp4 --output frame-evidence.json
```

Build a deterministic factual scene core contract from C2 frame evidence:

```bash
uv run caption-compass build-scene-core --evidence docs/artifacts/c2-frame-evidence.sample.json --output scene-core.json
```

Generate exactly four deterministic captions from a C3 scene core:

```bash
uv run caption-compass generate-captions --scene-core docs/artifacts/c3-scene-core.sample.json --output captions.json
```

Evaluate C4 captions against a C3 scene core:

```bash
uv run caption-compass evaluate-captions --scene-core docs/artifacts/c3-scene-core.sample.json --captions docs/artifacts/c4-four-tone-captions.sample.json --output evaluation.json
```

Run one bounded repair pass from C3, C4, and C5 contracts:

```bash
uv run caption-compass repair-captions --scene-core docs/artifacts/c3-scene-core.sample.json --captions docs/artifacts/c4-four-tone-captions.sample.json --evaluation docs/artifacts/c5-evaluation.sample.json --output repair-trace.json
```

## Test And Verification Commands

Run the full tests with:

```bash
uv run pytest
```

Run the focused C6A provider config tests with:

```bash
uv run pytest -k 'provider or config or fireworks'
```

Verify the C6A artifact exists with:

```bash
test -f docs/artifacts/c6a-provider-config.sample.json
```

Optional provider status smoke tests:

```bash
uv run caption-compass provider-status
CAPTION_COMPASS_PROVIDER=fireworks FIREWORKS_API_KEY=local-test-redacted CAPTION_COMPASS_VISION_MODEL=placeholder uv run caption-compass provider-status
```

The second command should report `"api_key_present": true` without printing the key.

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
| C6 | Implemented | One bounded repair pass |
| C6A | Implemented | Provider configuration boundary |
| C6B | Planned | Persisted frame artifacts for provider use |
| C6C | Planned | Vision observations from sampled frames |
| C6D | Planned | Scene core fusion from visual observations |
| C7 | Planned | Demo UI and golden path |
| C8 | Planned | Docker, README, slides/video script, submission readiness |

## Docs

- [`docs/README_GATE_POLICY.md`](docs/README_GATE_POLICY.md) - README truthfulness rules for every gate.
- [`docs/GATE_VISUAL_MAPS.md`](docs/GATE_VISUAL_MAPS.md) - visual overview of the gate system, artifacts, and judge-visible trace.

## Known Limitations

- This repo currently produces frame evidence metadata, a deterministic factual scene core contract, deterministic four-tone caption contract output, deterministic evaluator output, a deterministic one-pass repair trace, and sanitized provider configuration status.
- `uv sync` is the supported setup path.
- Manual test videos should stay outside git, for example under ignored `local_test_videos/`.
- Local provider outputs should stay outside git, for example under ignored `local_test_outputs/`.
- `.env` is ignored and must not be committed.
- Provider status never prints raw API keys.
- C6A does not make Fireworks/Gemma calls.
- C6A does not add pixel/audio understanding.
- Frame evidence output does not include absolute local paths.
- C2 does not interpret scene content.
- C3 deterministic mode does not inspect image pixels or identify entities, actions, settings, emotions, or intent.
- C3 marks unsupported facts as unknown or unsupported instead of guessing.
- C4 deterministic mode changes tone only; it does not add facts outside the C3 scene core.
- C5 deterministic mode is a heuristic evaluator. Its scores help catch obvious accuracy, tone, and clarity issues but do not prove objective truth.
- C6 repairs only failed captions marked repair-eligible by C5 and attempts at most one repair per failed caption.
- Live model behavior is not implemented yet.
- No persisted frame artifact provider seam exists yet.
- No demo UI exists yet.
- Docker support is planned for C8.

## README Discipline

After each gate, update this README to describe only behavior that actually exists. Future gates must remain planned until backed by a gate artifact, passing command, fixture, or schema.

## License

MIT
