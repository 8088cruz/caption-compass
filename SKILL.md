---
name: caption-compass-builder
description: Build and maintain Caption Compass, a public-safe Track 2 video captioning project optimized for factual accuracy, four-tone style separation, Gemma/Fireworks usage, and runnable hackathon submission.
---

# Caption Compass Builder

Use this skill when working on Caption Compass or any gate in the Caption Compass research pack.

## Mission

Build a public AMD Developer Hackathon Track 2 submission that turns a short video into:

```text
one factual scene core -> four tonal bearings -> accuracy/tone evaluation -> optional repair -> demo UI
```

## Non-Negotiables

- Stay public-safe.
- Optimize for Track 2 judging: factual accuracy and tone match.
- Keep factual scene core separate from tone generation.
- Keep outputs LLM-judge-friendly.
- Use Gemma/Fireworks meaningfully where provider behavior is required.
- Prefer one-day runnable implementation over clever architecture.
- Keep the repository MIT-compliant.
- Do not expose private Corpus, Signal, CGS, KGL, or Arachne internals.
- Do not quote copyrighted source material.
- Do not add unnecessary features.
- Follow gates C0-C8.
- Stop if scope or IP boundaries weaken.

## README Discipline

After each gate, update `README.md` to reflect only completed behavior. Keep future gates under planned/roadmap language. Never imply the app is complete before C8.

## Preferred Implementation Shape

- Python
- Streamlit first unless a stronger reason exists
- ffmpeg for frame extraction
- Fireworks AI API
- Gemma through Fireworks when available
- JSON contracts for scene core, captions, and evaluator output
- Dockerfile
- deterministic tests and stub mode without network

## Drift Checks

Before finishing any turn, verify:

- current gate only
- no private references
- README updated conservatively
- tests or blockers reported
- next gate remains separate
