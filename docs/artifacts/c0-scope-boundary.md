# C0 Scope Boundary

## Current Gate Status

C0 is implemented. Caption Compass is currently a documentation-only public repository state that locks the scope, IP boundary, judging target, and README gate policy before application behavior begins.

## Project Scope

Caption Compass is scoped to AMD Developer Hackathon: ACT II Track 2 video captioning.

The planned product path is:

```text
video clip -> timestamped evidence -> factual scene core -> four tonal bearings -> accuracy/tone evaluator -> one bounded repair pass -> demo UI
```

The project must preserve one style-free factual scene core and render four required caption tones from that same core:

- formal
- sarcastic
- humorous-tech
- humorous-non-tech

Future implementation should optimize for judge-readable factual accuracy, tone match, and traceability from evidence to output.

## Out Of Scope For C0

- Application scaffold
- Video upload
- Frame extraction
- Provider calls
- Caption generation
- Accuracy or tone evaluation
- Retry or repair behavior
- Streamlit UI
- Docker runtime
- Submission packaging

## Public-Safe Wording Rules

- Use only public hackathon, repository, and implementation language.
- Do not include secrets, API keys, local-only paths, private repo paths, private research material, or unpublished architecture.
- Do not quote copyrighted source material.
- Treat future behavior as planned until backed by a gate artifact, passing command, fixture, or schema.
- Keep provider outputs draft until evaluated or presented as generated outputs in a later gate.
- Keep factual scene reasoning separate from tone rendering in all future contracts.

## README Sync Evidence Used For This Gate

The README marks only C0 as implemented and keeps C1-C8 planned.

The README claims are backed by:

- this artifact: `docs/artifacts/c0-scope-boundary.md`
- the README gate policy: `docs/README_GATE_POLICY.md`
- the C0 verification commands:

```bash
true
test -f docs/artifacts/c0-scope-boundary.md
```

## Stop Conditions

Stop future work if a change claims unimplemented behavior, leaks private material, skips the factual scene core boundary, or moves app behavior ahead of the current gate.
