# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this plugin is

A Claude Code plugin that teaches Claude **34 structured reasoning modes** (Bayesian, causal, game theory, etc.) as native prompt-based skills. There is no runtime server — Claude learns each method from skill content and produces structured JSON thoughts directly.

**Current version:** v0.4.1. GitHub: https://github.com/danielsimonjr/deepthinking-plugin.

**Read before making changes:**
- `ARCHITECTURE.md` — the three-layer design (reasoning skills / output-format grammars / runtime helpers) and invocation flow diagrams
- `README.md` — user-facing install and command reference
- `CHANGELOG.md` — the v0.1.0 → v0.4.1 progression and what each release shipped

This file covers what isn't in any of those: the mode-set invariant, the design principles you must not break, common commands, and gotchas learned during development.

## Cross-repo relationship (important context)

This plugin **replaces** `deepthinking-mcp` (v9.1.3, at `C:/Users/danie/Dropbox/Github/deepthinking-mcp/`), which is now deprecated. The MCP was a 102K-LOC TypeScript MCP server that shipped 34 reasoning modes via JSON-RPC tools; the plugin ships the same methods as Claude Code skills with zero runtime.

**What's still useful in the deprecated MCP repo for this plugin:**

- **`docs/superpowers/knowledge-packs/<mode>.md`** (31 files, ~5KB each) — pre-distilled knowledge packs that the plugin's skills were authored from. If you're adding a new method or revising an existing one, these are the cheapest source of truth for what the MCP's handler computed.
- **`src/modes/handlers/<X>Handler.ts`** — the original handler code for each mode. These files contain the auto-computation logic (Bayes posteriors, Nash equilibria, Dempster-Shafer mass assignments, etc.) that the plugin skills were designed to teach Claude to perform in prose.
- **`docs/modes/<MODE>.md`** — per-mode documentation that was the input to the knowledge packs.

The MCP repo also hosts `docs/superpowers/plans/` for Phases 1–5 (the original implementation plans for this plugin) and `docs/superpowers/specs/` for the migration design spec, which document why the plugin was built the way it was.

The MCP's `README.md` and `CHANGELOG.md` now prominently direct users to this plugin via `DEPRECATED.md`. Any new mode work should land here, not there.

## The 34-mode invariant (most important thing to know)

The mode set is defined by the filenames in `test/schemas/*.json`. Every mode must appear in **10 places**, and they must stay in sync:

1. `test/schemas/<mode>.json` — authoritative JSON Schema
2. `test/samples/<mode>-valid.json` — realistic worked example
3. `reference/visual-grammar/<mode>.md` — per-mode Mermaid + DOT templates
4. `reference/output-formats/<mode>.md` — schema doc + example
5. `skills/think-<category>/SKILL.md` — the category skill that teaches it
6. `skills/think/SKILL.md` — the router table
7. `skills/think/mode-index.md` — auto-recommend decision tree
8. `reference/taxonomy.md` — canonical taxonomy entry
9. `test/smoke/prompts.json` — smoke-test prompt
10. `scripts/render-html-dashboard.py` — the `MODE_DISPLAY_NAMES` dict maps each mode slug to a human-readable title for the dashboard. Find it with `grep -n MODE_DISPLAY_NAMES scripts/render-html-dashboard.py` (line numbers drift; grep is the stable locator). **No automated check enforces this** — adding a new mode without an entry here silently falls back to `mode.capitalize() + " Reasoning"`, which is wrong for compound names like `gametheory` → "Game Theory" or `firstprinciples` → "First Principles Reasoning".

`python test/test_artifact_consistency.py` enforces set-equality across **1–5 and 9** and will tell you exactly what's missing or extra. Items 6–8 still require manual verification; item 10 has no test at all (drift here only surfaces visually in the rendered dashboard). **Run the consistency test after any mode-set change**, and `grep MODE_DISPLAY_NAMES scripts/render-html-dashboard.py` to verify item 10. The step-by-step for adding a mode is in `ARCHITECTURE.md` ("Adding a new mode").

## Design principles (don't break these)

- **Schema is truth.** If `test/schemas/<mode>.json` rejects a thought, the thought is wrong — not the schema. Skill templates, grammars, and docs defer to it.
- **Top-level strict, nested permissive.** Every schema has `additionalProperties: false` at the top-level thought object (catches typos in required fields) but allows additional properties in nested detail objects (lets Claude produce richer detail than the schema anticipated). Discovered during v0.4.1 smoke tests — see **Gotchas** below.
- **Reasoning and visualization are decoupled.** Skills teach reasoning (the JSON shape). Grammars teach rendering (views over that shape). Changing one must not require touching the other. When adding an export format, you do NOT create per-mode files — the `visual-exporter` agent combines existing per-mode semantic grammars with the new surface-syntax grammar at runtime.
- **Fail loudly.** Silent skips, swallowed exceptions, and default fallbacks are avoided. Where graceful degradation is necessary (e.g., `scripts/render-diagram.py` when `dot`/`mmdc` are missing), it's documented via explicit exit codes (127 missing, 2 with `--allow-skip`, 124 timeout).
- **Auto-discovery where possible; explicit enforcement where needed.** `harness.py` auto-discovers samples from filename conventions; `test_artifact_consistency.py` explicitly enforces set-equality. Both matter — auto-discovery is a force multiplier but silently tolerates gaps, so the set-equality test is the check that catches drift.
- **Some validation rules live in SKILL.md prose, not in JSON Schema.** JSON Schema can't express constraints like "exactly one element of this array has `isActual: true`" or "at least two distinct hypotheses with non-equal scores." These invariants live as written instructions in the relevant `skills/think-<category>/SKILL.md` files and are enforced only by the model following the skill prompt. Examples: `counterfactual` requires exactly one condition with `isIntervention: true`; `modal` requires exactly one world with `isActual: true`; `abductive` requires ≥2 distinct hypotheses (the schema only says `minItems: 1`); `historical` requires ≥2 episodes per pattern. **When editing a SKILL.md file, preserve any "must" / "exactly one" / "at least N" language** — those are load-bearing invariants the schema can't catch. The full per-mode catalog is in `docs/SKILL-INVARIANTS.md`.

## Out of scope (don't add these back)

These are deliberate omissions from the brainstorming session that produced the plugin's design. If you find yourself proposing one of them, stop — the user already declined.

- **No persistent session state across `/think` invocations.** Each invocation is self-contained. The user explicitly chose this in the brainstorming Q5 ("sessions out, visual exports in"). The MCP this plugin replaces had `SessionManager` + `FileSessionStore` + multi-instance file locking; none of it survived. If a user wants a chain, `/think sequential "..."` already returns an N-thought array in one response — no plugin state needed. Do not add a `~/.claude/deepthinking-plugin/thought-log.jsonl` or any equivalent.
- **No Node.js runtime.** Everything is prose + Python stdlib + optional external binaries (`dot`, `mmdc`). The whole point of this plugin is that there is no MCP server.
- **No hard dependency on `dot`/`mmdc`.** Detected at runtime via `shutil.which()`; their absence degrades gracefully via `--allow-skip`. Don't make them required.
- **No third-party test framework.** Tests are plain `python test/foo.py` invocations — no `pytest`, no `unittest`. The repo *does* have a test harness (8 fast Python files + 2 smoke runners totalling 118 automated checks at v0.4.1); it's just not built on a third-party framework. Solo-maintainer simplicity wins over framework features here.

## Skills vs slash commands (architectural distinction)

Claude Code has **two completely separate systems** that can both live in a plugin:

- **Skills** (`skills/<category>/SKILL.md`) are **automatically invoked** by Claude based on conversation context. They are NOT user-typed and have NO `/command` form. Their job is to inject knowledge into Claude's context when relevant.
- **Slash commands** (`commands/<name>.md`) are **user-typed** as `/deepthinking-plugin:<name>`. They are thin invocation wrappers that use `$ARGUMENTS` and typically delegate to a skill for the actual knowledge.

**This plugin uses both:** `commands/think.md` is the user-facing slash command; `skills/think/SKILL.md` (and 12 category skills) carry the reasoning knowledge that the command delegates to. The router skill is loaded automatically when the command body asks Claude to think with a specific mode.

**If you want to add a new user-facing `/foo` command:** create `commands/foo.md`, NOT `skills/foo/SKILL.md`. Putting it in `skills/` will produce confusing "Unknown skill" errors when a user types `/foo` because skills don't have a slash-command surface. (This was discovered the hard way during v0.1.0 manual testing — see Gotcha #6 below for the matching invocation form caveat.)

## Common commands

### Fast automated tests (~5 seconds, no external calls)

```bash
python test/test_plugin_json.py            # plugin.json validity
python test/test_skill_frontmatter.py      # all SKILL.md frontmatter
python test/test_artifact_consistency.py   # 34-mode set-equality across dirs
python test/test_format_grammars.py        # per-format grammar structure
python test/harness.py                     # 40 JSON schema validations (34 valid + 6 invalid)
python test/visual/validate-mermaid.py     # 34 per-mode Mermaid grammars parse
python test/visual/validate-dot.py         # 34 per-mode DOT grammars parse
python test/visual/test-dashboard.py       # HTML dashboard integration
```

Run the full fast suite before committing. Most invariant violations surface in `test_artifact_consistency.py` or `harness.py`. Total: **118 automated checks** at v0.4.1.

### End-to-end smoke tests (invokes headless `claude -p`)

```bash
python test/smoke/run-all-modes.py                        # all 34 modes, ~30–60 min
SMOKE_MODE=bayesian python test/smoke/run-all-modes.py    # single mode
SMOKE_TIMEOUT=300 SMOKE_MODE=analogical python test/smoke/run-all-modes.py  # override timeout for slow modes
python test/smoke/run-router-tests.py                     # /think auto-recommend tests (~20–40 min)
```

Captured outputs land in `test/smoke/captured/` (gitignored). Use single-mode runs when debugging a specific skill — full runs are slow and rarely needed during iteration.

**Timeout guidance from v0.4.1 smoke run:** these modes timed out at 150s and needed 300–420s: physics, evidential, gametheory, analogical, firstprinciples, cryptanalytic, engineering, modal, stochastic. Pass `SMOKE_TIMEOUT=420` when re-running any of them.

## Where to look when…

- **A schema validation is failing** — read the schema in `test/schemas/<mode>.json` first; the error message refers to it directly. Then compare against `test/samples/<mode>-valid.json`. The harness reports up to 5 errors per sample via `Draft7Validator.iter_errors` — look for the first one's `path` field.
- **A skill needs updating** — the router is `skills/think/SKILL.md`; individual methods live in `skills/think-<category>/SKILL.md`. Categories group 2–4 related modes. The auto-recommend decision tree is a separate file: `skills/think/mode-index.md`. The reference schemas in `reference/output-formats/<mode>.md` are what the skill body defers to.
- **A rendering bug appears** — the visual-exporter agent (`agents/visual-exporter.md`) combines `reference/visual-grammar/<mode>.md` (semantic) with `reference/visual-grammar/formats/<format>.md` (surface syntax). Both are plain-text grammar references — not code.
- **The dashboard is broken** — it's a single HTML template at `reference/html-dashboard-template.html`, rendered by `scripts/render-html-dashboard.py`. No build tools, no framework. Uses Mermaid via CDN, pinned to `@11.4.1`.
- **Something is silently swallowing an error** — check `scripts/render-diagram.py` exit codes (0/2/124/127), `run-all-modes.py` repair attribution (look for `PASS (with backslash repair — ...)`), and `validate-*.py` which FAIL on missing code blocks (don't SKIP).

## Gotchas from v0.4.x development

These are real issues that surfaced during the v0.4.0 → v0.4.1 smoke test run and schema relaxation pass. Preserve these patterns:

### 1. Hand-crafted samples can't find schema bugs

The v0.2.0–v0.3.0 hand-crafted samples all validated by design (they were written TO pass the schemas). Real smoke tests with `claude -p` surfaced **6 distinct schema bugs** invisible to the unit tests:

- Nested objects had `additionalProperties: false` too aggressively (e.g., `computability.diagonalization` rejected `contradictionPoint` + `diagonalMatrix` — both legitimate Cantor-diagonal-argument fields)
- Optional scalar fields didn't accept `null`, but Claude commonly emits `null` for absent optionals
- `hybrid.primaryMode` enum only had 4 values; Claude uses any of 34
- `hybrid.thoughtType` enum was 22-valued; Claude uses `"analysis"`, `"evaluation"`, etc.
- `recursive.haltingCondition` and `scientificmethod.falsificationCriteria` were missing top-level fields
- `analogical.sourceDomains` (plural) for multi-source analogies — Claude uses the plural form naturally

**Lesson:** Hand-crafted samples ≠ real Claude output. Always run the end-to-end smoke tests before declaring a schema done. The smoke tests are expensive (~30–60 min full run) but catch a class of bug that unit tests cannot.

### 2. LaTeX-in-JSON-strings

Physics, mathematics, and formallogic modes emit JSON strings containing LaTeX escapes like `F^{μ}_{\ ν}` where `\ ` (backslash-space) is invalid JSON. `run-all-modes.py` has a `repair_lone_backslashes` pass that doubles any backslash not followed by a valid JSON escape character (`\\`, `\"`, `\/`, `\b`, `\f`, `\n`, `\r`, `\t`, `\u`). When the repair triggers, the runner prints `PASS (with backslash repair — JSON escape bug in model output)` so it's attributed, not silent.

**Long-term fix:** Update the affected SKILL.md files to explicitly instruct "escape all backslashes in JSON strings as `\\`". For now, the repair is the safety net.

### 3. Windows + UTF-8

All Python scripts specify `encoding="utf-8"` for every file I/O and subprocess call. `run-all-modes.py` reconfigures `sys.stdout` to UTF-8 (`sys.stdout.reconfigure(encoding="utf-8", errors="replace")`) at the top of the file because arrow characters and math symbols in Claude's output crash cp1252 prints on Windows otherwise.

**Lesson:** Run all scripts with `python -X utf8` or set `PYTHONIOENCODING=utf-8` if you see `UnicodeEncodeError` on Windows.

### 4. `test/visual/validate-*.py` used to SKIP on missing code blocks

This is a regression that v0.4.1 fixed. The original design treated "no mermaid block in a grammar file" as SKIP, but that's exactly the regression the validators exist to catch. Now they FAIL (and there's an `ALLOWED_NO_*` empty allowlist as a pressure-release valve if a grammar legitimately needs to lack a block).

**Lesson:** `SKIP` is almost always wrong. Prefer `FAIL` with an explicit allowlist for the rare legitimate exceptions.

### 5. Security hardening for the HTML dashboard

The `html-dashboard-template.html` loads Mermaid from a CDN. In v0.4.0 it was pinned to `mermaid@11` (floating major-version tag), which would execute arbitrary JavaScript in every historical dashboard if jsdelivr's `@11` tag were ever compromised. v0.4.1 pins to `mermaid@11.4.1` exactly, switches `securityLevel` from `loose` to `strict`, and HTML-escapes ALL user-supplied content injected into the template (including the Mermaid source, which is read by Mermaid's `textContent` so escaping is safe).

**Lesson:** Never use floating CDN tags in content that ships to users and is preserved on disk. Pin the exact version.

### 6. `/think` bare vs `/deepthinking-plugin:think` namespaced

Plugin commands are always namespaced in Claude Code: the canonical form is `/deepthinking-plugin:think`. The shorter `/think` form requires a personal alias at `~/.claude/commands/think.md` — we ship an example at `examples/personal-command-alias/think.md`. This was discovered during v0.1.0 manual testing when the user's first `/think bayesian "..."` failed because the bare form had no resolver.

**Lesson:** Plugin command docs should always document BOTH forms. See README.md "Usage" for the pattern.

## Windows-specific notes for this repo

- Scripts use `python` (not `python3`). When running under the Bash tool on Windows, use forward slashes in paths (e.g., `python test/harness.py`, not `test\harness.py`).
- Optional diagram binaries (`dot` from Graphviz, `mmdc` from `@mermaid-js/mermaid-cli`) are detected at runtime via `shutil.which()` — their absence degrades gracefully; don't add a hard dependency. Install hints for both live in `INSTALL_HINTS` in `scripts/render-diagram.py`.
- Git may warn about `LF will be replaced by CRLF` — that's normal for a Windows-primary repo and not an error.

## Publishing and releases

Version bumps touch:

1. `.claude-plugin/plugin.json` — the `"version"` field (authoritative)
2. `CHANGELOG.md` — new entry above the previous one

This plugin is **not published to npm** — it's installed via `--plugin-dir` or by copying into `~/.claude/plugins/`. Releases are cut via git tags and GitHub Releases:

```bash
git tag -a v0.X.Y -m "v0.X.Y: summary"
git push origin master --tags
gh release create v0.X.Y --title "v0.X.Y — summary" --notes "..."
```

**Release sequence (don't reorder):**

1. Run the full **fast suite** (8 tests, ~5 s). If anything fails, fix it before going further.
2. Commit the changes.
3. Run the full **smoke suite** (`test/smoke/run-all-modes.py`, 30–60 min). This is the only test that catches schema/skill drift against real model output.
4. If smoke surfaces schema bugs, fix them and re-run **just the affected modes** (`SMOKE_MODE=<mode>`).
5. Re-run the **fast suite** to confirm fixes didn't break the structural invariants.
6. Bump `plugin.json` version + `CHANGELOG.md` entry. Do this LAST, in the same commit — if you bump earlier and have to revert, the version goes with the reversion.
7. `git tag -a v0.X.Y` → `git push origin master --tags` → `gh release create v0.X.Y --latest`.

**Watch out for hardcoded equality assertions in tests.** v0.4.1 fixed a latent bug where `plugin.json` was stuck at `0.1.0` for **four releases** because `test_plugin_json.py` had `assert version == "0.1.0"` and was passing vacuously. The fix is to use `re.match(r"^\d+\.\d+\.\d+$", version)`. If you add a new test that checks a count or version, prefer regex / range checks over literal equality — the literal becomes a silent correctness hole the moment the value changes.

v0.4.1 is the current release; see the GitHub Releases page for the full history.

## What's NOT in this file

- User-facing install/usage → `README.md`
- Architecture deep-dive → `ARCHITECTURE.md`
- Per-mode reference schemas → `reference/output-formats/<mode>.md`
- Category skill content → `skills/think-<category>/SKILL.md`
- Visual grammar rules → `reference/visual-grammar/<mode>.md` and `reference/visual-grammar/formats/<format>.md`
- Version history → `CHANGELOG.md`
- Migration from the MCP → `DEPRECATED.md` in the deepthinking-mcp repo
