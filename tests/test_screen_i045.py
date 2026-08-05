"""Focused tests for the I-045 cheap screen (Insight Foundry Wave 2).

These establish LINEAGE properties, not the verdict. The central ones:

  * `independent` and `verification` are NOT ordinal here, and the screen must contain no
    ordering between them — a ranking would silently recreate the I-040 vocabulary in a place
    where it does not apply;
  * the two halves are different COLUMNS, so attribution is observable — the traced column set
    must actually match the hand-written attribution rather than merely agreeing in prose;
  * the controlling card is `foster2025_2`, and the `foster2025` TEMPLATE_DEVIATION must not be
    inherited;
  * the adversarial scan must not bleed across manifest rows, and must not classify a hit using
    a fragment that does not contain that hit's token. Both were real defects during the screen.
"""
import csv
import json
import pathlib
import re

import pytest

from puckworks.analysis import screen_i045_evidence_halves as S

REPO = pathlib.Path(__file__).resolve().parents[1]
BUNDLE = REPO / "docs/insights/screens/I-045"


@pytest.fixture(scope="module")
def result():
    return S.screen()


# --------------------------------------------------------------------------------------------
# Source authority
# --------------------------------------------------------------------------------------------
def test_manifest_wording_is_byte_identical():
    with open(REPO / "puckworks/data/MANIFEST.csv", newline="", encoding="utf-8") as fh:
        rows = {r["dataset_id"]: r for r in csv.DictReader(fh)}
    row = rows[S.DATASET_ID]
    assert row["validation_strength"] == S.MANIFEST_VALIDATION_STRENGTH
    assert row["caveat"] == S.MANIFEST_CAVEAT


def test_controlling_card_is_foster2025_2_and_resolves():
    card = REPO / S.SOURCE_CARD
    assert card.exists(), "the controlling card must resolve"
    assert S.SOURCE_CARD.endswith("foster2025_2.md")
    # the manifest row must actually name this card
    with open(REPO / "puckworks/data/MANIFEST.csv", newline="", encoding="utf-8") as fh:
        rows = {r["dataset_id"]: r for r in csv.DictReader(fh)}
    assert rows[S.DATASET_ID]["source_card"] == "foster2025_2"


def test_the_other_foster_card_is_not_used():
    """foster2025.md carries its own TEMPLATE_DEVIATION and must not be INHERITED.

    The module may name it — it does, to say it is not used — but it must not be the controlling
    card, and no scanned surface may be that file.
    """
    assert S.SOURCE_CARD == "docs/cards/foster2025_2.md"
    assert all(rel != "docs/cards/foster2025.md" for _, rel, _ in S.SCAN_SURFACES)
    r = S.screen(run_trace=False)
    assert r["controlling_source_card"] == "docs/cards/foster2025_2.md"
    assert "does not use or inherit" in r["source_card_note"]


def test_controlling_card_carries_the_circularity_note():
    """This sentence is what settles which SENSE of 'independent' the CT half can carry."""
    text = (REPO / S.SOURCE_CARD).read_text(encoding="utf-8")
    norm = " ".join(text.split())
    assert " ".join(S.CARD_CIRCULARITY_NOTE.split()) in norm


# --------------------------------------------------------------------------------------------
# THE NON-ORDINAL REQUIREMENT
# --------------------------------------------------------------------------------------------
def test_independent_and_verification_are_not_ranked():
    """No ordering may exist between the two evidentiary functions anywhere in the screen."""
    src = pathlib.Path(S.__file__).read_text(encoding="utf-8")
    # ordering CONSTRUCTS, not the mere word: an ordered list or a comparison would rank them
    for banned in ("STRENGTH_ORDER", "stronger than", "weaker than", "_rung(", "rung_index"):
        assert banned not in src, "an ordering crept in: %r" % banned
    assert "not ordinal" in src.lower()
    # the classifications must be a SET in the result, never a ranked sequence
    r = S.screen(run_trace=False)
    assert isinstance(r["consumers_by_classification"], dict)
    assert "evidence_types_are_not_ordinal" in r
    # the four classifications are a set, not a sequence with an implied rank
    assert {S.CLS_INDEPENDENT, S.CLS_VERIFICATION, S.CLS_BOTH, S.CLS_NEITHER} == {
        "INDEPENDENT_LOAD_BEARING", "VERIFICATION_LOAD_BEARING",
        "BOTH_LOAD_BEARING", "NEITHER_LOAD_BEARING"}


def test_both_is_an_allowed_and_present_outcome():
    """'uses both' must be a first-class correct outcome, not a defect class."""
    both = [c for c in S.CONSUMERS if c["classification"] == S.CLS_BOTH]
    assert both, "the legitimate both-halves case must be representable and represented"
    for c in both:
        assert c["both_legitimately_required"] is True
        assert c["independence_load_bearing"] and c["verification_reproduction_load_bearing"]


# --------------------------------------------------------------------------------------------
# The halves are columns — so attribution is observable
# --------------------------------------------------------------------------------------------
def test_halves_partition_the_real_columns():
    from puckworks import data as d
    cols = set(d.foster_fig12_14_curves()[0].keys())
    declared = set()
    for h in S.HALVES.values():
        declared |= set(h["columns"])
    assert declared == cols, "the declared halves must cover exactly the real columns"
    # and no column may belong to two halves
    seen = []
    for h in S.HALVES.values():
        seen += h["columns"]
    assert len(seen) == len(set(seen)), "a column appears in two halves"


def test_traced_columns_match_the_hand_attribution(result):
    """The observed read-set must agree with what the attribution table claims."""
    tr = result["enumeration"]["traced"]["gate_foster_ct_trajectory"]
    cols = set(tr["columns_read"])
    ver = set(S.HALVES["verification_fitted_curves"]["columns"])
    ind = set(S.HALVES["independent_ct_data"]["columns"])
    assert cols & ver, "the gate must read the fitted-curve columns"
    assert cols & ind, "the gate must read the CT columns"
    rec = [c for c in S.CONSUMERS if c["consumer"] == "gate_foster_ct_trajectory"][0]
    assert rec["classification"] == S.CLS_BOTH
    assert set(tr["halves_touched"]) >= {"verification_fitted_curves", "independent_ct_data"}


def test_column_tracing_is_transparent_to_the_consumer():
    """The tracing wrapper must not change what a consumer sees."""
    from puckworks import data as d
    real = d.foster_fig12_14_curves()
    seen = set()
    traced = [S._TracingRow(r, seen) for r in real]
    assert len(traced) == len(real)
    assert traced[0]["t_s"] == real[0]["t_s"]
    assert "t_s" in seen
    assert dict(traced[5]) == dict(real[5])


def test_enumeration_is_complete(result):
    e = result["enumeration"]
    assert e["uncovered_call_site_functions"] == []
    assert e["uncovered_traced_consumers"] == []
    assert e["complete"] is True
    assert e["n_static_call_sites"] >= 2


# --------------------------------------------------------------------------------------------
# Adversarial scan — the two defects it had, and the surface prose cannot cover
# --------------------------------------------------------------------------------------------
def test_scan_classifies_every_hit(result):
    scan = result["adversarial_text_scan"]
    assert scan["n_hits"] > 0
    assert scan["n_unclassified"] == 0
    assert set(scan["tokens"]) == set(S.SCAN_TOKENS)


def test_manifest_scan_is_clipped_to_the_target_row():
    """Defect 1: a character window bled into neighbouring dataset rows."""
    text = S._surface_text("puckworks/data/MANIFEST.csv", S.DATASET_ID)
    assert text.startswith(S.DATASET_ID + ",")
    assert "\n" not in text.strip("\n"), "more than one manifest row was captured"
    for foreign in ("de1_fixtureA", "mo2023", "fig15_flow_pressure"):
        assert foreign not in text, "the scan window bled into %s" % foreign


def test_hit_classification_requires_the_fragment_to_contain_the_token():
    """Defect 2: first-fragment-wins mislabelled the docstring's 'independent' hit.

    Every rule must be self-consistent (its fragment contains its token), and the docstring's
    'independent' hit must not be reclassified as correct usage by the adjacent reproduction
    phrase.
    """
    for rule in S.HIT_RULES:
        assert rule["token"] in rule["fragment"].lower(), rule
    ctx = ("curves to line width (<0.2 mm RMSE, verifying the port) and bracket a majority of "
           "the CT data points within their error bars (independent, 'qualitative-good').")
    got = S._classify_hit("independent", ctx)
    assert got["classification"] == "AMBIGUOUS_MEASUREMENT_SENSE", (
        "the wording risk must not be reclassified as correct usage by a neighbouring fragment")


def test_unscanned_reproduction_phrase_is_recorded_as_a_coverage_note():
    """The docstring says 'verifying', which is outside the five specified tokens.

    That is a coverage limit of the prose scan, not a gap in the audit: the phrase is read by
    hand attribution. It must be declared so nobody concludes it went unexamined.
    """
    notes = S.SCAN_COVERAGE_NOTES
    assert notes, "the unscanned reproduction phrase must be declared"
    n = notes[0]
    assert n["token_scanned"] is False
    assert "verifying" in n["phrase"]
    assert not any(re.search(r"\b%s\b" % t, n["phrase"]) for t in S.SCAN_TOKENS)


def test_structural_independence_fields_cover_a_prose_silent_surface(result):
    """EVIDENCE_LINKS states independence in a FIELD, not in prose — read the field."""
    st = result["structural_independence_fields"]
    assert st["n_prose_token_hits_on_this_surface"] == 0
    vals = {r.get("independence") for r in st["records"] if "independence" in r}
    assert vals == {"same_campaign", "fit_input"}, vals
    assert st["asserts_independence"] is False
    fields = {r.get("field"): r.get("value") for r in st["records"] if "field" in r}
    assert fields["reality_facing"] is False
    assert fields["support_status"] == "context_only"
    assert fields["relationship"] == "same_campaign_not_held_out"


# --------------------------------------------------------------------------------------------
# Decision, derived rather than asserted
# --------------------------------------------------------------------------------------------
def test_decision_follows_from_its_own_inputs(result):
    mis = result["misattribution_analysis"]
    st = result["structural_independence_fields"]
    complete = result["enumeration"]["complete"]
    if not complete:
        expected = "NEEDS_NEW_DATA"
    elif mis["arm_a_findings"] or mis["propagates"] or st["asserts_independence"]:
        expected = "SURVIVE"
    else:
        expected = "RETIRE"
    assert result["decision"] == expected


def test_no_consumer_claims_independence_without_reading_a_ct_column(result):
    """The SURVIVE arm (a), stated as a property rather than as an outcome."""
    traced = result["enumeration"]["traced"]
    ind_cols = set(S.HALVES["independent_ct_data"]["columns"])
    for c in S.CONSUMERS:
        if not c["independence_load_bearing"]:
            continue
        tr = traced.get(c["consumer"])
        if tr is None or not tr["columns_read"]:
            continue
        assert set(tr["columns_read"]) & ind_cols, c["consumer"]


def test_wording_risk_is_recorded_and_its_containment_is_evidenced(result):
    mis = result["misattribution_analysis"]
    assert mis["wording_risk_located_at"]
    assert mis["downstream_consumers_asserting_independence"] == []
    assert mis["propagates"] is False
    flagged = [c for c in S.CONSUMERS if c["misleading_wording"]]
    assert flagged, "the docstring wording risk must be recorded on its consumer row"


# --------------------------------------------------------------------------------------------
# Committed bundle
# --------------------------------------------------------------------------------------------
def test_bundle_is_present_and_carries_the_disposition():
    for rel in ("README.md", "result.json", "decision.md", "figures/primary.png"):
        assert (BUNDLE / rel).exists(), rel
    for rel in ("README.md", "decision.md"):
        text = (BUNDLE / rel).read_text(encoding="utf-8")
        for token in ("CHEAP_SCIENTIFIC_SCREEN", "NOT_A_PUBLICATION_RESULT",
                      "NOT_A_MODEL_VALIDATION_UPGRADE"):
            assert token in text, (rel, token)


def test_committed_result_does_not_drift_from_a_fresh_run(result):
    committed = json.loads((BUNDLE / "result.json").read_text(encoding="utf-8"))
    assert committed["decision"] == result["decision"]
    assert committed["enumeration"]["complete"] == result["enumeration"]["complete"]
    assert (committed["adversarial_text_scan"]["n_unclassified"]
            == result["adversarial_text_scan"]["n_unclassified"])
    assert committed["manifest_validation_strength_verbatim"] == S.MANIFEST_VALIDATION_STRENGTH
    assert (committed["enumeration"]["traced"]["gate_foster_ct_trajectory"]["columns_read"]
            == result["enumeration"]["traced"]["gate_foster_ct_trajectory"]["columns_read"])


def test_decision_records_a_claim_ceiling_and_a_reopen_condition():
    text = (BUNDLE / "decision.md").read_text(encoding="utf-8")
    for section in ("## Claim ceiling", "## Adversarial check",
                    "## Strongest alternative explanation", "## Primary figure"):
        assert section in text, section
    committed = json.loads((BUNDLE / "result.json").read_text(encoding="utf-8"))
    if committed["decision"] == "RETIRE":
        assert "## Reopen condition" in text


def test_retirement_record_matches_the_committed_decision():
    committed = json.loads((BUNDLE / "result.json").read_text(encoding="utf-8"))
    text = (REPO / "docs/insights/RETIRED_CANDIDATES.md").read_text(encoding="utf-8")
    if committed["decision"] == "RETIRE":
        assert "**I-045**" in text and "screens/I-045/" in text
    else:
        assert "**I-045**" not in text


def test_no_unauthorised_candidate_bundle_was_created():
    """Only I-040, I-010, I-024 (merged) and I-045, I-076 (this PR) may have bundles."""
    allowed = {"I-040", "I-010", "I-024", "I-045", "I-076", "README.md"}
    present = {p.name for p in (REPO / "docs/insights/screens").iterdir()}
    assert present <= allowed, present - allowed
