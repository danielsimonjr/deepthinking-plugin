"""
test_skill_invariants.py — validate per-mode rules that JSON Schema cannot enforce.

The canonical catalog of these rules is docs/SKILL-INVARIANTS.md. A given
mode's JSON Schema defines the SHAPE of a valid thought, but cannot express
constraints like "exactly one element of this array has isActual=true" or
"the conclusion's confidence must not exceed the minimum in its derivation
chain". Those invariants live in the skill prose (skills/think-<category>/
SKILL.md) and are expected to be followed by the model.

This test walks both test/samples/<mode>-valid.json (the hand-crafted
reference fixtures, always checked) and test/smoke/captured/<mode>-parsed.json
(the last real Claude output, checked only if present) and applies the
invariant check for each relevant mode. It complements test/harness.py:

  - harness.py    : does the thought MATCH the schema?
  - this file     : does the thought HONOR the schema-unenforceable rules?

Exit 0 if every applicable file satisfies its invariant; exit non-zero on
any failure with a clear per-check report.

Run with `python test/test_skill_invariants.py` — no pytest, no unittest,
plain stdlib. Do NOT run with `python -O` since any `assert` usage would be
stripped (the test uses explicit if/return instead for safety).
"""

import json
import re
import sys
from pathlib import Path

PLUGIN_ROOT = Path(__file__).parent.parent
SAMPLES_DIR = PLUGIN_ROOT / "test" / "samples"
CAPTURED_DIR = PLUGIN_ROOT / "test" / "smoke" / "captured"


# ---------------------------------------------------------------------------
# Per-mode invariant checks
#
# Each function takes a parsed thought (dict) and returns (ok, reason).
# A return of (True, "...") means the invariant is satisfied.
# A return of (False, "...") means the invariant was violated; the reason
# string should be concrete enough to diagnose the specific violation.
#
# Array-of-thoughts modes (sequential, shannon, hybrid) are handled at the
# dispatch layer below — none of the 6 invariant-bearing modes is an
# array-of-thoughts mode, so the check functions only handle dict input.
# ---------------------------------------------------------------------------


def check_abductive(thought: dict) -> tuple[bool, str]:
    """≥2 hypotheses with non-equal scores.

    JSON Schema has only `hypotheses.minItems: 1` on abductive, which is
    under-constrained: a thought with a single hypothesis is not abduction
    (abduction is explicitly inference to the BEST explanation, which
    requires at least one competitor). Two hypotheses with IDENTICAL scores
    are also insufficient — the whole point is to have a preference ordering.
    """
    hyps = thought.get("hypotheses")
    if not isinstance(hyps, list):
        return False, "no hypotheses array"
    if len(hyps) < 2:
        return False, (
            f"abductive requires ≥2 hypotheses, got {len(hyps)} — "
            "a single hypothesis is not abduction"
        )
    # Distinguish "missing scores" from "equal scores" — they warrant
    # different error messages. The schema requires `score` on every
    # hypothesis, so a missing score would typically fail schema validation
    # first; this check is defensive for the case where the schema pass
    # somehow lets a scoreless hypothesis through.
    scores_present = []
    missing_count = 0
    for h in hyps:
        if not isinstance(h, dict):
            continue
        s = h.get("score")
        if s is None:
            missing_count += 1
        else:
            scores_present.append(s)
    if missing_count > 0:
        return False, (
            f"abductive: {missing_count} of {len(hyps)} hypotheses lack a "
            "`score` field — the schema requires a score on every hypothesis "
            "so this should have failed schema validation first"
        )
    if len(set(scores_present)) < 2:
        return False, (
            f"abductive requires hypotheses with non-equal scores, got "
            f"{scores_present} — abduction is a preference ordering, not a tie"
        )
    return True, "ok"


def check_counterfactual(thought: dict) -> tuple[bool, str]:
    """Exactly one condition with isIntervention=True per counterfactual scenario.

    JSON Schema cannot express "exactly N of this kind". The rule: a
    counterfactual scenario isolates ONE intervention against the actual
    baseline; multiple simultaneous interventions break isolation and make
    the analysis unfalsifiable (you can't tell which change caused which
    outcome). A counterfactual thought may contain multiple scenarios in the
    top-level counterfactuals[] array, and each scenario must have exactly
    one intervention.
    """
    counterfactuals = thought.get("counterfactuals")
    if not isinstance(counterfactuals, list):
        return False, "no counterfactuals array"
    if len(counterfactuals) == 0:
        return False, (
            "counterfactual requires at least one scenario in the "
            "counterfactuals array — a counterfactual thought with zero "
            "scenarios has nothing to compare against the actual baseline"
        )
    for i, cf in enumerate(counterfactuals):
        if not isinstance(cf, dict):
            continue
        conds = cf.get("conditions")
        if not isinstance(conds, list):
            return False, f"counterfactuals[{i}] has no conditions array"
        iv_count = sum(
            1 for c in conds if isinstance(c, dict) and c.get("isIntervention") is True
        )
        if iv_count != 1:
            label = cf.get("id") or f"index {i}"
            return False, (
                f"counterfactuals[{label}] has {iv_count} interventions, "
                "must be exactly 1 (one intervention per scenario)"
            )
    return True, "ok"


def check_historical(thought: dict) -> tuple[bool, str]:
    """Patterns with verdictApplies=True require ≥2 distinct episodes.

    JSON Schema has `patterns.items.episodes.minItems: 1`, which is correct
    for REJECTED patterns (verdictApplies=False — you considered one similar
    incident and explained why the pattern doesn't actually apply) but
    under-constrained for ASSERTED patterns (verdictApplies=True — you're
    claiming a generalization from the data). A generalization from n=1 is
    an anecdote, not a pattern.

    Patterns without a verdictApplies field, or with verdictApplies=False,
    are exempt from this check — only the assertive case triggers the rule.
    """
    patterns = thought.get("patterns")
    if not isinstance(patterns, list):
        return True, "ok (no patterns to check)"
    for i, p in enumerate(patterns):
        if not isinstance(p, dict):
            continue
        # Only assertive patterns trigger the rule. Rejected or unverdicted
        # patterns are exempt because they are not claiming a generalization.
        if p.get("verdictApplies") is not True:
            continue
        episodes = p.get("episodes")
        if not isinstance(episodes, list) or len(episodes) < 2:
            label = p.get("id") or f"index {i}"
            count = len(episodes) if isinstance(episodes, list) else 0
            return False, (
                f"historical pattern[{label}] is asserted (verdictApplies=True) "
                f"but has {count} episode(s); asserted patterns require ≥2 "
                "distinct episodes (one is anecdote, not pattern)"
            )
    return True, "ok"


def check_modal(thought: dict) -> tuple[bool, str]:
    """Exactly one world in possibleWorlds has isActual=True.

    JSON Schema cannot express "exactly N true values across array elements".
    Modal reasoning requires a single distinguished ground-truth world to
    anchor the possibility/necessity relations; having zero actual worlds
    means no anchor, and having multiple actual worlds means the model has
    no referent for "what actually happened" vs the alternatives.

    Consistency check: if the thought also has a top-level `actualWorld`
    field (a string reference), its value should match the `id` of the world
    with isActual=True. Mismatch is a softer violation — reported but still
    counts as a failure since it indicates the two signals disagree.
    """
    worlds = thought.get("possibleWorlds")
    if not isinstance(worlds, list):
        return False, "no possibleWorlds array"
    actual_worlds = [
        w for w in worlds if isinstance(w, dict) and w.get("isActual") is True
    ]
    if len(actual_worlds) != 1:
        return False, (
            f"modal requires exactly 1 world with isActual=True, "
            f"got {len(actual_worlds)} — modal reasoning needs a single "
            "distinguished ground-truth world"
        )
    # Secondary consistency: the top-level actualWorld reference should point
    # to the world marked isActual. A mismatch indicates the thought is
    # internally inconsistent even though both fields individually validate.
    actual_world_ref = thought.get("actualWorld")
    if isinstance(actual_world_ref, str):
        marked_id = actual_worlds[0].get("id")
        if isinstance(marked_id, str) and marked_id != actual_world_ref:
            return False, (
                f"modal has top-level actualWorld={actual_world_ref!r} but the "
                f"world with isActual=True has id={marked_id!r} — these must agree"
            )
    return True, "ok"


def check_firstprinciples(thought: dict) -> tuple[bool, str]:
    """conclusion.certainty must not exceed min(step.confidence in derivation chain).

    A cross-field semantic rule: a first-principles conclusion cannot be MORE
    certain than its weakest supporting step. JSON Schema cannot express
    constraints that compare values across different fields of the same
    thought.

    The check:
      1. Read `conclusion.certainty` (the final confidence in the conclusion).
      2. Read `conclusion.derivationChain` (array of step numbers).
      3. For each step number in the chain, look up the matching
         `derivationSteps[i].confidence` and collect them.
      4. If any are present, assert `conclusion.certainty ≤ min(collected)`.

    If the chain is empty, the certainty field is missing, or no steps carry
    confidence values, the check passes (nothing to compare against).
    """
    conc = thought.get("conclusion")
    steps = thought.get("derivationSteps")
    if not isinstance(conc, dict) or not isinstance(steps, list):
        return True, "ok (no conclusion or derivationSteps to check)"
    cert = conc.get("certainty")
    chain = conc.get("derivationChain")
    if cert is None or not isinstance(chain, list):
        return True, "ok (no certainty or chain)"
    # Build two maps: step number → confidence (only when present), and
    # the set of ALL step numbers that actually exist. We need the second
    # to detect broken chain references (chain references a step number
    # that doesn't exist in derivationSteps at all).
    step_numbers_present = set()
    step_confs_by_num: dict = {}
    for s in steps:
        if not isinstance(s, dict):
            continue
        num = s.get("stepNumber")
        if num is None:
            continue
        step_numbers_present.add(num)
        conf = s.get("confidence")
        if conf is not None:
            step_confs_by_num[num] = conf
    # Detect chain entries that point to step numbers that don't exist —
    # this is a referential-integrity bug in the thought even though the
    # schema permits it (JSON Schema can't express cross-field integrity).
    missing_refs = [n for n in chain if n not in step_numbers_present]
    if missing_refs:
        return False, (
            f"firstprinciples conclusion.derivationChain references step "
            f"number(s) {missing_refs} that do not exist in derivationSteps — "
            "broken chain reference"
        )
    chain_confs = [step_confs_by_num[n] for n in chain if n in step_confs_by_num]
    if not chain_confs:
        return True, "ok (chain resolves but no confidence values to compare)"
    min_conf = min(chain_confs)
    if cert > min_conf:
        return False, (
            f"firstprinciples conclusion.certainty ({cert}) > min step "
            f"confidence ({min_conf}) in chain — conclusion cannot be more "
            "certain than its weakest derivation step"
        )
    return True, "ok"


# Regexes for the bayesian check — compiled once at module load.
# _BAYESIAN_NUMBER_RE matches a numeric sequence (integer or decimal); real
# arithmetic requires AT LEAST TWO numbers so we can verify operands exist,
# not just a result. _BAYESIAN_ARITH_OP_RE matches TRUE arithmetic operators
# (NOT `=` — equals alone appears in prose like "probability = high" which
# isn't arithmetic). Unicode × and ÷ are included because Claude commonly
# emits them in math output instead of the ASCII * and /.
_BAYESIAN_NUMBER_RE = re.compile(r"\d+(?:\.\d+)?")
_BAYESIAN_ARITH_OP_RE = re.compile(r"[+\-*/×÷]")


def check_bayesian(thought: dict) -> tuple[bool, str]:
    """posterior.calculation must show arithmetic, not just a final number.

    A skill-prose rule: the bayesian worked output is supposed to be
    auditable — readers and verifiers need to see the math, not just the
    result. A calculation field containing only "0.66" or "probability =
    high" is formally valid JSON but defeats the purpose of the mode.

    Heuristic check (the invariant is qualitative, so we approximate):
      1. The calculation field must be a non-empty string ≥ 10 characters.
      2. It must contain at least TWO distinct numeric sequences (the
         operands of arithmetic, not just a single result value).
      3. It must contain at least one TRUE arithmetic operator from
         {+, -, *, /, ×, ÷} — the equals sign alone is insufficient because
         prose like "probability = high" would otherwise pass.

    This won't catch every evasion (a well-crafted non-arithmetic string
    with two numbers and a dash could satisfy all three), but it catches
    the common failure modes: a bare result, a prose summary, or a
    single-number statement.
    """
    post = thought.get("posterior")
    if not isinstance(post, dict):
        return False, "no posterior object"
    calc = post.get("calculation")
    if not isinstance(calc, str):
        return (
            False,
            f"bayesian.posterior.calculation must be a string, got {type(calc).__name__}",
        )
    if len(calc.strip()) < 10:
        return False, (
            f"bayesian.posterior.calculation too short to be arithmetic: {calc!r}"
        )
    numbers = _BAYESIAN_NUMBER_RE.findall(calc)
    if len(numbers) < 2:
        return False, (
            f"bayesian.posterior.calculation must contain ≥2 numbers to show "
            f"arithmetic (found {len(numbers)}: {numbers}): {calc!r}"
        )
    if not _BAYESIAN_ARITH_OP_RE.search(calc):
        return False, (
            f"bayesian.posterior.calculation has no arithmetic operator "
            f"from {{+, -, *, /, ×, ÷}} — '=' alone is not arithmetic: {calc!r}"
        )
    return True, "ok"


# ---------------------------------------------------------------------------
# Dispatch
# ---------------------------------------------------------------------------

CHECKS = {
    "abductive": check_abductive,
    "counterfactual": check_counterfactual,
    "historical": check_historical,
    "modal": check_modal,
    "firstprinciples": check_firstprinciples,
    "bayesian": check_bayesian,
}


def check_file(mode: str, source_label: str, path: Path):
    """Run the mode's invariant check against a single file.

    Returns a tuple (mode, source_label, ok, reason) or None if the file
    doesn't exist (the captured/ source is optional, so missing files are
    not a failure — they're just not checked).
    """
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError, UnicodeDecodeError) as e:
        return (mode, source_label, False, f"ERROR parsing {path.name}: {e}")

    # None of the 6 invariant-bearing modes produces an array-of-thoughts
    # output (those are sequential/shannon/hybrid, which have no invariants
    # in this test). If we see an array anyway, skip the check — the
    # schema-validation harness.py will catch any structural problem.
    # Use None as the ok value to signal "skipped" in the dispatch/summary,
    # distinct from (True, ...) which is a genuine pass.
    if not isinstance(data, dict):
        return (
            mode,
            source_label,
            None,
            "skipped (array-of-thoughts — no invariant applies)",
        )

    check = CHECKS[mode]
    ok, reason = check(data)
    return (mode, source_label, ok, reason)


def main() -> int:
    results = []
    for mode in sorted(CHECKS.keys()):
        sample_path = SAMPLES_DIR / f"{mode}-valid.json"
        captured_path = CAPTURED_DIR / f"{mode}-parsed.json"
        for source_label, path in (
            ("sample", sample_path),
            ("captured", captured_path),
        ):
            r = check_file(mode, source_label, path)
            if r is not None:
                results.append(r)

    if not results:
        print("ERROR: no sample or captured files found for any invariant-bearing mode")
        return 1

    passed = sum(1 for _, _, ok, _ in results if ok is True)
    failed = sum(1 for _, _, ok, _ in results if ok is False)
    skipped = sum(1 for _, _, ok, _ in results if ok is None)

    print(
        f"Running skill-invariant checks on "
        f"{len(CHECKS)} modes ({', '.join(sorted(CHECKS.keys()))}):"
    )
    print()
    # Group by mode for readability; within a mode, show sample first then captured.
    by_mode: dict[str, list] = {}
    for mode, source, ok, reason in results:
        by_mode.setdefault(mode, []).append((source, ok, reason))
    for mode in sorted(by_mode.keys()):
        for source, ok, reason in by_mode[mode]:
            if ok is None:
                marker = "SKIP"
            elif ok:
                marker = "PASS"
            else:
                marker = "FAIL"
            print(f"  [{marker}] {mode:20s} ({source:8s}): {reason}")
    print()
    skipped_note = f" ({skipped} skipped)" if skipped else ""
    print(
        f"===== Summary: {passed}/{passed + failed} invariant checks passed, "
        f"{failed} failed{skipped_note} ====="
    )

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
