# deepthinking-plugin

Structured reasoning methods for Claude Code. This plugin teaches Claude 34 reasoning modes (Bayesian inference, causal analysis, game theory, etc.) as native skills. Unlike the original `deepthinking-mcp` TypeScript server, no external runtime is required — Claude learns each method from skill content and produces the structured output directly.

## Status

**v0.1.0 — Prototype.** Three modes implemented: Sequential, Inductive, Deductive. The remaining 31 modes ship in subsequent versions.

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

## Testing

    cd test && python harness.py

Runs JSON schema validation over the sample outputs.

## Migration from deepthinking-mcp

This plugin replaces the MCP server at `C:/Users/danie/Dropbox/Github/deepthinking-mcp`. The main differences:

- No Node.js process
- No persistent session state
- Claude reasons natively instead of calling tools
- Structured output enforced by skill templates, not Zod validators

See `docs/superpowers/specs/2026-04-12-deepthinking-plugin-migration-design.md` in the source repo for the full rationale.
