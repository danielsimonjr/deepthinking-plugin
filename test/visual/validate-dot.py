"""
Validate that every mode's visual grammar contains at least one parseable
DOT code block. Syntactic check only -- does not invoke graphviz.
"""

import re
import sys
from pathlib import Path

GRAMMAR_DIR = Path(__file__).parent.parent.parent / "reference" / "visual-grammar"

DOT_START = re.compile(r"(strict\s+)?(digraph|graph)\s+\w*\s*\{", re.MULTILINE)


def extract_dot_blocks(text: str):
    return re.findall(r"```dot\n(.*?)\n```", text, re.DOTALL)


def validate_dot(source: str):
    if not DOT_START.search(source):
        return False, "no digraph/graph declaration"
    if source.count("{") != source.count("}"):
        return False, "unbalanced curly braces"
    return True, "ok"


def main():
    passed = 0
    failed = 0
    skipped = 0
    for grammar_file in sorted(GRAMMAR_DIR.glob("*.md")):
        content = grammar_file.read_text(encoding="utf-8")
        blocks = extract_dot_blocks(content)
        if not blocks:
            print(f"SKIP: {grammar_file.name} has no dot block")
            skipped += 1
            continue
        all_ok = True
        for i, block in enumerate(blocks):
            ok, reason = validate_dot(block)
            if not ok:
                print(f"FAIL: {grammar_file.name} block {i + 1}: {reason}")
                all_ok = False
        if all_ok:
            print(f"PASS: {grammar_file.name} ({len(blocks)} blocks)")
            passed += 1
        else:
            failed += 1
    print()
    print(f"Results: {passed} passed, {failed} failed, {skipped} skipped")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
