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


def test_manuscript_uses_schema_v2_axes_not_deprecated_kind_as_authoritative():
    text = _text()
    # the three authoritative axes must be named; 'kind' must be described as deprecated
    for axis in ("execution_role", "provenance_class", "evidence_strength"):
        assert axis in text, f"schema-v2 axis {axis!r} not mentioned in the manuscript"
    assert re.search(r"`kind`[^.]*deprecated", text, re.IGNORECASE), \
        "manuscript must mark the legacy `kind` field as deprecated"
