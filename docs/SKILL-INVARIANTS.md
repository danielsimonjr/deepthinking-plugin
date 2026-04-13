# Per-Mode Skill Invariants — Validation Rules JSON Schema Cannot Enforce

This document catalogs the validation rules that live in `skills/think-<category>/SKILL.md` prose because JSON Schema lacks the expressive power to encode them. They are enforced **only by the model following the skill prompt** — there is no test harness that catches violations.

When editing a SKILL.md file, preserve any "must" / "exactly one" / "at least N" language — those are load-bearing invariants the schema cannot catch.

## Why JSON Schema can't express these

JSON Schema is the source of truth for what *shape* a thought must have, but it cannot express:

- **Exactly N of something** — e.g., "exactly one element of `possibleWorlds` has `isActual: true`"
- **Distinctness across array elements** — e.g., "at least two hypotheses with non-equal scores"
- **Cross-field semantic constraints** — e.g., "the conclusion's confidence must not exceed the lowest premise confidence"
- **Domain-specific minimums** — e.g., "synthesis of one source is summary, not synthesis"

These rules live as written instructions in the relevant `skills/think-<category>/SKILL.md` files. They exist as English prose in the skill body, not as JSON Schema constraints.

## The invariants (per mode)

### Cardinality and distinctness rules

| Mode | Invariant | Skill file | Schema status |
|---|---|---|---|
| `abductive` | ≥2 distinct hypotheses with non-equal scores; a single hypothesis is not abduction | `skills/think-core/SKILL.md` | Schema has only `minItems: 1` on hypotheses (under-constrained) |
| `counterfactual` | Exactly one condition marked `isIntervention: true`; multiple simultaneous interventions break isolation and make the analysis unfalsifiable | `skills/think-causal/SKILL.md` | Not expressible in JSON Schema |
| `historical` | ≥2 distinct episodes per pattern; one episode is anecdote, not pattern | `skills/think-temporal/SKILL.md` | Schema has `patterns.items.episodes.minItems: 1` (under-constrained) |
| `modal` | Exactly one world in `possibleWorlds` has `isActual: true`, enforcing a single ground truth | `skills/think-advanced/SKILL.md` | Not expressible in JSON Schema |
| `gametheory` | ≥2 players (single-agent decision problems must use `optimization` instead) | `skills/think-strategic/SKILL.md` | Schema enforces `players.minItems: 2` (already covered) |
| `synthesis` | ≥2 sources (synthesis of one source is summary, not synthesis) | `skills/think-academic/SKILL.md` | Schema enforces `sources.minItems: 2` (already covered) |
| `engineering` | Trade studies require ≥2 alternatives | `skills/think-engineering/SKILL.md` | Schema enforces `tradeStudy.alternatives.minItems: 2` (already covered) |

The first four rows (`abductive`, `counterfactual`, `historical`, `modal`) are **schema-unenforceable** — only the model following the SKILL.md prose keeps them honest. The last three rows (`gametheory`, `synthesis`, `engineering`) are listed for completeness; they happen to be enforced by `minItems` in their schemas.

### Cross-field semantic rules

| Mode | Invariant | Skill file |
|---|---|---|
| `firstprinciples` | The conclusion's confidence must not exceed the lowest confidence value of any principle cited in the derivation chain | `skills/think-analytical/SKILL.md` |
| `bayesian` | The `posterior.calculation` field must show full arithmetic (e.g. `0.6 × 0.8 / (0.6 × 0.8 + 0.4 × 0.2) = 0.857`), not just the final result — readers and verifiers need to check the math | `skills/think-probabilistic/SKILL.md` |

These are correctness rules that depend on values across multiple fields, which JSON Schema cannot validate without custom keyword extensions.

## How to apply this list

### When editing a SKILL.md file

- Search for the words `must`, `exactly one`, `at least`, `distinct`, `non-equal`, and `≥` in the existing text before making changes
- Each occurrence is likely a load-bearing invariant — preserve the wording even if rewriting the surrounding prose
- If intentionally rewriting an invariant, add a corresponding test sample to `test/samples/<mode>-invalid.json` that exercises the rule, so a future regression is caught at the smoke-test layer

### When adding a new mode

- Decide whether the mode has cardinality or distinctness invariants
- Encode whatever can be encoded in the JSON Schema (`minItems`, `const`, `enum`)
- Document the rest as explicit `must` clauses in the SKILL.md template
- Add a row to this document so the rule is not lost

### When debugging a smoke-test failure that "looks valid but feels wrong"

- Check this list — the failure may be a violation of an unenforceable invariant that the schema accepted
- Example: a `counterfactual` thought with two interventions will pass schema validation but is semantically broken; only the SKILL.md "exactly one `isIntervention`" rule catches it

## Distinction from schema bugs

Schema bugs (relaxed nested `additionalProperties: false`, `null` on optional scalars, expanded enums) are cases where the schema is **wrong** and rejects legitimate Claude output. The invariants in this document are different: they are cases where the schema is **correct but under-constrained** — it accepts output that is structurally valid but semantically broken.

Different problem, different fix:

- **Schema bugs** → relax the schema
- **Schema-unenforceable invariants** → tighten the SKILL.md prose, accept that automated tests cannot catch all of them, document the rules here so future contributors preserve them

## See also

- `CLAUDE.md` design principle: "Some validation rules live in SKILL.md prose, not in JSON Schema"
- `docs/ROADMAP-FUTURE-MODES-AND-FORMATS.md` "Strategic gaps" section for the related "no automated check for cross-field semantic rules" gap
- The schema files at `test/schemas/<mode>.json` are the source of truth for what *shape* a thought must have; this document is the source of truth for what *additional rules* the SKILL.md prose enforces beyond the schema
