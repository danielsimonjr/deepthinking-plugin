"""Validate each SKILL.md has the required YAML frontmatter."""

import re
from pathlib import Path

PLUGIN_ROOT = Path(__file__).parent.parent
SKILLS_DIR = PLUGIN_ROOT / "skills"

REQUIRED_KEYS = ["name", "description"]
FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)


def check_skill(skill_md):
    content = skill_md.read_text(encoding="utf-8")
    match = FRONTMATTER_RE.match(content)
    assert match, f"{skill_md}: no YAML frontmatter found"
    frontmatter = match.group(1)
    for key in REQUIRED_KEYS:
        assert re.search(rf"^{key}:\s*.+", frontmatter, re.MULTILINE), (
            f"{skill_md}: missing required key '{key}'"
        )
    # Description should be substantial (>20 chars)
    desc_match = re.search(r"^description:\s*(.+)", frontmatter, re.MULTILINE)
    desc_text = desc_match.group(1).strip() if desc_match else ""
    assert len(desc_text) > 20, f"{skill_md}: description too short"


def main():
    skills = sorted(SKILLS_DIR.rglob("SKILL.md"))
    assert len(skills) == 3, f"Expected 3 SKILL.md files, found {len(skills)}"
    for s in skills:
        check_skill(s)
        print(f"PASS: {s.relative_to(PLUGIN_ROOT)}")
    print(f"\nAll {len(skills)} skills have valid frontmatter.")


if __name__ == "__main__":
    main()
