# Fold reasoning-skill + algorithm-skill into deepthinking as first-class /think modes — Design

## Goal

Absorb the two standalone skills `reasoning-skill` and `algorithm-skill` into the
deepthinking-plugin as **13 new `/think` modes**, each carrying the full per-mode
artifact set the plugin's invariant requires. After this, everything reasoning/analytical/
algorithmic is reachable through the one `/think` system, and the two standalone
local-marketplace plugins are retired. Mode count goes **34 → 46**.

## Motivation

`reasoning-skill` (12 analytical frameworks + a 110-type reasoning taxonomy + a
cognitive-bias system) and `algorithm-skill` (CLRS algorithm/data-structure selection +
a Shinka evolutionary-optimization workflow) overlap and sit beside the deepthinking
`/think` modes. Consolidating removes the overlap, gives every method one uniform,
schema-validated, visualizable output contract, and leaves a single home for reasoning
knowledge.

## Scope decisions (settled)

- **Only net-new content becomes modes.** reasoning-skill's *reasoning modes*
  (inductive, deductive, abductive, causal, bayesian, gametheory, systemsthinking, etc.)
  ALREADY exist in deepthinking (`think-core`, `think-causal`, `think-probabilistic`,
  `think-strategic`, `think-scientific`). They are **not** duplicated. The net-new content
  is the **12 analytical frameworks** and the **algorithmic selection** method.
- **Output treatment: full JSON schemas** — each new mode is uniform with the existing 34
  (schema + sample + grammar + output-format + category skill + router + mode-index +
  taxonomy + smoke prompt + dashboard name). No second/parallel class.
- **Cognitive-bias system → reference, NOT a mode.** It is a cross-cutting checker, not a
  single "thought." It ships as reference material under `think-frameworks` (a
  "run the bias check before committing" step the decision modes point to).
- **Shinka evolutionary-optimization workflow → guidance, NOT a mode.** It is an action
  loop that shells out to `shinka-*`, not a JSON thought. It ships as guidance inside the
  `think-algorithmic` SKILL body + its `shinka-evolution.md` reference, triggered by
  "optimize / make faster / find a better algorithm."
- **Retire the standalones.** `reasoning-skill` and `algorithm-skill` are removed from
  `local-marketplace/.claude-plugin/marketplace.json` and `~/.claude/settings.json`
  (no double-load). Their `~/Github/skills` reference material migrates into the plugin.

## The 13 new modes

### New category `think-frameworks` — 12 modes
`5w1h`, `swot`, `fivewhys`, `fishbone`, `pestle`, `forcefield`, `decisionmatrix`,
`pareto`, `stakeholder`, `costbenefit`, `riskassessment`, `gapanalysis`

### New category `think-algorithmic` — 1 mode
`algorithmic` — CLRS algorithm & data-structure selection, Big-O analysis, pitfalls.

## Per-mode schema shapes (authoritative field intent; exact Draft-7 JSON is a plan task)

Every schema is **top-level `additionalProperties: false`, nested permissive** (the
plugin's established rule) and every thought carries `"mode": "<name>"`.

- **5w1h** — `who, what, when, where, why, how` (each string or string[]), `summary`.
- **swot** — `subject`, `strengths[]`, `weaknesses[]`, `opportunities[]`, `threats[]`, `recommendation`.
- **fivewhys** — `problem`, `whys[{question, answer}]` (chain), `rootCause`, `correctiveAction`.
- **fishbone** — `effect`, `categories[{name, causes[]}]` (6Ms/8Ps), `primaryCauses[]`.
- **pestle** — `subject`, `political[]`, `economic[]`, `social[]`, `technological[]`, `legal[]`, `environmental[]`, `keyFactors[]`.
- **forcefield** — `change`, `drivingForces[{force, strength(1-5)}]`, `restrainingForces[{force, strength(1-5)}]`, `netAssessment`, `recommendation`.
- **decisionmatrix** — `options[]`, `criteria[{name, weight}]`, `scores[{option, perCriterion[], total}]`, `recommendation` (scoring math shown).
- **pareto** — `items[{name, value}]`, `cumulativePercent[]`, `vitalFew[]`, `recommendation`.
- **stakeholder** — `stakeholders[{name, power, interest, quadrant, strategy}]`, `recommendation`.
- **costbenefit** — `option`, `costs[{item, amount}]`, `benefits[{item, amount}]`, optional `npv/roi/paybackPeriod`, `recommendation`.
- **riskassessment** — `risks[{risk, probability, impact, score, mitigation}]`, `topRisks[]`, `recommendation`.
- **gapanalysis** — `currentState`, `desiredState`, `gaps[{dimension, current, desired, gap, action}]`, `actionPlan[]`.
- **algorithmic** — `problem`, optional `currentComplexity`, `candidates[{algorithm, time, space, when}]`, `recommendation`, optional `dataStructures[]`, `pitfalls[]`, optional `evolutionSuggested` (bool, points to the Shinka guidance).

Each mode also enforces any "must / exactly one / at least N" invariants in its category
SKILL prose (deepthinking's pattern for constraints JSON Schema can't express — e.g.
`decisionmatrix` requires ≥2 options and ≥2 criteria; `fivewhys` requires ≥1 why with a
terminal `rootCause`).

## The 10 artifacts each new mode must land (the invariant)

Per the plugin's CLAUDE.md "34-mode invariant", every mode appears in 10 places, kept in
sync and enforced by `test/test_artifact_consistency.py` (items 1–5, 9) plus manual items
6–8 and item 10 (dashboard). For each of the 13 modes:

1. `test/schemas/<mode>.json` — Draft-7 schema
2. `test/samples/<mode>-valid.json` — realistic worked example that validates
3. `reference/visual-grammar/<mode>.md` — Mermaid + DOT templates
4. `reference/output-formats/<mode>.md` — schema doc + example
5. `skills/think-frameworks/SKILL.md` or `skills/think-algorithmic/SKILL.md` — teaches it
6. `skills/think/SKILL.md` — router table row + category read-mapping
7. `skills/think/mode-index.md` — auto-recommend decision-tree entry
8. `reference/taxonomy.md` — canonical taxonomy entry
9. `test/smoke/prompts.json` — smoke prompt
10. `scripts/render-html-dashboard.py` — `MODE_DISPLAY_NAMES` entry (e.g. `swot → "SWOT Analysis"`, `5w1h → "5W1H"`, `algorithmic → "Algorithm Selection"`)

Plus: the `commands/think.md` mode list/schema-reference table gains the 13 rows, and the
category-read mapping in `commands/think.md` "Method Instructions" gains the two new
categories.

## Migrated reference material (progressive disclosure)

- reasoning-skill's `references/01-5w1h.md … 12-gap-analysis.md`, `analytical-methodology-examples.md`,
  `reasoning-types-reference.md`, `reasoning_patterns.md`, `quick_reference.md`, `domain_mappings.md`
  → become `references/` under `skills/think-frameworks/` (per-framework deep-dives loaded on demand).
- reasoning-skill's `cognitive-biases/*` → `skills/think-frameworks/references/cognitive-biases/`
  (the bias-check reference; not a mode).
- algorithm-skill's `references/clrs-full-extraction.json` + `shinka-evolution.md`
  → `references/` under `skills/think-algorithmic/`.

## Invariant + docs update

- `CLAUDE.md`: the "34-mode invariant" becomes the **46-mode invariant**; note the two new
  categories, the bias-as-reference and Shinka-as-guidance decisions.
- `test/test_artifact_consistency.py`: the authoritative set is the 46 `test/schemas/*.json`
  filenames; it enforces set-equality across items 1–5 and 9 automatically.
- `ARCHITECTURE.md` + `README.md`: document the two new categories and the mode-count change.

## Retire the standalone plugins

- Remove `reasoning-skill` and `algorithm-skill` entries from
  `~/Github/skills/.claude-plugin/marketplace.json` (local-marketplace manifest) and their
  `"<name>@local-marketplace": true` keys from `~/.claude/settings.json`.
- The `~/Github/skills/reasoning-skill/` and `~/Github/skills/algorithm-skill/` folders remain
  as authoring source but stop being delivered as plugins. (User runs `/reload-plugins` after.)

## Release

Version-bump `.claude-plugin/plugin.json` (0.5.4 → next), add a `CHANGELOG.md` entry, and
cut a git tag / GitHub release per the plugin's release sequence.

## Non-goals

- No duplication of the reasoning modes deepthinking already ships.
- No forcing the bias system or the Shinka workflow into schema'd modes.
- No Node.js runtime, no MCP server, no third-party test framework (the plugin's standing constraints).
- No change to the existing 34 modes.

## Testing

Documentation/artifact work — the gate is the plugin's **fast suite**, which must stay
green after every task:
`test/test_plugin_json.py`, `test/test_skill_frontmatter.py`,
`test/test_artifact_consistency.py` (46-way set-equality), `test/test_format_grammars.py`,
`test/harness.py` (schema validations: 46 valid samples + the existing invalid cases),
`test/visual/validate-mermaid.py`, `test/visual/validate-dot.py`,
`test/visual/test-dashboard.py`. Each new mode's `-valid.json` sample must validate against
its schema (`harness.py`), and its Mermaid/DOT grammars must parse. The expensive smoke
suite (`test/smoke/`) is out of scope for the automated gate but recommended before the
release tag.

## Success criteria

1. 13 new modes exist, each landing all 10 artifacts; `test_artifact_consistency.py` passes
   with a 46-mode set (no missing/extra).
2. The full fast suite is green.
3. `/think swot "…"`, `/think decisionmatrix "…"`, `/think algorithmic "…"` (etc.) route to
   the new category skills and emit schema-valid JSON + summary; `/think-render` renders them.
4. The bias-check reference and Shinka guidance are present (as reference/guidance, not modes).
5. `reasoning-skill` and `algorithm-skill` no longer load as standalone plugins; no double-load.
6. deepthinking-plugin version bumped, CHANGELOG updated, release cut.
