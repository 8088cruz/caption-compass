# Execution: C4 - Four-Tone Caption Generation

## Goal

Generate exactly four captions from the same factual scene core:

1. formal
2. sarcastic
3. humorous-tech
4. humorous-non-tech

Each caption must preserve the same factual scene core while changing only presentation style.

## Why This Exists

Track 2 is judged on factual accuracy and tone match. A basic caption generator may produce fluent text, but Caption Compass should be stronger because it explicitly separates:

```text
timestamped evidence -> factual scene core -> four tone renderings
```

C4 is the first place the project becomes visibly different from a generic video summarizer. The judge should be able to see that the same facts survive across all four required tones.

## Source-of-Truth References

- `SKILL.md`
- `docs/README_GATE_POLICY.md`
- `docs/implementation-prompts/gate-c4.prompt.md`
- `docs/implementation-prompts/todos/c4-t01-four-tone-caption-contract.prompt.md`
- C3 factual scene core from `docs/execution/03-factual-scene-core.execution.md`

## Scope

- Generate exactly the four required Track 2 tones.
- Use one `scene_core_id` for all four captions.
- Preserve factual content from the C3 scene core.
- Use uncertainty from C3 instead of inventing details.
- Exclude C3 `unsupported_inferences` from caption facts.
- Make tone differences obvious to an LLM judge.
- Keep humor accessible, short, and non-obscure.
- Return machine-readable JSON for UI and evaluator use.

## Out of Scope

- Evaluator scoring
- Retry/repair logic
- Advanced humor models
- User-customized styles
- Non-required tones
- Fine-tuning
- New scene facts not present in the factual scene core

## Prerequisites

- C3 factual scene core contract exists.
- C3 exposes `scene_core_id`, observed facts, uncertainties, and `unsupported_inferences`.
- Provider adapter or deterministic stub exists.
- README gate policy has been read before README edits.

## Files/Packages Likely Touched

```text
app/contracts.py
app/captions.py
app/providers.py
app/prompts/
tests/test_captions.py
README.md
```

## Commands or UI Actions Added

Suggested verification command:

```bash
python -m pytest -k "caption or tone or style"
```

## Data Contracts

### Four-Tone Caption Set

C4 should implement this contract or a clearly equivalent typed model:

```json
{
  "scene_core_id": "stable-scene-core-id",
  "source_video_id": "stable-video-id",
  "captions": {
    "formal": {
      "text": "Neutral professional caption.",
      "tone": "formal",
      "facts_used": ["observed_actions[0]", "setting"],
      "uncertainties_preserved": []
    },
    "sarcastic": {
      "text": "Mild dry caption that keeps the same facts.",
      "tone": "sarcastic",
      "facts_used": ["observed_actions[0]", "setting"],
      "uncertainties_preserved": []
    },
    "humorous_tech": {
      "text": "Developer-friendly caption that keeps the same facts.",
      "tone": "humorous-tech",
      "facts_used": ["observed_actions[0]", "setting"],
      "uncertainties_preserved": []
    },
    "humorous_non_tech": {
      "text": "General-audience funny caption that keeps the same facts.",
      "tone": "humorous-non-tech",
      "facts_used": ["observed_actions[0]", "setting"],
      "uncertainties_preserved": []
    }
  }
}
```

### Factual Stability Rule

All four captions must be generated from the same `scene_core_id`. They may vary wording, rhythm, and tone, but they must not:

- add entities absent from the factual scene core
- add actions absent from the factual scene core
- upgrade uncertainty into fact
- use `unsupported_inferences` as caption facts
- infer private emotion, intent, motive, identity, or causality

## Tone Rubric

### Formal

Purpose:

- Provide a neutral, professional caption or summary.

Required signals:

- clear, concise, objective wording
- no jokes
- no slang
- no sarcasm
- no exaggerated adjectives

Prohibited:

- humor
- irony
- emotional mind-reading
- unsupported interpretation
- casual filler

Judge-friendly cue:

- The caption should read like a professional accessibility caption or concise report.

Failure modes:

- too playful
- too vague
- adds interpretation instead of visible fact

### Sarcastic

Purpose:

- Provide mild dry irony while preserving facts.

Required signals:

- restrained sarcasm
- obvious contrast between mundane facts and dry phrasing
- no cruelty
- no hidden references
- no new facts

Prohibited:

- insults
- mean-spirited jokes
- obscure references
- dramatic claims not supported by the scene
- sarcasm that changes what happened

Judge-friendly cue:

- An LLM judge should immediately recognize dry irony without needing cultural or insider context.

Failure modes:

- sounds merely humorous, not sarcastic
- becomes hostile
- adds invented frustration, incompetence, or intent

### Humorous-Tech

Purpose:

- Provide developer/software-flavored humor while preserving facts.

Required signals:

- accessible tech analogy
- light developer vocabulary
- no dependency on deep insider knowledge
- same factual core as the formal caption

Allowed examples of style:

- bug, deploy, loading, patch, version, queue, script, process, runtime

Prohibited:

- obscure framework jokes
- private project references
- jargon that hides the scene facts
- claims that the video contains software unless visibly true

Judge-friendly cue:

- The caption should clearly be tech-flavored even for a non-expert judge.

Failure modes:

- too technical to score
- not funny
- facts disappear behind analogy
- tech metaphor becomes a false factual claim

### Humorous-Non-Tech

Purpose:

- Provide general-audience humor while preserving facts.

Required signals:

- broadly understandable joke
- no technical vocabulary required
- no obscure cultural reference
- same factual core as the formal caption

Prohibited:

- software/developer framing
- private references
- sarcasm that overlaps too much with the sarcastic tone
- jokes that require knowing context outside the video

Judge-friendly cue:

- The caption should be clearly funny or playful to a general audience.

Failure modes:

- too similar to sarcastic
- too vague
- joke replaces factual content
- depends on external context

## Tone Separation Requirements

The four captions should be distinguishable by a judge without reading labels:

| Tone | Main Difference |
| --- | --- |
| formal | neutral/professional |
| sarcastic | mild dry irony |
| humorous-tech | tech/developer-flavored joke |
| humorous-non-tech | general-audience joke |

Do not optimize for cleverness at the expense of factual accuracy. A simple clear joke beats an ambiguous clever joke.

## Service Boundary

- Caption generation consumes the C3 factual scene core.
- Caption generation does not inspect raw private docs or implementation-pack context.
- Caption generation does not mutate the factual scene core.
- Caption generation does not evaluate or repair; C5/C6 handle that later.
- UI may display captions later, but C4 should remain usable as a service with tests.

## Provider/API Boundary

If using Fireworks/Gemma, send only public-safe scene core fields and the tone rubric. Never send secrets, private docs, local paths, implementation pack contents, or private research material as model context.

Provider output is draft text until C5 evaluates it.

## Prompt Contracts

The caption-generation prompt must:

- require exactly four captions
- require strict JSON
- include the same `scene_core_id` in output
- preserve the factual scene core
- exclude unsupported inferences
- preserve uncertainty rather than resolving it
- make tone labels explicit
- keep each caption short
- avoid obscure references
- avoid emotion, motive, identity, or causality inference unless supported by the factual core

## Tests

Add deterministic tests for:

- exactly four required keys are returned
- every caption uses the same `scene_core_id`
- no caption uses C3 `unsupported_inferences`
- captions do not add facts absent from the fixture scene core
- formal caption has no joke/sarcasm marker in stub output
- sarcastic caption is distinguishable from formal and humorous outputs
- humorous-tech contains accessible tech framing in stub output
- humorous-non-tech avoids tech framing in stub output
- malformed provider JSON fails safely
- public output contains no local paths, secrets, or private research terms

## README Update Requirements

Update README.md to reflect this gate's actual completed behavior. Do not document future gates as implemented.

The README must include current gate status, working commands only, known limitations, and planned gates as future work.

## Acceptance Criteria

- Four captions can be produced from one factual scene core in stub mode.
- Captions preserve the same factual core.
- All four tones are clearly distinguishable.
- Unsupported inferences do not become caption facts.
- JSON output is usable by C5 evaluator.

## Implementation Steps

1. Read `SKILL.md`.
2. Read `docs/README_GATE_POLICY.md`.
3. Read this execution document.
4. Inspect C3 scene core contract.
5. Define or update the caption contract.
6. Add deterministic stub tests first where practical.
7. Implement only C4 generation behavior.
8. Run the suggested verification command.
9. Update README with actual completed behavior only.
10. Report changed files, test results, risks, and next gate.

## Reviewer Confidence Signal

A reviewer should be able to see exactly how one factual scene core produced four style-specific captions, how factual stability was preserved, how tone separation was tested, and what remains deferred to C5 evaluator or later.

## Benchmark / Evidence Artifact

This gate should leave behind at least one concrete artifact:

- passing four-tone caption contract tests
- a sample C3 scene core fixture
- a sample four-caption JSON fixture
- a tone-separation test fixture
- a documented blocker with the exact provider, schema, or prompt issue

## Demo Commands

```bash
python -m pytest -k "caption or tone or style"
```

## Expected Output

A public-safe four-caption JSON object that is ready for C5 evaluator scoring.

## Failure Cases

- Captions invent details
- Formal caption includes humor
- Sarcastic caption becomes hostile or ambiguous
- Humorous-tech caption depends on obscure jargon
- Humorous-non-tech caption overlaps too much with sarcastic
- Tone labels are treated as emotion or intent inference
- Unsupported inferences leak into captions
- Provider output is malformed JSON
- README claims evaluator or repair exists before C5/C6

## Stop/Gate Criteria

Stop if tone rendering changes the factual claim set, uses unsupported inferences, weakens public-safe boundaries, removes README synchronization, or starts evaluator/repair work.

## Suggested Conventional Commit

```text
feat(captions): generate four judged tones
```
