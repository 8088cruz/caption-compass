# Execution: C2 - Video Upload and Frame Extraction

## Goal

Implement local video file acceptance and deterministic timestamped frame sampling for 30 second to 2 minute clips.

## Why This Exists

Caption Compass depends on a stable evidence layer. C2 produces the inspectable frame anchors that C3 uses to build a factual scene core. Later captions should be traceable back to sampled evidence instead of free-floating model interpretation.

This gate should make the first judge-visible proof point possible:

```text
video -> timestamped frame evidence packet
```

## Source-of-Truth References

- `SKILL.md`
- `docs/README_GATE_POLICY.md`
- `docs/implementation-prompts/gate-c2.prompt.md`
- `docs/implementation-prompts/todos/c2-t01-video-upload-and-frame-sampling.prompt.md`

## Scope

- Accept a local video path or uploaded file.
- Validate a short-video target range of 30 seconds to 2 minutes when duration metadata is available.
- Sample a bounded number of frames deterministically.
- Produce stable `frame_id` values and `timestamp_seconds` values.
- Save or expose frames through safe relative artifact references only.
- Return frame metadata without leaking local filesystem paths.
- Fail with clear errors when ffmpeg is unavailable or input is invalid.

## Out of Scope

- Scene understanding
- Caption generation
- Provider calls
- Audio transcription unless later clips clearly require it
- Cloud storage
- Any claim that sampled frames capture every event in the video

## Prerequisites

- C1 scaffold exists.
- `ffmpeg` or an equivalent local frame extraction path is available.
- Stub/test mode can run without network.
- README gate policy has been read before README edits.

## Files/Packages Likely Touched

```text
app/video.py
app/contracts.py
tests/test_video.py
tests/fixtures/
README.md
```

## Commands or UI Actions Added

Suggested verification command:

```bash
python -m pytest -k "video or frame or sampling"
```

## Data Contracts

### Frame Evidence Packet

C2 should produce this contract or a clearly equivalent typed model:

```json
{
  "video_id": "stable-video-id",
  "duration_seconds": 42.0,
  "sample_strategy": {
    "mode": "bounded_uniform",
    "max_frames": 8,
    "requested_range_seconds": [30, 120]
  },
  "frames": [
    {
      "frame_id": "f001",
      "timestamp_seconds": 0.0,
      "ordinal": 1,
      "image_ref": "artifacts/frames/f001.jpg",
      "width": 1280,
      "height": 720,
      "sha256": "optional-content-hash"
    }
  ],
  "warnings": []
}
```

### Public-Safe Output Rule

`image_ref` must be relative or UI-safe. Public JSON, screenshots, and README examples must not include absolute local paths such as `/home/...`, `/workspace/...`, or temporary upload paths.

## Service Boundary

- Frame extraction is separate from scene reasoning.
- C2 produces evidence packets only.
- C2 does not create scene summaries, captions, jokes, scores, or repair output.
- UI may display extracted frames later, but C2 should remain usable as a service with tests.

## Provider/API Boundary

No Fireworks/Gemma call is allowed in C2.

## Prompt Contracts

No model prompt is required in C2.

## Tests

Add deterministic tests for:

- valid short video returns a `video_id`, duration, and bounded frame list
- each frame has `frame_id`, `timestamp_seconds`, `ordinal`, and `image_ref`
- frame IDs are stable for the same fixture and sampling options
- invalid input fails with a clear error
- missing ffmpeg is surfaced as a clear dependency error
- public output does not include absolute local paths

## README Update Requirements

Update README.md to reflect this gate's actual completed behavior. Do not document future gates as implemented.

The README must include current gate status, working commands only, known limitations, and planned gates as future work.

## Acceptance Criteria

- A short fixture video can produce deterministic frame metadata.
- The frame evidence packet is JSON-serializable.
- No absolute local path appears in public output.
- The output gives C3 enough evidence anchors to build a factual scene core.

## Reviewer Confidence Signal

A reviewer should be able to see exactly what evidence was extracted, how frame IDs and timestamps are represented, how local paths are kept out of public output, how the gate was verified, and what remains deferred to C3 or later.

## Benchmark / Evidence Artifact

This gate should leave behind at least one concrete artifact:

- passing frame-extraction tests
- a sample frame evidence packet
- a working command that extracts frames from a fixture video
- a documented blocker with the exact dependency or input issue

## Demo Commands

```bash
python -m pytest -k "video or frame or sampling"
```

## Expected Output

Timestamped frame evidence suitable for C3 scene-core construction.

## Failure Cases

- Missing ffmpeg
- Unsupported file type
- Clip outside expected duration range
- Corrupt or unreadable video
- Sampling produces unstable IDs
- Public output leaks local filesystem paths
- Later code treats sampled frames as complete proof of every event

## Stop/Gate Criteria

Stop if frame extraction requires network, stores private paths in JSON, starts scene reasoning, or claims complete video understanding.

## Suggested Conventional Commit

```text
feat(video): add timestamped frame extraction
```
