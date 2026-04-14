# deepthinking-plugin

Structured reasoning methods for Claude Code. This plugin teaches Claude 34 reasoning modes (Bayesian inference, causal analysis, game theory, etc.) as native skills. Unlike the original `deepthinking-mcp` TypeScript server, no external runtime is required — Claude learns each method from skill content and produces the structured output directly.

## Status

**v0.5.3 — All 34 reasoning modes shipped.** End-to-end smoke tested via headless `claude -p` against all modes; interactive HTML dashboard + 13 output formats supported. Both `deductive` and `inductive` now support optional multi-step reasoning chains (`derivationSteps[]` and `inductionSteps[]` respectively). See [CHANGELOG.md](CHANGELOG.md) for the v0.1.0 → v0.5.3 progression.

## Install

### Development (load from a local directory)

    claude --plugin-dir "C:/path/to/deepthinking-plugin"

### Permanent install

Copy the plugin directory into your personal plugins folder:

    cp -r deepthinking-plugin ~/.claude/plugins/

Claude Code will auto-discover it on the next session. No `--plugin-dir` flag needed.

### Optional: shorter `/think` alias

After installing the plugin, all commands are namespaced as `/deepthinking-plugin:think`. If you want the shorter bare `/think` form, copy the example personal command alias:

**Windows (PowerShell):**

    Copy-Item "examples/personal-command-alias/think.md" "$env:USERPROFILE\.claude\commands\think.md"

**macOS / Linux:**

    mkdir -p ~/.claude/commands
    cp examples/personal-command-alias/think.md ~/.claude/commands/think.md

See `examples/personal-command-alias/README.md` for details.

## Usage

### Canonical form (works after plugin install)

    /deepthinking-plugin:think sequential "Break down the steps to migrate this database"
    /deepthinking-plugin:think inductive "Given these three incidents (A, B, C), what pattern do they share?"
    /deepthinking-plugin:think deductive "If all users in admin can edit posts and Alice is in admin, can Alice edit posts?"
    /deepthinking-plugin:think "Why did the last three deployments fail?"

### Short form (requires the optional personal alias installed above)

    /think sequential "Break down the steps to migrate this database"
    /think inductive "Given these three incidents (A, B, C), what pattern do they share?"
    /think deductive "If all users in admin can edit posts and Alice is in admin, can Alice edit posts?"
    /think "Why did the last three deployments fail?"

Both forms produce the same structured JSON output matching the mode's schema. See `reference/output-formats/` for per-mode schemas and worked examples.

### Rendering diagrams (v0.3.0+)

After any `/think` invocation, render the output as a diagram:

    /think-render                  # default: mermaid
    /think-render dot              # DOT source
    /think-render svg              # SVG (requires `dot` on PATH)
    /think-render png              # PNG (requires `mmdc` on PATH)

The `/think-render` command invokes the `visual-exporter` agent, which reads the per-mode grammar at `reference/visual-grammar/<mode>.md` and produces diagram source from your most recent structured thought. For SVG/PNG output, it pipes the source through `scripts/render-diagram.py` which wraps external binaries.

**Install optional diagram binaries:**

    # Graphviz (for DOT -> SVG/PNG)
    winget install Graphviz.Graphviz       # Windows
    brew install graphviz                   # macOS
    apt install graphviz                    # Linux

    # Mermaid CLI (for Mermaid -> SVG/PNG)
    npm install -g @mermaid-js/mermaid-cli

The render script **gracefully degrades** when binaries are missing — it prints the source to stdout with an install hint, so diagrams still work at the source level.

### All 13 export formats (v0.5.0+)

| Format | Source | Consumers |
|---|---|---|
| `mermaid` | per-mode grammar | GitHub markdown, Obsidian, Notion, mmdc |
| `dot` | per-mode grammar | Graphviz, yEd, any DOT viewer |
| `ascii` | format grammar | Terminal, commit messages, plain-text docs |
| `json` | thought native | jq, any JSON consumer |
| `markdown` | format grammar | GitHub, GitLab, wikis, Discord, Slack |
| `graphml` | format grammar | yEd, Gephi, Cytoscape, NetworkX |
| `html` | format grammar | Static sites, documentation, email |
| `tikz` | format grammar | LaTeX (Overleaf, pdflatex), academic papers |
| `uml` | format grammar | PlantUML, Mermaid (fallback UML) |
| `modelica` | format grammar | OpenModelica, Wolfram System Modeler |
| `dashboard` | template + renderer | Any modern browser (standalone HTML file) |
| `latex-math` | format grammar | Overleaf, pdflatex, MathJax/KaTeX, academic papers |
| `csv` | format grammar | Excel, R, pandas, databases, jq |

The `visual-exporter` agent routes your format choice by reading both the per-mode grammar (`reference/visual-grammar/<mode>.md`) and the format grammar (`reference/visual-grammar/formats/<format>.md`) and substituting field values from your thought.

### Interactive HTML dashboard

    /think-render dashboard

Produces a self-contained HTML file with:
- Rendered Mermaid diagram (via Mermaid CDN, loaded at view time)
- Collapsible JSON explorer for the thought
- Dark/light mode (respects `prefers-color-scheme`)
- Export buttons: Copy JSON, Download JSON, Print
- Responsive layout (works on phone, tablet, and desktop)

The dashboard is generated by `scripts/render-html-dashboard.py` which substitutes the thought JSON and Mermaid source into `reference/html-dashboard-template.html`. No build tools required.

## Testing

### Fast automated tests

    python test/test_plugin_json.py           # plugin.json validity
    python test/test_skill_frontmatter.py     # all 13 SKILL.md have valid frontmatter
    python test/harness.py                    # 35 JSON schema validations
    python test/visual/validate-mermaid.py    # 34 per-mode Mermaid grammars parse
    python test/visual/validate-dot.py        # 34 per-mode DOT grammars parse
    python test/visual/test-dashboard.py      # HTML dashboard integration

### End-to-end smoke tests (v0.4.0+)

    python test/smoke/run-all-modes.py

Runs headless `claude -p` for each of the 34 modes with a realistic test prompt, captures the JSON output, and validates it against the mode's schema. Takes ~30-60 minutes for all 34 (~90-150 seconds per mode). Environment variables:

- `SMOKE_TIMEOUT=120` — seconds per mode (default 180)
- `SMOKE_MODE=bayesian` — run only a single mode (useful for debugging)

Captured outputs land in `test/smoke/captured/` (gitignored).

## Migration from deepthinking-mcp

This plugin replaces the MCP server at `C:/Users/danie/Dropbox/Github/deepthinking-mcp`. The main differences:

- No Node.js process
- No persistent session state
- Claude reasons natively instead of calling tools
- Structured output enforced by skill templates, not Zod validators

See `docs/superpowers/specs/2026-04-12-deepthinking-plugin-migration-design.md` in the source repo for the full rationale.
