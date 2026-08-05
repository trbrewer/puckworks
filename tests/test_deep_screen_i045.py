"""Focused tests for the I-045 DEEP screen (Insight Foundry IF-7).

These establish the properties the classification rests on, not the classification:

  * the protocol commit PRECEDES every deep-result-producing commit, checked against git history;
  * NO MODEL IS EXECUTED — asserted by instrumenting the solvers the audited gate would use;
  * the committed deep_result.json reproduces EXACTLY from a fresh run (the defect that reached a
    reviewed head in IF-6b is not allowed to recur here);
  * the S0 glossary is verified verbatim at run time and drift is rejected;
  * the lineage determination is derived from quoted source locations, not asserted;
  * the mixed-strength selection is produced by the frozen rule, including the paren-awareness
    that stops caveat prose being read as a second label;
  * the blast radius covers every scanned surface AND the surfaces a needle scan cannot see;
  * the cheap screen's SURVIVE, result.json and figure are untouched;
  * no protected source or evidence surface is edited in this PR.
"""
import json
import pathlib
import subprocess

import pytest

from puckworks.analysis import deep_screen_i045_lineage as D

REPO = pathlib.Path(__file__).resolve().parents[1]
BUNDLE = REPO / "docs/insights/screens/I-045"
BASE = "7d8114931c5bafbf3915d9f70b7c4621f8261a22"


@pytest.fixture(scope="module")
def result():
    return D.deep_screen()


def _git(*args):
    return subprocess.run(("git",) + args, cwd=REPO, capture_output=True, text=True)


def _history_is_truncated():
    if _git("rev-parse", "--is-shallow-repository").stdout.strip() == "true":
        return True
    return len(_git("log", "--format=%H").stdout.split()) < 2


def _has_matplotlib():
    try:
        import matplotlib                                     # noqa: F401
    except ImportError:
        return False
    return True


# --------------------------------------------------------------------------------------------
# PROTOCOL FIRST
# --------------------------------------------------------------------------------------------
def test_protocol_exists_and_freezes_every_required_item():
    p = BUNDLE / "DEEP_SCREEN_PROTOCOL.md"
    assert p.exists()
    t = p.read_text(encoding="utf-8")
    for required in (
            "## 1. The exact deep-screen question",
            "## 2. Governing definitions",
            "## 3. Authorities",
            "## 4. Source-lineage questions",
            "## 5. Blast-radius surfaces to inspect",
            "## 6. Mixed-strength generality-selection rule",
            "## 7. Alternative formulations and alternative explanations",
            "## 8. Decision and output-class rules",
            "## 9. External novelty-search terms",
            "## 10. Stop conditions"):
        assert required in t, required
    for q in ("L1", "L2", "L3", "L4", "L5", "L6", "L7"):
        assert "**%s**" % q in t, q
    for a in ("A1", "A2", "A3", "A4", "A5"):
        assert "**%s**" % a in t, a
    for f in ("F1", "F2", "F3", "F4"):
        assert "**%s**" % f in t, f
    for s in ("S1", "S2", "S3", "S4", "S5", "S6"):
        assert "**%s**" % s in t, s
    for cls in D.OUTPUT_CLASSES:
        assert cls in t, cls


def test_protocol_commit_precedes_every_deep_result_producing_commit():
    if _history_is_truncated():
        pytest.skip("shallow/truncated checkout: per-path commit order is not observable here")

    def commits(path):
        return _git("log", "--format=%H", "--", path).stdout.split()   # newest first

    proto = commits("docs/insights/screens/I-045/DEEP_SCREEN_PROTOCOL.md")
    if not proto:
        pytest.skip("protocol not yet committed (working-tree run)")
    results = []
    for rel in ("docs/insights/screens/I-045/deep_result.json",
                "docs/insights/screens/I-045/deep_decision.md",
                "puckworks/analysis/deep_screen_i045_lineage.py"):
        results += commits(rel)
    if not results:
        pytest.skip("no deep-result-producing commit yet")
    order = _git("log", "--format=%H").stdout.split()
    pos = {h: i for i, h in enumerate(order)}                  # 0 = newest
    oldest_protocol = max(pos[h] for h in proto if h in pos)
    oldest_result = max(pos[h] for h in results if h in pos)
    assert oldest_protocol > oldest_result, (
        "the protocol commit must be OLDER than the first deep-result-producing commit")


def test_the_protocol_commit_contained_only_the_protocol():
    if _history_is_truncated():
        pytest.skip("shallow checkout")
    proto = _git("log", "--format=%H", "--",
                 "docs/insights/screens/I-045/DEEP_SCREEN_PROTOCOL.md").stdout.split()
    if not proto:
        pytest.skip("protocol not yet committed")
    first = proto[-1]
    files = _git("show", "--name-only", "--format=", first).stdout.split()
    assert files == ["docs/insights/screens/I-045/DEEP_SCREEN_PROTOCOL.md"], files


# --------------------------------------------------------------------------------------------
# NO MODEL EXECUTION  (protocol stop condition S5)
# --------------------------------------------------------------------------------------------
def test_no_model_is_executed_anywhere_in_the_deep_screen():
    """Instrument the solver the audited gate uses, then run the whole screen."""
    from puckworks.models.foster2025 import machine_mode as fm
    calls = []
    real_solve = fm.solve

    def spy(*a, **k):
        calls.append("foster2025.machine_mode.solve")
        return real_solve(*a, **k)

    fm.solve = spy
    try:
        r = D.deep_screen()
        if _has_matplotlib():
            D.figure(path=BUNDLE / "figures/_deep_test_tmp.png", result=r)
    finally:
        fm.solve = real_solve
        tmp = BUNDLE / "figures/_deep_test_tmp.png"
        if tmp.exists():
            tmp.unlink()
    assert calls == [], "a model was executed: %s" % calls
    assert r["models_executed"] is False


def test_the_producer_contains_no_solver_call():
    src = pathlib.Path(D.__file__).read_text(encoding="utf-8")
    for forbidden in ("machine_mode.solve(", "simulate_shot(", "simulate_fractions(",
                      "fm.solve(", "scipy.optimize", "curve_fit"):
        assert forbidden not in src, forbidden


# --------------------------------------------------------------------------------------------
# DETERMINISM — the IF-6b defect must not recur
# --------------------------------------------------------------------------------------------
def test_committed_deep_result_does_not_drift_from_a_fresh_run(result):
    """Full canonical equality, using the producer's own serialisation contract."""
    committed = (BUNDLE / "deep_result.json").read_text(encoding="utf-8")
    expected = json.dumps(result, indent=2) + "\n"
    if committed != expected:
        c = json.loads(committed)
        diffs = [k for k in sorted(set(c) | set(result)) if c.get(k) != result.get(k)]
        raise AssertionError(
            "deep_result.json is stale: it does not reproduce from a fresh run.\n"
            "  top-level keys that differ: %s\n"
            "  fix: python -m puckworks.analysis.deep_screen_i045_lineage\n"
            "  (regenerate AFTER every source/test/doc edit is final)" % (diffs or "formatting"))


def test_two_constructions_serialise_identically(result):
    again = D.deep_screen()
    assert json.dumps(again, indent=2) == json.dumps(result, indent=2)


# --------------------------------------------------------------------------------------------
# THE GOVERNING GLOSSARY
# --------------------------------------------------------------------------------------------
def test_the_deep_screen_verifies_S0_verbatim_at_run_time(result):
    g = result["glossary"]
    assert g["method"] == "VERBATIM_RUNTIME_VERIFICATION"
    assert g["all_expected_definitions_verified"] is True
    assert g["definitions"]["independent"] == "data not used in fitting the thing being tested"
    assert g["independent_is_about_the_fit_not_the_modality"] is True
    roadmap = " ".join((REPO / "docs/ROADMAP.md").read_text(encoding="utf-8").split())
    for term, expected in D.EXPECTED_GLOSSARY_DEFINITIONS.items():
        assert expected in roadmap, term


def test_a_reworded_glossary_is_rejected():
    roadmap = (REPO / "docs/ROADMAP.md").read_text(encoding="utf-8")
    live = D.verify_glossary(roadmap)
    altered = live.replace(D.EXPECTED_GLOSSARY_DEFINITIONS["independent"], "SOMETHING ELSE", 1)
    with pytest.raises(D.GLOSSARY_DRIFT_ERROR):
        D.verify_glossary(altered)


# --------------------------------------------------------------------------------------------
# PRIMARY-SOURCE LINEAGE
# --------------------------------------------------------------------------------------------
def test_every_lineage_question_is_settled_and_carries_quoted_evidence(result):
    lin = result["source_lineage"]["lineage"]
    assert set(lin) == {
        "L1_what_entered_the_objective", "L2_s_and_H_fitted_simultaneously",
        "L3_all_plotted_CT_times_entered_the_fit", "L4_any_held_out_data",
        "L5_error_bars_role", "L6_figure_and_column_roles", "L7_authors_own_terms"}
    quote_ids = {q["id"] for q in result["source_lineage"]["quotes"]}
    for name, v in lin.items():
        assert v["settled"] is True, name
        for qid in v.get("evidence", []):
            assert qid in quote_ids, "%s cites unknown quote %s" % (name, qid)


def test_every_quote_carries_a_checkable_location(result):
    for q in result["source_lineage"]["quotes"]:
        assert q["location"] and q["quote"], q
        assert any(k in q["location"] for k in ("Sec.", "Eq.", "Fig")), q["location"]


def test_the_ct_arm_is_the_fit_data_not_held_out(result):
    lin = result["source_lineage"]
    assert lin["lineage"]["L4_any_held_out_data"]["answer"].startswith("NO")
    assert lin["lineage"]["L2_s_and_H_fitted_simultaneously"]["answer"].startswith("YES")
    assert lin["ct_arm_evidence_type_under_S0"].startswith("post-fit")
    assert lin["manifest_wording_correct"] is False
    # and the objective is quoted, not paraphrased
    q2 = [q for q in lin["quotes"] if q["id"] == "Q2"][0]
    assert "minimizing the objective function" in q2["quote"]
    assert "Eq. (39)" in q2["location"]


def test_every_candidate_holdout_was_checked_and_rejected_with_a_reason(result):
    cands = result["source_lineage"]["lineage"]["L4_any_held_out_data"]["candidates_checked"]
    assert len(cands) >= 6
    names = " ".join(c["candidate"] for c in cands).lower()
    for must in ("centre-line", "radial-shell", "coarse-grind", "sensitivity"):
        assert must in names, must
    for c in cands:
        assert c["held_out"] is False
        assert len(c["why"]) > 60, c["candidate"]


def test_the_source_does_not_support_the_independent_label(result):
    l7 = result["source_lineage"]["lineage"]["L7_authors_own_terms"]
    assert l7["source_supports_independent_label"] is False
    assert "never" in l7["answer"].lower()
    assert "future" in l7["validation_word_usage"].lower()


def test_the_card_was_checked_against_the_paper_not_assumed(result):
    c = result["source_lineage"]["card_check"]
    assert c["paper_confirms"] is True
    assert c["contradiction_found"] is False
    assert c["stop_condition_S2_triggered"] is False
    card = (REPO / "docs/cards/foster2025_2.md").read_text(encoding="utf-8")
    assert " ".join(c["circularity_note"].split()) in " ".join(card.split())


def test_source_access_is_recorded_including_what_was_blocked(result):
    a = result["source_lineage"]["access"]
    assert a["doi"] == "10.1063/5.0245167"
    assert a["publisher_pdf_blocked"] is True
    assert a["obtained_from"]
    assert a["vendored_into_repository"] is False
    assert result["source_lineage"]["verifiable_in_repository"] is False, (
        "the quotes are hand-transcribed and must be declared as such")


# --------------------------------------------------------------------------------------------
# BLAST RADIUS
# --------------------------------------------------------------------------------------------
def test_blast_radius_coverage_is_complete_and_classified(result):
    b = result["blast_radius"]
    assert b["coverage_complete"] is True
    assert b["unattributed"] == []
    for s in b["surfaces"]:
        assert s["exposure"] in D.EXPOSURE_CLASSES, s["path"]
        assert isinstance(s["reader_can_take_the_independent_reading"], bool)


def test_the_needle_scan_blind_spot_is_covered_by_path_inspection(result):
    """EVIDENCE_LINKS, PV-02, the registry and public claims carry NEITHER needle."""
    b = result["blast_radius"]
    assert b["n_surfaces_inspected_by_path_without_a_needle"] >= 3
    by_path = {s["path"]: s for s in b["surfaces"]}
    for p in ("puckworks/paper3/EVIDENCE_LINKS.json", "puckworks/public/claims.py",
              "docs/public/generated/claims.json"):
        assert p in by_path, p
        assert by_path[p]["scanned_by_needle"] is False
        assert by_path[p]["reader_can_take_the_independent_reading"] is False


def test_exactly_the_manifest_and_the_gate_are_current_miswordings(result):
    b = result["blast_radius"]
    mis = sorted(s["path"] for s in b["surfaces"]
                 if s["exposure"] == "CURRENT_INTERNAL_MISWORDING")
    assert mis == ["puckworks/data/MANIFEST.csv", "puckworks/validation/gates.py"]
    assert sorted(b["correction_required"]) == mis


def test_no_reader_facing_overclaim_and_pages_is_clean(result):
    b = result["blast_radius"]
    assert b["n_reader_facing_overclaims"] == 0
    assert b["reader_facing_overclaims"] == []
    assert b["pages_carries_attribution"] is False
    # the publish root really is what the workflow publishes
    wf = (REPO / ".github/workflows/pages.yml").read_text(encoding="utf-8")
    assert b["pages_publish_root"] in wf
    site = REPO / b["pages_publish_root"]
    if site.exists():
        for p in site.rglob("*"):
            if p.is_file():
                try:
                    t = p.read_text(encoding="utf-8")
                except (UnicodeDecodeError, OSError):
                    continue
                for needle in D.SCAN_NEEDLES:
                    assert needle not in t, "%s carries %r" % (p, needle)


def test_the_defect_is_present_in_released_source(result):
    """Recorded honestly: this is the reason to fix it."""
    rel = {r["ref"]: r for r in result["blast_radius"]["released_content"]}
    v = rel.get("v0.3.0")
    assert v and v["present"], "v0.3.0 tag must be present to make this claim"
    assert v["files"]["puckworks/data/MANIFEST.csv"] >= 1
    assert v["files"]["puckworks/validation/gates.py"] >= 1


def test_the_screen_excludes_its_own_output_and_says_so(result):
    b = result["blast_radius"]
    assert b["self_exclusion_reason"]
    for p in b["self_excluded"]:
        assert not any(s["path"] == p for s in b["surfaces"])


# --------------------------------------------------------------------------------------------
# BOUNDED GENERALITY
# --------------------------------------------------------------------------------------------
def test_paren_aware_split_does_not_read_caveat_prose_as_a_second_label():
    """The rule that stops a false positive — frozen in the protocol before the answer."""
    cell = ("qualitative (blog; measured within-session contrasts are independent, mechanistic "
            "chain is endpoint-anchored/circular)")
    segs = D.split_segments(cell)
    assert len(segs) == 1, segs
    assert D.head_label(segs[0]) == "qualitative"
    heads = [D.head_label(s) for s in D.split_segments(
        "independent (CT data) / verification (fitted curves)")]
    assert heads == ["independent", "verification"]


def test_the_primary_set_is_produced_by_the_rule_not_by_inspection(result):
    g = result["generality"]
    primary, _ = D.select_mixed_strength()
    assert g["primary_set"] == [r["dataset_id"] for r in primary]
    assert D.DATASET_ID in g["primary_set"]
    assert g["n_manifest_rows"] == len(D.manifest_rows())
    for r in g["rows"]:
        assert len(r["distinct_s0_labels"]) >= 2, r["dataset_id"]


def test_every_primary_row_is_adjudicated_on_G1_to_G5(result):
    for r in result["generality"]["rows"]:
        assert r["adjudicated"], r["dataset_id"]
        f = r["findings"]
        for k in ("G1_same_evidence_unit", "G2_scope", "G3_wording_identifies_scope",
                  "G4_consumer_could_attach_stronger_label_to_wrong_assertion",
                  "G5_downstream_propagates_ambiguity"):
            assert k in f, (r["dataset_id"], k)


def test_only_the_audited_row_is_called_wrong(result):
    g = result["generality"]
    assert g["confirmed_incorrect_strength"] == [D.DATASET_ID]
    assert g["is_the_defect_general"] is False
    assert g["no_other_candidate_adjudicated"] is True
    # scope is stated everywhere — that is the finding that kills the general reading
    assert g["n_with_scope_stated"] == g["n_primary"]


def test_the_secondary_set_is_counted_but_not_adjudicated(result):
    g = result["generality"]
    assert g["n_secondary"] >= 1
    assert g["secondary_note"]
    for row in g["secondary_set"]:
        assert set(row) == {"dataset_id", "validation_strength"}, (
            "secondary rows must carry no adjudication")


# --------------------------------------------------------------------------------------------
# ALTERNATIVES, FORMULATIONS, DECISION
# --------------------------------------------------------------------------------------------
def test_all_five_alternatives_are_tested_and_each_names_its_evidence(result):
    alts = {a["id"]: a for a in result["alternatives"]}
    assert set(alts) == {"A1", "A2", "A3", "A4", "A5"}
    for a in alts.values():
        assert a["verdict"] and a["settled_by"] and a["evidence"]
    for i in ("A1", "A2", "A3", "A5"):
        assert alts[i]["verdict"].startswith("FAILS"), i
    assert alts["A4"]["verdict"].startswith("PARTLY"), (
        "containment is real and must be recorded as partly succeeding, not dismissed")


def test_all_four_formulations_are_assessed_and_none_implemented(result):
    forms = {f["id"]: f for f in result["formulations"]}
    assert set(forms) == {"F1", "F2", "F3", "F4"}
    for f in forms.values():
        for k in ("scientifically_accurate", "glossary_compatible", "preserves_source_wording",
                  "consumable_by_current_tools", "migration_cost",
                  "risk_of_implying_held_out_validation", "generalizes", "assessment"):
            assert k in f, (f["id"], k)
    assert "RECOMMENDED" in forms["F2"]["assessment"]
    assert "REJECTED" in forms["F3"]["assessment"]
    assert result["decision"]["recommended_correction_wording"] == forms["F2"]["wording"]


def test_the_classification_is_derived_not_asserted(result):
    d = result["decision"]
    assert d["output_class"] in D.OUTPUT_CLASSES
    dv = d["derivation"]
    assert dv["lineage_settled_from_primary_source"] is True
    assert dv["no_data_held_out"] is True
    assert dv["attribution_confirmed_incorrect"] is True
    assert dv["survives_alternatives_A1_A2_A3_A5"] is True
    assert dv["containment_measured"] is True
    assert dv["defect_is_general"] is False
    assert d["output_class"] == "CORRECTION_ONLY"


def test_retire_after_deep_screen_was_genuinely_available():
    """If the paper had shown a holdout, the screen must reach a different class."""
    lin = D.source_lineage()
    lin = json.loads(json.dumps(lin))
    lin["lineage"]["L4_any_held_out_data"]["answer"] = "YES — the CT points were held out."
    lin["manifest_wording_correct"] = True
    out = D.decide(lin, D.blast_radius(), D.generality(), D.alternatives())
    assert out["output_class"] == "RETIRE_AFTER_DEEP_SCREEN"


def test_an_unsettled_lineage_routes_to_needs_primary_source():
    lin = json.loads(json.dumps(D.source_lineage()))
    lin["lineage"]["L1_what_entered_the_objective"]["settled"] = False
    out = D.decide(lin, D.blast_radius(), D.generality(), D.alternatives())
    assert out["output_class"] == "NEEDS_PRIMARY_SOURCE"


def test_a_general_defect_would_route_to_a_technical_note():
    gen = json.loads(json.dumps(D.generality()))
    gen["is_the_defect_general"] = True
    out = D.decide(D.source_lineage(), D.blast_radius(), gen, D.alternatives())
    assert out["output_class"] == "TECHNICAL_NOTE_CANDIDATE"


def test_the_decision_states_both_the_supported_and_the_unsupported_claim(result):
    d = result["decision"]
    assert len(d["strongest_supported_claim"]) > 200
    assert len(d["strongest_claim_NOT_supported"]) > 150
    assert d["separate_correction_pr_recommended"] is True
    assert d["manuscript_work_justified"] is False
    assert d["further_literature_review_justified"] is False
    assert len(d["future_correction_targets"]) == 3
    for t in d["future_correction_targets"]:
        assert t["edited_in_this_pr"] is False
        assert t["recommended"]


# --------------------------------------------------------------------------------------------
# THE CHEAP SCREEN AND THE PROTECTED SURFACES ARE UNTOUCHED
# --------------------------------------------------------------------------------------------
def test_the_cheap_screen_history_is_preserved_not_rewritten(result):
    assert result["cheap_screen"]["disposition"] == "SURVIVE"
    assert result["cheap_screen"]["not_rewritten_by_this_screen"] is True
    committed = json.loads((BUNDLE / "result.json").read_text(encoding="utf-8"))
    assert committed["decision"] == "SURVIVE"
    dec = (BUNDLE / "deep_decision.md").read_text(encoding="utf-8")
    assert "cheap screen : SURVIVE" in dec
    assert "deep screen  : CORRECTION_ONLY" in dec


def test_protected_surfaces_are_byte_unchanged_in_this_pr():
    if _git("cat-file", "-e", BASE + "^{commit}").returncode != 0:
        pytest.skip("branch base %s not present in this checkout" % BASE[:7])
    for path in ("puckworks/data/MANIFEST.csv",
                 "puckworks/validation/gates.py",
                 "puckworks/paper3/EVIDENCE_LINKS.json",
                 "docs/paper3_resource/generated",
                 "docs/public/generated",
                 "puckworks/models/__init__.py",
                 "puckworks/public/claims.py",
                 "docs/cards",
                 "docs/insights/generated",
                 "docs/insights/ID_REGISTRY.json",
                 "puckworks/viz",
                 "docs/figures/viz",
                 "docs/insights/screens/I-045/result.json",
                 "docs/insights/screens/I-045/figures/primary.png",
                 "docs/insights/screens/I-045/decision.md",
                 "docs/insights/screens/I-045/README.md",
                 "docs/insights/screens/I-076",
                 "puckworks/analysis/screen_i045_evidence_halves.py"):
        r = _git("diff", "--numstat", BASE, "HEAD", "--", path)
        assert r.returncode == 0, r.stderr
        assert r.stdout.strip() == "", "%s was modified: %s" % (path, r.stdout.strip())


def test_the_deep_figure_is_not_registered_in_the_viz_registry():
    reg = (REPO / "puckworks/viz/registry.py").read_text(encoding="utf-8")
    for name in ("deep_primary", "deep_screen_i045", "I-045"):
        assert name not in reg, name


def test_novelty_findings_are_not_fabricated_into_the_deterministic_output(result):
    """Stop condition S6 — external findings live in the review, not in the JSON."""
    blob = json.dumps(result, ensure_ascii=False).lower()
    for leaked in ("bioleak", "openlineage", "datahub", "verra", "asme", "arxiv"):
        assert leaked not in blob, leaked
    assert result["novelty_review"]["path"].endswith("NOVELTY_REVIEW.md")
    nr = (BUNDLE / "NOVELTY_REVIEW.md").read_text(encoding="utf-8")
    assert "INCREMENTAL" in nr
    assert "Search date" in nr or "search date" in nr
    assert "## 3. Exact queries" in nr
