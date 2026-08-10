"""Focused tests for the I-093 cheap screen (Insight Foundry Wave 4).

These protect the scientific decision and its reproducibility. **They do not re-run the solver**:
the screen costs ~66 min of CPU and CLAUDE.md rule 3 keeps that out of CI. What CI checks is the
committed artifact, the decision logic recomputed from it, and the cheap invariants (scenario,
gate, units, hashes) that can be evaluated without a solve.

  * protocol frozen before the module, checked against git history, and hash-bound — to the
    HISTORICAL source blobs the screen actually ran, recovered from git, not to the working tree;
  * the comparability gate is fail-closed and no route runs after it fails;
  * declared validity ranges are enforced, not assumed;
  * the decision is RECOMPUTED from the machine-readable result, not restated;
  * the RVE stabilisation criterion and the trend metric are recomputed from the stored rows;
  * INCONCLUSIVE-vs-SURVIVE hinges on reaching the card's box guidance, and that is asserted;
  * a compute bound is never recorded as a data request;
  * the confound between RVE and realisation noise is disclosed, not buried;
  * no evidence rung is changed and no manifest dataset is consumed.
"""
import copy
import hashlib
import json
import pathlib
import subprocess

import pytest

from puckworks.analysis import screen_i093_crossscale_permeability as S

REPO = pathlib.Path(__file__).resolve().parents[1]
BUNDLE = REPO / "docs/insights/screens/I-093"
RESULT = BUNDLE / "result.json"


def _git(*args):
    return subprocess.run(("git",) + args, cwd=REPO, capture_output=True, text=True)


def _history_is_truncated():
    if _git("rev-parse", "--is-shallow-repository").stdout.strip() == "true":
        return True
    return len(_git("log", "--format=%H").stdout.split()) < 2


@pytest.fixture(scope="module")
def result():
    if not RESULT.exists():
        pytest.skip("result not yet written")
    return json.loads(RESULT.read_text(encoding="utf-8"))


# --------------------------------------------------------------------------------------------
# PROTOCOL FIRST, AND BOUND BY HASH
# --------------------------------------------------------------------------------------------
def test_protocol_exists_and_freezes_all_ten_items():
    text = (BUNDLE / "PROTOCOL.md").read_text(encoding="utf-8")
    for n in range(1, 11):
        assert ("\n## %d." % n) in text, "protocol item %d is missing" % n
    for anchor in ("Candidate-selection record", "Decision logic", "Claim ceiling",
                   "Compute budget", "Issue #231 disposition"):
        assert anchor in text or anchor.lower() in text.lower(), anchor


def test_protocol_commit_precedes_every_result_producing_commit():
    if _history_is_truncated():
        pytest.skip("shallow checkout: per-path commit order is not observable here")

    def commits(path):
        return _git("log", "--format=%H", "--", path).stdout.split()
    proto = commits("docs/insights/screens/I-093/PROTOCOL.md")
    if not proto:
        pytest.skip("protocol not yet committed")
    results = []
    for rel in ("docs/insights/screens/I-093/result.json",
                "puckworks/analysis/screen_i093_crossscale_permeability.py",
                "docs/insights/screens/I-093/decision.md"):
        results += commits(rel)
    if not results:
        pytest.skip("no result-producing commit yet")
    order = _git("log", "--format=%H").stdout.split()
    pos = {h: i for i, h in enumerate(order)}
    assert max(pos[h] for h in proto if h in pos) > max(pos[h] for h in results if h in pos), (
        "the protocol commit must be OLDER than the first result-producing commit")


def _protocol_freeze_commit():
    """The commit that ADDED the frozen protocol, located from git history — never inferred from
    HEAD. `git log` lists newest first, so the adding commit is the last entry."""
    out = _git("log", "--format=%H", "--diff-filter=A", "--",
               "docs/insights/screens/I-093/PROTOCOL.md").stdout.split()
    return out[-1] if out else None


def _blob_sha256(commit, rel):
    """SHA-256 of the RAW blob at `commit`, or None if the object is absent.

    Deliberately NOT text=True: decoding would apply newline translation and change the digest.
    """
    p = subprocess.run(("git", "cat-file", "blob", "%s:%s" % (commit, rel)),
                       cwd=REPO, capture_output=True)
    return hashlib.sha256(p.stdout).hexdigest() if p.returncode == 0 else None


def test_result_is_hash_bound_to_protocol_freeze_source_blobs(result):
    """The frozen screen is bound to the source it ACTUALLY RAN, recovered from git history.

    This previously compared every recorded input digest with the CURRENT WORKING TREE, which
    encodes the wrong invariant: it makes a frozen historical result a permanent prohibition on
    any later backward-compatible evolution of a component it once used, and it would demand an
    ~8 h re-execution of the cheap and deep screens to record a byte-identical scientific result.
    A frozen result must stay pinned to its own historical source — which git preserves — not to
    whatever that file becomes later. The screen's evidence is unaffected by, say, an inert
    optional diagnostic return value added to the solver years afterwards (RP-D.1).

    Still enforced, and strictly:
      * the frozen PROTOCOL.md is byte-identical on disk AND at the freeze commit;
      * every recorded input digest equals the raw blob at the protocol-freeze commit;
      * the recorded input SET still equals the module's declared INPUT_FILES;
      * the immutable base commit is unchanged.
    Lineage (protocol-before-result, first-commit-on-base) is checked by its own tests above.
    """
    assert result["protocol"]["sha256"] == S._sha256(S.PROTOCOL_PATH)
    assert result["provenance"]["base_commit"] == S.BASE_COMMIT == \
        "892e5ec78f7a0dcf1b1f2de85ccfff8f39e0effa"
    assert set(result["provenance"]["input_sha256"]) == set(S.INPUT_FILES)

    if _history_is_truncated():
        pytest.skip("shallow checkout: historical source blobs are not observable here")
    freeze = _protocol_freeze_commit()
    if freeze is None:
        pytest.skip("protocol not yet committed")
    for rel, digest in result["provenance"]["input_sha256"].items():
        historical = _blob_sha256(freeze, rel)
        if historical is None:
            pytest.skip("historical blob for %s is absent from this checkout" % rel)
        assert historical == digest, (
            "recorded input hash for %s does not match the blob at the protocol-freeze commit "
            "%s — the frozen result no longer points at the source it ran" % (rel, freeze))


def test_the_first_branch_commit_sits_on_the_immutable_base():
    if _history_is_truncated():
        pytest.skip("shallow checkout")
    base = S.BASE_COMMIT
    if _git("cat-file", "-e", base + "^{commit}").returncode != 0:
        pytest.skip("base not present")
    proto = _git("log", "--format=%H", "--", "docs/insights/screens/I-093/PROTOCOL.md").stdout.split()
    if not proto:
        pytest.skip("protocol not committed")
    first = proto[-1]
    parents = _git("rev-list", "--parents", "-n", "1", first).stdout.split()
    assert parents[1:] == [base], "the first I-093 commit must have the immutable base as parent"


# --------------------------------------------------------------------------------------------
# SCENARIO AND COMPARABILITY — evaluable without a solve
# --------------------------------------------------------------------------------------------
def test_scenario_values_are_provenance_bound_not_invented():
    from puckworks.models.brewer2026 import pack_generator as pg
    scn = S.scenario()
    assert scn["grain_radius_um"] == pytest.approx(float(pg.boulder_radius_um(S.GS)))
    # the voxel size is DERIVED so the grain radius is exactly the card's admissibility floor
    assert scn["grain_radius_voxels"] == 10.0
    assert scn["voxel_um"] == pytest.approx(scn["grain_radius_um"] / 10.0)
    assert scn["grain_radius_m"] == pytest.approx(scn["grain_radius_um"] * 1e-6)


def test_comparability_gate_enforces_both_components_declared_ranges():
    scn = S.scenario()
    g = S.comparability_gate(scn)
    assert g["passed"] is True and g["failed"] == []
    assert set(g["checks"]) == {"G1_grain_radius_in_closure_range",
                                "G2_porosity_family_in_closure_range",
                                "G3_grain_resolution_admissible",
                                "G4_same_observable_definition"}
    # the ranges are the registry's, not the screen's invention
    from puckworks.registry import components
    wad = [c for c in components() if c.name == "wadsworth2026.permeability"][0]
    assert "145" in wad.valid_range and "818" in wad.valid_range
    assert "0.37-0.67" in wad.assumptions


def test_gate_fails_closed_on_an_out_of_range_scenario():
    """A guard that has never been shown to fail is not evidence of anything."""
    scn = dict(S.scenario())
    scn["grain_radius_um"] = 1200.0                       # outside the closure's declared range
    g = S.comparability_gate(scn)
    assert g["passed"] is False
    assert "G1_grain_radius_in_closure_range" in g["failed"]
    assert g["execution_permitted"] is False


def test_no_route_executes_after_a_failed_gate(monkeypatch):
    """Fail the gate and assert neither the pack generator nor the solver is entered."""
    from puckworks.models.brewer2026 import pack_generator as pg, lb_reference as lb
    calls = []
    monkeypatch.setattr(S, "comparability_gate",
                        lambda scn: dict(checks={}, passed=False, failed=["forced"],
                                         execution_permitted=False))
    monkeypatch.setattr(pg, "make_pack", lambda *a, **k: calls.append("make_pack"))
    monkeypatch.setattr(lb, "solve", lambda *a, **k: calls.append("solve"))
    r = S.screen(budget_s=1.0)
    assert calls == [], "a route ran after the comparability gate failed: %s" % calls
    assert r["models_executed"] == []
    assert r["stopped_at"] == "comparability_gate"
    assert r["decision"] == "INCONCLUSIVE"


def test_positive_control_is_the_analytic_case_and_passed(result):
    pc = result["positive_control"]
    assert pc["passed"] is True
    assert pc["relative_error"] < pc["tolerance"] < 0.05
    assert pc["converged"] is True
    assert pc["k_exact_lu"] > 0


# --------------------------------------------------------------------------------------------
# THE DECISION, RECOMPUTED FROM THE ARTIFACT
# --------------------------------------------------------------------------------------------
def test_rve_stabilisation_criterion_recomputed_from_the_stored_rows(result):
    v = result["rve_sweep"]
    ks = [r["k_lu"] for r in v["rows"]]
    dev = [abs(k - ks[-1]) / ks[-1] for k in ks]
    top = abs(ks[-1] - ks[-2]) / ks[-1]
    assert top == pytest.approx(v["change_between_two_largest"], abs=1e-4)
    # no L satisfies the frozen criterion
    star = None
    for i in range(len(ks)):
        if all(d <= S.RVE_REL_TOL for d in dev[i:]) and top <= S.RVE_TOP_TOL:
            star = v["rows"][i]["L"]; break
    assert star is None and v["L_star"] is None
    assert top > S.RVE_TOP_TOL, "the criterion must actually be violated"


def test_the_sweep_reached_the_card_box_guidance_so_this_is_not_a_compute_bound(result):
    """This is what separates SURVIVE from INCONCLUSIVE, so it is asserted, not assumed."""
    v = result["rve_sweep"]
    assert max(v["box_grain_diameters_reached"]) >= S.CARD_BOX_GRAIN_DIAMETERS
    assert v["reached_card_box_guidance"] is True
    assert v["outcome"] == "NO_SIZE_STABILISES"
    assert result["compute"]["exceeded"] is False
    assert result["compute"]["wall_s"] < result["compute"]["budget_s"]


def test_trend_metric_recomputed_from_the_stored_rows(result):
    m, rows = result["metric"], result["family"]["rows"]
    g = max(r["ratio_percolation"] for r in rows) / min(r["ratio_percolation"] for r in rows)
    assert g == pytest.approx(m["G_percolation"], abs=5e-5)   # stored rounded to 4 dp
    g_ck = max(r["ratio_carman_kozeny"] for r in rows) / min(r["ratio_carman_kozeny"] for r in rows)
    assert g_ck == pytest.approx(m["G_carman_kozeny"], abs=5e-5)
    assert m["agreement_floor"] == pytest.approx(max(m["U"], S.PUBLISHED_COLLAPSE_SCATTER))
    assert m["percolation_trend_preserved"] is (m["G_percolation"] <= m["agreement_floor"])


def test_the_agreement_floor_uses_the_closures_own_published_scatter(result):
    """The floor may not be tighter than the closure ever claimed for itself."""
    src = (REPO / "puckworks/models/wadsworth2026/permeability.py").read_text(encoding="utf-8")
    assert "1.31" in src, "the published collapse scatter must be sourced, not invented"
    assert S.PUBLISHED_COLLAPSE_SCATTER == 1.31
    assert result["metric"]["agreement_floor"] >= S.PUBLISHED_COLLAPSE_SCATTER


def test_decision_recomputes_to_survive_from_the_stored_evidence(result):
    recomputed = S.decide(result["rve_sweep"], result["metric"])
    assert recomputed["decision"] == result["decision"] == "SURVIVE"
    assert "no RVE size stabilises" in recomputed["arm"]
    assert recomputed["is_compute_bound"] is False


def test_decision_mapping_is_exercised_not_restated(result):
    """Drive the frozen rule with inputs other than the live one."""
    # compute bound -> INCONCLUSIVE, and explicitly NOT a data request
    rve = copy.deepcopy(result["rve_sweep"])
    rve["outcome"] = "COMPUTE_BOUND_BEFORE_CARD_BOX"
    d = S.decide(rve, result["metric"])
    assert d["decision"] == "INCONCLUSIVE"
    assert d["is_compute_bound"] is True and d["is_data_request"] is False
    # stabilised + trends preserved -> RETIRE
    rve2 = copy.deepcopy(result["rve_sweep"]); rve2["outcome"] = "STABILISED"; rve2["L_star"] = 64
    met = copy.deepcopy(result["metric"])
    met["percolation_trend_preserved"] = True; met["carman_kozeny_trend_preserved"] = True
    assert S.decide(rve2, met)["decision"] == "RETIRE"
    # stabilised + trends diverge -> SURVIVE on the other arm
    met2 = copy.deepcopy(met); met2["percolation_trend_preserved"] = False
    d3 = S.decide(rve2, met2)
    assert d3["decision"] == "SURVIVE" and "diverge" in d3["arm"]


def test_a_compute_bound_is_never_recorded_as_a_data_request(result):
    assert result["decision_record"]["is_data_request"] is False
    text = (BUNDLE / "decision.md").read_text(encoding="utf-8")
    assert "not a compute bound" in text.lower() or "NOT a compute bound" in text


# --------------------------------------------------------------------------------------------
# UNITS, LINEAGE AND THE DISCLOSED CONFOUND
# --------------------------------------------------------------------------------------------
def test_lattice_to_si_conversion_is_the_exact_declared_one(result):
    h = result["scenario"]["voxel_m"]
    for r in result["family"]["rows"]:
        assert r["k_m2"] == pytest.approx(r["k_lu"] * h * h, rel=1e-12)


def test_seeds_are_labelled_geometry_realisations_not_experimental_replicates():
    src = pathlib.Path(S.__file__).read_text(encoding="utf-8")
    assert "NOT experimental replicates" in src
    dec = (BUNDLE / "decision.md").read_text(encoding="utf-8")
    assert "realisation" in dec


def test_the_rve_confound_is_disclosed_not_buried(result):
    """The screen's own limitation must be in the reader-facing record, not only in my head."""
    for f in ("decision.md", "README.md"):
        t = (BUNDLE / f).read_text(encoding="utf-8")
        assert "confound" in t.lower(), f
        assert "seed" in t.lower(), f
    m = result["metric"]
    assert m["U_seed"] > 1.0, "seed spread must be measured, not assumed zero"


def test_the_closure_fit_lineage_is_recorded(result):
    """The closure is itself LB-anchored; agreement would be weak evidence and the record says so."""
    card = (REPO / "docs/cards/wadsworth2026.md").read_text(encoding="utf-8")
    assert "LBflow" in card
    assert "LB-anchored" in result["claim_ceiling"] or \
        "LB-anchored" in (BUNDLE / "decision.md").read_text(encoding="utf-8")


def test_the_anchor_is_the_cpu_reference_not_the_accelerator(result):
    assert "lb_reference" in result["anchor"] and "lb_taichi is NOT used" in result["anchor"]
    src = pathlib.Path(S.__file__).read_text(encoding="utf-8")
    assert "lb_taichi" not in src.replace("lb_taichi is NOT used", "")


# --------------------------------------------------------------------------------------------
# NOTHING WAS UPGRADED OR CONSUMED
# --------------------------------------------------------------------------------------------
def test_no_manifest_dataset_is_consumed_and_no_rung_changes(result):
    assert result["evidence_labels_unchanged"] is True
    assert result["administrative_exception_invoked"] is False
    assert result["issue_231_disposition"] == "NOT_MATERIAL_TO_SELECTED_DECISION"
    # no dataset is LOADED: the two names appear only in the issue-231 explanatory text,
    # never in an import or a read
    src = pathlib.Path(S.__file__).read_text(encoding="utf-8")
    for forbidden in ("puckworks import data", "from puckworks import data",
                      "MANIFEST.csv", "de1_fixtureA.json", "_manifest_rows", "data_fixture"):
        assert forbidden not in src, "the screen appears to consume a dataset via %r" % forbidden
    assert result["family"]["rows"], "the family must come from generated geometry only"


def test_registry_evidence_strengths_are_untouched():
    from puckworks.registry import components
    live = {c.name: c.evidence_strength for c in components()}
    assert live["wadsworth2026.permeability"] == "source_curve_reproduction"
    assert live["brewer2026.lb_reference"] == "code_verification"
    assert live["brewer2026.pack_generator"] == "qualitative_capacity"


def test_claim_ceiling_refuses_the_representativeness_reading(result):
    c = result["claim_ceiling"]
    assert "does NOT establish that the family is representative" in c or \
        "does NOT establish" in c and "representative" in c
    assert "SYNTHETIC" in c or "synthetic" in c
    assert "not empirical validation" in c


def test_bundle_is_complete_and_carries_the_disposition():
    for name in ("PROTOCOL.md", "result.json", "decision.md", "README.md"):
        assert (BUNDLE / name).exists(), name
    assert (BUNDLE / "figures/primary.png").exists()
    dec = (BUNDLE / "decision.md").read_text(encoding="utf-8")
    for tag in ("CHEAP_SCIENTIFIC_SCREEN", "NOT_A_PUBLICATION_RESULT",
                "NOT_A_MODEL_VALIDATION_UPGRADE"):
        assert tag in dec


def test_the_screen_figure_is_not_registered_as_a_viz_spec():
    """Screen provenance, not a mechanism render with a fidelity ceiling."""
    reg = (REPO / "puckworks/viz/registry.py").read_text(encoding="utf-8")
    assert "I-093" not in reg and "i093" not in reg
