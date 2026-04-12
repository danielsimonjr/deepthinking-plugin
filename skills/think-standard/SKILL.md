---
name: think-standard
description: Standard sequential and iterative reasoning methods. Use when the user invokes `/think sequential` or asks to break down a complex task into ordered steps, iterate on a plan, or revise earlier thinking. In v0.1.0 this skill contains only the Sequential method; Shannon and Hybrid ship in future versions.
argument-hint: "[sequential] <problem>"
---

# think-standard — Standard Sequential Reasoning Methods

## User Invocation

```
$ARGUMENTS
```

Parse these arguments. The first word should be `sequential` (or omitted if invoked via the `think` router). The rest is the problem to reason about.

This category skill contains the **Sequential** reasoning method. Shannon and Hybrid will join this skill in a future version.

---

## Sequential Reasoning

Sequential reasoning is general-purpose iterative thinking: break a problem into a chain of thoughts, each building on the previous, with the ability to revise or branch as understanding deepens.

### When to Use

- Breaking a complex task into ordered steps
- Planning a multi-step workflow (refactor, migration, investigation)
- Iterating on an approach where earlier thoughts may need revision
- Situations that benefit from explicit step-tracking

**Do not use Sequential** when:
- The user wants a pattern from multiple observations → use Inductive
- The user wants formal logical inference from premises → use Deductive
- The user wants a probabilistic belief update → (use Bayesian in a future version)

### How to Think Sequentially

1. **Assess total scope.** Estimate `totalThoughts` — how many steps you expect this will take. It's fine to adjust later.
2. **Produce thought N.** Each thought is a single logical step. Keep it focused on one idea or action.
3. **Track dependencies.** If thought N builds on an earlier thought, reference its id in `dependencies`.
4. **Revise if needed.** If a later thought invalidates an earlier one, set `isRevision: true`, set `revisesThought` to the earlier thought's id, and explain in `revisionReason`.
5. **Branch if exploring alternatives.** Use `branchFrom` and `branchId` to explore a parallel line of thinking without abandoning the main chain.
6. **Emit the structured output.** Follow the schema in `reference/output-formats/sequential.md`.
7. **Continue if more is needed.** Set `nextThoughtNeeded: true` when the reasoning is not complete. Set it to `false` only when the chain has reached a conclusion.

### Output Format

See `reference/output-formats/sequential.md` for the authoritative JSON schema, worked example, and verification checklist.

### Quick Template

```json
{
  "mode": "sequential",
  "thoughtNumber": 1,
  "totalThoughts": <your estimate>,
  "content": "<this thought as natural language>",
  "nextThoughtNeeded": <true if more steps remain>,
  "dependencies": [<ids of earlier thoughts this builds on>]
}
```

### Verification Before Emitting

- `mode` is exactly `"sequential"`
- `thoughtNumber` ≤ `totalThoughts`
- `content` is a complete sentence, not a stub
- `nextThoughtNeeded` is a boolean
- If `isRevision: true`, then `revisesThought` is set

### Worked Example

Input: "Break down the steps to migrate our Postgres database to a new region."

Output (thought 1 of a chain):

```json
{
  "mode": "sequential",
  "thoughtNumber": 1,
  "totalThoughts": 4,
  "content": "First, inventory the services that touch the database. We need to know everything that will need its connection string updated: API, workers, cron jobs, and any dashboards.",
  "nextThoughtNeeded": true,
  "dependencies": []
}
```

Natural-language summary: "I'm treating this as a four-step migration plan. Step 1 is service inventory — without knowing what connects to the DB, any migration plan is incomplete."

---

## Future Methods (not in v0.1.0)

- **Shannon** — Information-theoretic problem decomposition. Uses entropy to measure reducible uncertainty.
- **Hybrid** — Combines multiple modes for cross-cutting problems.

These ship in a future version of this skill.
