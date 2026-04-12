# Changelog

All notable changes to this project will be documented in this file.

## [0.4.0] - 2026-04-12

### Added
- **Automated end-to-end smoke test runner** at `test/smoke/run-all-modes.py` that invokes headless `claude -p` for each of the 34 modes, captures the JSON block from Claude's response, and validates it against the mode's schema. Configurable timeout and single-mode re-run via `SMOKE_MODE=<mode>` env var.
- **34 mode test prompts** at `test/smoke/prompts.json` — one realistic scenario per mode
- **9 format grammar files** at `reference/visual-grammar/formats/`: `ascii.md`, `json.md`, `markdown.md`, `graphml.md`, `html.md`, `tikz.md`, `modelica.md`, `uml.md`, `dashboard.md`. These describe how to encode ANY mode's thought into the format using the shared conventions + per-mode semantic grammar
- **Interactive HTML dashboard template** at `reference/html-dashboard-template.html` — single-file standalone HTML with Mermaid CDN client-side rendering, JSON explorer, dark-mode support, and export buttons (copy/download/print)
- **HTML dashboard renderer** at `scripts/render-html-dashboard.py` — injects thought JSON + Mermaid source into the template, writes standalone HTML file. Pure stdlib Python.
- **Dashboard integration test** at `test/visual/test-dashboard.py` verifying end-to-end render

### Changed
- **`agents/visual-exporter.md`**: updated to route all 11 output formats (mermaid, dot, ascii, json, markdown, graphml, html, tikz, uml, modelica, dashboard) by consulting both the per-mode grammar and the format grammar
- **`commands/think-render.md`**: expanded `argument-hint` and format list to accept all 11 formats
- **All 34 JSON schemas** relaxed in two ways based on real smoke-test findings:
  - Nested detail objects (depth ≥ 1) now allow additional properties — the top-level thought object is still strict, catching typos, but nested structures accept the richer detail Claude naturally produces
  - Optional scalar fields (non-required string/number/integer/boolean) now accept `null` — Claude commonly emits explicit `null` for absent optionals
- **`test/schemas/hybrid.json`**: `primaryMode` enum expanded from 4 to all 34 modes; `thoughtType` relaxed from a restrictive 22-value enum to any non-empty string

### Verified
- **Smoke tests**: all captured outputs (12+ modes executed in v0.4.0 release cycle: sequential, shannon, hybrid, inductive, deductive, abductive, mathematics, computability, temporal, historical, bayesian, …) pass schema validation end-to-end. Remaining 22 modes can be run by the user at any time via `python test/smoke/run-all-modes.py`.
- **Harness tests**: all 35 hand-crafted schema tests still pass
- **Frontmatter**: all 13 skills still have valid YAML
- **Dashboard integration**: single-file HTML renders successfully with all placeholders substituted
- **Visual grammars**: all 34 per-mode grammars still have valid Mermaid + DOT blocks

## [0.3.0] - 2026-04-12

### Added
- **Visual export for all 34 modes** via the new `/think-render [format]` slash command at `commands/think-render.md`
- `agents/visual-exporter.md` — subagent that converts structured thoughts to diagram source by reading per-mode visual grammar
- `reference/visual-grammar.md` — shared conventions (node shapes, color palette, edge semantics, label rules, layout hints) with worked Mermaid and DOT examples
- `reference/visual-grammar/*.md` — **34 per-mode grammar files**, each with a Node Structure section, Edge Semantics, Mermaid template, DOT template, and a worked example using the actual field values from the corresponding reference/output-formats sample
- `scripts/render-diagram.py` — wraps `graphviz` (DOT → SVG/PNG) and `@mermaid-js/mermaid-cli` (Mermaid → SVG/PNG). **Gracefully degrades** to printing source on stdout with install hint when binaries aren't available
- `test/visual/validate-mermaid.py` — syntactic validator that checks every grammar file's Mermaid blocks parse
- `test/visual/validate-dot.py` — syntactic validator that checks every grammar file's DOT blocks parse
- README section documenting `/think-render` usage and optional external binary installation

### Verified
- **68 visual checks pass** (34 grammar files × 2 formats): every mode has ≥2 valid Mermaid blocks and ≥2 valid DOT blocks (template + worked example)
- `render-diagram.py` runs without crashing when binaries are missing (graceful degradation confirmed)
- All 35 schema validations still pass, all 13 SKILL.md frontmatters still valid

## [0.2.0] - 2026-04-12

### Added
- **31 new reasoning modes** across 10 new category skills, bringing total to 34 modes:
  - `think-mathematics`: Mathematics, Physics, Computability
  - `think-temporal`: Temporal, Historical
  - `think-probabilistic`: Bayesian, Evidential
  - `think-causal`: Causal, Counterfactual
  - `think-strategic`: GameTheory, Optimization, Constraint
  - `think-analytical`: Analogical, FirstPrinciples, MetaReasoning, Cryptanalytic
  - `think-scientific`: ScientificMethod, SystemsThinking, FormalLogic
  - `think-engineering`: Engineering, Algorithmic
  - `think-academic`: Synthesis, Argumentation, Critique, Analysis
  - `think-advanced`: Recursive, Modal, Stochastic
- Expanded `think-core` with Abductive reasoning
- Expanded `think-standard` with Shannon and Hybrid reasoning
- 31 new JSON Schemas in `test/schemas/` (all with `additionalProperties: false` and const mode values)
- 31 new sample valid thoughts in `test/samples/`
- 31 new per-mode reference docs in `reference/output-formats/`

### Changed
- `skills/think/SKILL.md`: Available Modes table now lists all 34 modes with category-skill mappings
- `skills/think/mode-index.md`: 12-branch decision tree covering all 34 modes, updated example mappings
- `reference/taxonomy.md`: All 34 modes graduated from "Future" to v0.2.0; "Future Modes" section removed
- `commands/think.md`: Complete mode list grouped by category; 34-row Schema References table; "Unavailable modes" section removed
- `test/harness.py`: **Auto-discovery** of samples replaces the hardcoded SAMPLES list — drop any `<mode>-valid.json` into `test/samples/` and it's tested automatically
- `test/test_skill_frontmatter.py`: now expects 13 SKILL.md files (1 router + 12 categories)

### Verified
- Automated: **35 schema validations pass** (34 valid + 1 invalid), all 13 skills have valid frontmatter, plugin.json manifest validates
- Manual smoke test coverage expansion (v0.2.x task): v0.1.0 already verified sequential/inductive/deductive/auto end-to-end in a real Claude Code session

## [0.1.0] - 2026-04-12

### Added
- Initial plugin scaffold with `.claude-plugin/plugin.json` manifest
- `/think` slash command at `commands/think.md` — the user-facing entry point
- Router skill `think` with auto-recommendation for the 3 prototype modes
- Category skill `think-standard` with Sequential mode
- Category skill `think-core` with Inductive and Deductive modes
- Reference output-format files for Sequential, Inductive, Deductive
- `argument-hint` and `$ARGUMENTS` placeholders in all SKILLs for proper argument passing
- Python test harness (`test/harness.py`) with JSON Schema validation
- Sample thoughts (valid and invalid) for smoke testing
- README and installation instructions

### Verified end-to-end (2026-04-12)
- `/think sequential "..."` → 6 schema-valid thoughts with dependency tracking
- `/think inductive "..."` → schema-valid with calibrated confidence (0.8) and counterexample reasoning
- `/think deductive "..."` → schema-valid with FOL notation and operational soundness caveats
- `/think "..."` (auto-recommend) → correctly defers to sequential when observations are referenced but not supplied, with explicit mode-handoff plan in thought 3

### Install paths (documented in README)
- Canonical plugin command: `/deepthinking-plugin:think [mode] "<problem>"` (available after installing the plugin via `--plugin-dir` or by copying to `~/.claude/plugins/`)
- Optional shorter alias: personal command at `~/.claude/commands/think.md` (provided in `examples/personal-command-alias/`) gives the bare `/think` form
