# Changelog

All notable changes to this project will be documented in this file.

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
