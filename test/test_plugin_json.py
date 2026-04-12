"""Smoke test: plugin.json parses and has required fields."""

import json
from pathlib import Path

PLUGIN_ROOT = Path(__file__).parent.parent
MANIFEST = PLUGIN_ROOT / ".claude-plugin" / "plugin.json"


def test_plugin_json_exists_and_parses():
    assert MANIFEST.exists(), f"Missing manifest at {MANIFEST}"
    with open(MANIFEST, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data["name"] == "deepthinking-plugin"
    assert data["version"] == "0.1.0"
    assert "description" in data and len(data["description"]) > 10
    assert "author" in data


if __name__ == "__main__":
    test_plugin_json_exists_and_parses()
    print("PASS: plugin.json is valid")
