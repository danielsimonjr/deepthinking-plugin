---
name: think
description: Route a reasoning task to the appropriate thinking mode. Use when the user invokes `/think <mode?> "<problem>"` or asks for structured reasoning, critical analysis, Bayesian inference, causal analysis, inductive/deductive reasoning, hypothesis formation, or any form of disciplined thinking. Supports explicit mode selection (e.g., `/think bayesian ...`) and auto-recommendation (`/think ...`).
argument-hint: "[mode] <problem>"
---

# Think — Reasoning Router

## User Invocation

The user invoked this skill with the following arguments:

```
$ARGUMENTS
```

Parse the arguments above. The first word may be a mode name (`sequential`, `inductive`, or `deductive`). Everything else is the problem statement. If the first word is NOT one of the recognized modes, treat the entire argument string as a problem statement and auto-recommend a mode per the decision tree in `mode-index.md`.

---

This skill routes a reasoning task to the appropriate category skill containing the relevant method(s). Your job as the router is:

1. **Parse the invocation.** Look for a mode name in the arguments. If the user wrote `/think bayesian "..."`, the mode is `bayesian`.
2. **Load the right category skill.** Each category skill holds 2-4 reasoning methods. Use the mapping in `mode-index.md`.
3. **Apply the method.** Once the category skill is loaded, follow its instructions to produce structured output matching the mode's JSON schema.
4. **Emit the structured output.** Every reasoning output MUST be a valid JSON object matching the schema in `reference/output-formats/<mode>.md`.

## Available Modes (v0.1.0)

Only three modes are available in this version. The remaining 31 ship in later versions.

| Mode | Category skill | Use when |
|---|---|---|
| `sequential` | `think-standard` | Breaking a complex problem into ordered steps, iterative planning, revision-friendly workflows |
| `inductive` | `think-core` | Forming general principles from specific observations; pattern recognition across cases |
| `deductive` | `think-core` | Drawing specific conclusions from established premises; formal logical inference |

## Invocation Patterns

### Explicit mode

    /think sequential "Break down the steps to migrate this database"
    /think inductive "Given these three incidents, what pattern do they share?"
    /think deductive "If all users in admin can edit posts and Alice is in admin, can Alice edit posts?"

If the user provided an explicit mode name, load the corresponding category skill and apply that method.

### Auto-recommend (no mode specified)

    /think "Why did the last three deployments fail?"

If no mode is specified, read `mode-index.md` for the decision tree and pick the mode whose shape best matches the problem. Explain your choice to the user in one sentence before producing the structured output.

### Unavailable mode in v0.1.0

If the user names a mode not yet available (e.g., `/think bayesian`), respond:

> "The `<mode>` mode is not yet available in v0.1.0 of deepthinking-plugin. Currently available: sequential, inductive, deductive. The router will auto-recommend one of these for your problem instead."

Then proceed with auto-recommendation.

## Output Format Contract

Every reasoning output from this plugin follows a consistent pattern:

1. **One sentence of meta** explaining which mode was chosen (only for auto-recommend cases).
2. **A JSON code block** containing the structured thought matching the mode's schema.
3. **A short natural-language summary** (2-4 sentences) explaining the reasoning for humans.

Example of a well-formed response to `/think inductive "..."`:

    Using inductive reasoning to generalize from the three observed incidents.

    ```json
    {
      "mode": "inductive",
      "observations": ["..."],
      "generalization": "...",
      "confidence": 0.85,
      "sampleSize": 3
    }
    ```

    The three deploy failures all occurred at the same phase with identical symptoms, which supports a strong generalization that the issue is upstream of DB connection handling. Confidence is 0.85 because the sample is small (n=3) and we have not yet ruled out confounders.

## Decision Tree Reference

For auto-recommendation, consult `skills/think/mode-index.md`.

## Output-Format References

For the JSON schema and verification checklist for each mode, see:
- `reference/output-formats/sequential.md`
- `reference/output-formats/inductive.md`
- `reference/output-formats/deductive.md`
