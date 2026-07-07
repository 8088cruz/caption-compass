---
name: caption-compass-builder
description: Build and maintain Caption Compass, a public-safe Track 2 video captioning project optimized for factual accuracy, four-tone style separation, Gemma/Fireworks usage, and runnable hackathon submission.
---

# Caption Compass Builder

Use this skill when working on Caption Compass or any gate in the Caption Compass research pack.

## Mission

Build a public AMD Developer Hackathon Track 2 submission that turns a short video into:

```text
timestamped video evidence -> one factual scene core -> four tonal bearings -> accuracy/tone evaluation -> one bounded repair pass -> demo UI
```

## Non-Negotiables

- Stay public-safe.
- Optimize for Track 2 judging: factual accuracy and tone match.
- Keep factual scene core separate from tone generation.
- Treat tone labels as output styles, not as claims about emotions, intent, or inner states.
- Keep outputs LLM-judge-friendly: short, explicit, non-obscure, and easy to score.
- Use Gemma/Fireworks meaningfully where provider behavior is required.
- Prefer one-day runnable implementation over clever architecture.
- Keep the repository MIT-compliant.
- Do not expose private research systems, internal project names, private repo paths, unpublished architecture, or long-term product strategy.
- Do not quote copyrighted source material.
- Do not add unnecessary features.
- Follow gates C0-C8.
- Stop if scope or IP boundaries weaken.

## Product Spine

The public demo should make the quality path visible:

1. Show sampled frame/timestamp evidence.
2. Show a style-free factual scene core.
3. Show four captions generated from the same factual scene core.
4. Show evaluator scores and issue codes.
5. Show one repair pass only when a caption fails.

## Tone Safety

The four required tones are rendering targets only:

- `formal`: neutral, concise, professional, no joke.
- `sarcastic`: mild dry irony, no cruelty, no invented facts.
- `humorous-tech`: accessible software/developer humor, no obscure insider dependency.
- `humorous-non-tech`: general audience humor, no technical knowledge required.

Do not infer private emotions, intentions, identity, motives, or mental states from the video. If a fact is unclear, mark uncertainty instead of turning it into a joke.

## Repair Discipline

Repair is bounded to one pass. A failed caption may be rewritten once using the factual scene core and evaluator feedback. Do not implement unbounded agent loops, repeated retries, or self-improvement flows unless a later gate explicitly changes scope.

## README Discipline

After each gate, update `README.md` to reflect only completed behavior. Keep future gates under planned/roadmap language. Never imply the app is complete before C8.

## Preferred Implementation Shape

- Python
- Streamlit first unless a stronger reason exists
- ffmpeg for frame extraction
- Fireworks AI API
- Gemma through Fireworks when available
- JSON contracts for scene core, captions, evaluator output, and repair history
- Dockerfile
- deterministic tests and stub mode without network

## Drift Checks

Before finishing any turn, verify:

- current gate only
- no private references
- factual core remains separate from tone rendering
- tone labels are treated as styles, not emotion or intent inference
- evaluator output is visible and judge-readable
- repair is bounded to one pass
- README updated conservatively
- tests or blockers reported
- next gate remains separate
