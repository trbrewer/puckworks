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


# --- scoped evidence vector (review P0-4 option b + step 0) -----------------------------------
def test_s5_2_dependency_counts_match_the_public_claims():
    """S5.2 quotes how many dependency edges there are and how they split by kind. Bind them, so a
    new claim or a re-identified dependency cannot leave the prose behind."""
    from puckworks.public.claims import PUBLIC_CLAIMS
    deps = [d for c in PUBLIC_CLAIMS for d in c.dependencies]
    kinds = {k: sum(1 for d in deps if d.kind == k) for k in ("component", "producer", "dataset")}
    text = _text()
    assert "%d dependency edges" % len(deps) in text, len(deps)
    assert "registry component (%d)" % kinds["component"] in text, kinds
    assert "producer function (%d)" % kinds["producer"] in text, kinds
    assert "dataset manifest row (%d)" % kinds["dataset"] in text, kinds


def test_s5_2_evidence_profile_numbers_match_the_producer():
    """The composition claim's evidence is quoted as evidence that one label is insufficient.

    Third review P0-1 made the INVENTORY and the SELECTION two different quantities, and the
    manuscript must bind both: the inventory shows the spread a single `evidence_strength` cannot
    express, and the selection shows that the claim does not inherit all of it.
    """
    from puckworks.public.claims import PUBLIC_CLAIMS
    text = _text()

    c = next(x for x in PUBLIC_CLAIMS if x.claim_id == "PV-05")
    inv, sel = c.evidence_inventory(), c.selected_evidence()
    n_rel = len({r["relation"] for r in inv})
    n_scope = len({r["scope"] for r in inv})
    assert "inventory of **%d records" % len(inv) in text, len(inv)
    assert "spanning %d relations across %d observables" % (n_rel, n_scope) in text
    assert "selects **%d**" % len(sel) in text, len(sel)
    assert len(sel) < len(inv), (
        "if a claim selected its whole inventory the selection would be doing no work")

    # the machine-capacity claim, whose excluded records are NEGATIVE-outcome findings
    c2 = next(x for x in PUBLIC_CLAIMS if x.claim_id == "PV-02")
    inv2, sel2 = c2.evidence_inventory(), c2.selected_evidence()
    assert "inventory of %d and selects %d" % (len(inv2), len(sel2)) in text
    excluded = [e for e in inv2 if e not in sel2]
    assert any(e["outcome"] == "negative" for e in excluded), (
        "the paper's example depends on negative-outcome records being excluded")


def test_a_claim_does_not_inherit_its_components_whole_evidence_vector():
    """NON-VACUITY of the selection mechanism itself."""
    from puckworks.public.claims import PUBLIC_CLAIMS
    scoped = [c for c in PUBLIC_CLAIMS if c.evidence_selections]
    assert scoped, "no claim declares evidence selections"
    for c in scoped:
        assert list(c.evidence_profile()) == list(c.selected_evidence())
        assert len(c.selected_evidence()) <= len(c.evidence_inventory())


def test_unrelated_component_evidence_cannot_change_a_claims_badge():
    """The review's acceptance criterion: adding a strong, unrelated record to a component must
    not alter any claim's badge."""
    import dataclasses
    from puckworks.public.claims import PUBLIC_CLAIMS
    from puckworks.public.schema import ScopedEvidenceRef, derive_badge

    c = next(x for x in PUBLIC_CLAIMS if x.claim_id == "PV-03")
    before = derive_badge(c)[0]
    intruder = ScopedEvidenceRef(
        relation="controlled_independent", public_relation="independent",
        scope="an unrelated observable this claim says nothing about",
        gate="gate_unrelated", outcome="supported",
        evidence_id="unrelated::gate_unrelated",
        fit_evaluation="independent_external", reality_facing=True)
    deps = tuple(
        dataclasses.replace(d, evidence=d.evidence + (intruder,)) if d.kind == "component" else d
        for d in c.dependencies)
    louder = dataclasses.replace(c, dependencies=deps)
    assert derive_badge(louder)[0] == before, (
        "an unselected strong record changed the badge -- evidence is being inherited, not selected")


def test_selecting_evidence_from_another_dependency_is_rejected():
    import dataclasses
    from puckworks.public.claims import PUBLIC_CLAIMS
    from puckworks.public.schema import ClaimEvidenceSelection

    c = next(x for x in PUBLIC_CLAIMS if x.claim_id == "PV-03")
    bogus = ClaimEvidenceSelection(
        dependency_ref=c.dependencies[0].ref if c.dependencies[0].kind == "component"
        else "pannusch2024.solver",
        evidence_ids=("some.other.component::gate_elsewhere",),
        claim_observable="x", claim_domain="y", role_in_claim="produces_reported_value",
        rationale="z")
    broken = dataclasses.replace(c, evidence_selections=(bogus,))
    errs = broken.validate()
    assert any("does not belong to dependency" in e or "does not declare" in e for e in errs), errs


def test_a_badge_authored_stronger_than_the_evidence_is_rejected():
    """P0-2 acceptance: supplying or editing a badge by hand must fail verification."""
    import dataclasses
    from puckworks.public.claims import PUBLIC_CLAIMS

    c = next(x for x in PUBLIC_CLAIMS if x.claim_id == "PV-03")
    assert c.validate() == []
    inflated = dataclasses.replace(c, badge="PREDICTED")
    errs = inflated.validate()
    assert any("was authored but the selected evidence derives" in e for e in errs), errs


def test_every_public_claim_badge_is_the_derived_one():
    from puckworks.public.claims import PUBLIC_CLAIMS
    for c in PUBLIC_CLAIMS:
        derived, why, _limiting = c.derived_badge()
        assert c.badge == derived, f"{c.claim_id}: authored {c.badge}, derived {derived} ({why})"

def test_s5_2_states_the_profile_is_not_a_transitive_closure():
    """The bound the abstract had to be softened for; it must stay stated."""
    text = _text().lower()
    assert "profile, not a transitive closure" in text


def test_every_producer_named_in_the_claim_ownership_table_exists():
    """P1-14. A claim-ownership table whose producer column is filled in optimistically is the
    same defect this paper is about; four entries were invented on the first pass and caught here.
    Rows that legitimately have no producer must say so in words, not name a plausible one."""
    import importlib
    import re

    text = _text()
    block = text[text.index("| Claim ID |"):]
    block = block[:block.index("\n\n")]
    refs, missing = [], []
    for line in block.splitlines()[2:]:
        cells = [c.strip() for c in line.split("|")]
        if len(cells) < 6:
            continue
        producer = cells[4]
        if producer in ("—", "") or "none" in producer.lower() or producer.startswith("**none"):
            continue
        m = re.search(r"`([A-Za-z0-9_.]+)`", producer)
        if not m:
            continue
        refs.append(m.group(1))
    assert refs, "no producer references parsed -- this guard would be vacuous"
    from puckworks.paper3 import evidence_graph as _EG
    gates = {l["gate"] for l in _EG.load_links()}
    for ref in refs:
        if ref in gates:                       # a wired gate is a legitimate canonical producer
            continue
        if ref.endswith(".py") or "/" in ref:
            assert (_ROOT / ref).exists(), ref
            continue
        # resolve the FULL reference only: module = everything before the last dot, attribute =
        # the last segment. An earlier version tried every prefix split, so naming a real module
        # with an invented function passed -- exactly the failure this guard exists to catch.
        mod, _, attr = ref.rpartition(".")
        if not mod:
            missing.append(ref)
            continue
        found = False
        for base in ("puckworks.", "puckworks.validation.slow.", "puckworks.models.brewer2026.",
                     "puckworks.models.", ""):
            try:
                if hasattr(importlib.import_module(base + mod), attr):
                    found = True
                    break
            except Exception:  # noqa: BLE001
                continue
        if not found:
            missing.append(ref)
    assert not missing, f"producers named in the ownership table do not exist: {missing}"


def test_the_scorecard_row_names_its_live_producer():
    """Third review P0-4. This test previously required the string "hand-maintained" to be
    present, which was correct when Table 6 really was hand-maintained. The generator landed, the
    implementation-status table and Figure 7 were updated to say so -- and this test kept the
    ownership table asserting the opposite, so the manuscript preserved a historical defect as
    though it were current while simultaneously claiming it had been fixed.

    The ownership row must now name the live producer, and the correction must be recorded rather
    than made silently."""
    text = _text()
    assert "`paper3.named_shot_scorecard.scorecard`" in text, (
        "the P3-SCORECARD ownership row must name its producer")
    # Checked on the TABLE ROW, not the document: the historical note deliberately quotes the
    # retired string, and a document-wide ban would forbid the paper from recording its own
    # correction.
    row = next(ln for ln in text.splitlines() if ln.startswith("| `P3-SCORECARD`"))
    assert "hand-maintained" not in row, f"the stale ownership row is back: {row}"
    assert "none" not in row.lower(), f"the ownership row still claims no producer: {row}"
    # the correction is disclosed, not quietly applied
    assert "It is no longer true." in text
    # and the declared-configuration / generated-claims distinction is drawn
    assert "declared configuration" in text and "generated claims" in text


# ── contract schema version and field coverage (third review P0-5) ────────────────────────────
def test_the_manuscript_states_the_live_contract_schema_version():
    """§4.1 said 0.6, Table 7 said 0.7, and `contracts.py` was 0.7. The version is not cosmetic:
    0.7 added the fines-provenance fields that prevent comparison of fines fractions defined at
    different thresholds, by different dispersion methods, or on different bases."""
    from puckworks import contracts
    text = _text()
    live = contracts.SCHEMA_VERSION
    assert f"The current contract schema is version {live}." in text, (
        f"the manuscript does not state the live schema version {live}")
    for stale in ("contract schema is version 0.6",):
        assert stale not in text, f"stale schema version: {stale}"


def test_table_2a_lists_the_fines_provenance_fields_that_motivated_the_bump():
    """The manuscript understated one of its best examples of a semantic contract improvement:
    Table 2a listed only setting, fines fraction and radii."""
    from puckworks import contracts
    import dataclasses
    text = _text()
    fields = {f.name for f in dataclasses.fields(contracts.GrindState)}
    for required in ("fines_threshold_um", "fines_dispersion_method", "fines_basis"):
        assert required in fields, f"{required} is not a GrindState field any more"
    row = next(ln for ln in text.splitlines() if ln.startswith("| `GrindState`"))
    for human in ("fines threshold", "fines dispersion method", "fines basis"):
        assert human in row, f"Table 2a omits {human}"
    # and they must be described as declarations, not conversions
    assert "declarations, not conversion formulas" in row


# ── observational basis of the temporal/composition RMSEs (third review P0-6) ─────────────────
def test_mean_trace_metrics_are_labelled_as_mean_trace():
    """0.573 / 0.648 / 0.116 / 0.096 are scores against the preprocessed mean of five 9-bar shots
    over 15-95 s, not errors on any individual shot. Averaging removes variability the models were
    never required to predict, so a reader must not be able to read them as shot-prediction error.
    """
    text = _text()
    assert "preprocessed mean of five 9-bar shots over 15–95 s" in text
    assert "not errors on any individual shot" in text
    # the abstract, where an editor reads them first
    abstract = text.split("\n")[10]
    assert "not shot-level prediction errors" in abstract


def test_the_per_shot_results_are_reported_with_the_shot_as_the_unit():
    text = _text()
    assert "five individual 9-bar shots, mean ± SD" in text
    for v in ("0.580 ± 0.054", "0.661 ± 0.100", "0.189 ± 0.061", "0.107 ± 0.016"):
        assert v in text, f"per-shot value {v} missing"
    assert "shot is the unit of replication" in text
    assert "do not divide the number of time samples into an apparent sample size" in text


def test_the_near_flexible_floor_claim_is_withdrawn():
    """The 0.083 g/s per-shot temporal-versus-cubic gap is not resolved at n=5."""
    text = _text()
    assert "not supported at shot level and has been withdrawn" in text
    assert "nearly reaches" not in text.replace(
        'the earlier reading that the temporal branch "nearly reaches" the flexible floor', "")


def test_the_blocked_holdout_reason_is_stated():
    """P0-6 item 8: a fully held-out temporal prediction is blocked by a DATA limitation."""
    text = _text()
    assert "never shot-matched to the five flow traces" in text


def test_the_manifest_count_is_not_described_as_validation_datasets():
    """`supported by 107 dataset-manifest records` reads as 107 validation datasets."""
    text = _text()
    assert "supported by 107 dataset-manifest records" not in text
    assert "described by 107 provenance-manifest records" in text
