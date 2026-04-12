# Inductive Thought — Output Format

Reasoning from specific observations to general principles.

## JSON Schema

```json
{
  "mode": "inductive",
  "observations": ["<specific case 1>", "<specific case 2>", ...],
  "pattern": "<identified pattern across observations, optional>",
  "generalization": "<the general principle derived>",
  "confidence": <number 0-1>,
  "counterexamples": ["<known exception 1>", ...],
  "sampleSize": <integer, optional>
}
```

## Required Fields

- `mode` — always `"inductive"`
- `observations` — at least one specific observation
- `generalization` — the inferred general principle
- `confidence` — strength of the inference in [0, 1]

## Worked Example

Input: "Given these three incidents, what pattern do they share?"

Context observed:
- Deploy on Monday 2026-04-06 failed with DB connection timeout
- Deploy on Wednesday 2026-04-08 failed with DB connection timeout
- Deploy on Friday 2026-04-10 failed with DB connection timeout

Output:

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

## Verification Checklist

Before emitting, verify:
- `mode` is exactly `"inductive"`
- `observations` has at least 1 entry
- `confidence` is in [0, 1]
- `confidence` should be lower when `sampleSize` is small or when `counterexamples` exist
- `generalization` is logically supported by the observations (not a leap)
