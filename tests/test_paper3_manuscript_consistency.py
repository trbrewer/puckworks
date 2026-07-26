"""Bind Paper 3's inline prose counts to the LIVE registry / manifest, so a stale hand-typed
number fails CI instead of silently drifting.

This is the MC2 fix from the consolidated review action plan
(`docs/paper3_resource/PAPER_3_REVIEW_CONSOLIDATED_ACTION_PLAN.md`): the manuscript itself claims
"a CI lane fails on any drift", but `puckworks.paper3.build verify` only checks that the *generated
artifacts* are fresh -- nothing parsed the manuscript body. These tests do.

Ground truth is computed from the live registry and `MANIFEST.csv` (NOT from the generated JSON),
so the manuscript is pinned to the code: if the registry grows or the manifest changes, the
manuscript number must be updated or CI fails.
"""
import csv
import re
from pathlib import Path

import puckworks.models  # noqa: F401  (registers components)
from puckworks import registry as R

_ROOT = Path(__file__).resolve().parents[1]
_MS = _ROOT / "docs" / "PAPER_3_PUCKWORKS_DRAFT.md"
_MANIFEST = _ROOT / "puckworks" / "data" / "MANIFEST.csv"


def _text():
    return _MS.read_text(encoding="utf-8")


def _n_components():
    return len(R.components())


def _role_counts():
    counts = {}
    for c in R.components():
        counts[c.execution_role] = counts.get(c.execution_role, 0) + 1
    return counts


def _n_manifest_rows():
    with open(_MANIFEST, newline="", encoding="utf-8-sig") as fh:
        return sum(1 for r in csv.DictReader(fh) if any((v or "").strip() for v in r.values()))


def test_component_count_matches_live_registry():
    n = _n_components()
    text = _text()
    # the headline corpus-size claims must equal the live registry count
    claims = re.findall(r"contains (\d+) (?:registered )?components?\b", text)
    claims += re.findall(r"(\d+) registered components\b", text)
    assert claims, "no component-count claim found in the manuscript"
    for c in claims:
        assert int(c) == n, f"manuscript says {c} components; live registry has {n}"


def test_manifest_record_count_matches_manifest_csv():
    n = _n_manifest_rows()
    text = _text()
    # every phrasing of the manifest size must equal the actual logical-row count
    claims = re.findall(r"(\d+) dataset-manifest records", text)
    claims += re.findall(r"data manifest contains (\d+) records", text)
    claims += re.findall(r"(\d+)-row manifest", text)
    assert claims, "no manifest-count claim found in the manuscript"
    for c in claims:
        assert int(c) == n, f"manuscript says {c} manifest records; MANIFEST.csv has {n} rows"
    # and the stale value must not reappear in a manifest context
    assert not re.search(r"\b70[ -](?:dataset-manifest records|records|row manifest)", text), \
        "stale '70' manifest count is back in the manuscript"


def test_table1_role_split_matches_registry_and_has_no_synthesis_role():
    roles = _role_counts()
    text = _text()
    m = re.search(r"(\d+) runtime, (\d+) calibration", text)
    assert m, "Table 1 execution-role split line not found"
    runtime, calibration = int(m.group(1)), int(m.group(2))
    assert runtime == roles.get("runtime", 0), \
        f"manuscript says {runtime} runtime; registry has {roles.get('runtime', 0)}"
    assert calibration == roles.get("calibration", 0), \
        f"manuscript says {calibration} calibration; registry has {roles.get('calibration', 0)}"
    # "synthesis" is a provenance class, never an execution role (schema v2)
    assert "synthesis" not in R.EXECUTION_ROLES
    assert not re.search(r"\d+\s+synthesis\b", text), \
        "manuscript still counts 'synthesis' as an execution role"


def test_table3_relation_names_match_evidence_strength_enum():
    # MC4: Table 3 relations must be the exact registry enum (no drift, no display-label aliases
    # like "Independent external" standing in for `controlled_independent`).
    text = _text()
    for rel in R.EVIDENCE_STRENGTHS:
        assert f"`{rel}`" in text, f"evidence relation {rel!r} is not documented in the manuscript"


def test_manuscript_uses_schema_v2_axes_not_deprecated_kind_as_authoritative():
    text = _text()
    # the three authoritative axes must be named; 'kind' must be described as deprecated
    for axis in ("execution_role", "provenance_class", "evidence_strength"):
        assert axis in text, f"schema-v2 axis {axis!r} not mentioned in the manuscript"
    assert re.search(r"`kind`[^.]*deprecated", text, re.IGNORECASE), \
        "manuscript must mark the legacy `kind` field as deprecated"


# --- section numbering integrity (found while promoting the MC10 benchmark) -------------------
def _headings(text):
    import re
    return re.findall(r"^(#{2,4})\s+(\d+(?:\.\d+)?)\.?\s+(.*)$", text, re.M)


def test_every_subsection_number_matches_its_parent_section():
    """Promoting a section to top level renumbered the parents but left the subsections behind,
    which also exposed a pre-existing duplicate (two different sections both numbered 13.1). A
    reader following '13.2' had no way to know which one was meant."""
    import re
    text = _text()
    cur, bad = None, []
    for line in text.splitlines():
        m2 = re.match(r"^## (\d+)\. ", line)
        m3 = re.match(r"^### (\d+)\.(\d+) ", line)
        if m2:
            cur = m2.group(1)
        elif m3 and cur and m3.group(1) != cur:
            bad.append((cur, line.strip()[:70]))
    assert not bad, "subsection numbered outside its parent section: %s" % bad


def test_top_level_section_numbers_are_contiguous_and_unique():
    import re
    nums = [int(m.group(1)) for m in re.finditer(r"^## (\d+)\. ", _text(), re.M)]
    assert nums == sorted(nums), "sections out of order: %s" % nums
    assert len(set(nums)) == len(nums), "duplicate section number: %s" % nums
    assert nums == list(range(nums[0], nums[0] + len(nums))), "gap in numbering: %s" % nums


def test_no_heading_number_is_used_twice():
    seen = {}
    for _lvl, num, title in _headings(_text()):
        assert num not in seen, "number %s used by both %r and %r" % (num, seen[num], title)
        seen[num] = title


def test_every_internal_section_reference_resolves():
    """A dangling reference is a reader-facing defect; a reference that resolves to the WRONG
    section is worse, which is why the numbering tests above run alongside this one."""
    import re
    text = _text()
    heads = {num for _lvl, num, _t in _headings(text)}
    assert heads, "no numbered headings found -- this guard would be vacuous"
    refs = set(re.findall(r"§(\d+(?:\.\d+)?)", text))
    dangling = sorted(r for r in refs
                      if r not in heads and not any(h.startswith(r + ".") for h in heads))
    assert not dangling, "dangling section references: %s" % dangling


def test_the_defect_injection_section_exists_and_is_top_level():
    """MC10: the benchmark evaluates ALL guardrails, so it must not sit under Demonstration 1."""
    import re
    text = _text()
    m = re.search(r"^## (\d+)\. Evaluating the guardrails by deliberate defect injection",
                  text, re.M)
    assert m, "the defect-injection benchmark section is missing or not top-level"
