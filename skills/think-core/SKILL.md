---
name: think-core
description: Core reasoning triad — Inductive, Deductive, and Abductive. Use when the user invokes `/think inductive`, `/think deductive`, or `/think abductive`, or asks to generalize from examples, derive conclusions from rules, or find the best explanation for observations.
argument-hint: "[inductive|deductive|abductive] <problem>"
---

# think-core — Core Reasoning Triad

## User Invocation

```
$ARGUMENTS
```

Parse these arguments. The first word should be `inductive`, `deductive`, or `abductive`. The rest is the problem to reason about. If invoked via the `think` router, `$ARGUMENTS` is the same string the user originally typed after `/think`.

This category skill contains all three fundamental reasoning patterns: **Inductive** (specific → general), **Deductive** (general → specific), and **Abductive** (inference to the best explanation).

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

## Abductive Reasoning

Abductive reasoning moves from surprising observations to the best available explanation. Unlike induction (which generalizes from cases) or deduction (which derives conclusions from rules), abduction asks: "What hypothesis, if true, would best explain what I am seeing?" You generate multiple candidate explanations and select the most plausible one.

### When to Use

- You have a surprising or anomalous observation that needs to be explained
- Diagnosing a bug, incident, or system failure where root cause is unknown
- Multiple causes are possible and you need to rank them before investigating
- You want to generate testable predictions from each candidate explanation
- "Why is this happening?" problems — not "what follows?" (deductive) or "what pattern is here?" (inductive)

**Do not use Abductive** when:
- You have only one plausible explanation and no alternatives — you are not choosing between hypotheses
- You have an established rule and want to apply it to a case → use Deductive
- You are extracting a pattern from repeated observations → use Inductive
- The problem is open-ended brainstorming with no observable phenomenon to explain → use Sequential or a different mode

### How to Reason Abductively

1. **State the surprising observation.** Describe what you observed, why it is unexpected, and your confidence in the observation itself.
2. **Generate at least two hypotheses.** Each hypothesis must: (a) actually explain the observation if true, and (b) differ from the others in its assumptions. Do not stop at one — the core move of abduction is comparison.
3. **List each hypothesis's assumptions.** These are the background claims the hypothesis depends on. Explicit assumptions make each hypothesis falsifiable.
4. **Derive testable predictions.** For each hypothesis, what would you expect to find if that hypothesis were true? Good predictions are specific and discriminating — different hypotheses should predict different things.
5. **Collect and classify evidence.** For each piece of available evidence, note which hypothesis it supports, contradicts, or is neutral toward, and how strongly.
6. **Score each hypothesis.** A number in [0, 1] reflecting overall plausibility after weighing the evaluation criteria. Scores must be distinct — ties indicate the evaluation is unfinished.
7. **Apply the evaluation criteria.** Score the overall analysis on four dimensions:
   - **Parsimony** — Does the best hypothesis avoid unnecessary assumptions? (Occam's Razor)
   - **Explanatory power** — Does it account for all observations, or only some?
   - **Plausibility** — Is the hypothesis consistent with what is already known about the system?
   - **Testability** — Can the hypothesis be checked with feasible observations or experiments?
8. **Name the best explanation.** Choose the highest-scoring hypothesis as `bestExplanation`. If scores are close (gap < 0.05), flag the ambiguity explicitly in your natural-language summary.

### Output Format

See `reference/output-formats/abductive.md` for the authoritative JSON schema.

### Quick Template

```json
{
  "mode": "abductive",
  "observations": [
    { "id": "o1", "description": "<what was observed>", "confidence": 0.9 }
  ],
  "hypotheses": [
    {
      "id": "h1",
      "explanation": "<candidate explanation A>",
      "assumptions": ["<assumption 1>", "<assumption 2>"],
      "predictions": ["<testable prediction 1>"],
      "score": 0.0
    },
    {
      "id": "h2",
      "explanation": "<candidate explanation B>",
      "assumptions": ["<assumption 1>"],
      "predictions": ["<testable prediction 1>"],
      "score": 0.0
    }
  ],
  "evaluationCriteria": {
    "parsimony": 0.0,
    "explanatoryPower": 0.0,
    "plausibility": 0.0,
    "testability": true
  },
  "evidence": [],
  "bestExplanation": null
}
```

### Verification Before Emitting

- `mode` is exactly `"abductive"`
- `observations` has at least one entry with `id`, `description`, and `confidence` in [0, 1]
- `hypotheses` has at least **two** entries — a single hypothesis is an assumption, not abductive reasoning
- All hypothesis `score` values are distinct and non-equal — update scoring if any two are identical
- The highest-scoring hypothesis and `bestExplanation` point to the same `id` (unless explicitly overridden)
- `evaluationCriteria` is fully populated with all four fields
- `parsimony` reflects assumption count — hypotheses with fewer assumptions score higher
- `explanatoryPower` reflects how many observations the best hypothesis accounts for
- If any `evidence` is available, it is listed with correct `hypothesisId` references

### Worked Example

Input: "Users on the analytics dashboard are seeing 503 errors, but ONLY on Tuesday mornings between 9–10 AM. What's the best explanation?"

Three hypotheses were generated:
- **h1** (score 0.82): A weekly ETL/scheduled job fires at 09:00 every Tuesday and saturates the database
- **h2** (score 0.71): The weekly BI report pipeline materializes data at 09:00, causing table lock contention
- **h3** (score 0.54): Application cache is flushed Monday night, causing a cold-start stampede Tuesday morning

Evidence collected:
- Application logs confirm a `weekly_etl_job` entry at 09:00:02 every Tuesday — **supporting h1** (strength 0.85)
- Database slow-query log shows a 47-minute INSERT…SELECT on `report_snapshots` starting at 09:00 — **supporting h2** (strength 0.78)
- Cache monitoring shows hit rates normal (>90%) at 9 AM Tuesday — **contradicting h3** (strength 0.72)

Output:

```json
{
  "mode": "abductive",
  "observations": [
    { "id": "o1", "description": "Analytics dashboard returns 503 errors exclusively on Tuesday mornings between 9:00 AM and 10:00 AM", "confidence": 0.97 },
    { "id": "o2", "description": "Error rate returns to zero by 10:05 AM with no manual intervention", "confidence": 0.95 },
    { "id": "o3", "description": "Affected endpoint is /api/reports/dashboard — other API endpoints remain healthy during the same window", "confidence": 0.92 },
    { "id": "o4", "description": "Database CPU spikes to 95% during the 9–10 AM Tuesday window; normal the rest of the week", "confidence": 0.88 }
  ],
  "hypotheses": [
    {
      "id": "h1",
      "explanation": "A weekly scheduled ETL job runs at 9 AM every Tuesday and saturates the database, crowding out dashboard queries",
      "assumptions": ["A cron job fires at 09:00 on Tuesdays specifically", "The job issues heavy queries that compete with dashboard traffic", "The connection pool is shared between the job and the dashboard API"],
      "predictions": ["Cron job logs show a Tuesday 09:00 entry", "Disabling the job would eliminate the 503 window"],
      "score": 0.82
    },
    {
      "id": "h2",
      "explanation": "Weekly BI report materialization at 09:00 causes write-heavy lock contention on the reports table",
      "assumptions": ["BI pipeline writes to the same table the dashboard reads", "Table-level locks are held during materialization"],
      "predictions": ["Lock-wait logs show contention on the reports table on Tuesdays 09:00–10:00"],
      "score": 0.71
    },
    {
      "id": "h3",
      "explanation": "Cache flushed Monday night causes a cold-start stampede when users arrive Tuesday morning",
      "assumptions": ["Dashboard cache is cleared on Monday nights", "User surge at 9 AM Tuesday overwhelms the DB on cache miss"],
      "predictions": ["Cache hit rates near zero Tuesday 9–9:30 AM"],
      "score": 0.54
    }
  ],
  "evaluationCriteria": {
    "parsimony": 0.75,
    "explanatoryPower": 0.88,
    "plausibility": 0.82,
    "testability": true
  },
  "evidence": [
    { "hypothesisId": "h1", "type": "supporting", "description": "weekly_etl_job log entries confirmed at 09:00:02 every Tuesday for six weeks", "strength": 0.85 },
    { "hypothesisId": "h2", "type": "supporting", "description": "Slow-query log shows 47-minute INSERT…SELECT on report_snapshots starting at 09:00 Tuesdays", "strength": 0.78 },
    { "hypothesisId": "h3", "type": "contradicting", "description": "Cache hit rates normal (>90%) at 9 AM Tuesday — no cold-start stampede", "strength": 0.72 }
  ],
  "bestExplanation": {
    "id": "h1",
    "explanation": "A weekly scheduled ETL job runs at 9 AM every Tuesday and saturates the database, crowding out dashboard queries",
    "assumptions": ["A cron job fires at 09:00 on Tuesdays specifically", "The job issues heavy queries that compete with dashboard traffic", "The connection pool is shared between the job and the dashboard API"],
    "predictions": ["Cron job logs show a Tuesday 09:00 entry", "Disabling the job would eliminate the 503 window"],
    "score": 0.82
  }
}
```

Natural-language summary: "h1 is the best explanation: direct log evidence places the ETL job at exactly 09:00:02 every Tuesday, the database CPU spike aligns precisely with the error window, and the self-healing by 10:05 AM matches the expected job completion time. h2 is credible but explains lock contention rather than outright DB saturation — the two causes may coexist, but h1 has more direct support. h3 is ruled out by the cache hit-rate data. Next step: reschedule the ETL job to 06:00 AM Tuesday and monitor."
