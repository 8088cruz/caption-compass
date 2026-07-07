# README Gate Policy

Caption Compass must not get ahead of itself in the public README.

## Rule

```text
Update README.md to reflect this gate's actual completed behavior. Do not document future gates as implemented.
```

## Why

Hackathon judges need a truthful, runnable project. The README should be an accurate map of current behavior, not an aspirational product page.

## Required After Every Gate

- Update current gate status.
- Describe only implemented behavior.
- Put future work under "Planned" or "Roadmap".
- Include run commands only if they work.
- Include test commands only if they exist.
- Include known limitations.
- Keep Fireworks/Gemma setup honest.
- Keep Docker instructions honest.

## Forbidden

- Claiming the app is complete before C8.
- Claiming real model support before provider calls work.
- Claiming evaluator/retry behavior before it exists.
- Mentioning private research systems or private repo paths.
- Adding source-book quotes or private orchestration docs.
