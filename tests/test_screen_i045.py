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
    if S.live_source_is_corrected():
        pytest.skip("live source is corrected; this asserts a property of the PRE-CORRECTION\n                    repository. The historical finding is protected by the pinned snapshot hashes.")
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
# THE GOVERNING GLOSSARY — the correction this screen turns on
# --------------------------------------------------------------------------------------------
def test_classification_is_bound_to_the_repository_glossary():
    """The screen VERIFIES its definitions verbatim against ROADMAP S0 at run time.

    It does not parse them out of the document, and it does not restate them from memory: it
    carries the text it expects and fails if the authority no longer says it.
    """
    g = S.glossary()
    assert g["anchor_found"] is True
    assert "not used in fitting" in g["definitions"]["independent"]
    assert g["independent_requires_held_out"] is True
    b = g["binding"]
    assert b["source"] == "docs/ROADMAP.md S0"
    assert b["method"] == "VERBATIM_RUNTIME_VERIFICATION"
    assert b["all_expected_definitions_verified"] is True
    assert set(b["terms_verified"]) == {"independent", "post-fit reconstruction", "verification"}
    # every expected definition really is present verbatim in the live ROADMAP
    roadmap = " ".join((REPO / "docs/ROADMAP.md").read_text(encoding="utf-8").split())
    assert S.GLOSSARY_ANCHOR in roadmap
    for term, expected in S.EXPECTED_GLOSSARY_DEFINITIONS.items():
        assert expected in roadmap, term


@pytest.mark.parametrize("term", ["independent", "post-fit reconstruction", "verification"])
def test_a_reworded_glossary_is_rejected_rather_than_silently_overridden(term):
    """Supply altered authority text to the bounded verifier; it must refuse to proceed.

    The live block is reflowed across lines, so the alteration is applied to the normalised
    block the verifier actually compares against.
    """
    roadmap = (REPO / "docs/ROADMAP.md").read_text(encoding="utf-8")
    live = S.verify_glossary(roadmap)               # unaltered authority verifies
    assert live.startswith(S.GLOSSARY_ANCHOR)

    expected = S.EXPECTED_GLOSSARY_DEFINITIONS[term]
    assert expected in live, "the expected definition must occur in the authority to begin with"
    altered = live.replace(expected, "SOMETHING THE SCREEN DOES NOT EXPECT", 1)
    assert altered != live
    with pytest.raises(S.GlossaryDrift) as exc:
        S.verify_glossary(altered)
    assert term in str(exc.value)
    assert expected in str(exc.value), "the error must name the definition it expected"


def test_a_missing_glossary_anchor_is_rejected():
    with pytest.raises(S.GlossaryDrift):
        S.verify_glossary("a ROADMAP with no validation-strength section at all")


def test_ct_observations_belong_to_the_fitting_campaign():
    """Proved from the controlling card, which is what makes the CT arm post-fit."""
    card = (REPO / S.SOURCE_CARD).read_text(encoding="utf-8")
    norm = " ".join(card.split())
    assert " ".join(S.CARD_CIRCULARITY_NOTE.split()) in norm
    # the specific quantities and the specific curves
    assert "fitted" in norm and "s/H curves being reproduced" in norm
    assert "k" in S.CARD_CIRCULARITY_NOTE and "phi_T" in S.CARD_CIRCULARITY_NOTE.replace(
        "\u03c6_T", "phi_T")


def test_the_measurement_modality_reinterpretation_is_rejected():
    """The earlier local reading must be recorded as rejected, not quietly dropped."""
    rr = S.REJECTED_REINTERPRETATION
    assert "MEASUREMENT MODALITY" in rr["reading"]
    assert "not the repository's definition" in rr["why_rejected"]
    assert "foster2025_2" in rr["settled_by"]
    r = S.screen(run_trace=False)
    assert r["rejected_reinterpretation"] == rr


def test_ct_arm_is_post_fit_same_campaign_not_independent():
    h = S.HALVES["post_fit_ct_same_campaign"]
    assert h["evidence_type_under_glossary"].startswith("post-fit")
    assert h["held_out"] is False
    assert h["same_campaign"] is True
    assert h["manifest_wording"] == "independent (CT data)"
    assert h["manifest_wording_correct"] is False, (
        "the manifest calls this arm independent; under the glossary it is not")


def test_fitted_curve_arm_is_verification():
    h = S.HALVES["verification_fitted_curves"]
    assert h["evidence_type_under_glossary"] == "verification"
    assert h["manifest_wording_correct"] is True


def test_no_arm_of_this_dataset_is_independent_evidence():
    types = {h["evidence_type_under_glossary"] for h in S.HALVES.values()}
    assert "independent" not in types
    r = S.screen(run_trace=False)
    assert "Neither arm is independent" in r["no_independent_evidence_in_this_dataset"]
    # and no consumer may be classified as independent-load-bearing
    assert not [c for c in S.CONSUMERS if c["classification"] == S.CLS_INDEPENDENT]


def test_the_gate_is_classified_verification_and_post_fit():
    gate = [c for c in S.CONSUMERS if c["consumer"] == "gate_foster_ct_trajectory"][0]
    assert gate["classification"] == S.CLS_BOTH == "VERIFICATION_AND_POST_FIT_SAME_CAMPAIGN"
    assert gate["verification_reproduction_load_bearing"] is True
    assert gate["post_fit_same_campaign_load_bearing"] is True
    assert gate["both_arms_required"] is True
    assert "INDEPENDENT" not in gate["classification"]


def test_survive_is_derived_from_the_incorrect_independent_attribution(result):
    """The verdict must follow from a consumer claiming a rung the glossary denies it."""
    mis = result["misattribution_analysis"]
    assert mis["n_findings"] >= 1
    f = mis["findings"][0]
    assert f["consumer"] == "gate_foster_ct_trajectory"
    assert f["claimed"] == "independent"
    assert f["actual_under_glossary"].startswith("post-fit")
    assert f["affects_numerical_result"] is False
    assert result["decision"] == "SURVIVE"


def test_future_correction_targets_are_named_and_not_edited(result):
    targets = result["future_correction_targets"]
    assert len(targets) >= 2
    joined = " ".join(t["target"] for t in targets)
    assert "MANIFEST.csv" in joined
    assert "gate_foster_ct_trajectory" in joined
    for t in targets:
        assert t["edited_in_this_pr"] is False
    assert result["already_bounded_surface"]["edited_in_this_pr"] is False


def test_the_named_source_surfaces_are_untouched_in_this_pr():
    """A screen may identify an attribution defect; it may not repair these files."""
    if S.live_source_is_corrected():
        pytest.skip("live source is corrected; this asserted the PRE-CORRECTION state "
                    "of surfaces the correction was authorised to change. The historical\n"
                    "finding is protected by the pinned snapshot hashes; the CURRENT "
                    "state is asserted by tests/test_correction_i045.py.")
    import subprocess

    def git(*args):
        return subprocess.run(("git",) + args, cwd=REPO, capture_output=True, text=True)

    base = "14c3753c6e8dab2995332dbe1c3d1e04c4348051"
    if git("cat-file", "-e", base + "^{commit}").returncode != 0:
        # a shallow checkout cannot answer this; skip loudly rather than pass on empty stdout
        pytest.skip("branch base %s not present in this checkout" % base[:7])
    for path in ("puckworks/data/MANIFEST.csv", "puckworks/validation/gates.py",
                 "puckworks/paper3/EVIDENCE_LINKS.json", "docs/paper3_resource/generated"):
        r = git("diff", "--numstat", base, "HEAD", "--", path)
        assert r.returncode == 0, r.stderr
        assert r.stdout.strip() == "", "%s was modified: %s" % (path, r.stdout.strip())


def test_evidence_links_already_refuses_held_out_and_reality_facing(result):
    """The one surface that must NOT be a correction target, because it is already right."""
    st = result["structural_independence_fields"]
    vals = {r.get("independence") for r in st["records"] if "independence" in r}
    assert vals == {"same_campaign", "fit_input"}
    fields = {r.get("field"): r.get("value") for r in st["records"] if "field" in r}
    assert fields["relationship"] == "same_campaign_not_held_out"
    assert fields["reality_facing"] is False
    assert fields["support_status"] == "context_only"
    assert st["asserts_independence"] is False


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
    ind = set(S.HALVES["post_fit_ct_same_campaign"]["columns"])
    assert cols & ver, "the gate must read the fitted-curve columns"
    assert cols & ind, "the gate must read the CT columns"
    rec = [c for c in S.CONSUMERS if c["consumer"] == "gate_foster_ct_trajectory"][0]
    assert rec["classification"] == S.CLS_BOTH
    assert set(tr["halves_touched"]) >= {"verification_fitted_curves",
                                        "post_fit_ct_same_campaign"}


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
    if S.live_source_is_corrected():
        pytest.skip("live source is corrected; this asserts a property of the PRE-CORRECTION\n                    repository. The historical finding is protected by the pinned snapshot hashes.")
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
    assert got["classification"] == "INCORRECT_INDEPENDENT_ATTRIBUTION", (
        "the finding must not be reclassified as correct usage by a neighbouring fragment")


def test_the_gate_hit_is_an_incorrect_attribution_not_an_ambiguous_sense(result):
    """The governing S0 meaning is EXCLUSIVE — there is no second valid current reading."""
    if S.live_source_is_corrected():
        pytest.skip("live source is corrected; this asserts a property of the PRE-CORRECTION\n                    repository. The historical finding is protected by the pinned snapshot hashes.")
    hits = result["adversarial_text_scan"]["hits"]
    gate = [h for h in hits if h["token"] == "independent" and "docstring" in h["surface"]]
    assert len(gate) == 1, gate
    c = gate[0]["context_classification"]
    assert c["classification"] == "INCORRECT_INDEPENDENT_ATTRIBUTION"
    assert "not independent" in c["note"]
    assert "REJECTED" in c["note"], "the modality reading must be named as rejected, not valid"


def test_the_manifest_independent_hit_is_the_target_incorrect_label(result):
    if S.live_source_is_corrected():
        pytest.skip("live source is corrected; this asserts a property of the PRE-CORRECTION\n                    repository. The historical finding is protected by the pinned snapshot hashes.")
    hits = result["adversarial_text_scan"]["hits"]
    man = [h for h in hits if h["token"] == "independent" and "MANIFEST" in h["surface"]]
    assert len(man) == 1, man
    c = man[0]["context_classification"]
    assert c["classification"] == "TARGET_CELL_WITH_INCORRECT_INDEPENDENT_LABEL"
    for flag in ("POST_FIT_SAME_CAMPAIGN", "NOT_HELD_OUT", "NOT_INDEPENDENT"):
        assert flag in c["note"], flag


def test_the_manifest_verification_hit_remains_correct(result):
    if S.live_source_is_corrected():
        pytest.skip("live source is corrected; this asserts a property of the PRE-CORRECTION\n                    repository. The historical finding is protected by the pinned snapshot hashes.")
    hits = result["adversarial_text_scan"]["hits"]
    ver = [h for h in hits if h["token"] == "verification" and "MANIFEST" in h["surface"]]
    assert len(ver) == 1, ver
    c = ver[0]["context_classification"]
    assert c["classification"] == "TARGET_CELL_CORRECT_VERIFICATION_HALF"
    assert "not a correction target" in c["note"]


def test_no_production_rule_or_result_carries_the_ambiguous_sense_classification(result):
    """The rejected reading may be recorded as history — never as a live classification."""
    blob = json.dumps(result, ensure_ascii=False)
    assert "AMBIGUOUS_MEASUREMENT_SENSE" not in blob
    src = pathlib.Path(S.__file__).read_text(encoding="utf-8")
    assert "AMBIGUOUS_MEASUREMENT_SENSE" not in src
    for rule in S.HIT_RULES:
        assert rule["classification"] != "AMBIGUOUS_MEASUREMENT_SENSE"


def test_no_live_surface_calls_the_modality_reading_true(result):
    """It survives ONLY inside rejected_reinterpretation, and only as an error."""
    rr = result["rejected_reinterpretation"]
    assert "MEASUREMENT MODALITY" in rr["reading"]
    assert rr["why_rejected"]
    live = dict(result)
    live.pop("rejected_reinterpretation")
    blob = json.dumps(live, ensure_ascii=False).lower()
    for phrase in ("true in the measurement", "valid in the measurement",
                   "correct in the measurement", "ambiguous"):
        assert phrase not in blob, phrase


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
    elif mis["findings"] or st["asserts_independence"]:
        expected = "SURVIVE"
    else:
        expected = "RETIRE"
    assert result["decision"] == expected


def test_containment_is_evidenced_but_does_not_excuse_the_attribution(result):
    mis = result["misattribution_analysis"]
    assert mis["downstream_consumers_claiming_independence"] == []
    assert mis["propagates_downstream"] is False
    assert "does not make the attribution correct" in mis["containment"]
    assert mis["no_independent_evidence_exists_in_this_dataset"] is True


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
    if S.live_source_is_corrected():
        pytest.skip("live source is corrected; this asserts a property of the PRE-CORRECTION\n                    repository. The historical finding is protected by the pinned snapshot hashes.")
    if S.live_source_is_corrected():
        pytest.skip("live source is corrected; the bundle is a pinned historical "
                    "snapshot and is protected by hash instead")
    """The committed bytes must be EXACTLY what the producer emits today.

    Selected-field equality is not enough. The producer records static call-site LINE NUMBERS,
    so any edit to a scanned file silently invalidates the committed record while every
    scientific assertion still passes — which is precisely how two stale line numbers reached a
    reviewed head. Compare the whole canonical serialisation instead.

    `line` fields are deliberately NOT normalised, masked or excluded: they are the volatile
    fields, so ignoring them would defeat the test.
    """
    committed = (BUNDLE / "result.json").read_text(encoding="utf-8")
    # the producer's own serialisation contract — screen_i045_evidence_halves.main()
    expected = json.dumps(result, indent=2) + "\n"
    if committed != expected:
        c, e = json.loads(committed), result
        diffs = [k for k in sorted(set(c) | set(e)) if c.get(k) != e.get(k)]
        raise AssertionError(
            "docs/insights/screens/I-045/result.json is stale: it does not reproduce from a "
            "fresh run of its producer.\n"
            "  top-level keys that differ: %s\n"
            "  fix: python -m puckworks.analysis.screen_i045_evidence_halves\n"
            "  (regenerate AFTER every source/test/doc edit is final — the producer records "
            "call-site line numbers)" % (diffs or "none (formatting only)"))


def test_committed_result_matches_on_the_decision_bearing_fields(result):
    """Diagnostics kept alongside the canonical check, so a failure says WHAT moved."""
    if S.live_source_is_corrected():
        pytest.skip("live source is corrected; this asserts a property of the PRE-CORRECTION\n                    repository. The historical finding is protected by the pinned snapshot hashes.")
    committed = json.loads((BUNDLE / "result.json").read_text(encoding="utf-8"))
    assert committed["decision"] == result["decision"]
    assert committed["enumeration"]["complete"] == result["enumeration"]["complete"]
    assert (committed["adversarial_text_scan"]["n_unclassified"]
            == result["adversarial_text_scan"]["n_unclassified"])
    assert committed["manifest_validation_strength_verbatim"] == S.MANIFEST_VALIDATION_STRENGTH
    assert (committed["enumeration"]["traced"]["gate_foster_ct_trajectory"]["columns_read"]
            == result["enumeration"]["traced"]["gate_foster_ct_trajectory"]["columns_read"])


def test_the_screen_producer_is_deterministic(result):
    """Two constructions in one process must serialise identically."""
    again = S.screen()
    assert json.dumps(again, indent=2) == json.dumps(result, indent=2)


def test_decision_records_a_claim_ceiling():
    text = (BUNDLE / "decision.md").read_text(encoding="utf-8")
    for section in ("## Claim ceiling", "## Adversarial check",
                    "## Strongest alternative explanation", "## Primary figure"):
        assert section in text, section
    committed = json.loads((BUNDLE / "result.json").read_text(encoding="utf-8"))
    if committed["decision"] == "RETIRE":
        assert "## Reopen condition" in text
    if committed["decision"] == "SURVIVE":
        assert "## Affected surfaces" in text


def test_retirement_record_matches_the_committed_decision():
    committed = json.loads((BUNDLE / "result.json").read_text(encoding="utf-8"))
    text = (REPO / "docs/insights/RETIRED_CANDIDATES.md").read_text(encoding="utf-8")
    if committed["decision"] == "RETIRE":
        assert "**I-045**" in text and "screens/I-045/" in text
    else:
        assert "**I-045**" not in text, (
            "I-045 is in RETIRED_CANDIDATES.md but its screen did not return RETIRE")


def test_no_unauthorised_candidate_bundle_was_created():
    """A screen bundle may exist only for a candidate a HUMAN shortlisted at IF-5.

    Wave 1 I-040, I-010, I-024; Wave 2 I-045, I-076; Wave 3 I-072, I-090. The list stays a
    literal so that adding a bundle requires editing a reviewed line, and the second assertion
    keeps the guard honest: every name on it must actually appear as a shortlisted candidate in
    the human triage record, so the list cannot be padded with something nobody selected.
    """
    allowed = {"I-040", "I-010", "I-024", "I-045", "I-076", "I-072", "I-090", "README.md"}
    present = {p.name for p in (REPO / "docs/insights/screens").iterdir()}
    assert present <= allowed, present - allowed

    triage = (REPO / "docs/insights/IF5_HUMAN_TRIAGE_DECISION.md").read_text(encoding="utf-8")
    for name in allowed - {"README.md"}:
        assert "**%s**" % name in triage, (
            "%s is allowlisted but is not a human-shortlisted candidate at IF-5" % name)


# --------------------------------------------------------------------------------------------
# HISTORICAL LIFECYCLE — the bundle is a PRE-CORRECTION snapshot
# --------------------------------------------------------------------------------------------
def test_the_bundle_is_declared_a_historical_pre_correction_snapshot():
    assert S.SNAPSHOT_KIND == "HISTORICAL_PRE_CORRECTION_SNAPSHOT"
    assert set(S.SNAPSHOT_SHA256) == {"docs/insights/screens/I-045/result.json",
                                     "docs/insights/screens/I-045/figures/primary.png"}


def test_the_committed_snapshot_matches_its_pinned_hashes():
    """Exact bytes, pinned. This is what protects the finding once the source is corrected."""
    import hashlib
    for rel, want in S.SNAPSHOT_SHA256.items():
        got = hashlib.sha256((REPO / rel).read_bytes()).hexdigest()
        assert got == want, "%s drifted from its pinned pre-correction hash" % rel


def test_the_producer_refuses_to_overwrite_the_snapshot_after_correction(monkeypatch):
    """A fresh run against corrected source would erase the finding. It must refuse."""
    monkeypatch.setattr(S, "live_source_is_corrected", lambda: True)
    with pytest.raises(S.HistoricalSnapshotProtected) as exc:
        S.refuse_if_corrected()
    msg = str(exc.value)
    assert "HISTORICAL_PRE_CORRECTION_SNAPSHOT" in msg
    assert "correction_i045_lineage" in msg, "must direct the user to the status checker"
    assert "not drift" in msg


def test_the_guard_reads_the_live_manifest():
    corrected = S.live_source_is_corrected()
    import csv as _csv
    with open(REPO / "puckworks/data/MANIFEST.csv", newline="", encoding="utf-8") as fh:
        cell = next(r["validation_strength"] for r in _csv.DictReader(fh)
                    if r["dataset_id"] == "foster2025_2/fig12_14_curves")
    assert corrected == (S.CORRECTED_MANIFEST_WORDING.lower() in cell.lower())
