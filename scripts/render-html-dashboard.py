"""
render-html-dashboard.py — render a deepthinking thought as a standalone HTML dashboard.

Usage:
    python render-html-dashboard.py --thought thought.json --output dashboard.html [--mermaid diagram.mmd]

Reads the template at reference/html-dashboard-template.html, substitutes placeholder
tokens with the thought JSON (and optional pre-rendered Mermaid source), and writes
a single self-contained HTML file. No dependencies beyond the Python stdlib; Mermaid
is loaded from a CDN at page view time.
"""

import argparse
import html
import json
import sys
from datetime import datetime
from pathlib import Path

PLUGIN_ROOT = Path(__file__).parent.parent
TEMPLATE_PATH = PLUGIN_ROOT / "reference" / "html-dashboard-template.html"

MODE_DISPLAY_NAMES = {
    "sequential": "Sequential Reasoning",
    "shannon": "Shannon-Style Decomposition",
    "hybrid": "Hybrid Reasoning",
    "inductive": "Inductive Reasoning",
    "deductive": "Deductive Reasoning",
    "abductive": "Abductive Reasoning",
    "mathematics": "Mathematical Reasoning",
    "physics": "Physical Reasoning",
    "computability": "Computability & Complexity",
    "temporal": "Temporal Reasoning",
    "historical": "Historical Reasoning",
    "bayesian": "Bayesian Inference",
    "evidential": "Evidential Reasoning",
    "causal": "Causal Analysis",
    "counterfactual": "Counterfactual Reasoning",
    "gametheory": "Game Theory",
    "optimization": "Optimization",
    "constraint": "Constraint Satisfaction",
    "analogical": "Analogical Reasoning",
    "firstprinciples": "First Principles Reasoning",
    "metareasoning": "Meta-Reasoning",
    "cryptanalytic": "Cryptanalytic Reasoning",
    "scientificmethod": "Scientific Method",
    "systemsthinking": "Systems Thinking",
    "formallogic": "Formal Logic",
    "engineering": "Engineering Reasoning",
    "algorithmic": "Algorithmic Reasoning",
    "synthesis": "Synthesis",
    "argumentation": "Argumentation (Toulmin)",
    "critique": "Peer-Review Critique",
    "analysis": "Layered Analysis",
    "recursive": "Recursive Reasoning",
    "modal": "Modal Reasoning",
    "stochastic": "Stochastic Reasoning",
}


def fallback_mermaid(thought):
    """Minimal Mermaid diagram derived from top-level thought fields when no source provided."""
    mode = thought.get("mode", "unknown") if isinstance(thought, dict) else "chain"
    lines = [f"graph TD", f'  root["{mode}"]']
    if isinstance(thought, list):
        for i, t in enumerate(thought[:8], start=1):
            label = str(t.get("content", t.get("thoughtNumber", f"thought {i}")))[
                :60
            ].replace('"', "'")
            lines.append(f'  t{i}["{label}"]')
            lines.append(f"  root --> t{i}")
    elif isinstance(thought, dict):
        i = 1
        for key, value in list(thought.items())[:8]:
            if key == "mode":
                continue
            preview = json.dumps(value)[:60].replace('"', "'")
            lines.append(f'  n{i}["{key}: {preview}"]')
            lines.append(f"  root --> n{i}")
            i += 1
    return "\n".join(lines)


def render(thought, mermaid_source, output_path):
    template = TEMPLATE_PATH.read_text(encoding="utf-8")

    if isinstance(thought, list) and thought:
        first_mode = (
            thought[0].get("mode", "unknown")
            if isinstance(thought[0], dict)
            else "chain"
        )
        mode = first_mode
    elif isinstance(thought, dict):
        mode = thought.get("mode", "unknown")
    else:
        mode = "unknown"

    mode_display = MODE_DISPLAY_NAMES.get(mode, mode.capitalize() + " Reasoning")
    thought_json = json.dumps(thought, indent=2, ensure_ascii=False)

    rendered = template
    rendered = rendered.replace("{{MODE}}", html.escape(mode))
    rendered = rendered.replace("{{MODE_DISPLAY}}", html.escape(mode_display))
    rendered = rendered.replace("{{THOUGHT_JSON}}", html.escape(thought_json))
    rendered = rendered.replace("{{THOUGHT_JSON_RAW}}", html.escape(thought_json))
    rendered = rendered.replace("{{MERMAID_SOURCE}}", mermaid_source)
    rendered = rendered.replace(
        "{{TIMESTAMP}}", datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )

    output_path.write_text(rendered, encoding="utf-8")
    return output_path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--thought", required=True, type=Path, help="Path to thought JSON file"
    )
    parser.add_argument(
        "--output", required=True, type=Path, help="Path to write dashboard HTML"
    )
    parser.add_argument(
        "--mermaid", type=Path, help="Optional path to pre-rendered Mermaid source"
    )
    args = parser.parse_args()

    if not args.thought.exists():
        print(f"ERROR: thought file not found: {args.thought}", file=sys.stderr)
        return 1
    if not TEMPLATE_PATH.exists():
        print(f"ERROR: template not found at {TEMPLATE_PATH}", file=sys.stderr)
        return 1

    thought = json.loads(args.thought.read_text(encoding="utf-8"))

    if args.mermaid and args.mermaid.exists():
        mermaid_source = args.mermaid.read_text(encoding="utf-8")
    else:
        mermaid_source = fallback_mermaid(thought)

    render(thought, mermaid_source, args.output)
    print(f"Wrote {args.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
