# Changelog

All notable changes to this project will be documented in this file.

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
