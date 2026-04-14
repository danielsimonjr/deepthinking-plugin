# Changelog

All notable changes to this project will be documented in this file.

## [0.5.2] - 2026-04-12

Schema enrichment release. Introduces the first of three planned core-triad enrichments: an optional `derivationSteps[]` field on the `deductive` mode for multi-step proof chains. Backward-compatible — atomic single-jump deductions continue to validate unchanged. Also promotes `test/test_skill_invariants.py` from "unreleased" to its first shipped release, extending it with a new `check_deductive()` enforcing the 5 schema-unenforceable rules the new field introduces.

### Added

- **`test/schemas/deductive.json` — optional `derivationSteps[]` array.** Added under a new top-level property (not in `required`, so thoughts without it validate as before). Each step object has 3 required fields (`stepNumber: integer ≥ 1`, `intermediateConclusion: string minLength 1`, `inferenceRule: string minLength 1`) and 2 optional array fields (`premisesUsed: integer[≥0]`, `stepsUsed: integer[≥1]`). `inferenceRule` is free-text in v0.5.2 to let authors capture non-classical or informal rules; a future release may tighten to an enum once the usage patterns are observed across samples. Nested step object has `additionalProperties: false` so typos in the per-step field names are caught — the top-level `additionalProperties: false` policy is preserved.
- **`reference/output-formats/deductive.md`** — rewritten to document the new field shape, the required-vs-optional split, two worked examples (atomic single-jump "Alice-admin" example and multi-step "Request R audit-trail" example), and the 5 referential-integrity invariants the field must follow (sequential numbers, no forward refs, valid premise indices, non-empty inputs per step, final-step closure).
- **`reference/visual-grammar/deductive.md`** — rewritten with conditional rendering dispatch: if `derivationSteps` is absent or empty, render the classic 3-tier pyramid (premises → logical connective → conclusion); if populated, render a multi-tier flow (premises → per-step intermediate nodes → final conclusion) where intermediate step nodes are always neutral gray and only the final conclusion carries the validity/soundness color. Mermaid and DOT templates for both cases plus the full worked example.
- **`skills/think-core/SKILL.md`** — the deductive section gained a new "Multi-step derivations — when to use `derivationSteps[]`" subsection, a new step #3 in "How to Reason Deductively" ("decide if the derivation is atomic or multi-step"), a second Quick Template covering the multi-step shape, a second Worked Example (the Request-R audit-trail chain), and an expanded verification checklist reflecting the 5 new invariants (including the enforced "final step must close the chain" rule).
- **`test/test_skill_invariants.py::check_deductive()`** — new invariant check enforcing 5 rules that JSON Schema cannot express: (1) step numbers must be sequential 1..N with no gaps or duplicates, (2) `stepsUsed[]` may only contain integers in `[1, stepNumber-1]` — no forward references, no self-references, no references to non-existent steps, (3) `premisesUsed[]` indices must be valid 0-indexed positions into the top-level `premises[]` array, (4) every step must derive from something (at least one of `premisesUsed[]` / `stepsUsed[]` must be non-empty — a free-standing assertion isn't a derivation), (5) the final step's `intermediateConclusion` must match the top-level `conclusion` after whitespace/trailing-period normalization. Wired into the `CHECKS` dispatch dict so the existing test harness picks it up automatically. Total invariant checks grew from 12 to 14 (both the sample and the v0.5.2 captured smoke output pass).
- **`test/test_skill_invariants.py`** — new fast test enforcing the 6 per-mode semantic rules catalogued in `docs/SKILL-INVARIANTS.md` that JSON Schema cannot express (first shipped in this release; originally developed during the v0.5.1 cycle but not cut as its own release). Complements `test/harness.py` with a layer that catches structural-valid-but-semantically-broken Claude output. Runs against both `test/samples/<mode>-valid.json` and `test/smoke/captured/<mode>-parsed.json` when present. Checks: `abductive` requires ≥2 hypotheses with non-equal scores; `counterfactual` requires exactly one `isIntervention=True` condition per scenario; `historical` requires asserted patterns to have ≥2 distinct episodes; `modal` requires exactly one world with `isActual=True`; `firstprinciples` enforces referential integrity of `conclusion.derivationChain` and `conclusion.certainty ≤ min(step.confidence in chain)`; `bayesian` requires `posterior.calculation` to contain real arithmetic (≥2 numbers, at least one operator). Fast test count: 9 → 10. With the new `check_deductive()`, the test now covers 7 modes.
- **`docs/SKILL-INVARIANTS.md`** — new "Referential integrity rules (v0.5.2+)" section with 5 rows documenting the deductive rules, pointing to `test/test_skill_invariants.py::check_deductive()` as the enforcement mechanism.
- **`test/samples/deductive-valid.json`** — rewritten as a worked 3-premise 2-step chain exercising the new field (the "Request R audit-trail → alert" example used in all documentation). Old hand-crafted single-jump sample preserved conceptually in the "atomic" example in `output-formats/deductive.md` for comparison.
- **`test/smoke/prompts.json`** — the deductive smoke prompt was rewritten to a deliberately different multi-step problem from the sample (the "published blog post / author / registered user" chain). Keeping the prompt and sample structurally parallel but semantically distinct is the methodological guarantee that smoke runs test *generalization*, not sample pattern-matching. Verified: real `claude -p` populated `derivationSteps[]` correctly for the new example with all 5 invariants satisfied.

### Fixed

- **`test/samples/firstprinciples-valid.json`** — dropped `conclusion.certainty` from `0.92` to `0.88` to match the minimum step confidence in the derivation chain. The previous value violated the "conclusion cannot be more certain than its weakest derivation step" invariant, caught on the first run of `test_skill_invariants.py`. Exactly the class of semantic bug the new test was designed to catch.

### Internal

- **`.gitignore`** — added `.rlm_*.py` and `.rlm_*.json` patterns so the 5-specialist Recursive Language Model review artifacts used during the v0.5.2 release cycle (and any future cycle) stay local-only.

## [0.5.1] - 2026-04-13

Patch release fixing a subprocess cleanup bug in the parallel smoke runner introduced by v0.5.0's T6 refactor. No functional changes; single-file targeted fix.

### Fixed

- **`test/smoke/run-all-modes.py`** — prevents orphaned `claude -p` grandchildren when the smoke runner is interrupted. The v0.5.0 refactor from sequential `subprocess.run` to parallel `ThreadPoolExecutor` with `subprocess.run(timeout=N)` inside each worker introduced a cleanup gap: `ThreadPoolExecutor.__exit__` waits for all futures to complete before the Python interpreter exits, so a killed bash wrapper would leave the main Python process stuck on worker threads that were blocked on their own `subprocess.run` calls, which in turn held live `claude -p` grandchildren. The fix replaces each `subprocess.run` with `subprocess.Popen + communicate()`, registers each child in a module-level `_active_procs` set (thread-safe via a `threading.Lock`), and installs `atexit` + `SIGINT` / `SIGTERM` handlers that walk the set and force-kill any still-running children before the interpreter exits. Signal exit uses code 128 + signum (130 for SIGINT, 143 for SIGTERM) per the POSIX convention. Verified: single-mode smoke run exits cleanly with zero orphan `python.exe` processes created, timeout path still works, `SMOKE_WORKERS=1` sequential escape hatch preserved, deterministic alphabetical summary ordering unchanged.

### Internal

- Fixed a pre-existing `SyntaxWarning` on line 147 of `test/smoke/run-all-modes.py` — the `repair_lone_backslashes` docstring contained `"\ "` (backslash-space) as a literal example, which Python 3.12+ flags as an invalid escape sequence. Added an `r` prefix to make it a raw string literal.

## [0.5.0] - 2026-04-13

Format expansion + quality infrastructure release. Grows the effective output format count from 11 to 13 (2 new mode-agnostic grammars), adds cross-file version consistency and MODE_DISPLAY_NAMES sync tests, parallelizes the smoke test runner, and fixes two pre-existing version-drift bugs caught by the new consistency test. No new reasoning modes — the 34 canonical modes are unchanged.

### Added

- **`reference/visual-grammar/formats/latex-math.md`** — new mode-agnostic AMS-math LaTeX format grammar, distinct from the canonical `tikz` format (which is for TikZ vector diagrams). Provides clean math rendering for the 7 math-heavy modes (mathematics, physics, computability, formallogic, firstprinciples, bayesian, evidential) with step-by-step arithmetic preservation, `\tag{<field-path>}` labels for equation traceability, and `\intertext{...}` for prose between equation blocks. Includes a complete bayesian worked example that compiles with `pdflatex` + `amsmath` + `amssymb`.
- **`reference/visual-grammar/formats/csv.md`** — new mode-agnostic RFC 4180 CSV format grammar with per-mode flattening rules covering all 34 canonical modes (9 Excellent, 17 Moderate, 8 Fallback tier). Provides tabular export for the majority of modes whose schemas contain wide array-of-objects fields (e.g., `bayesian.evidence`, `gametheory.payoffMatrix.entries`, `optimization.alternatives`, `engineering.tradeStudy.alternatives`). Multi-table support via `# table: <name>` comment lines; fallback to 2-column `field,value` representation for prose-primary modes.
- **`test/test_version_consistency.py`** — new cross-file version coherence check that reads the authoritative version from `.claude-plugin/plugin.json` and verifies every version mention in the repo agrees (CHANGELOG's first real release heading, README.md Status section, `skills/think/SKILL.md` Available Modes heading, `CLAUDE.md` intro). Prevents the latent-bug class where `plugin.json` can drift from the version mentioned in docs (the v0.4.1 plugin.json-stuck-at-0.1.0 story).
- **`MODE_DISPLAY_NAMES` sync check** added to `test/test_artifact_consistency.py`. Parses the dict from `scripts/render-html-dashboard.py` via `ast` (no import, no side effects) and verifies its keys match the authoritative schemas set from `test/schemas/*.json`. This was the hidden 10th sync location in the 34-mode invariant — drift previously surfaced only as a wrong dashboard title.
- **`examples/personal-command-alias/think-render.md`** — optional personal command alias parallel to the existing `think.md`. Lets users who install the alias type `/think-render <format>` instead of `/deepthinking-plugin:think-render <format>`. Description includes all 15 accepted format values (13 grammar-based + svg + png).
- **`docs/ROADMAP-FUTURE-MODES-AND-FORMATS.md`** — forward-looking inventory of reasoning mode and output format candidates with tier assignments (Strong / Plausible / Rejected) and rationale. 0 Tier 1 modes (the 34 canonical modes are feature-complete); 1 Tier 2 mode (`decisionanalysis`, held pending a design spike); Tier 3 documents rejected candidates with rationale. Includes a "Strategic gaps" section covering mode-count ceiling, smoke test scalability, mode deprecation path, telemetry gap, and hybrid mode evolution.
- **`docs/SKILL-INVARIANTS.md`** — catalog of per-mode validation rules that JSON Schema cannot express: 4 schema-unenforceable cardinality rules (`counterfactual` exactly-one-isIntervention, `modal` exactly-one-isActual, `abductive` ≥2 distinct hypotheses, `historical` ≥2 episodes per pattern), 3 already enforced in schemas (`gametheory`, `synthesis`, `engineering`), and 2 cross-field semantic rules (`firstprinciples` confidence chain, `bayesian` arithmetic display). When editing a SKILL.md file, preserve any "must" / "exactly one" / "at least N" language.
- **`docs/PLAN-v0.5.0.md`** — agent-driven implementation plan for this release. 16 tasks organized in 3 dependency-ordered waves with self-contained subagent briefs. Preserved as a template for future release planning.

### Changed

- **`test/smoke/run-all-modes.py`** — refactored from sequential to parallel execution using `concurrent.futures.ThreadPoolExecutor` with a configurable worker count (`SMOKE_WORKERS` env var, default 4, max 8). Preserves all existing behavior: per-mode timeouts, JSON repair attribution via `repair_lone_backslashes`, stderr capture to `captured/<mode>-stderr.txt`, single-mode mode (`SMOKE_MODE=bayesian`), sequential escape hatch (`SMOKE_WORKERS=1`), and deterministic alphabetical summary ordering. Expected wall-clock: 30–60 min → 10–15 min with 4 workers. Extracted `run_single_mode()` as a pure function for reuse across the executor and single-mode paths.
- **`test/test_format_grammars.py`** — `EXPECTED_FORMATS` grew from 9 to 11, adding `csv` and `latex-math` in alphabetical order.
- **`commands/think-render.md`** — format list expanded from 13 to 15 accepted values (adds `latex-math`, `csv`).
- **`agents/visual-exporter.md`** — frontmatter description updated from "Supports 11 formats" to "Supports 13 formats"; body "Your Inputs" section and direct-emit format list in step 6 both updated.
- **`README.md`** — the "All 11 export formats" table heading becomes "All 13 export formats (v0.5.0+)"; two new table rows for `latex-math` and `csv`; Status-line mention of "11 output formats" → "13 output formats".
- **`CLAUDE.md`** — expanded with: the 34-mode invariant promoted from 9 places to 10 places (`MODE_DISPLAY_NAMES` dict is the 10th sync location, with `grep -n` as the stable locator); a new design principle "Some validation rules live in SKILL.md prose, not in JSON Schema" (full per-mode catalog in `docs/SKILL-INVARIANTS.md`); a new "Out of scope" section documenting deliberate non-goals (no persistent session state, no Node.js runtime, no hard `dot`/`mmdc` dependency, no third-party test framework); a new "Skills vs slash commands" architectural section clarifying that skills are auto-invoked while slash commands are user-typed; a new "Release sequence (don't reorder)" section under Publishing with a warning that hardcoded equality assertions in tests are a smell.

### Fixed

- **`README.md`** and **`skills/think/SKILL.md`** — updated two stale `v0.4.0` references to `v0.4.1`. These were pre-existing version-drift bugs from the v0.4.1 release cycle that were never caught. The new `test_version_consistency.py` flagged them on its first run, which is exactly the class of bug it was designed to catch.

## [0.4.1] - 2026-04-12

### Security
- **Pinned Mermaid CDN to an exact version** (`@11.4.1`) with `crossorigin="anonymous"`. Previously `@11` was a floating major-version tag — a compromised jsdelivr tag would execute JS in every historical dashboard. Now the CDN URL is frozen.
- **Switched Mermaid `securityLevel` from `loose` to `strict`**. Disables click-handlers and HTML embedding in labels — hardens against prompt-injected malicious diagram source.
- **HTML-escape all user-supplied content** in `render-html-dashboard.py`, including the Mermaid source (was previously interpolated raw). The `{{MODE}}` token is now injected via `json.dumps` into a JS string literal instead of `html.escape` into HTML context, which is the correct escape function for JS contexts.
- **Path validation** on `render-html-dashboard.py`'s `--output` and `--thought` flags — refuses paths that escape the current working directory or temp dir.
- **Mode slug sanitization** — validates mode against `^[a-z][a-z0-9_-]{0,40}$` before substituting into the HTML template and download filename.
- **Template token audit** — renderer now scans for unsubstituted `{{TOKEN}}` patterns after substitution and fails loudly if any remain.
- **Mermaid `parseError` callback** + `window.onerror` handler in the dashboard template — replaces the fragile substring-match error surfacing; also handles the case where the CDN fails to load (offline, blocked, or unreachable).
- **`copyJson()` fallback** for `file://` origins where `navigator.clipboard` is undefined — uses Selection API to let the user Ctrl+C the JSON.

### Fixed
- **Optimization worked example in `skills/think-strategic/SKILL.md`** was internally contradictory: structured fields showed `{a:10, b:12, value:260}` but the self-correcting `note` said the optimal was `{a:0, b:20, value:300}`. Rewritten to show the correct optimum directly.
- **`scripts/render-diagram.py` exit codes**: previously returned 0 both when a diagram was rendered AND when the binary was missing. Now uses distinct codes (0 success, 2 with `--allow-skip` for degradation, 127 for missing-binary hard fail, 124 for timeout). Callers can now distinguish "file exists" from "file not written".
- **`scripts/render-diagram.py` timeouts**: `dot` and `mmdc` subprocess calls had no timeout. Added a 60-second default. Both are wrapped in `try/except subprocess.TimeoutExpired`.
- **`test/smoke/run-all-modes.py` silent exception**: narrowed `except Exception: pass` on stdout reconfigure to `(AttributeError, io.UnsupportedOperation, ValueError)` with an explicit warning to stderr.
- **Repair attribution**: when `repair_lone_backslashes` recovers from a LaTeX-in-string JSON escape bug in Claude's output, the runner now prints `PASS (with backslash repair — JSON escape bug in model output)` and totals the repaired count in the summary. No more silent repairs.
- **`test/smoke/run-all-modes.py` prompt escaping**: prompts with literal `"` characters are now escaped before interpolation into the `/think` argument string. Also captures stderr from the subprocess alongside stdout for debugging.
- **`test/harness.py` error reporting**: uses `Draft7Validator.iter_errors` to report ALL validation failures per sample (capped at 5 for readability) with JSON path context, instead of just the first. Also catches `FileNotFoundError`, `JSONDecodeError`, `UnicodeDecodeError`, and `SchemaError` per-sample instead of crashing the whole run.
- **`test_plugin_json.py` version assertion**: was hardcoded to `"0.1.0"` — now uses a semver regex so version bumps don't break the test.
- **`test_skill_frontmatter.py` count assertion**: was hardcoded to `== 13` — now uses a sanity range (`1 <= n <= 100`) so adding a category skill doesn't falsely fail the test.
- **CRLF tolerance** in `test/visual/validate-{mermaid,dot}.py`: normalize `\r\n` → `\n` before regex-extracting code blocks.

### Changed
- **`test/visual/validate-{mermaid,dot}.py`**: missing code blocks are now **FAIL**, not **SKIP**. An explicit `ALLOWED_NO_*` allowlist (empty by default) covers the rare legitimate case. This catches the exact regression the validators exist to catch — a grammar file silently losing its code fence.
- **README.md Status section**: was stuck at "v0.1.0 Prototype, 3 modes" — now reflects v0.4.0 / 34 modes / smoke-tested.
- **`skills/think/SKILL.md` Available Modes heading**: was "(v0.2.0)" — now "(v0.4.0)".
- **`commands/think-render.md`**: was listing 7 formats in the workflow body; now lists all 13 consistently with the frontmatter and README.
- **`examples/personal-command-alias/think.md`**: frontmatter description was stale (claimed 3 modes). Updated to "any of the 34 available modes".
- **`agents/visual-exporter.md`**: removed hardcoded "All 34 modes are covered" — now says "Every mode has a grammar file… fall back to generic conventions if missing" so adding a mode doesn't silently drift the agent's prompt.

### Added
- **`test/test_artifact_consistency.py`** — enforces set-equality across `test/schemas/`, `test/samples/`, `reference/visual-grammar/`, `reference/output-formats/`, and `test/smoke/prompts.json`. Adding a new mode without all artifacts now fails immediately with a clear diff.
- **`test/test_format_grammars.py`** — validates the 9 format grammar files have the expected structure (required sections, minimum byte size). Previously this directory had zero test coverage.
- **`test/samples/{bayesian,inductive,deductive,abductive,causal}-invalid.json`** — 5 new negative sample fixtures exercising schema-validation failure modes (out-of-range probability, empty required array, wrong const mode, missing required field). Previously only 1 negative sample existed (`sequential-invalid.json`).
- **`test/smoke/router-prompts.json`** + **`test/smoke/run-router-tests.py`** — 12 test prompts for the `/think "<problem>"` auto-recommend branch with a list of acceptable modes per prompt. Previously this code path had zero test coverage.
- **`ARCHITECTURE.md`** — contributor-facing map of the three layers (reasoning skills, format grammars, runtime helpers), invocation flow diagrams, step-by-step "adding a new mode" and "adding a new format" recipes, and the five design principles.

### Verified
- **118 automated checks pass**: 1 plugin.json, 13 SKILL.md frontmatters, 34 mode-set consistency, 9 format grammars, 40 schema validations (34 valid + 6 invalid), 34 Mermaid grammars, 34 DOT grammars, 1 dashboard integration.
- Dashboard renders without the `loose` security level; no template tokens leak through; Mermaid CDN is pinned.

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
- **Smoke tests**: all 34 modes captured and validated end-to-end via `python test/smoke/run-all-modes.py` (headless `claude -p` → JSON extraction → schema validation). Re-runnable at any time.
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
