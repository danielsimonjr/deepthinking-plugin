"""
render-diagram.py — wraps external diagram-rendering binaries.

Usage:
    python render-diagram.py --format mermaid --output out.svg < input.mmd
    python render-diagram.py --format dot --output out.png --render-as png < input.dot

Input is read from stdin. If the required binary is not installed, the
script prints the source to stdout and exits 0 (graceful degradation).

Required binaries (optional):
    - graphviz (`dot` on PATH) - for DOT -> SVG/PNG
    - @mermaid-js/mermaid-cli (`mmdc` on PATH) - for Mermaid -> SVG/PNG
"""

import argparse
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


def render_dot(source: str, output: Path, fmt: str) -> int:
    if not shutil.which("dot"):
        print(
            "# graphviz not installed. Install with: winget install Graphviz.Graphviz",
            file=sys.stderr,
        )
        print(source)
        return 0
    with tempfile.NamedTemporaryFile(
        "w", suffix=".dot", delete=False, encoding="utf-8"
    ) as f:
        f.write(source)
        tmp = Path(f.name)
    try:
        result = subprocess.run(
            ["dot", f"-T{fmt}", str(tmp), "-o", str(output)],
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        if result.returncode != 0:
            print(f"ERROR from dot: {result.stderr}", file=sys.stderr)
            return result.returncode
        print(f"Wrote {output}")
        return 0
    finally:
        tmp.unlink(missing_ok=True)


def render_mermaid(source: str, output: Path, fmt: str) -> int:
    if not shutil.which("mmdc"):
        print(
            "# mermaid-cli not installed. Install with: npm install -g @mermaid-js/mermaid-cli",
            file=sys.stderr,
        )
        print(source)
        return 0
    with tempfile.NamedTemporaryFile(
        "w", suffix=".mmd", delete=False, encoding="utf-8"
    ) as f:
        f.write(source)
        tmp = Path(f.name)
    try:
        result = subprocess.run(
            ["mmdc", "-i", str(tmp), "-o", str(output)],
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        if result.returncode != 0:
            print(f"ERROR from mmdc: {result.stderr}", file=sys.stderr)
            return result.returncode
        print(f"Wrote {output}")
        return 0
    finally:
        tmp.unlink(missing_ok=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--format", choices=["mermaid", "dot"], required=True, help="Source format"
    )
    parser.add_argument("--output", required=True, type=Path, help="Output file path")
    parser.add_argument(
        "--render-as",
        choices=["svg", "png"],
        default="svg",
        help="Output format (svg/png)",
    )
    args = parser.parse_args()

    source = sys.stdin.read()
    if not source.strip():
        print("ERROR: no source on stdin", file=sys.stderr)
        return 1

    if args.format == "dot":
        return render_dot(source, args.output, args.render_as)
    if args.format == "mermaid":
        return render_mermaid(source, args.output, args.render_as)
    return 1


if __name__ == "__main__":
    sys.exit(main())
