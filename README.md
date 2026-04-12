# deepthinking-plugin

Structured reasoning methods for Claude Code. This plugin teaches Claude 34 reasoning modes (Bayesian inference, causal analysis, game theory, etc.) as native skills. Unlike the original `deepthinking-mcp` TypeScript server, no external runtime is required — Claude learns each method from skill content and produces the structured output directly.

## Status

**v0.1.0 — Prototype.** Three modes implemented: Sequential, Inductive, Deductive. The remaining 31 modes ship in subsequent versions.

## Install

Install locally for development:

    claude --plugin-dir "C:/Users/danie/Dropbox/Github/deepthinking-plugin"

## Usage

Invoke a specific mode:

    /think sequential "Break down the steps to migrate this database"
    /think inductive "Given these three incidents, what pattern do they share?"
    /think deductive "If all users in the admin group can edit posts, and Alice is in the admin group, can Alice edit posts?"

Or let the router auto-recommend:

    /think "Why did the last three deployments fail?"

Each invocation produces a structured JSON output matching the mode's schema. See `reference/output-formats/` for per-mode schemas and examples.

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
