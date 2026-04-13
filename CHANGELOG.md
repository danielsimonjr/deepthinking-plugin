# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

Docs and planning work — no source code changes. Captures forward-looking analysis and expanded contributor guidance produced by an RLM-driven deep-dive over the entire reference corpus, plus a 5-specialist (2× Opus + 3× Sonnet) review team pass and a HonestClaude programmatic verification pass.

### Added

- **`docs/ROADMAP-FUTURE-MODES-AND-FORMATS.md`** — forward-looking inventory artifact identifying which reasoning modes and output formats are referenced in the corpus but not yet implemented. Three review rounds: post-synthesis verification, 5-specialist review team, and HonestClaude programmatic verification. Final tier counts: 0 Tier 1 modes (intentionally — the plugin is essentially feature-complete on the modes side), 1 Tier 2 mode (`decisionanalysis`, on hold pending a design spike), 16 Tier 3 modes (rejected with rationale), 2 Tier 1 formats (`latex-math`, `csv`), 3 Tier 2 formats, 7 Tier 3 formats. The artifact also enumerates 5 strategic gaps the team flagged that are not directly roadmap items but should be on the maintainer's radar (mode-count ceiling, smoke test scalability, mode deprecation path, telemetry/feedback gap, hybrid mode evolution). Full methodology audit trail is embedded in the artifact itself under "Methodology Notes" rounds 1, 2, and 3.
- **`docs/SKILL-INVARIANTS.md`** — catalog of per-mode validation rules that JSON Schema cannot express. Documents 4 schema-unenforceable cardinality rules (counterfactual, modal, historical, abductive), 3 schema-already-enforced rules included for completeness (gametheory, synthesis, engineering), and 2 cross-field semantic rules (firstprinciples confidence chain, bayesian arithmetic display). When editing a SKILL.md file, preserve any "must" / "exactly one" / "at least N" language — those are load-bearing invariants the schema cannot catch.
- **`docs/PLAN-v0.5.0.md`** — agent-driven implementation plan for the next release. Prioritizes the Roadmap's Tier 1 items into 16 concrete tasks organized in 3 dependency-ordered waves (6 parallel Wave 1 tasks, 5 parallel Wave 2 cascade tasks, 5 sequential Wave 3 release-gate tasks). Each task includes a self-contained subagent brief with current state, goal, implementation guidance, acceptance criteria, expected LOC delta, and commit message. Scope: 2 new format grammars (`latex-math`, `csv`), 3 quality-infrastructure items (`test_version_consistency.py`, `MODE_DISPLAY_NAMES` sync check, smoke test parallelization), and 1 ergonomic fix (`think-render` alias). No new reasoning modes — per the Roadmap's three-round review verdict. Estimated wall-clock for agent-driven execution: 65-95 minutes vs 6-8 hours sequential. Dependency graph, review gates, and rollback instructions are embedded in the plan.

### Changed

- **`CLAUDE.md`** — substantially expanded based on session learnings:
  - **34-mode invariant promoted from 9 places to 10 places.** Added `MODE_DISPLAY_NAMES` dict in `scripts/render-html-dashboard.py` as the 10th sync location (find with `grep -n MODE_DISPLAY_NAMES scripts/render-html-dashboard.py` rather than a fragile line number). **No automated check enforces this** — `test_artifact_consistency.py` only covers items 1–5 and 9. Drift surfaces only as a wrong dashboard title (the fallback `mode.capitalize() + " Reasoning"` is wrong for compound names like `gametheory` → "Game Theory" or `firstprinciples` → "First Principles Reasoning").
  - **New design principle: "Some validation rules live in SKILL.md prose, not in JSON Schema."** Examples documented inline; full per-mode catalog in `docs/SKILL-INVARIANTS.md`.
  - **New "Out of scope" section.** Captures the durable user decisions from the original brainstorming session that should never be reintroduced: no persistent session state across `/think` invocations, no Node.js runtime, no hard `dot`/`mmdc` dependency, no third-party test framework (the repo *does* have an in-house test harness).
  - **New "Skills vs slash commands" architectural section.** Captures the v0.1.0 "Unknown skill: sequential" investigation: skills (`skills/<category>/SKILL.md`) are auto-invoked by Claude based on conversation context, slash commands (`commands/<name>.md`) are user-typed. They are completely separate systems. If you want to add a new user-facing `/foo` command, create `commands/foo.md`, NOT `skills/foo/SKILL.md`.
  - **New "Release sequence (don't reorder)"** under Publishing — documents the 7-step release gate (fast suite → commit → smoke suite → fix any schema drift → re-run fast suite → bump version + CHANGELOG → tag + release) with a warning that hardcoded equality assertions in tests are a smell (the v0.4.1 plugin.json-stuck-at-0.1.0 latent-bug story).

### Methodology — RLM-driven multi-stage review

This Unreleased entry was produced by a multi-stage Recursive Language Model (RLM) methodology with three independent review rounds. The full audit trail is embedded in `docs/ROADMAP-FUTURE-MODES-AND-FORMATS.md` (Methodology Notes sections); summary here:

- **Round 1 (post-synthesis verification)** caught 4 false-positive Tier 1 candidates (Toulmin, Socratic, mermaid, dot) that were already canonical inside parent modes or first-class formats in a different file location.
- **Round 2 (5-specialist review team)** dispatched Opus architect + Opus adversary + Sonnet technical + Sonnet domain + Sonnet editorial in parallel via `llm_query`. 99 findings, 11 concordant items. Verdict: round-1 corrections didn't go far enough — `dialectical`, `decisionanalysis`, `structuralcausalmodel`, and the entire computational-Tier 2 cluster failed the same "is this distinct?" test.
- **Round 3 (HonestClaude programmatic verification)** verified 36 verifiable claims (33 PASS, 2 WARN resolved, 1 false-positive FIX, 0 unresolvable failures) plus 41/41 source-citation paths to disk. Two real corrections applied: CSV "8-12 of 34" empirical correction to 27 of 34, structuralcausalmodel rejection strengthened with `do-operator` finding from `think-causal/SKILL.md`.

### Note on maintainer-private auto-memory

This session also updated the maintainer-private auto-memory at `~/.claude/projects/<plugin-slug>/memory/` with two new entries (`project_skill_invariants.md` consolidating the schema-unenforceable invariants, and `feedback_milestone_review_workflow.md` codifying the milestone-and-PR review workflow as a durable user preference). These files are **not part of this repo or this PR** — they live in the user's local Claude Code projects directory. The repo-facing version of the skill-invariants knowledge is `docs/SKILL-INVARIANTS.md` (added in this PR). The workflow rule is implicit in this PR's process and explicit in the PR template / commit messages going forward.

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
