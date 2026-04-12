# Deductive Thought — Output Format

Reasoning from general principles to specific conclusions. Classic logical inference (modus ponens, modus tollens, syllogisms).

## JSON Schema

```json
{
  "mode": "deductive",
  "premises": ["<general principle 1>", "<general principle 2>", ...],
  "conclusion": "<the specific conclusion>",
  "logicForm": "<e.g., 'modus ponens', 'modus tollens', 'syllogism', optional>",
  "validityCheck": <boolean>,
  "soundnessCheck": <boolean, optional>
}
```

## Required Fields

- `mode` — always `"deductive"`
- `premises` — at least one premise
- `conclusion` — the derived conclusion
- `validityCheck` — does the conclusion logically follow from the premises (true/false)?

## Key Distinction: Validity vs Soundness

- **Valid** means: IF the premises are true, the conclusion must be true. Validity is about logical form.
- **Sound** means: valid AND the premises are actually true. Soundness is about real-world truth.

## Worked Example

Input: "If all users in the admin group can edit posts, and Alice is in the admin group, can Alice edit posts?"

Output:

```json
{
  "mode": "deductive",
  "premises": [
    "All users in the admin group can edit posts",
    "Alice is in the admin group"
  ],
  "conclusion": "Alice can edit posts",
  "logicForm": "modus ponens",
  "validityCheck": true,
  "soundnessCheck": true
}
```

## Verification Checklist

Before emitting, verify:
- `mode` is exactly `"deductive"`
- `premises` has at least 1 entry
- `validityCheck` reflects whether the conclusion *necessarily* follows (not whether it's plausible)
- If you cannot verify premises are true in the real world, omit `soundnessCheck` or set it to the user's stated assumption
