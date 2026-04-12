---
name: think-core
description: Core reasoning triad — Inductive, Deductive, and Abductive. Use when the user invokes `/think inductive`, `/think deductive`, or `/think abductive`, or asks to generalize from examples, derive conclusions from rules, or find the best explanation for observations. In v0.1.0 this skill contains Inductive and Deductive; Abductive ships in a future version.
---

# think-core — Core Reasoning Triad

This category skill contains two of the three fundamental reasoning patterns: **Inductive** (specific → general) and **Deductive** (general → specific). **Abductive** (inference to the best explanation) will join this skill in a future version.

---

## Inductive Reasoning

Inductive reasoning moves from specific observations to general principles. You observe several cases, identify a pattern, and form a generalization whose confidence depends on the breadth and consistency of the observations.

### When to Use

- You have multiple specific examples and want to extract a pattern
- Finding trends across incidents, deployments, user behaviors, or measurements
- Forming a hypothesis that more observations could strengthen or refute
- Moving from particular cases to a rule

**Do not use Inductive** when:
- You have premises and want formal logical inference → use Deductive
- You have only one case → use Sequential or ask for more observations
- The generalization is already stated and you're evaluating it → use Deductive or Bayesian (future)

### How to Reason Inductively

1. **List every observation.** Do not summarize prematurely. Each observation is a concrete, specific case.
2. **Look for the invariant.** What is true in every observation? What varies?
3. **State the pattern.** A short phrase naming the invariant.
4. **Form the generalization.** One sentence extending the pattern beyond the observed cases.
5. **Assess confidence.** A number in [0, 1] reflecting strength of inference. Consider:
   - **Sample size** — more observations → higher confidence (within reason)
   - **Homogeneity** — if observations vary in relevant ways, the generalization is stronger
   - **Counterexamples** — any known cases where the pattern fails
6. **Note counterexamples.** Known exceptions lower confidence and narrow the generalization's scope.

### Output Format

See `reference/output-formats/inductive.md` for the authoritative JSON schema.

### Quick Template

```json
{
  "mode": "inductive",
  "observations": ["<case 1>", "<case 2>", "<case 3>"],
  "pattern": "<invariant in short form>",
  "generalization": "<general principle in one sentence>",
  "confidence": <0.0 to 1.0>,
  "counterexamples": [<optional known exceptions>],
  "sampleSize": <optional integer>
}
```

### Verification Before Emitting

- `mode` is exactly `"inductive"`
- `observations` has at least one entry (ideally ≥3)
- `confidence` is in [0, 1]
- `confidence` is lower when `sampleSize` is small OR `counterexamples` are present
- `generalization` is logically supported by the observations, not a leap
- `pattern` (if included) actually appears in every observation

### Worked Example

Input: "Given these three incidents, what pattern do they share? (1) Deploy on Mon 2026-04-06 failed with DB connection timeout. (2) Deploy on Wed 2026-04-08 failed with DB connection timeout. (3) Deploy on Fri 2026-04-10 failed with DB connection timeout."

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

Natural-language summary: "Three identical failures with no variation across day-of-week is a strong signal of a structural issue, not flakiness. Confidence is 0.85 (not 1.0) because n=3 is still small and we have not yet ruled out external factors like upstream DNS changes."

---

## Deductive Reasoning

Deductive reasoning moves from established premises to specific conclusions. If the premises are true and the form is valid, the conclusion must be true.

### When to Use

- You have explicit rules or premises and want to derive a conclusion
- Applying a policy to a specific case
- Formal logical inference (modus ponens, modus tollens, syllogisms)
- Verifying whether a claim follows from stated assumptions

**Do not use Deductive** when:
- You have uncertain premises (the conclusion inherits that uncertainty — consider Bayesian in a future version)
- You are deriving rules from observations → use Inductive
- The conclusion is plausible but not logically forced → you may be pattern-matching, not deducing

### Validity vs. Soundness

Two separate questions:

- **Validity** — Does the conclusion logically follow from the premises? (Logical form)
- **Soundness** — Validity PLUS the premises are actually true in the real world. (Form + truth)

A deduction can be valid but unsound. Example:
- Premise 1: "All unicorns can fly."
- Premise 2: "Sparky is a unicorn."
- Conclusion: "Sparky can fly."

This is **valid** (the logic is impeccable) but **unsound** (the premises are false).

### How to Reason Deductively

1. **List the premises.** Each as a clear statement.
2. **Identify the logical form.** Common forms:
   - **Modus ponens:** If P then Q. P. Therefore Q.
   - **Modus tollens:** If P then Q. Not Q. Therefore not P.
   - **Hypothetical syllogism:** If P then Q. If Q then R. Therefore if P then R.
   - **Categorical syllogism:** All A are B. X is A. Therefore X is B.
3. **Check validity.** Does the conclusion follow by logical form alone?
4. **Check soundness** (if you can). Are the premises actually true?
5. **State the conclusion** explicitly.

### Output Format

See `reference/output-formats/deductive.md` for the authoritative JSON schema.

### Quick Template

```json
{
  "mode": "deductive",
  "premises": ["<premise 1>", "<premise 2>"],
  "conclusion": "<the derived conclusion>",
  "logicForm": "<e.g., modus ponens>",
  "validityCheck": <true or false>,
  "soundnessCheck": <true, false, or omit if unknown>
}
```

### Verification Before Emitting

- `mode` is exactly `"deductive"`
- `premises` has at least one entry
- `validityCheck` is `true` ONLY if the conclusion *necessarily* follows from the premises
- If `validityCheck: false`, the conclusion is not actually entailed — flag this in the natural-language summary
- `soundnessCheck` is `true` only if you can actually verify the premises are true; otherwise omit

### Worked Example

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

Natural-language summary: "Classic modus ponens. The premises entail the conclusion by logical form, and both premises are stated as given, so soundness is also true. Alice can edit posts."

---

## Future Methods (not in v0.1.0)

- **Abductive** — Inference to the best explanation. Generate candidate hypotheses for a surprising observation and evaluate them against parsimony, explanatory power, plausibility, and testability.

This ships in a future version of this skill.
