---
description: "Render the most recent structured thought output (from /think) as a diagram. Usage: /think-render [format] where format is mermaid, dot, ascii, svg, or png (defaults to mermaid)."
argument-hint: "[mermaid|dot|ascii|svg|png]"
---

The user invoked `/think-render` with arguments: `$ARGUMENTS`

## What to do

1. **Find the most recent /think output in this conversation.** Look for a JSON code block matching one of the 34 mode schemas (any object with a `mode` field whose value is a recognized mode slug). If multiple recent outputs exist, use the latest one. If an array of thoughts exists (as for sequential or shannon chains), treat the whole array as the target.

2. **Parse the mode** from the JSON's `mode` field (or the first thought's `mode` if it's an array).

3. **Determine the target format** from `$ARGUMENTS`. Default to `mermaid` if `$ARGUMENTS` is empty. Accepted values: `mermaid`, `dot`, `ascii`, `json`, `markdown`, `svg`, `png`.

4. **Invoke the visual-exporter subagent** (at `agents/visual-exporter.md`) with:
   - The thought JSON
   - The target format
   The agent reads `reference/visual-grammar.md` (shared conventions) and `reference/visual-grammar/<mode>.md` (per-mode rules), then produces the diagram source by substituting the actual field values from the thought into the grammar templates.

5. **If format is `svg` or `png`:** after the agent emits Mermaid or DOT source, call `scripts/render-diagram.py` by piping the source through stdin:
   ```bash
   echo "<source>" | python scripts/render-diagram.py --format <mermaid|dot> --output <output-path> --render-as <svg|png>
   ```
   If the required binary (`dot` or `mmdc`) is not installed, the script gracefully prints the source to stdout with an install hint on stderr — that's acceptable fallback behavior.

6. **Return** the diagram source as a code block, plus the rendered file path if applicable. If a tool was missing, note the install command.

## If no recent /think output exists

Respond: "No recent `/think` output found in this conversation. Run `/think <mode> \"<problem>\"` first, then use `/think-render` to visualize the result."

## Fallback when the mode has no grammar file

If `reference/visual-grammar/<mode>.md` doesn't exist (shouldn't happen in v0.3.0 — all 34 modes have grammar files), fall back to a generic DAG rendering: each top-level field of the JSON as a node, nested objects as subgraphs, arrays as parallel sibling nodes.
