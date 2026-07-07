# Roadmap: C7 - Judge-Visible Trace UI

## Execution Source

`docs/execution/07-ui-demo-path.execution.md`

## Implementation Todos

### TODO C7-T01: Streamlit Demo UI

**Goal**  
Build a thin Streamlit UI that shows the judge-visible trace from input video/sample to evidence, factual scene core, four captions, evaluator scores, and one-pass repair state.

**Concrete artifact**  

```text
docs/artifacts/c7-demo-proof.md
```

Optional, only if safe:

```text
docs/artifacts/c7-demo-screenshot.png
```

**Source files to include in coding chat**  

```text
SKILL.md
docs/README_GATE_POLICY.md
docs/execution/07-ui-demo-path.execution.md
docs/implementation-prompts/todos/c7-t01-streamlit-demo-ui.prompt.md
app/main.py optional
app/ui.py optional
app/pipeline.py optional
app/contracts.py optional
tests/ optional
docs/artifacts/ optional
README.md
```

**Suggested test command**  

```bash
python -m pytest -k "ui or smoke or app or pipeline"
```

**Suggested artifact check**  

```bash
test -f docs/artifacts/c7-demo-proof.md
```

**Suggested conventional commit**  

```text
feat(ui): add judge-visible trace demo
```

## Architecture Guardrails

- UI stays thin; services own behavior.
- Factual scene core stays separate from tone rendering.
- Timestamped evidence remains visible.
- Evaluator scores and issue codes remain visible.
- Repair trace is bounded to one pass.
- Provider/API calls stay behind the existing adapter/service.
- Stub/test mode must work without network where practical.
- Public outputs must not expose secrets, absolute local paths, private references, or unrelated screenshots.
- C7 must not add Docker/submission work.
- C7 must not implement new captioning/evaluator/repair behavior.

## README Sync Requirement

Update README.md to reflect this gate's actual completed behavior. Do not document future gates as implemented.

README must reference:

- working UI command if verified
- test/smoke command
- `docs/artifacts/c7-demo-proof.md`
- screenshot path only if committed and safe
- known UI limitations
- C8 Docker/submission work as planned

If the C7 proof artifact is missing, do not mark C7 complete.

## Stop/Defer Rules

Stop if:

- trace sections cannot be displayed
- UI leaks private data or local-only paths
- provider failure is hidden
- README gets ahead of implementation
- implementation crosses into C8
- artifact cannot be produced
