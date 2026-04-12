"""
Test harness for deepthinking-plugin.
Validates sample thought outputs against JSON schemas.
"""

import json
import sys
from pathlib import Path

try:
    import jsonschema
except ImportError:
    print("ERROR: jsonschema library not installed. Run: pip install jsonschema")
    sys.exit(1)

TEST_DIR = Path(__file__).parent
SCHEMA_DIR = TEST_DIR / "schemas"
SAMPLE_DIR = TEST_DIR / "samples"

# Map each sample file to its expected schema + expected outcome
SAMPLES = [
    ("sequential-valid.json", "sequential.json", True),
    ("inductive-valid.json", "inductive.json", True),
    ("deductive-valid.json", "deductive.json", True),
    ("sequential-invalid.json", "sequential.json", False),
]


def load_schema(name):
    with open(SCHEMA_DIR / name, "r", encoding="utf-8") as f:
        return json.load(f)


def load_sample(name):
    with open(SAMPLE_DIR / name, "r", encoding="utf-8") as f:
        return json.load(f)


def run_tests():
    passed = 0
    failed = 0
    for sample_name, schema_name, should_pass in SAMPLES:
        try:
            sample = load_sample(sample_name)
            schema = load_schema(schema_name)
            jsonschema.validate(sample, schema)
            # Validation succeeded
            if should_pass:
                print(f"PASS: {sample_name} validates against {schema_name}")
                passed += 1
            else:
                print(f"FAIL: {sample_name} should have failed validation but passed")
                failed += 1
        except jsonschema.ValidationError as e:
            # Validation failed
            if not should_pass:
                print(f"PASS: {sample_name} correctly rejected by {schema_name}")
                passed += 1
            else:
                print(f"FAIL: {sample_name} should have validated but got: {e.message}")
                failed += 1
    print()
    print(f"Results: {passed} passed, {failed} failed")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(run_tests())
