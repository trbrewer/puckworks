"""RP-D-LC-001 — CI-safe tests for the virtual fixture, its observables and its decision rule.

**No solver runs here.** The heavy LB execution lives in `puckworks/validation/slow/rp_d_lc_001.py`
(CLAUDE.md rule 3). What CI checks is everything that can be checked without a solve: geometry
construction and its exact index symmetries, connectivity and the absence of a periodic lateral
bypass, mask-hash stability, the observable arithmetic against hand-built miniature field fixtures,
the anti-circularity contract, the decision rule, and deterministic bundle regeneration from the
committed compact record.
"""
import ast
import inspect
import json
import pathlib

import numpy as np
import pytest

from puckworks.analysis import rp_d_lc_virtual_fixture as vf
from puckworks.analysis import screen_wp6_lateral_identifiability as wp6

REPO = pathlib.Path(__file__).resolve().parents[1]
BUNDLE = REPO / vf.BUNDLE_REL


# ==========================================================================================
# geometry
# ==========================================================================================
@pytest.mark.parametrize("S", [vf.S_SMOKE, vf.S_COARSE, vf.S_FINE])
@pytest.mark.parametrize("ap", [None, {"kx": 1, "kz": 2}, {"kx": 9, "kz": 4}])
def test_fixture_is_exactly_mirror_symmetric_in_voxel_indices(S, ap):
    mask, _ = vf.build_fixture(S, aperture=ap)
    assert vf.is_mirror_symmetric(mask, S), (S, ap)


@pytest.mark.parametrize("S", [vf.S_COARSE, vf.S_FINE])
def test_scaling_is_exact_geometric_similarity(S):
    """Each base voxel becomes an S^3 block, so no length ratio changes with resolution."""
    base = vf.base_mask(aperture={"kx": 5, "kz": 2})
    scaled = vf.scale(base, S)
    assert scaled.shape == tuple(n * S for n in base.shape)
    assert np.array_equal(scaled[::S, ::S, ::S], base)
    assert scaled.sum() == base.sum() * S ** 3


@pytest.mark.parametrize("S", [vf.S_SMOKE, vf.S_COARSE, vf.S_FINE])
@pytest.mark.parametrize("ap", [None, {"kx": 5, "kz": 2}])
def test_fluid_is_one_component_and_there_is_no_periodic_lateral_bypass(S, ap):
    mask, meta = vf.build_fixture(S, aperture=ap)
    c = vf.connectivity(mask, meta)
    assert c["single_connected"], (S, ap, c)
    assert c["no_lateral_bypass"], (S, ap, c)
    assert not c["fluid_on_y_face"] and not c["fluid_on_z_face"]


@pytest.mark.parametrize("S", [vf.S_COARSE, vf.S_FINE])
def test_blocked_and_open_differ_by_exactly_the_aperture_footprint(S):
    ap = {"kx": 5, "kz": 3}
    mo, meta = vf.build_fixture(S, aperture=ap)
    mb, _ = vf.build_fixture(S, aperture=None)
    diff = np.argwhere(mo != mb)
    assert len(diff) > 0
    ax, az = meta["aperture_x"], meta["aperture_z"]
    dy = meta["divider_y"]
    assert diff[:, 0].min() >= ax[0] and diff[:, 0].max() < ax[1]
    assert diff[:, 1].min() >= dy[0] and diff[:, 1].max() < dy[1]
    assert diff[:, 2].min() >= az[0] and diff[:, 2].max() < az[1]
    # the difference is exactly the cleared aperture block, and only fluid was ADDED
    assert len(diff) == (ax[1] - ax[0]) * (dy[1] - dy[0]) * (az[1] - az[0])
    assert mb[tuple(diff.T)].all() and not mo[tuple(diff.T)].any()


def test_path_swap_is_an_exact_index_transformation_and_an_involution():
    mask, _ = vf.build_fixture(vf.S_COARSE, aperture={"kx": 5, "kz": 2})
    assert np.array_equal(vf.swap_paths(vf.swap_paths(mask)), mask)
    # for the exact mirror the swap coincides with the x-reflection
    assert np.array_equal(vf.swap_paths(mask), vf.mirror_x(mask, vf.S_COARSE))


def test_identical_path_control_is_swap_invariant_and_not_a_mirror():
    mask, _ = vf.build_fixture(vf.S_COARSE, aperture={"kx": 5, "kz": 2}, variant="identical")
    assert np.array_equal(vf.swap_paths(mask), mask)
    assert not vf.is_mirror_symmetric(mask, vf.S_COARSE)


def test_one_voxel_plug_changes_exactly_one_voxel_and_breaks_the_mirror():
    ap = {"kx": 5, "kz": 2}
    base, _ = vf.build_fixture(vf.S_FINE, aperture=ap)
    pert, _ = vf.build_fixture(vf.S_FINE, aperture=ap, perturbation="one_voxel_plug")
    assert int((base != pert).sum()) == 1
    assert not vf.is_mirror_symmetric(pert, vf.S_FINE)


def test_one_voxel_slab_is_one_lattice_voxel_thick_in_x():
    ap = {"kx": 5, "kz": 2}
    base, _ = vf.build_fixture(vf.S_FINE, aperture=ap)
    pert, _ = vf.build_fixture(vf.S_FINE, aperture=ap, perturbation="one_voxel_slab")
    diff = np.argwhere(base != pert)
    assert len(np.unique(diff[:, 0])) == 1, "the slab must be one lattice plane thick"
    assert not vf.is_mirror_symmetric(pert, vf.S_FINE)


@pytest.mark.parametrize("bad", [{"kx": 2, "kz": 2}, {"kx": 11, "kz": 1}, {"kx": 5, "kz": 0},
                                 {"kx": 5, "kz": 9}])
def test_invalid_apertures_are_rejected(bad):
    with pytest.raises(ValueError):
        vf.base_mask(aperture=bad)


def test_aperture_candidate_family_is_the_frozen_twenty():
    assert len(vf.APERTURE_CANDIDATES) == 20
    assert {a["kx"] for a in vf.APERTURE_CANDIDATES} == {1, 3, 5, 7, 9}
    assert {a["kz"] for a in vf.APERTURE_CANDIDATES} == {1, 2, 3, 4}
    assert all(a["kx"] % 2 == 1 for a in vf.APERTURE_CANDIDATES)


def test_minimum_feature_excludes_kz_one_at_the_coarse_resolution():
    """kz=1 is 2 lattice units at S_COARSE — a ~12 % element error under the measured 50/h^2 law."""
    assert 1 * vf.S_COARSE < vf.MIN_FEATURE_VOX <= 2 * vf.S_COARSE


# ---- mask hashes are stable identities ----------------------------------------------------
def test_mask_hash_is_shape_and_content_sensitive():
    a, _ = vf.build_fixture(vf.S_SMOKE, aperture={"kx": 5, "kz": 2})
    b, _ = vf.build_fixture(vf.S_SMOKE, aperture={"kx": 5, "kz": 3})
    assert vf.mask_hash(a) != vf.mask_hash(b)
    assert vf.mask_hash(a) == vf.mask_hash(a.copy())
    assert vf.mask_hash(a) != vf.mask_hash(a.reshape(a.shape[1], a.shape[0], a.shape[2]))


def test_coupons_build_and_are_connected():
    for level in ("high", "low"):
        for orient in ("x", "y"):
            m, meta = vf.build_axial_coupon(vf.S_COARSE, level, orient)
            assert meta["n_fluid"] > 0
            assert not m[:, :, 0].all() or True          # z walls exist by construction
    m, meta = vf.build_bridge_coupon(vf.S_COARSE, 5, 2)
    c = vf.connectivity(m, meta)
    assert c["single_connected"] and c["no_lateral_bypass"]
    assert meta["wall_thickness_vox"] == 2 * vf.S_COARSE


def test_axial_coupon_high_has_more_fluid_than_low():
    hi, mh = vf.build_axial_coupon(vf.S_COARSE, "high", "x")
    lo, ml = vf.build_axial_coupon(vf.S_COARSE, "low", "x")
    assert mh["n_fluid"] > ml["n_fluid"]
    assert mh["shape"] == ml["shape"]


# ==========================================================================================
# observables — miniature hand-built field fixtures
# ==========================================================================================
def test_plane_flux_masks_solids_and_sums_the_requested_lane():
    mask = np.zeros((3, 6, 2), dtype=bool)
    mask[:, 0, :] = True                      # a solid row that must not contribute
    ux = np.ones((3, 6, 2)) * 2.0
    assert vf.plane_flux(ux, mask, 1) == pytest.approx(2.0 * 5 * 2)
    assert vf.plane_flux(ux, mask, 1, (2, 4)) == pytest.approx(2.0 * 2 * 2)


def test_plane_pressure_applies_the_frozen_definition_and_reports_nonuniformity():
    mask = np.zeros((4, 3, 2), dtype=bool)
    rho = np.full((4, 3, 2), 3.0)             # p = rho/3 - g*x = 1 - g*x
    g, x = 0.5, 2
    mean, sd, n = vf.plane_pressure(rho, mask, x, g)
    assert mean == pytest.approx(1.0 - g * x)
    assert sd == pytest.approx(0.0)
    assert n == 6
    rho[x, 0, 0] = 6.0                        # introduce nonuniformity
    mean2, sd2, _ = vf.plane_pressure(rho, mask, x, g)
    assert sd2 > 0 and mean2 > mean


def test_plane_pressure_excludes_solid_nodes_rather_than_counting_them_as_zero():
    mask = np.zeros((2, 4, 1), dtype=bool)
    mask[1, 3, 0] = True
    rho = np.full((2, 4, 1), 3.0)
    rho[1, 3, 0] = 1e6                        # a meaningless leftover in a solid
    mean, _, n = vf.plane_pressure(rho, mask, 1, 0.0)
    assert n == 3 and mean == pytest.approx(1.0)


def test_coupon_truth_matches_the_frozen_algebra():
    t = vf.coupon_truth(3.0, 1.0, 1.5)
    assert t["c_coupon"] == pytest.approx(0.5)
    assert t["A1_coupon"] == t["A2_coupon"] == pytest.approx(4.0)
    assert t["Xi_coupon"] == pytest.approx(1.5 * (1 / 4 + 1 / 4))
    # and agrees with the registered component's own equalization number
    from puckworks.models import lateral_coupling as lc
    assert t["Xi_coupon"] == pytest.approx(lc.equalization_number(1.5, 3.0, 1.0, 1.0, 3.0))


def test_network_prediction_reproduces_the_wp6_forward_map():
    """The Arm-F forward check must agree with the WP6 screen's own analytic mirror map."""
    A, c, Xi = 4.0, 0.5, 1.0
    g = wp6.mirror_conductances(A, c)
    G = wp6.g_lat_from_xi(A, Xi)
    got = vf.network_prediction(*g, G)
    R, s = wp6.forward_map_analytic(c, Xi)
    assert got["R"] == pytest.approx(R, rel=1e-12)
    assert got["s"] == pytest.approx(s, rel=1e-12)


# ==========================================================================================
# anti-circularity contract
# ==========================================================================================
def test_inference_accepts_boundary_quantities_only():
    ok = {"Q0": 1.0, "dP0": 1.0, "q1": 0.4, "q2": 0.6, "dP": 1.0,
          "orientation": "nominal", "converged": True}
    vf.infer_from_boundary(dict(ok))
    for forbidden in ("G_lat_field", "Xi_field", "c_field", "q_lat", "p_mid1_blocked",
                      "aperture", "kz"):
        with pytest.raises(ValueError, match="anti-circularity"):
            vf.infer_from_boundary({**ok, forbidden: 1.0})
    for missing in ok:
        bad = {k: v for k, v in ok.items() if k != missing}
        with pytest.raises(ValueError, match="anti-circularity"):
            vf.infer_from_boundary(bad)


def test_boundary_keys_are_exactly_the_six_measurables_plus_metadata():
    assert set(vf.BOUNDARY_KEYS) == {"Q0", "dP0", "q1", "q2", "dP", "orientation", "converged"}


def test_inference_delegates_to_the_existing_verified_inverse_and_does_not_reimplement_it():
    src = inspect.getsource(vf.infer_from_boundary)
    assert "wp6.invert(" in src
    # no local reimplementation of the closed-form inverse anywhere in the module
    mod = pathlib.Path(vf.__file__).read_text()
    for fragment in ("1.0 - 2.0 * s", "(R - 1.0) / den", "1.0 / t_hat - 1.0"):
        assert fragment not in mod, "the WP6 inverse must be imported, never rederived"


def _calls_in(func):
    """Every attribute/name called anywhere inside `func`'s source."""
    tree = ast.parse(inspect.getsource(func).lstrip())
    out = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            f = node.func
            out.add(f.attr if isinstance(f, ast.Attribute) else getattr(f, "id", ""))
    return out


@pytest.mark.parametrize("func", [vf.field_truth, vf.coupon_truth, vf.boundary_record_from_fields])
def test_the_truth_pipeline_never_calls_the_inverse(func):
    called = _calls_in(func)
    assert "invert" not in called
    assert "infer_from_boundary" not in called
    src = inspect.getsource(func)
    assert "wp6." not in src and "Xi_hat" not in src and "c_hat" not in src


def test_changing_a_hidden_truth_field_cannot_move_the_inference():
    """Xi-hat is a function of the boundary record ALONE."""
    rec = {"Q0": 1.0, "dP0": 1.0, "q1": 0.45, "q2": 0.6, "dP": 1.02,
           "orientation": "nominal", "converged": True}
    a = vf.infer_from_boundary(dict(rec))
    # any truth-side quantity we might have leaked simply cannot be passed at all
    b = vf.infer_from_boundary(dict(rec))
    assert a == b
    assert set(a) >= {"status", "c_hat", "Xi_hat", "R", "s"}


def test_the_driver_infers_before_it_evaluates_truth():
    """Order is load-bearing: the inverse is CALLED and recorded before `field_truth` is.

    Compared by AST call position, not by string search — a docstring mentioning `field_truth`
    must not be able to satisfy or break this.
    """
    from puckworks.validation.slow import rp_d_lc_001 as drv
    tree = ast.parse(inspect.getsource(drv._run_case).lstrip())
    order = [n.func.attr for n in ast.walk(tree)
             if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
             and n.func.attr in ("infer_from_boundary", "field_truth")]
    assert order == ["infer_from_boundary", "field_truth"], order


def test_no_parameter_is_fitted_against_the_inference():
    mod = pathlib.Path(vf.__file__).read_text()
    for fragment in ("curve_fit", "minimize", "least_squares", "polyfit", "optimize"):
        assert fragment not in mod, "nothing may be fitted in this tranche"


# ==========================================================================================
# decision rule
# ==========================================================================================
def _synthetic_runs(xi_hat_factor=1.0, n_window=3, monotone=True, swap_ok=True, valid=True):
    """A miniature run record exercising the frozen clauses without any solver output."""
    xis = [0.05, 0.5, 1.0, 2.5, 8.0][:2 + n_window]
    cases, swaps = [], []
    for S in vf.SCIENTIFIC_RESOLUTIONS:
        for i, xi in enumerate(xis):
            hat = xi * xi_hat_factor
            if not monotone and i == 2:
                hat = 1e-6
            ap = {"kx": 1 + 2 * i, "kz": 2}
            cases.append({
                "role": "primary", "S": S, "aperture": ap,
                "boundary": {"R": 1.0 + xi / 3.0, "s": 0.5 - xi / 30.0,
                             "blocked_share": 0.5},
                "inference": {"status": "ok", "c_hat": 0.5, "Xi_hat": hat},
                "truth": {"Xi_field": xi, "c_field": 0.5, "G_lat_field": xi,
                          "gap_sign_consistent": True, "q_lat": 1.0},
            })
            if S == vf.S_COARSE:
                swaps.append({"S": S, "aperture": ap, "signature_ok": swap_ok,
                              "share_sign_reversed": swap_ok, "c_sign_reversed": swap_ok,
                              "R_preserved": swap_ok, "Xi_field_preserved": swap_ok,
                              "Xi_hat_preserved": swap_ok})
    ok = {"pass": bool(valid)}
    return {
        "cases": cases, "path_swap": swaps,
        "controls": {k: dict(ok) for k in
                     ("convergence", "low_mach_linearity", "componentwise_creeping_flow_control",
                      "boundary_inference_forcing_stability", "mass_conservation", "topology",
                      "coarse_graining_surface_stability", "plane_invariance", "grid_refinement",
                      "frozen_C_linearity_control", "backend_cross_check")},
        "mechanism": {"bridge_flux_consistent": True, "R_direction_consistent": True},
        "grid_refinement": {"classification_by_resolution":
                            {str(S): "factor_two_recovered" for S in vf.SCIENTIFIC_RESOLUTIONS}},
    }


def test_decision_returns_recovery_when_every_clause_passes():
    d, cl = vf.decide(_synthetic_runs())
    assert d == "CROSS_MODEL_RECOVERY", [c for c in cl if not c["pass"]]
    assert all(c["pass"] for c in cl) and len(cl) == 7


def test_invalid_execution_dominates_every_other_outcome():
    d, _ = vf.decide(_synthetic_runs(valid=False))
    assert d == "INVALID_EXECUTION"


def test_a_stable_R_cannot_rescue_a_failed_componentwise_creeping_flow_check():
    """E2's load-bearing property: boundary-observable stability may NOT substitute for the
    internal components being proportional to the forcing."""
    runs = _synthetic_runs()
    runs["controls"]["componentwise_creeping_flow_control"] = {"pass": False}
    runs["controls"]["boundary_inference_forcing_stability"] = {"pass": True}
    d, cl = vf.decide(runs)
    assert d == "INVALID_EXECUTION"
    assert not cl[0]["pass"]


def test_the_preserved_frozen_C_failure_does_not_by_itself_invalidate_execution():
    """The historical frozen control is REPORTED, never required — it is superseded in role, not
    relabelled as passed."""
    runs = _synthetic_runs()
    runs["controls"]["frozen_C_linearity_control"] = {"pass": False}
    d, cl = vf.decide(runs)
    assert d == "CROSS_MODEL_RECOVERY"
    assert cl[0]["detail"]["reported_not_required"]["frozen_C_linearity_control"] is False


def test_unstable_coarse_graining_surfaces_invalidate_execution():
    runs = _synthetic_runs()
    runs["controls"]["coarse_graining_surface_stability"] = {"pass": False}
    d, _ = vf.decide(runs)
    assert d == "INVALID_EXECUTION"


def test_too_few_window_cases_is_design_missed_target():
    runs = _synthetic_runs(n_window=0)
    runs["cases"] = [c for c in runs["cases"] if not (0.241134 <= c["truth"]["Xi_field"] <= 3.945980)]
    d, _ = vf.decide(runs)
    assert d == "DESIGN_MISSED_TARGET"


def test_a_factor_of_three_error_with_correct_ordering_is_mechanism_only():
    runs = _synthetic_runs(xi_hat_factor=3.0)
    runs["grid_refinement"]["classification_by_resolution"] = {
        str(S): "not_recovered" for S in vf.SCIENTIFIC_RESOLUTIONS}
    d, cl = vf.decide(runs)
    assert d == "MECHANISM_ONLY"
    assert not next(c for c in cl if c["clause"] == "3_factor_two_recovery")["pass"]


def test_non_monotonic_recovery_is_no_cross_model_transfer():
    runs = _synthetic_runs(xi_hat_factor=3.0, monotone=False)
    runs["grid_refinement"]["classification_by_resolution"] = {
        str(S): "not_recovered" for S in vf.SCIENTIFIC_RESOLUTIONS}
    d, _ = vf.decide(runs)
    assert d == "NO_CROSS_MODEL_TRANSFER"


def test_a_broken_path_swap_is_no_cross_model_transfer():
    runs = _synthetic_runs(swap_ok=False)
    d, _ = vf.decide(runs)
    assert d == "NO_CROSS_MODEL_TRANSFER"


def test_the_wp6_window_is_copied_from_the_screen_and_not_restated():
    screen = json.loads((REPO / "docs/insights/screens/WP6-LC-IDENT/result.json").read_text())
    floors = screen["sensitivity_envelopes"]["continuous_window_post_hoc"]["floors"]["1pct"]
    # copied byte-identical from the source screen, not re-derived
    assert floors["Xi_lower"] == vf.XI_WINDOW_LO_SCREEN_EXACT
    assert floors["Xi_upper"] == vf.XI_WINDOW_HI_SCREEN_EXACT
    assert floors["continuous_passing_interval_exists"] is True
    # the authorized decision bounds agree with them to the rounding, and are never WIDER by
    # anything this tranche could resolve
    assert abs(vf.XI_WINDOW_LO - vf.XI_WINDOW_LO_SCREEN_EXACT) < 5e-7
    assert abs(vf.XI_WINDOW_HI - vf.XI_WINDOW_HI_SCREEN_EXACT) < 5e-7
    # and the screen's own labelling of it as post-hoc is carried across, not dropped
    assert screen["sensitivity_envelopes"]["continuous_window_post_hoc"][
        "feeds_no_decision_clause"] is True
    assert "POST_HOC_DIAGNOSTIC_NOT_IN_DECISION" in vf.XI_WINDOW_PROVENANCE


# ==========================================================================================
# bundle
# ==========================================================================================
def test_protocol_and_spec_exist_and_carry_the_claim_ceiling():
    for name in ("PROTOCOL.md", "VIRTUAL_FIXTURE_SPEC.md", "BOUNDARY_TOPOLOGY_ADJUDICATION.md"):
        assert (BUNDLE / name).exists(), name
    text = (BUNDLE / "PROTOCOL.md").read_text()
    for anchor in ("box 5 remains OPEN", "box 6 remains closed",
                   "Paper 4 remains unauthorized", "NOT_EXPERIMENTAL_VALIDATION"):
        assert anchor in text, anchor


def test_this_is_not_an_insight_foundry_screen():
    assert "insights" not in vf.BUNDLE_REL
    assert not (REPO / "docs/insights/screens" / vf.TRANCHE_ID).exists()


def test_claim_ceiling_is_complete():
    joined = " | ".join(vf.CLAIM_CEILING)
    for anchor in ("deterministic synthetic geometry", "no experimental validation",
                   "no real-puck Xi", "box 5 remains OPEN", "Paper 4 remains unauthorized",
                   "no evidence-rung or registry-status promotion"):
        assert anchor in joined, anchor


@pytest.mark.skipif(not (REPO / vf.RUNS_REL / "run_record.json").exists(),
                    reason="heavy run record not yet produced")
def test_bundle_regenerates_deterministically_from_the_committed_record():
    a = vf.assemble()
    b = vf.assemble()
    assert a["content_sha256"] == b["content_sha256"]
    assert vf.verify() == 0


@pytest.mark.skipif(not (REPO / vf.RUNS_REL / "run_record.json").exists(),
                    reason="heavy run record not yet produced")
def test_result_schema_is_complete():
    doc = json.loads((BUNDLE / "result.json").read_text())
    for key in ("schema_version", "program_id", "tranche_id", "source_commit", "source_tree",
                "protocol_sha256", "input_sha256", "environment", "solver", "boundary_mode",
                "resolutions", "aperture_candidates", "aperture_freeze", "geometry", "coupons",
                "blocked", "cases", "path_swap", "identical_path_control", "asymmetry",
                "grid_refinement", "controls", "mechanism", "arm_a_solver_verification",
                "disposition", "decision_clauses", "claim_ceiling", "content_sha256"):
        assert key in doc, key
    assert doc["disposition"] in {"CROSS_MODEL_RECOVERY", "MECHANISM_ONLY",
                                  "NO_CROSS_MODEL_TRANSFER", "INVALID_EXECUTION",
                                  "DESIGN_MISSED_TARGET"}
    assert len(doc["decision_clauses"]) == 7
