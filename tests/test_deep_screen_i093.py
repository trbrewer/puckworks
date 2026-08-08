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
