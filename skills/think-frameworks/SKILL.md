---
name: think-frameworks
description: Analytical framework reasoning methods — 5W1H, SWOT, 5 Whys, Fishbone, PESTLE, Force Field, Decision Matrix, Pareto, Stakeholder, Cost-Benefit, Risk Assessment, Gap Analysis. Use when the user invokes `/think <framework>` or asks for structured problem definition, strategic analysis, root-cause, prioritization, decision comparison, risk, or gap analysis.
argument-hint: "[framework] <problem>"
---

# think-frameworks — Analytical Framework Reasoning Methods

## User Invocation

```
$ARGUMENTS
```

Parse these arguments. The first word should be one of this category's framework modes (`5w1h`, `swot`, `fivewhys`, `fishbone`, and later `pestle`, `forcefield`, `decisionmatrix`, `pareto`, `stakeholder`, `costbenefit`, `riskassessment`, `gapanalysis`). The rest is the problem to reason about. If invoked via the `think` router, `$ARGUMENTS` is the same string the user originally typed after `/think`.

This category skill teaches structured **analytical frameworks** — well-established business, engineering, and quality-management templates for scoping problems, assessing strategic position, finding root causes, and (in later modes) prioritizing and deciding. Unlike the free-form reasoning modes in other categories, each framework here has a fixed, named structure (a grid, a chain, a spine) that the output must fill in completely.

---

## Output Quality Rules

These rules apply to every mode in this category:

1. **Fill every field, or say "none identified."** A framework field left implicitly empty is a sign of an incomplete analysis, not a legitimately empty category. If a quadrant, category, or dimension genuinely has nothing to report, say so explicitly (e.g., `"none identified"`) rather than omitting the field or leaving an empty array with no explanation.
2. **Show scoring math for weighted modes.** Any mode that scores or weights options (future modes in this category, e.g. Decision Matrix, Pareto) must show the arithmetic — weight × score = weighted score — not just the final ranking. A bare number without its derivation cannot be checked or trusted.
3. **End with an action.** Every framework output should conclude with something actionable — a recommendation, a corrective action, a prioritized cause, a next step. A framework that only classifies without pointing toward a decision has done half the job.

### Bias Check

Before finalizing any framework output, check it against the cognitive-bias reference at `references/cognitive-biases/` (populated in Task 4 of this project). Common biases specific to this category: confirmation bias when populating SWOT opportunities/threats, availability bias when enumerating fishbone causes (favoring recently-seen causes over structurally likely ones), and premature convergence in 5 Whys (stopping at a comfortable answer instead of a genuine process-level root cause).

---

## 5W1H

5W1H is a **problem-scoping** framework — it forces a complete definition of an event or problem across six dimensions before any analysis (root-cause, strategic, or otherwise) begins.

### When to Use

- Before starting an incident investigation, to make sure the problem is fully scoped
- Briefing someone who wasn't present when the event happened
- Writing an incident summary or postmortem "what happened" section
- Any time the instinct is to jump straight to "why" before the "what/who/when/where" are nailed down

**Do not use 5W1H** when the problem is already fully scoped and the need is root-cause analysis (use `fivewhys` or `fishbone` instead) or strategic assessment (use `swot`).

### Required Fields

`mode, who, what, when, where, why, how` — all six dimensions are required. Each accepts a string or an array of strings.

### Prose Invariants

- Every one of the six dimensions must be populated — a dimension that is genuinely unknown should contain `"unknown"` or `"not yet determined"`, never be silently thin.
- `why` here is the *currently understood* reason, not a drilled-down root cause — if the user needs a root cause, hand off to `fivewhys` after scoping.

See `reference/output-formats/5w1h.md` for the authoritative schema, worked example, and verification checklist.

---

## SWOT

SWOT assesses **strategic position** by crossing two axes — Internal vs. External, and Positive vs. Negative — into a 2×2 grid: Strengths, Weaknesses, Opportunities, Threats.

### When to Use

- Evaluating whether to pursue a strategic initiative (new product, new market, new pricing model)
- Assessing a company, team, or product's competitive position
- Any "should we do this?" question where both internal capability and external environment matter

**Do not use SWOT** when the question is purely about root cause (use `fivewhys`/`fishbone`) or purely about problem scoping with no strategic dimension (use `5w1h`).

### Required Fields

`mode, strengths, weaknesses, opportunities, threats` — the four quadrant arrays.

### Prose Invariants

- **At least one item in at least two quadrants.** A SWOT with content in only one quadrant is incomplete, not legitimately lopsided — this is not schema-enforced because "at least two of four" isn't a clean per-property JSON Schema constraint, so it lives here as a prose rule.
- `strengths`/`weaknesses` must be genuinely internal (about the subject itself); `opportunities`/`threats` must be genuinely external (about the environment). Do not put a competitor's move in `weaknesses` — that's a `threat`.
- `recommendation` (optional but encouraged) should cross quadrants — e.g., use a strength to capture an opportunity, or flag where a weakness blocks an opportunity — not just restate the subject.

See `reference/output-formats/swot.md` for the authoritative schema, worked example, and verification checklist.

---

## 5 Whys

5 Whys drills from a symptom to a **single root cause** by repeatedly asking "why" — a linear chain, not a branching structure.

### When to Use

- Root-causing an incident that appears to have one linear causal chain
- Any "why did this happen" question where a single drill-down (not multiple independent categories) is expected to reach the answer

**Do not use 5 Whys** when the investigation reveals multiple independent contributing categories (people, process, tooling, environment) — use `fishbone` instead. Forcing a multi-category cause structure into a single chain produces a chain that jumps between unrelated causes at each step.

### Required Fields

`mode, problem, whys, rootCause` — `whys` is an array of `{question, answer}` pairs, `minItems: 1` (classically five, but use as many as the chain genuinely needs).

### Prose Invariants

- Each `whys[i+1].question` must ask "why" about `whys[i].answer` — the chain must actually chain, not restate the original `problem` five times with different words.
- `rootCause` must match (or closely match) the final `whys` entry's `answer`.
- `rootCause` should name a process/system-level cause, not a person — "the engineer made a mistake" is not a root cause; "no process caught the mistake before it shipped" is.

See `reference/output-formats/fivewhys.md` for the authoritative schema, worked example, and verification checklist.

---

## Fishbone (Ishikawa)

Fishbone (Ishikawa) diagrams cause analysis into **multiple independent categories** ("ribs") converging on one effect — used when a problem plausibly has causes spanning different dimensions rather than one linear chain.

### When to Use

- Cause analysis needing multiple cause **categories** (people, process, tooling, environment, etc.) rather than a single linear drill-down
- Enumerating the full landscape of candidate causes before prioritizing which to address first
- Quality/manufacturing-style root-cause analysis using the classic "6Ms" (Manpower, Method, Machine, Material, Measurement, Environment) or a domain-appropriate variant (e.g., People, Process, Technology, Environment for software contexts)

**Do not use Fishbone** when the causation is a single linear chain — use `fivewhys` instead, which drills deeper rather than enumerating breadth.

### Required Fields

`mode, effect, categories` — `categories` is an array of `{name, causes[]}` objects, `minItems: 1`.

### Prose Invariants

- Category names must reflect genuinely distinct dimensions — do not split one cause across two categories, and do not create a category that only restates `effect`.
- `primaryCauses` (optional), if present, must cross-reference causes that also appear verbatim within `categories[].causes[]` — it highlights priority causes, it does not introduce new ones.
- Causes must be specific and evidence-based — "process issues" is too generic; name the actual broken process.

See `reference/output-formats/fishbone.md` for the authoritative schema, worked example, and verification checklist.

---

## Choosing Among These Four

- Problem not yet fully scoped? → **5w1h** first, always.
- Scoped, and the question is strategic position (should we do this, given internal + external factors)? → **swot**.
- Scoped, and the question is root cause with one expected linear chain? → **fivewhys**.
- Scoped, and the question is root cause with multiple expected independent categories? → **fishbone**.

These four often chain together in a real investigation: `5w1h` to scope an incident, then `fivewhys` or `fishbone` to find the cause, with `swot` reserved for the separate question of whether/how to respond strategically once the cause is known.
