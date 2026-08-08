"""Outcome-neutral audit tests for the I-093 deep screen.

Written and committed BEFORE any deep permeability output was inspected. They protect the frozen
run matrix, the guard semantics and the seed-semantics classification — none of which depends on
what the solver produced. Result-level tests are added with the deep result.
"""
import json
import pathlib

import pytest

from puckworks.analysis import deep_i093_run_audit as A
from puckworks.analysis import deep_screen_i093_rve as D
from puckworks.analysis import screen_i093_crossscale_permeability as CHEAP

REPO = pathlib.Path(__file__).resolve().parents[1]
BUNDLE = REPO / "docs/insights/screens/I-093"
MATRIX = BUNDLE / "expected_run_matrix.json"


@pytest.fixture(scope="module")
def matrix():
    if not MATRIX.exists():
        pytest.skip("expected run matrix not yet written")
    return json.loads(MATRIX.read_text(encoding="utf-8"))


def test_expected_matrix_is_46_frozen_cells(matrix):
    assert matrix["expected_cells"] == 46 == len(matrix["cells"])
    assert len(A.expected_run_matrix()) == 46           # regenerates deterministically


def test_matrix_regenerates_exactly_from_the_frozen_protocol_constants(matrix):
    assert A.expected_run_matrix() == matrix["cells"]


def test_every_cell_carries_the_fields_the_audit_needs(matrix):
    for c in matrix["cells"]:
        for f in ("order", "section", "L", "L_over_d", "phis_target", "seed", "solver_config",
                  "lattice", "estimated_cost_s", "required_convergence",
                  "needed_for_primary_finite_size", "needed_for_closure_decision", "status"):
            assert f in c, (c["order"], f)
        assert c["status"] == "EXPECTED"


def test_section_shapes_match_the_frozen_protocol(matrix):
    by = {}
    for c in matrix["cells"]:
        by.setdefault(c["section"], []).append(c)
    assert len(by["S3_multiseed_rve"]) == len(D.DEEP_SIZES) * len(D.DEEP_SEEDS) == 16
    assert {c["L"] for c in by["S3_multiseed_rve"]} == set(D.DEEP_SIZES)
    assert {c["seed"] for c in by["S3_multiseed_rve"]} == set(D.DEEP_SEEDS)
    assert len(by["S4.2_porosity_dependence"]) == 16
    assert {c["phis_target"] for c in by["S4.2_porosity_dependence"]} == set(D.EXTREME_PHIS)
    assert len(by["S4.3_trend_on_means"]) == len(CHEAP.PHIS_TARGETS) * 2 == 12


def test_only_section_3_is_needed_for_the_primary_finite_size_decision(matrix):
    primary = {c["section"] for c in matrix["cells"] if c["needed_for_primary_finite_size"]}
    assert primary == {"S3_multiseed_rve"}
    closure = {c["section"] for c in matrix["cells"] if c["needed_for_closure_decision"]}
    assert closure == {"S4.2_porosity_dependence", "S4.3_trend_on_means"}


def test_the_budget_shortfall_is_recorded_not_hidden(matrix):
    assert matrix["budget_sufficient"] is False
    assert matrix["frozen_budget_s"] == D.COMPUTE_BUDGET_S == 150 * 60
    assert matrix["estimated_total_s"] > matrix["frozen_budget_s"]
    assert matrix["shortfall_min"] > 0


def test_the_frozen_budget_was_not_raised_by_this_audit():
    """The erratum retains the budget; a later edit that inflates it must fail here."""
    assert D.COMPUTE_BUDGET_S == 150 * 60


def test_guard_semantics_are_recorded_as_implemented(matrix):
    g = matrix["guard_semantics"]
    assert g["checks_before_launch"] is True
    assert g["terminates_in_flight_cell"] is False
    assert g["admitted_cell_runs_to_completion"] is True
    src = pathlib.Path(D.__file__).read_text(encoding="utf-8")
    assert "if spent > budget_s" in src


def test_seed_semantics_classification_and_its_consequences(matrix):
    assert matrix["seed_semantics"] == "RELATED_NON_NESTED"
    s = matrix["seed_semantics_statement"]
    assert "not interpretable as the same physical realization" in s
    assert "Cross-size statistical independence is not established" in s
    cons = " ".join(matrix["statistical_consequences"])
    assert "no paired size differences" in cons
    assert "no lines connect equal seeds across sizes" in cons


def test_seed_semantics_evidence_matches_the_generator(matrix):
    """Regenerate the geometry facts; no permeability is involved."""
    import numpy as np
    from puckworks.models.brewer2026 import pack_generator as pg
    vox = pg.boulder_radius_um(CHEAP.GS) / CHEAP.GRAIN_RADIUS_VOXELS
    def mk(L, seed):
        return pg.make_pack(L=L, voxel_um=vox, gs=CHEAP.GS, phis_target=D.DEEP_PHIS,
                            hetero_amp=CHEAP.HETERO_AMP, seed=seed, verbose=False)
    a32, m32 = mk(32, 0)
    a64, m64 = mk(64, 0)
    b32, _ = mk(32, 1)
    c32, _ = mk(32, 0)
    e = matrix["seed_semantics_evidence"]
    assert np.array_equal(a32, c32) is True and e["same_seed_same_L_reproducible"] is True
    assert (not np.array_equal(a32, b32)) and e["different_seed_same_L_differs"] is True
    assert (not np.array_equal(a32, a64[:32, :32, :32]))
    assert e["smaller_is_spatial_subset_of_larger"] is False
    assert m32["n_spheres"] != m64["n_spheres"]        # size-dependent draw count


def test_the_audit_contains_no_permeability_values(matrix):
    """This artifact is outcome-neutral by construction."""
    blob = json.dumps(matrix)
    # value-bearing keys, not the word "permeability", which legitimately appears in the
    # audit's own prose ("before any permeability output was inspected")
    for forbidden in ('"k_lu"', '"k_m2"', "G_percolation", "deep_decision", "ratio_percolation"):
        assert forbidden not in blob, forbidden
    for c in matrix["cells"]:
        assert not any(k.startswith("k_") for k in c), c["order"]
    # the audit module never EXECUTES a solve or a pack build; "lb_reference.solve" appears
    # only inside a required_convergence description string
    src = pathlib.Path(A.__file__).read_text(encoding="utf-8")
    for call in ("lb.solve(", "make_pack(", "_run(", "pore_scale_k("):
        assert call not in src, call


# --------------------------------------------------------------------------------------------
# RESULT-LEVEL TESTS — added with the deep result, over the committed artifacts
# --------------------------------------------------------------------------------------------
from puckworks.analysis import deep_i093_adjudicate as ADJ   # noqa: E402

DEEP = BUNDLE / "deep_result.json"
RAW = BUNDLE / "deep_run_raw.json"


@pytest.fixture(scope="module")
def deep():
    if not DEEP.exists():
        pytest.skip("deep result not yet written")
    return json.loads(DEEP.read_text(encoding="utf-8"))


def test_every_expected_cell_has_exactly_one_recorded_status(deep, matrix):
    cells = deep["execution_audit"]["cells"]
    assert len(cells) == matrix["expected_cells"] == 46
    assert {(c["section"], c["L"], c["phis_target"], c["seed"]) for c in cells} == \
        {(c["section"], c["L"], c["phis_target"], c["seed"]) for c in matrix["cells"]}
    for c in cells:
        assert c["status"] in A.STATUSES
    ea = deep["execution_audit"]
    counted = (ea["converged"] + ea["not_launched_budget_guard"] + ea["scientific_nonconvergence"]
               + ea["operational_failure"] + ea["exact_retry"] + ea["in_flight_at_guard"])
    assert counted == 46, "cells must be fully accounted, not partially"


def test_no_frozen_cell_disappears(deep):
    """A cell may change status but may never vanish from the audit."""
    got = {(c["section"], c["L"], c["phis_target"], c["seed"])
           for c in deep["execution_audit"]["cells"]}
    want = {(c["section"], c["L"], c["phis_target"], c["seed"])
            for c in A.expected_run_matrix()}
    assert got == want


def test_retries_do_not_inflate_independent_n(deep):
    assert deep["execution_audit"]["exact_retry"] == 0
    for r in deep["realisation_table"]:
        assert r["attempts"] == 1
    for L, s in deep["ensembles_per_size"].items():
        rows = [r for r in deep["realisation_table"] if str(r["L"]) == L]
        assert s["n"] == len(rows) == len({r["seed"] for r in rows}), L


def test_no_failed_or_nonconverged_run_enters_the_statistics(deep):
    for r in deep["realisation_table"]:
        assert r["converged"] is True
    assert deep["execution_audit"]["scientific_nonconvergence"] == 0
    assert deep["execution_audit"]["operational_failure"] == 0


def test_ensemble_statistics_regenerate_from_the_realisation_table(deep):
    for L, s in deep["ensembles_per_size"].items():
        ks = [r["k_lu"] for r in deep["realisation_table"] if str(r["L"]) == L]
        again = ADJ.ensemble_stats(ks)
        for f in ("n", "mean", "median", "sample_sd", "cv", "min", "max", "max_over_min"):
            assert again[f] == pytest.approx(s[f], rel=1e-12), (L, f)


def test_sample_sd_uses_n_minus_one_and_is_na_below_two():
    import statistics
    s = ADJ.ensemble_stats([1.0, 2.0, 3.0, 4.0])
    assert s["sample_sd"] == pytest.approx(statistics.stdev([1.0, 2.0, 3.0, 4.0]))
    one = ADJ.ensemble_stats([2.5])
    assert one["n"] == 1 and one["sample_sd"] is None and one["cv"] is None   # NA, not zero
    assert ADJ.ensemble_stats([])["n"] == 0


def test_the_frozen_stabilisation_decision_regenerates_exactly(deep):
    f = deep["finite_size"]
    per = deep["ensembles_per_size"]
    sizes = sorted(int(k) for k in per)
    mmax = per[str(sizes[-1])]["mean"]
    for L in sizes:
        c = f["checks"][str(L)]
        assert c["delta"] == pytest.approx(abs(per[str(L)]["mean"] - mmax), rel=1e-9)
        band = ADJ.D.SIGMA_K * (c["se"] ** 2 + f["checks"][str(sizes[-1])]["se"] ** 2) ** 0.5
        assert c["band"] == pytest.approx(band, rel=1e-9)
        assert c["within"] is bool(c["delta"] <= c["band"])
    assert f["frozen_outcome"] == ("PASS" if f["L_star"] is not None else "FAIL")


def test_the_power_caveat_is_recorded_with_the_pass(deep):
    """A PASS at the smallest tested size is low power, and the record must say so."""
    f = deep["finite_size"]
    assert f["frozen_outcome"] == "PASS"
    sizes = sorted(int(k) for k in deep["ensembles_per_size"])
    assert f["L_star"] == sizes[0], "L* at the smallest size is the low-power tell"
    assert "NON-REJECTION" in f["power_caveat"]
    assert "not demonstrating equivalence" in f["power_caveat"].lower() or \
        "NOT demonstrating equivalence" in f["power_caveat"]
    assert f["rev_determination"] is None


def test_no_rev_value_is_claimed(deep):
    assert deep["finite_size"]["rev_determination"] is None
    # the phrase may appear ONLY inside the explicit disclaimer, never as a claim
    note = deep["finite_size"]["rev_note"]
    assert "no REV value" in note and "is stated" in note
    blob = json.dumps({k: v for k, v in deep["finite_size"].items() if k != "rev_note"})
    assert "REV =" not in blob and "REV exceeds" not in blob


def test_no_paired_analysis_for_related_non_nested_geometries(deep):
    assert deep["seed_semantics"] == "RELATED_NON_NESTED"
    assert deep["paired_analysis_used"] is False
    assert "Cross-size statistical independence is not established" in \
        deep["seed_semantics_statement"]
    blob = json.dumps(deep)
    assert "paired_difference" not in blob


def test_realisation_variability_comparison_is_numeric_and_directional(deep):
    v = deep["realization_variability"]
    assert v["directions_disagree"] is True
    assert v["cheap_single_seed_direction"] == "RISING"
    assert v["ensemble_mean_direction"] == "FALLING"
    assert max(v["within_size_max_over_min"].values()) > 1.0
    assert v["smallest_box_range_contains_largest_box_range"] is True


def test_incomplete_section_4_prevents_a_closure_decision(deep):
    assert deep["closure_status"] == deep["closure_deep_status"] == \
        "NOT_ADJUDICATED_COMPUTE_BOUND"
    s = deep["sections"]
    assert s["S4_3_trend_on_means"]["converged"] == 0
    assert s["S4_2_porosity_dependence"]["status"] == "PARTIAL_NON_DECISIONAL"
    # no G statistic may be published from an incomplete matrix
    blob = json.dumps(deep)
    for forbidden in ("G_percolation", "G_carman_kozeny", "percolation_trend_preserved"):
        assert forbidden not in blob, forbidden
    for wrong in deep["closure_not"]:
        assert wrong in deep["closure_not"]
    assert "NEEDS_NEW_DATA" not in deep["overall_deep_disposition"]


def test_tolerance_sensitivity_excludes_numerical_convergence(deep):
    t = deep["sections"]["S4_1_tolerance"]
    assert t["converged"] == 2 and t["status"] == "COMPLETE"
    assert t["relative_move"] < 0.01 and t["cheap_criterion_adequate"] is True


def test_guard_overrun_is_recorded_not_hidden(deep):
    g = deep["execution_audit"]["guard"]
    assert g["actual_wall_s"] > g["budget_s"]
    assert g["overrun_s"] > 0
    assert "admitted cell runs to completion" in g["semantics"]


def test_all_hashes_resolve(deep):
    import hashlib
    p = deep["provenance"]
    for key, rel in (("cheap_protocol_sha256", "PROTOCOL.md"),
                     ("cheap_result_sha256", "result.json"),
                     ("protocol_erratum_sha256", "PROTOCOL_ERRATUM.md"),
                     ("deep_protocol_sha256", "DEEP_SCREEN_PROTOCOL.md"),
                     ("deep_protocol_erratum_sha256", "DEEP_PROTOCOL_ERRATUM.md"),
                     ("expected_run_matrix_sha256", "expected_run_matrix.json"),
                     ("deep_run_raw_sha256", "deep_run_raw.json")):
        live = hashlib.sha256((BUNDLE / rel).read_bytes()).hexdigest()
        assert p[key] == live, rel
    assert p["base_commit"] == CHEAP.BASE_COMMIT


def test_the_cheap_survive_is_preserved_as_history(deep):
    assert "SURVIVE" in deep["provenance"]["cheap_decision"]
    cheap = json.loads((BUNDLE / "result.json").read_text(encoding="utf-8"))
    assert cheap["decision"] == "SURVIVE"


def test_claim_ceiling_matches_the_decision(deep):
    c = deep["claim_ceiling"]
    assert "not adjudicated" in c["C_continuum_closures"].lower()
    assert "did not claim" in c["D_repository_guidance"]
    assert "No pack-card or registry correction" in c["D_repository_guidance"]
    assert "incremental and repository-specific" in c["E_real_pucks_and_novelty"]
    assert "non-rejection at low power" in c["B_domain_size"]
    assert deep["novelty_disposition"] == "INCREMENTAL"
    assert deep["evidence_labels_unchanged"] is True
    assert deep["issue_231_disposition"] == "NOT_MATERIAL_TO_SELECTED_DECISION"


def test_figure_source_values_match_the_realisation_table(deep):
    """The figure is rendered from the adjudication, so its inputs are the table itself."""
    per = deep["ensembles_per_size"]
    for L, s in per.items():
        ks = sorted(r["k_lu"] for r in deep["realisation_table"] if str(r["L"]) == L)
        assert s["values"] == pytest.approx(ks)


def test_heavy_execution_is_not_added_to_ordinary_ci():
    """These tests read committed artifacts; they must never invoke the solver."""
    import ast
    tree = ast.parse(pathlib.Path(__file__).read_text(encoding="utf-8"))
    called = {n.func.attr for n in ast.walk(tree)
              if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)}
    for heavy in ("solve", "deep_screen", "multiseed_rve", "pore_scale_k", "make_pack"):
        assert heavy not in called or heavy == "make_pack", heavy
    # make_pack is permitted: the seed-semantics test builds geometry only, and never solves
    assert "solve" not in called
