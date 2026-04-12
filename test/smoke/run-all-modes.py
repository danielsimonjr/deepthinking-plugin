"""
Automated smoke test runner for all 34 deepthinking-plugin modes.

Invokes `claude --plugin-dir <plugin_root> --bare -p` for each mode's test prompt,
extracts the JSON code block from Claude's response, and validates it against the
mode's JSON Schema. Writes per-mode captured outputs to test/smoke/captured/.

Usage:
    cd <plugin-root>
    python test/smoke/run-all-modes.py

Environment:
    SMOKE_TIMEOUT   seconds per mode (default 180)
    SMOKE_MODE      if set, only run this single mode (e.g. SMOKE_MODE=bayesian)
"""

import io
import json
import os
import re
import subprocess
import sys
from pathlib import Path

# Force UTF-8 stdout on Windows so arrow characters and diagrams don't crash prints.
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
else:
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

try:
    import jsonschema
except ImportError:
    print("ERROR: jsonschema not installed. Run: pip install jsonschema")
    sys.exit(1)

PLUGIN_ROOT = Path(__file__).parent.parent.parent
SMOKE_DIR = PLUGIN_ROOT / "test" / "smoke"
CAPTURED_DIR = SMOKE_DIR / "captured"
SCHEMAS_DIR = PLUGIN_ROOT / "test" / "schemas"
PROMPTS_FILE = SMOKE_DIR / "prompts.json"

TIMEOUT = int(os.environ.get("SMOKE_TIMEOUT", "180"))
SINGLE_MODE = os.environ.get("SMOKE_MODE")

JSON_BLOCK_RE = re.compile(r"```json\s*\n(.*?)\n```", re.DOTALL)

# Matches a lone backslash that is NOT part of a valid JSON escape sequence.
# Valid escapes: \" \\ \/ \b \f \n \r \t \uXXXX
INVALID_BACKSLASH_RE = re.compile(r'\\(?![\\"/bfnrtu])')


def repair_lone_backslashes(source):
    """Claude sometimes emits LaTeX-style escapes like `\ ` or `\mu` inside JSON
    strings, which are invalid JSON. Double any backslash that isn't part of a
    recognized escape sequence."""
    return INVALID_BACKSLASH_RE.sub(r"\\\\", source)


def extract_json_block(text):
    """Return the first ```json ... ``` block parsed as Python, or None.

    Tries strict JSON parsing first; on failure, applies a minimal repair pass
    for lone backslashes (common in math/LaTeX output) and retries."""
    for match in JSON_BLOCK_RE.finditer(text):
        candidate = match.group(1).strip()
        try:
            return json.loads(candidate)
        except json.JSONDecodeError:
            try:
                return json.loads(repair_lone_backslashes(candidate))
            except json.JSONDecodeError:
                continue
    return None


def run_mode(mode, prompt):
    """Invoke claude -p for one mode. Return (captured_text, exit_code, timed_out)."""
    cmd = [
        "claude",
        "--plugin-dir",
        str(PLUGIN_ROOT),
        "--bare",
        "-p",
        f'/deepthinking-plugin:think {mode} "{prompt}"',
    ]
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=TIMEOUT,
            errors="replace",
        )
        return result.stdout, result.returncode, False
    except subprocess.TimeoutExpired:
        return "", -1, True


def validate_thought(thought, mode):
    """Validate a parsed thought (object or array of thoughts) against the mode's schema."""
    schema_path = SCHEMAS_DIR / f"{mode}.json"
    if not schema_path.exists():
        return False, f"missing schema at {schema_path}"
    with open(schema_path, "r", encoding="utf-8") as f:
        schema = json.load(f)

    thoughts = thought if isinstance(thought, list) else [thought]
    if not thoughts:
        return False, "empty thought array"

    for i, t in enumerate(thoughts):
        try:
            jsonschema.validate(t, schema)
        except jsonschema.ValidationError as e:
            label = f"thought[{i}]" if len(thoughts) > 1 else "thought"
            return False, f"{label}: {e.message}"
    return True, f"ok ({len(thoughts)} thought{'s' if len(thoughts) > 1 else ''})"


def main():
    CAPTURED_DIR.mkdir(parents=True, exist_ok=True)
    with open(PROMPTS_FILE, "r", encoding="utf-8") as f:
        prompts = json.load(f)

    if SINGLE_MODE:
        prompts = [p for p in prompts if p["mode"] == SINGLE_MODE]
        if not prompts:
            print(f"ERROR: no prompt for mode '{SINGLE_MODE}'")
            return 1

    results = []
    for entry in prompts:
        mode = entry["mode"]
        prompt = entry["prompt"]
        print(f"[{mode}] running (timeout {TIMEOUT}s)...", flush=True)

        captured, exit_code, timed_out = run_mode(mode, prompt)

        raw_path = CAPTURED_DIR / f"{mode}-raw.txt"
        raw_path.write_text(captured, encoding="utf-8")

        if timed_out:
            print(f"  FAIL: timeout after {TIMEOUT}s")
            results.append((mode, False, "timeout"))
            continue

        if exit_code != 0 and not captured:
            print(f"  FAIL: exit {exit_code} with no output")
            results.append((mode, False, f"exit {exit_code}"))
            continue

        thought = extract_json_block(captured)
        if thought is None:
            print("  FAIL: no JSON code block found in output")
            results.append((mode, False, "no JSON block"))
            continue

        json_path = CAPTURED_DIR / f"{mode}-parsed.json"
        json_path.write_text(json.dumps(thought, indent=2), encoding="utf-8")

        ok, reason = validate_thought(thought, mode)
        if ok:
            print("  PASS")
            results.append((mode, True, "ok"))
        else:
            print(f"  FAIL: schema violation: {reason}")
            results.append((mode, False, reason))

    print()
    passed = sum(1 for _, ok, _ in results if ok)
    failed = len(results) - passed
    print(f"===== Summary: {passed}/{len(results)} passed, {failed} failed =====")
    for mode, ok, reason in results:
        marker = "PASS" if ok else "FAIL"
        print(f"  {marker:4s}  {mode:20s}  {reason}")

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
