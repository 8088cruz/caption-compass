# C1 Scaffold Proof

## Current Gate Status

C1 is implemented. Caption Compass now has a minimal runnable Python scaffold, `uv sync` setup, and deterministic tests. No video processing, provider calls, caption generation, evaluator logic, repair loop, UI, or Docker behavior is implemented.

## Project Tree After Scaffold

```text
.gitignore
LICENSE
README.md
SKILL.md
caption_compass/
  __init__.py
  __main__.py
  scaffold.py
docs/
  GATE_VISUAL_MAPS.md
  README_GATE_POLICY.md
  artifacts/
    c0-scope-boundary.md
    c1-scaffold-proof.md
pyproject.toml
pytest.py
tests/
  test_scaffold.py
uv.lock
```

## Exact Setup Command

```bash
uv sync
```

Expected output summary:

- creates or updates the local `.venv`
- treats the C1 scaffold as a non-package app project
- does not require network dependencies at C1

## Exact Run Command

```bash
uv run python -m caption_compass
```

Expected output summary:

- prints JSON
- reports `project` as `Caption Compass`
- reports `gate` as `C1`
- reports `status` as `scaffold-ready`
- lists future behavior as not implemented

## Exact Test Or Verification Command

```bash
uv run python -m pytest
```

Expected output summary:

- runs 3 deterministic scaffold tests
- verifies the C1 status shape
- verifies future-gate behavior is not claimed as implemented
- verifies the run command emits valid JSON

Focused artifact check:

```bash
test -f docs/artifacts/c1-scaffold-proof.md
```

## Known Limitations

- This is a scaffold, not the full captioning app.
- `uv sync` is the supported setup path.
- No video upload or frame extraction exists yet.
- No Fireworks/Gemma provider calls exist yet.
- No factual scene core, captions, evaluator, repair loop, UI, or Docker runtime exists yet.
- `pytest.py` is a temporary offline compatibility runner for the C1 scaffold. A later gate can replace it with the real pytest package when third-party dependencies are introduced.
