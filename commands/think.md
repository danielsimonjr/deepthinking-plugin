---
description: "Apply a structured reasoning method to a problem. Usage: /think [mode] \"<problem>\" where mode is sequential, inductive, deductive, or omitted for auto-recommend."
argument-hint: "[mode] <problem>"
---

The user invoked `/think` with these arguments:

```
$ARGUMENTS
```

## What to do

Parse the arguments above. The first word may be one of the three available modes in v0.1.0:

- **`sequential`** — Iterative step-by-step reasoning. Breaking down a task into ordered thoughts with revision support.
- **`inductive`** — Reasoning from specific observations to general principles. Pattern recognition across cases.
- **`deductive`** — Reasoning from established premises to specific conclusions. Formal logical inference.

If the first word is a recognized mode name, apply that method. If the first word is NOT a mode name (or no mode was given), treat the entire `$ARGUMENTS` as the problem and auto-recommend a mode using the decision tree below.

## Method Instructions

Load the relevant category skill for background on the method:

- **Sequential** → read `skills/think-standard/SKILL.md` in this plugin for the method description
- **Inductive, Deductive** → read `skills/think-core/SKILL.md` for the method descriptions

Then read `reference/output-formats/<mode>.md` for the authoritative JSON schema the output must match.

## Auto-Recommendation Decision Tree

If no mode was specified, pick one using these signals:

1. **Multiple observations provided, asking for pattern?** → `inductive`
   - Signals: "what pattern", "in general", "these all show", "the last N X"
2. **Explicit premises, asking if a conclusion follows?** → `deductive`
   - Signals: "if X then Y", "given these rules", "can we conclude"
3. **Complex task needing ordered steps or planning?** → `sequential`
   - Signals: "break down", "plan", "steps to", "how should I approach"
4. **None of the above clear?** → default to `sequential` and explain you're treating it as iterative planning.

## Output Format

Every response from `/think` MUST follow this structure:

1. **One sentence of meta** — explain which mode was chosen and (if auto-recommend) why.
2. **A JSON code block** containing the structured thought matching the mode's schema.
3. **A short natural-language summary** (2-4 sentences) explaining the reasoning for humans.

### Example response

Using inductive reasoning to generalize from the three observed deployment failures.

```json
{
  "mode": "inductive",
  "observations": [
    "Deploy on Monday 2026-04-06 failed with DB connection timeout",
    "Deploy on Wednesday 2026-04-08 failed with DB connection timeout",
    "Deploy on Friday 2026-04-10 failed with DB connection timeout"
  ],
  "pattern": "All recent deploys fail at the DB connection phase",
  "generalization": "Recent production deploys consistently fail at the DB connection phase, suggesting a configuration or network issue introduced prior to 2026-04-06",
  "confidence": 0.85,
  "sampleSize": 3
}
```

The three deploy failures all occurred at the same phase with identical symptoms, which supports a strong generalization that the issue is upstream of DB connection handling. Confidence is 0.85 because the sample is small (n=3) and we have not yet ruled out confounders.

## Schema References

| Mode | Output schema |
|---|---|
| sequential | `reference/output-formats/sequential.md` |
| inductive | `reference/output-formats/inductive.md` |
| deductive | `reference/output-formats/deductive.md` |

## Unavailable modes

If the user names a mode not in v0.1.0 (e.g., `bayesian`, `causal`, `gametheory`), respond:

> "The `<mode>` mode is not yet available in v0.1.0 of deepthinking-plugin. Currently available: sequential, inductive, deductive. Auto-recommending one of these for your problem instead."

Then proceed with auto-recommendation.
