"""RP-D-LC-001b preflight tests.

Every test here is geometry, configuration, serialisation, hashing or decision-contract. NONE
runs a lattice-Boltzmann solve, and one of them proves that none can: the driver's single solver
call site refuses while the tranche is pre-execution.
"""

import ast
import hashlib
import inspect
import json
import math
import pathlib
import subprocess

import numpy as np
import pytest

from puckworks.analysis import rp_d_lc_001b_virtual_fixture as vf
from puckworks.analysis import rp_d_lc_virtual_fixture as vf001
from puckworks.validation.slow import rp_d_lc_001b as drv

REPO = pathlib.Path(__file__).resolve().parents[1]


def _git(*args):
    try:
        return subprocess.run(["git", *args], cwd=REPO, capture_output=True, text=True,
                              check=True).stdout.strip()
    except Exception:
        return None


# ==========================================================================================
# 1. Starting authority and the immutability of the closed predecessor
# ==========================================================================================

def test_base_authority_is_the_exact_frozen_commit_and_tree():
    assert vf.BASE_COMMIT == "7d656811e6bf99d447dcd4f6eac04cac233a99f4"
    assert vf.BASE_TREE == "e31dc057a3e4d933ca71888b39e8b4d27ee6970d"
    assert len(vf.BASE_COMMIT) == 40 and len(vf.BASE_TREE) == 40
    assert all(c in "0123456789abcdef" for c in vf.BASE_COMMIT + vf.BASE_TREE)


def test_the_recorded_base_commit_really_carries_the_recorded_tree():
    tree = _git("rev-parse", "%s^{tree}" % vf.BASE_COMMIT)
    if not tree:
        pytest.skip("shallow checkout: the base commit object is not observable here")
    assert tree == vf.BASE_TREE


def test_the_closed_001_bundle_is_untouched_by_this_tranche():
    """RP-D-LC-001's failure is part of the durable scientific record. 001b re-executes the
    question; it never edits that bundle."""
    if _git("rev-parse", "%s^{tree}" % vf.BASE_COMMIT) is None:
        pytest.skip("shallow checkout: cannot diff against the base commit here")
    diff = _git("diff", "--stat", vf.BASE_COMMIT, "--", "docs/analysis/rp_d_lc_001")
    assert diff == "", "the closed 001 bundle changed:\n%s" % diff


def test_001_scientific_constants_are_not_restated_or_moved():
    assert vf001.G_PRIMARY == 2.0e-5                    # the forcing 001b reduces from
    assert vf.PREDECESSOR["disposition"] == "INVALID_EXECUTION"
    assert vf.PREDECESSOR["cross_model_transfer_adjudicated"] is False
    assert vf.PREDECESSOR["axial_artifact_at_zero_lateral_driver"] == 0.014277334586
    # the claim ceiling is COPIED, never renegotiated by a re-execution
    assert vf.CLAIM_CEILING == tuple(vf001.CLAIM_CEILING)
    assert "lateral_coupling_feasibility card box 5 remains OPEN" in vf.CLAIM_CEILING
    assert "Paper 4 remains unauthorized" in vf.CLAIM_CEILING


# ==========================================================================================
# 2. Forcing law, ladders and dynamic similarity
# ==========================================================================================

def test_forcing_law_is_g_proportional_to_S_cubed_inverse():
    for S in (1, 2, 3, 4, 6):
        assert vf.forcing_central(S) == pytest.approx(
            vf.G_REF * (vf.S_REF / S) ** 3, rel=1e-15)
    # exact ratio between the two scientific resolutions
    assert (vf.forcing_central(2) / vf.forcing_central(3)) == pytest.approx(27 / 8, rel=1e-15)


def test_the_exact_frozen_central_forcings():
    assert vf.forcing_central(2) == 2.0e-6
    assert vf.forcing_central(3) == 5.925925925925926e-7


def test_the_exact_per_resolution_forcing_ladders():
    assert vf.forcing_ladder(2) == {"low": 1.0e-6, "central": 2.0e-6, "high": 4.0e-6}
    assert vf.forcing_ladder(3) == {"low": 2.962962962962963e-7,
                                    "central": 5.925925925925926e-7,
                                    "high": 1.1851851851851852e-6}


def test_each_resolution_gets_its_own_ladder_around_its_own_central_forcing():
    for S in vf.SCIENTIFIC_RESOLUTIONS:
        lad = vf.forcing_ladder(S)
        assert lad["central"] == vf.forcing_central(S)
        assert lad["low"] == pytest.approx(lad["central"] / 2, rel=1e-15)
        assert lad["high"] == pytest.approx(lad["central"] * 2, rel=1e-15)


def test_the_design_reynolds_number_is_identical_at_both_resolutions():
    """This is what 001 did NOT hold (erratum E5): at fixed lattice g and nu,
    Re(S=3)/Re(S=2) = (3/2)^3 = 3.375, so the two resolutions were different dimensionless
    problems. Under the frozen law they are the same one."""
    a, b = (vf.design_reynolds(S) for S in vf.SCIENTIFIC_RESOLUTIONS)
    assert a == b
    # and the 001 configuration demonstrably does not have that property
    old = [vf001.G_PRIMARY * (vf.SIMILARITY_LENGTH_BASE * S) ** 3 / vf.NU ** 2
           for S in vf.SCIENTIFIC_RESOLUTIONS]
    assert old[1] / old[0] == pytest.approx(3.375, rel=1e-12)


def test_the_reduction_against_001_is_between_eight_and_ten_fold_at_the_reference_resolution():
    cfg = vf.protocol_config()["forcing"]["reduction_vs_001"]
    assert 8.0 <= cfg["S2"] <= 10.0 + 1e-9
    assert cfg["S2"] == pytest.approx(10.0, rel=1e-12)
    assert cfg["S3"] == pytest.approx(33.75, rel=1e-12)


def test_nu_matches_the_actual_solver_implementation():
    from puckworks.models.brewer2026 import lb_reference
    src = inspect.getsource(lb_reference.solve)
    assert "nu = (tau_plus - 0.5) / 3.0" in src
    assert vf.NU == (vf.TAU_PLUS - 0.5) / 3.0 == 0.5


def test_the_mach_scale_is_reported_as_a_diagnostic_and_is_not_held_invariant():
    a, b = (vf.design_mach_scale(S) for S in vf.SCIENTIFIC_RESOLUTIONS)
    assert a != b and b < a          # falls as 1/S; low Mach is not a similarity parameter


# ==========================================================================================
# 3. Geometry — the corrected lateral-only bridge
# ==========================================================================================

SCI = vf.SCIENTIFIC_BRIDGE_CANDIDATES
PROBE = ({"w": 3, "kz": 2}, {"w": 5, "kz": 3}, {"w": 9, "kz": 4})


@pytest.mark.parametrize("S", [vf.S_SMOKE, vf.S_COARSE, vf.S_FINE])
@pytest.mark.parametrize("b", PROBE)
@pytest.mark.parametrize("connected", [False, True])
def test_fixture_is_exactly_mirror_symmetric_in_voxel_indices(S, b, connected):
    mask, _ = vf.build_fixture(S, bridge=b, connected=connected)
    assert vf.is_mirror_symmetric(mask, S)


@pytest.mark.parametrize("S", [vf.S_COARSE, vf.S_FINE])
def test_path_swap_is_an_exact_index_transformation_and_an_involution(S):
    mask, _ = vf.build_fixture(S, bridge={"w": 5, "kz": 3}, connected=True)
    assert np.array_equal(vf.swap_paths(vf.swap_paths(mask)), mask)
    # the y layout is palindromic, so the swap is exact rather than an approximate rebuild
    assert np.array_equal(vf.swap_paths(mask), np.flip(mask, axis=1))
    b = vf.BASE
    assert (b["lane1_hi"] - b["lane1_lo"]) == (b["lane2_hi"] - b["lane2_lo"])
    assert (b["portA_hi"] - b["portA_lo"]) == (b["portB_hi"] - b["portB_lo"])
    assert b["ny"] - 1 - b["portA_lo"] == b["portB_hi"]
    assert b["ny"] - 1 - b["duct_lo"] == b["duct_hi"]


@pytest.mark.parametrize("S", [vf.S_COARSE, vf.S_FINE])
def test_scaling_is_exact_geometric_similarity(S):
    base = vf.base_mask(bridge={"w": 5, "kz": 3}, connected=True)
    mask, _ = vf.build_fixture(S, bridge={"w": 5, "kz": 3}, connected=True)
    assert mask.shape == tuple(np.array(base.shape) * S)
    assert int(mask.sum()) == int(base.sum()) * S ** 3


@pytest.mark.parametrize("S", [vf.S_SMOKE, vf.S_COARSE, vf.S_FINE])
@pytest.mark.parametrize("b", PROBE)
def test_axial_end_caps_are_solid_on_both_faces(S, b):
    for connected in (False, True):
        mask, meta = vf.build_fixture(S, bridge=b, connected=connected)
        topo = vf.bridge_topology(mask, meta)
        assert topo["axial_end_caps_solid"], (S, b, connected)
        assert topo["bridge_x_span"] == topo["bridge_x_expected"]


@pytest.mark.parametrize("S", [vf.S_COARSE, vf.S_FINE])
@pytest.mark.parametrize("b", PROBE)
def test_no_axial_through_route_is_confined_to_the_bridge(S, b):
    """The bridge occupies a bounded x interval whose neighbours are fully solid across the
    whole divider cross-section, so no route through it connects two different x stations."""
    mask, meta = vf.build_fixture(S, bridge=b, connected=True)
    bxlo, bxhi = meta["bridge_x"]
    dlo, dhi = meta["divider_y"]
    assert mask[bxlo - 1, dlo:dhi, :].all()
    assert mask[bxhi, dlo:dhi, :].all()
    lxlo, lxhi = meta["lane_x"]
    band = mask[lxlo:lxhi, dlo:dhi, :]
    xs = np.unique(np.argwhere(~band)[:, 0]) + lxlo
    assert int(xs.min()) == bxlo and int(xs.max()) == bxhi - 1


@pytest.mark.parametrize("S", [vf.S_SMOKE, vf.S_COARSE, vf.S_FINE])
@pytest.mark.parametrize("b", PROBE)
def test_there_is_no_periodic_lateral_bypass_and_one_connected_fluid_domain(S, b):
    for connected in (False, True):
        mask, meta = vf.build_fixture(S, bridge=b, connected=connected)
        c = vf.connectivity(mask, meta)
        assert c["no_lateral_bypass"] and not c["fluid_on_y_face"] and not c["fluid_on_z_face"]
        assert c["single_connected"]


@pytest.mark.parametrize("S", [vf.S_COARSE, vf.S_FINE])
@pytest.mark.parametrize("b", PROBE)
def test_the_intended_lateral_connection_exists_only_in_the_open_fixture(S, b):
    """Global connectivity cannot answer this — the common plenum joins the lanes at both ends
    by design — so it is decided inside the lane region, with the plenum excluded."""
    opn, m_o = vf.build_fixture(S, bridge=b, connected=True)
    blk, m_b = vf.build_fixture(S, bridge=b, connected=False)
    ref, m_r = vf.build_fixture(S, bridge=None)
    assert vf.lane_connection(opn, m_o)["lanes_joined_in_lane_region"] is True
    assert vf.lane_connection(blk, m_b)["lanes_joined_in_lane_region"] is False
    assert vf.lane_connection(ref, m_r)["lanes_joined_in_lane_region"] is False


@pytest.mark.parametrize("S", [vf.S_SMOKE, vf.S_COARSE, vf.S_FINE])
@pytest.mark.parametrize("b", SCI)
def test_blocked_and_open_differ_by_exactly_the_duct_footprint(S, b):
    """The whole point of the corrected apparatus: the lane-facing ports are present in BOTH
    fixtures, so R compares the same axial network with the lateral connection off and on."""
    d = vf.blocked_open_delta(S, b)
    assert d["is_exactly_the_duct_footprint"], (S, b, d)
    assert d["solid_in_blocked_fluid_in_open"]
    expected = (b["w"] * S) * ((vf.BASE["duct_hi"] - vf.BASE["duct_lo"] + 1) * S) * (b["kz"] * S)
    assert d["n_differing_voxels"] == expected


@pytest.mark.parametrize("S", [vf.S_COARSE, vf.S_FINE])
@pytest.mark.parametrize("b", PROBE)
def test_the_ports_are_common_mode_between_blocked_and_open(S, b):
    """A regression guard on the remedy for 001's defect D2: if a future edit made the ports
    open-only, the blocked/open delta would stop being the duct alone."""
    blk, meta = vf.build_fixture(S, bridge=b, connected=False)
    topo = vf.bridge_topology(blk, meta)
    assert topo["ports_present"] and not topo["duct_present"]
    opn, meta_o = vf.build_fixture(S, bridge=b, connected=True)
    topo_o = vf.bridge_topology(opn, meta_o)
    assert topo_o["ports_present"] and topo_o["duct_present"]


@pytest.mark.parametrize("b", SCI)
def test_every_critical_feature_clears_the_minimum_resolution_at_the_coarse_resolution(b):
    rep = vf.minimum_feature_report(vf.S_COARSE, b)
    assert rep["all_resolved"], rep["under_resolved"]


def test_kz_one_is_a_declared_candidate_but_excluded_from_the_scientific_subset():
    assert any(c["kz"] == 1 for c in vf.BRIDGE_CANDIDATES)
    assert all(c["kz"] >= 2 for c in vf.SCIENTIFIC_BRIDGE_CANDIDATES)
    assert not vf.minimum_feature_report(vf.S_COARSE, {"w": 3, "kz": 1})["all_resolved"]


def test_candidate_family_is_deterministic_and_frozen():
    assert vf.BRIDGE_CANDIDATES == tuple(
        {"w": w, "kz": kz} for w in (3, 5, 7, 9) for kz in (1, 2, 3, 4))
    assert len(vf.BRIDGE_CANDIDATES) == 16 and len(SCI) == 12
    # the family is an ordered tuple, so a selection over it cannot depend on set iteration order
    assert [(c["w"], c["kz"]) for c in SCI] == sorted((c["w"], c["kz"]) for c in SCI)
    assert all(c["w"] % 2 == 1 for c in vf.BRIDGE_CANDIDATES)


@pytest.mark.parametrize("bad", [{"w": 2, "kz": 2}, {"w": 11, "kz": 2}, {"w": 5, "kz": 0},
                                 {"w": 5, "kz": 5}])
def test_invalid_bridges_are_rejected(bad):
    with pytest.raises(ValueError):
        vf.base_mask(bridge=bad)


def test_connected_without_a_bridge_is_rejected():
    with pytest.raises(ValueError):
        vf.base_mask(bridge=None, connected=True)


def test_identical_path_control_is_swap_invariant_and_not_a_mirror():
    mask, _ = vf.build_fixture(vf.S_COARSE, bridge={"w": 5, "kz": 3}, connected=True,
                               variant="identical")
    assert np.array_equal(vf.swap_paths(mask), mask)


def test_mask_hash_is_shape_and_content_sensitive():
    a, _ = vf.build_fixture(vf.S_COARSE, bridge={"w": 3, "kz": 2}, connected=True)
    b, _ = vf.build_fixture(vf.S_COARSE, bridge={"w": 3, "kz": 2}, connected=False)
    assert vf.mask_hash(a) != vf.mask_hash(b)
    assert vf.mask_hash(a) == vf.mask_hash(a.copy())


def test_the_bridge_geometry_actually_differs_from_the_closed_001_aperture():
    """001's divider was 2 base voxels thick and its aperture pierced it in one step, so the
    pocket was open to both lanes along its whole length. 001b's divider is a three-layer
    structure and the lane-facing ports are separated from the connecting duct."""
    assert vf001.BASE["ny"] == 20 and vf.BASE["ny"] == 24
    assert (vf001.BASE["div_hi"] - vf001.BASE["div_lo"] + 1) == 2
    assert (vf.BASE["portB_hi"] - vf.BASE["portA_lo"] + 1) == 6


# ==========================================================================================
# 4. Measurement planes and the volume-vs-mass-flux record contract
# ==========================================================================================

def test_every_required_measurement_plane_is_defined_and_ordered():
    for S in vf.SCIENTIFIC_RESOLUTIONS:
        _, meta = vf.build_fixture(S, bridge={"w": 5, "kz": 3}, connected=True)
        for k in ("x_node_in", "x_node_out", "x_meas_a", "x_meas_b", "x_meas_in",
                  "y_face1", "y_face2", "y_portA_in", "y_duct_a", "y_duct_b", "y_portB_out"):
            assert isinstance(meta[k], (int, np.integer)), k
        assert meta["x_node_in"] < meta["x_meas_in"] < meta["x_meas_b"] < meta["x_meas_a"] \
            < meta["x_node_out"]
        assert meta["y_face1"] < meta["y_portA_in"] < meta["y_duct_a"] <= meta["y_duct_b"] \
            < meta["y_portB_out"] < meta["y_face2"]
        assert len(meta["axial_conservation_planes"]) == len(vf.AXIAL_CONSERVATION_BASE) + 1
        assert meta["node_offsets"] == (1, 2)


def test_the_transverse_planes_lie_inside_the_bridge_they_instrument():
    S, b = vf.S_COARSE, {"w": 5, "kz": 3}
    mask, meta = vf.build_fixture(S, bridge=b, connected=True)
    xs, xe = meta["bridge_x"]
    zs, ze = meta["bridge_z"]
    for k in ("y_portA_in", "y_duct_a", "y_duct_b", "y_portB_out"):
        assert (~mask[xs:xe, meta[k], zs:ze]).all(), k


def test_volume_and_mass_flux_are_distinct_retained_fields_and_are_never_conflated():
    assert "sum_ux" in vf.AXIAL_PLANE_FIELDS and "sum_rho_ux" in vf.AXIAL_PLANE_FIELDS
    assert "sum_uy" in vf.TRANSVERSE_PLANE_FIELDS and "sum_rho_uy" in vf.TRANSVERSE_PLANE_FIELDS
    assert vf.QUANTITY_ROLES["sum_rho_ux"] == "adjudicative_conservation"
    assert vf.QUANTITY_ROLES["sum_ux"] == "diagnostic_and_inverse_input"
    cfg = vf.protocol_config()["observables"]
    assert cfg["inverse_consumes"] == "PRESSURE_NORMALISED_VOLUME_FLUX"
    assert cfg["conservation_evaluated_on"] == "DENSITY_WEIGHTED_MASS_FLUX sum(rho*u_x)"


def _synthetic(S=vf.S_SMOKE, b=None, rho_ramp=0.0, unit_plane_flux=False, uy_amp=0.25,
               uz_amp=0.0, connected=True, variant="mirror"):
    """A deterministic synthetic field. ``unit_plane_flux`` scales each x plane so that the
    VOLUME flux through every plane is exactly 1 — a divergence-free-by-construction field, which
    is what makes the density-ramp test a clean statement about mass versus volume flux."""
    b = b or {"w": 3, "kz": 2}
    mask, meta = vf.build_fixture(S, bridge=b, connected=connected, variant=variant)
    nx, ny, nz = mask.shape
    ux = np.zeros(mask.shape)
    ux[~mask] = 1.0
    if unit_plane_flux:
        for x in range(nx):
            n = int((~mask[x]).sum())
            if n:
                ux[x][~mask[x]] = 1.0 / n
    uy = np.zeros(mask.shape)
    uy[~mask] = uy_amp
    uz = np.zeros(mask.shape)
    uz[~mask] = uz_amp
    rho = np.ones(mask.shape) + rho_ramp * np.arange(nx)[:, None, None]
    return mask, meta, {"ux": ux, "uy": uy, "uz": uz, "rho": rho, "steps": 3000}


def test_the_plane_record_retains_raw_sums_and_the_area_count_not_a_normalised_number():
    mask, meta, res = _synthetic()
    r = vf.axial_plane_record("x_meas_a", meta["x_meas_a"], res["ux"], res["rho"], mask, 1e-6)
    assert set(r) == set(vf.AXIAL_PLANE_FIELDS)
    assert r["orientation"] == "x"
    assert r["sum_ux"] == pytest.approx(float(r["n_fluid"]))       # unit velocity, unit density
    assert r["sum_rho_ux"] == pytest.approx(float(r["n_fluid"]))
    assert r["n_fluid"] > 0


def test_solid_nodes_are_excluded_from_a_plane_record_never_counted_as_zero():
    mask, meta, res = _synthetic()
    x = meta["x_meas_a"]
    r = vf.axial_plane_record("x_meas_a", x, res["ux"], res["rho"], mask, 1e-6)
    assert r["n_fluid"] == int((~mask[x]).sum()) < mask[x].size


def test_the_mass_flux_residual_sees_a_density_gradient_the_volume_proxy_cannot():
    """The 001 failure mode in miniature: a uniform velocity field with a density ramp conserves
    VOLUME flux exactly while the mass flux varies. A control written on sum(u) alone cannot see
    it — which is why the two are recorded separately and only the mass form adjudicates."""
    mask, meta, res = _synthetic(rho_ramp=1e-3, unit_plane_flux=True)
    recs = [vf.axial_plane_record("cons_%d" % i, x, res["ux"], res["rho"], mask, 1e-6)
            for i, x in enumerate(meta["axial_conservation_planes"])]
    c = vf.conservation_residuals(recs)
    assert c["volume_flux_residual"] == pytest.approx(0.0, abs=1e-12)
    assert c["mass_flux_residual"] > 1e-3
    assert c["mass_conservation_pass"] is False
    assert c["volume_flux_uniformity_pass"] is True
    assert c["mass_flux_residual_role"] == "adjudicative"
    assert c["volume_flux_residual_role"] == "diagnostic"


def test_transverse_records_carry_the_sign_convention_and_the_footprint():
    mask, meta, res = _synthetic()
    r = vf.transverse_plane_record("y_duct_a", meta["y_duct_a"], res["uy"], res["rho"], mask,
                                   meta["bridge_x"], meta["bridge_z"])
    assert set(r) == set(vf.TRANSVERSE_PLANE_FIELDS)
    assert r["sign_convention"] == vf.SIGN_CONVENTION_TRANSVERSE
    assert r["footprint_x"] == tuple(int(v) for v in meta["bridge_x"])
    assert r["sum_uy"] > 0 and r["sum_rho_uy"] > 0


# ==========================================================================================
# 5. Anti-circularity: the boundary allowlist
# ==========================================================================================

def test_boundary_keys_are_the_frozen_six_plus_metadata_and_are_imported_not_recopied():
    assert vf.BOUNDARY_KEYS == tuple(vf001.BOUNDARY_KEYS)
    assert set(vf.BOUNDARY_KEYS) == {"Q0", "dP0", "q1", "q2", "dP", "orientation", "converged"}
    assert vf.infer_from_boundary is vf001.infer_from_boundary


def _ok_record():
    return {"Q0": 1.0, "dP0": 0.1, "q1": 0.55, "q2": 0.5, "dP": 0.1,
            "orientation": "nominal", "converged": True}


@pytest.mark.parametrize("extra", list(vf.FORBIDDEN_BOUNDARY_KEYS))
def test_an_undeclared_key_is_rejected_rather_than_ignored(extra):
    rec = _ok_record()
    rec[extra] = 1.0
    with pytest.raises(ValueError):
        vf.assert_boundary_record(rec)
    with pytest.raises(ValueError):
        vf.infer_from_boundary(rec)


def test_a_missing_declared_key_is_rejected_too():
    rec = _ok_record()
    rec.pop("dP0")
    with pytest.raises(ValueError):
        vf.assert_boundary_record(rec)


def test_the_driver_builds_a_boundary_record_that_carries_no_truth_side_quantity():
    mask, meta, res = _synthetic()
    opn = drv.case_record(res, mask, meta, 1e-6, stage="unit")
    blk_mask, blk_meta, blk_res = _synthetic(connected=False, uy_amp=0.0)
    blk = drv.case_record(blk_res, blk_mask, blk_meta, 1e-6, stage="unit")
    rec = drv.boundary_record(opn, blk)
    assert tuple(sorted(rec)) == tuple(sorted(vf.BOUNDARY_KEYS))
    for k in vf.FORBIDDEN_BOUNDARY_KEYS:
        assert k not in rec


def test_the_case_record_keeps_the_inverse_input_labelled_as_volume_flux():
    mask, meta, res = _synthetic()
    rec = drv.case_record(res, mask, meta, 1e-6, stage="unit")
    assert "Q_volume" in rec and "q1_volume" in rec and "q2_volume" in rec
    assert "Q_mass_diagnostic" in rec
    assert rec["conservation"]["mass_flux_residual_role"] == "adjudicative"
    assert rec["transverse_planes"] and len(rec["transverse_planes"]) == 4


# ==========================================================================================
# 6. Negative-control artifact budget and reachable-set admission
# ==========================================================================================

def test_the_artifact_budget_is_the_repository_nuisance_scale_not_a_new_number():
    assert vf.ARTIFACT_BUDGET_R_ABS == vf001.TOL_RETURN_PATH_R_REL == 1.0e-3
    # erratum PE-6: the borrowed constant is GONE; R uncertainty has its own frozen method
    assert not hasattr(vf, "NUMERICAL_UNCERTAINTY_R_ABS")
    assert vf.NUMERICAL_DISCREPANCY_SAFETY_FACTOR == 2.0


def test_the_001_artifact_would_have_failed_the_budget_by_more_than_an_order_of_magnitude():
    m = vf.artifact_metrics(C_open=1.0143, C_blocked=1.0,
                            R_identical=1.0 + vf.PREDECESSOR[
                                "axial_artifact_at_zero_lateral_driver"],
                            numerical_uncertainty=0.0)
    assert m["within_budget"] is False
    assert m["pressure_normalised_R_change"] / vf.ARTIFACT_BUDGET_R_ABS > 14


def test_artifact_metrics_report_every_required_form_and_name_the_adjudicative_one():
    m = vf.artifact_metrics(C_open=25.5, C_blocked=25.4, R_identical=1.0004,
                            R_identical_mass=1.0005, numerical_uncertainty=1e-4)
    assert m["adjudicative_metric"] == (
        "abs(pressure_normalised_R_change) + numerical_uncertainty_R_abs")
    assert m["signed_conductance_change"] == pytest.approx(0.1)
    assert m["absolute_conductance_change"] == pytest.approx(0.1)
    assert m["relative_conductance_change"] == pytest.approx(0.1 / 25.4)
    assert m["mass_flux_R_change"] == pytest.approx(5e-4)
    assert m["artifact_upper_bound"] == pytest.approx(4e-4 + 1e-4)
    assert m["within_budget"] is True


def test_the_reachable_ceiling_matches_the_screen_forward_map_exactly():
    """R - 1 = [c^2/(1-c^2)][Xi/(1+Xi)] (WP6-LC-IDENT DECISIVE_EXPERIMENT.md §7); the ceiling is
    its Xi -> infinity limit."""
    for c in (0.1, 0.3218, 0.5, 0.8):
        K = vf.reachable_ceiling(c)
        assert K == pytest.approx(c * c / (1 - c * c), rel=1e-15)
        assert vf.predicted_R_minus_1(c, 1e12) == pytest.approx(K, rel=1e-10)
        assert vf.predicted_R_minus_1(c, 0.0) == 0.0
        # and it agrees with the VERIFIED inverse: the (R, s) the map produces must invert back
        # to the same Xi, so the gate's arithmetic and the inverse's are the same mathematics
        for Xi in (0.3, 1.0, 3.5):
            R = 1.0 + vf.predicted_R_minus_1(c, Xi)
            s = 0.5 * (1.0 - (R - 1.0) / (c * R))      # the c_hat relation, solved for s
            got = vf001.wp6.invert(R, s)
            assert got["status"] == "ok", (c, Xi, got)
            assert got["c_hat"] == pytest.approx(c, rel=1e-9)
            assert got["Xi_hat"] == pytest.approx(Xi, rel=1e-9)


def test_the_001_largest_aperture_observation_is_outside_the_reachable_set():
    assert 0.1338 > vf.reachable_ceiling(0.3218)


def test_the_admission_test_has_the_required_structure_and_a_material_margin():
    a = vf.reachable_set_admission(c_lower=0.31, c_upper=0.33, Xi_upper=1.0,
                                   artifact_upper=5e-4)
    assert a["lhs"] == pytest.approx(a["predicted_signal_upper"] + a["artifact_upper"]
                                     + a["other_nonoverlapping_numerical_upper"])
    assert a["rhs"] == pytest.approx(a["reachable_ceiling"] - a["safety_margin"])
    assert a["admitted"] is True
    # the margin is a fixed fraction of the ceiling, not a microscopic point-estimate pass
    assert a["safety_margin"] == pytest.approx(0.10 * a["reachable_ceiling"])
    assert a["safety_margin"] > 20 * a["artifact_upper"]
    # conservative on BOTH sides: ceiling from c_lower, signal from c_upper
    assert a["reachable_ceiling"] == pytest.approx(vf.reachable_ceiling(0.31))
    assert a["reachable_ceiling_at_c_upper"] > a["reachable_ceiling"]


def test_the_admission_test_rejects_a_candidate_that_saturates_the_model():
    a = vf.reachable_set_admission(c_lower=0.31, c_upper=0.33, Xi_upper=50.0,
                                   artifact_upper=5e-4)
    assert a["admitted"] is False
    assert a["headroom"] < 0


def test_a_large_artifact_alone_can_close_the_admission_gate():
    a = vf.reachable_set_admission(c_lower=0.31, c_upper=0.33, Xi_upper=1.0,
                                   artifact_upper=0.5)
    assert a["admitted"] is False


def test_most_of_the_wp6_window_is_admissible_at_the_expected_contrast():
    """Ex-ante feasibility, reported honestly. Under the corrected gate (erratum PE-7) the signal
    is taken at the UPPER contrast and the ceiling at the LOWER one, which is conservative on both
    sides and materially tighter than the superseded single-sided form. At an illustrative +/-2.5 %
    contrast interval around 001's measured c_field the lower half of the window is comfortably
    admitted while the very top is NOT — a live design risk recorded in PRE_EXECUTION_REVIEW,
    not something to tune away."""
    lo, hi = 0.3218 * 0.975, 0.3218 * 1.025
    for Xi in (vf.XI_WINDOW_LO, 1.0, 2.0):
        assert vf.reachable_set_admission(lo, hi, Xi, vf.ARTIFACT_BUDGET_R_ABS)["admitted"], Xi
    top = vf.reachable_set_admission(lo, hi, vf.XI_WINDOW_HI, vf.ARTIFACT_BUDGET_R_ABS)
    assert top["admitted"] is False
    assert vf.max_admissible_Xi(lo, vf.ARTIFACT_BUDGET_R_ABS, c_upper=hi) < vf.XI_WINDOW_HI


def test_the_artifact_budget_costs_less_than_a_quarter_of_the_factor_of_two_criterion():
    j = vf.artifact_budget_justification(0.3218)  # c_gate is now passed directly, not derived
    assert j["well_inside_factor_of_two"]
    assert j["max_relative_Xi_bias"] < 0.10


# ==========================================================================================
# 7. Resolution consistency — derived ex ante, and never called a convergence order
# ==========================================================================================

def test_the_element_error_law_is_the_measured_channel_law():
    assert vf.CHANNEL_ERR_LAW_PCT == "50/h^2"
    assert vf.element_error(10) == pytest.approx(0.005)          # 50/100 percent
    for h, pct in ((3, 5.556), (11, 0.413), (31, 0.0520)):
        assert vf.element_error(h) * 100 == pytest.approx(pct, rel=2e-3)


def test_resolution_consistency_tolerances_are_feature_derived_and_strictly_ordered():
    b = {"w": 5, "kz": 2}
    tol_R_blocked = vf.resolution_consistency_tolerance("R_reference_blocked")
    tol_R_open = vf.resolution_consistency_tolerance("R_open", b)
    tol_Xi = vf.resolution_consistency_tolerance("Xi_field", b)
    assert tol_Xi >= tol_R_open > tol_R_blocked > 0
    # derived, not chosen: the lane-only tolerance is kappa times (sum + worst) over the two
    # slot heights — the explicit junction/end allowance, declared as a factor
    dd = [abs(vf.element_error(f * vf.S_COARSE) - vf.element_error(f * vf.S_FINE))
          for f in (vf.BASE["h_low"], vf.BASE["h_high"])]
    expect = vf.KAPPA_RES * (sum(dd) + vf.JUNCTION_ALLOWANCE * max(dd))
    assert tol_R_blocked == pytest.approx(expect, rel=1e-15)
    # a smaller bridge feature earns a LOOSER tolerance, because it is less well resolved
    assert (vf.resolution_consistency_tolerance("Xi_field", {"w": 5, "kz": 2})
            > vf.resolution_consistency_tolerance("Xi_field", {"w": 5, "kz": 4}))


def test_the_resolution_test_is_never_labelled_a_convergence_order_estimate():
    cfg = vf.protocol_config()["resolution_consistency"]
    assert cfg["kind"] == "FROZEN_RESOLUTION_CONSISTENCY_TEST_NOT_A_CONVERGENCE_ORDER_ESTIMATE"
    assert "rp_d_lc_001" in cfg["provenance"]
    txt = " ".join((REPO / vf.BUNDLE_REL / "PROTOCOL.md").read_text().split())
    assert "frozen resolution-consistency test" in txt.lower()
    assert "does not claim, and no 001b surface may state, a formal asymptotic " \
           "convergence-order estimate" in txt


# ==========================================================================================
# 8. Deterministic selection, decision ordering and fail-closed semantics
# ==========================================================================================

def _env(xi, u=0.05):
    est = [{"S": S, "forcing_level": lv, "coupon_source": "bridge_coupon", "Xi": xi * f}
           for S in vf.SCIENTIFIC_RESOLUTIONS
           for lv, f in (("low", 0.99), ("central", 1.0), ("high", 1.01))]
    return vf.xi_envelope(est, u)


def _cand(w, kz, xi, eligible=True, u=0.05):
    return {"w": w, "kz": kz, "eligible": eligible, "xi_envelope": _env(xi, u)}


def _full_set():
    """One candidate per categorical slot plus spares — every envelope unambiguous."""
    return [_cand(3, 2, 0.10), _cand(3, 3, 0.35), _cand(5, 2, 0.9),
            _cand(5, 3, 2.2), _cand(7, 4, 3.0), _cand(9, 4, 6.0)]


def test_the_selection_coordinate_and_envelope_are_frozen_and_cross_resolution():
    e = _env(1.0)
    assert e["selection_coordinate"] == "geometric_mean_of_valid_positive_coupon_estimates"
    assert e["resolutions"] == list(vf.SCIENTIFIC_RESOLUTIONS)
    assert sorted(e["forcing_levels"]) == ["central", "high", "low"]
    assert e["n_estimates"] == 6
    assert e["Xi_lower"] < e["Xi_select"] < e["Xi_upper"]
    # the geometric mean of a symmetric multiplicative spread returns the centre
    assert e["Xi_select"] == pytest.approx((0.99 * 1.0 * 1.01) ** (1 / 3), rel=1e-12)


def test_a_candidate_is_never_collapsed_to_one_unspecified_xi():
    e = _env(1.0)
    for r in e["estimates"]:
        assert set(r) >= {"S", "forcing_level", "coupon_source", "Xi"}


@pytest.mark.parametrize("xi,cat", [(0.05, "below"), (1.0, "inside"), (20.0, "above")])
def test_category_is_decided_on_the_whole_envelope(xi, cat):
    assert _env(xi)["category"] == cat


def test_an_envelope_straddling_a_window_edge_is_boundary_ambiguous_and_unusable():
    for xi in (vf.XI_WINDOW_LO, vf.XI_WINDOW_HI):
        e = _env(xi)
        assert e["category"] == "boundary_ambiguous"
        assert e["categorically_usable"] is False


def test_bridge_selection_is_deterministic_and_reads_no_mirror_observable():
    a = vf.select_bridges(_full_set())
    b = vf.select_bridges(_full_set())
    assert [(c["w"], c["kz"]) for c in a] == [(c["w"], c["kz"]) for c in b]
    assert len(a) == vf.N_FROZEN_BRIDGES == 4
    src = inspect.getsource(vf.select_bridges) + inspect.getsource(vf.xi_envelope)
    for forbidden in ("Xi_hat", "c_hat", "R_open", "outlet_share"):
        assert forbidden not in src


def test_an_ineligible_candidate_can_never_be_selected():
    cs = _full_set()
    for c in cs:
        if (c["w"], c["kz"]) == (5, 3):
            c["eligible"] = False
    sel = vf.select_bridges(cs)
    assert (5, 3) not in [(c["w"], c["kz"]) for c in sel]


def test_selection_ties_break_on_the_integer_geometry():
    cs = [_cand(9, 2, 0.05), _cand(3, 4, 0.05), _cand(3, 3, 0.35), _cand(5, 2, 0.9),
          _cand(5, 3, 2.2), _cand(9, 4, 6.0)]
    sel = vf.select_bridges(cs)
    assert (sel[0]["w"], sel[0]["kz"]) == (3, 4)          # smaller w wins the tie


@pytest.mark.parametrize("drop,reason", [
    ("below", "NO_UNAMBIGUOUS_BELOW_CANDIDATE"),
    ("inside", "INSUFFICIENT_UNAMBIGUOUS_INSIDE_CANDIDATES"),
])
def test_a_missing_categorical_slot_stops_rather_than_improvising(drop, reason):
    cs = [c for c in _full_set() if c["xi_envelope"]["category"] != drop]
    with pytest.raises(vf.DesignBlocked) as exc:
        vf.select_bridges(cs)
    assert exc.value.reason == reason
    assert exc.value.reason in vf.DESIGN_BLOCKED_REASONS


def test_no_eligible_candidate_at_all_is_a_design_stop():
    cs = _full_set()
    for c in cs:
        c["eligible"] = False
    with pytest.raises(vf.DesignBlocked) as exc:
        vf.select_bridges(cs)
    assert exc.value.reason == "NO_CANDIDATE_ADMITTED_BY_REACHABLE_SET"


def test_exactly_four_unique_candidates_or_stop():
    sel = vf.select_bridges(_full_set())
    assert len({(c["w"], c["kz"]) for c in sel}) == vf.N_FROZEN_BRIDGES == 4


def test_no_above_window_slot_is_required_and_above_is_diagnostic_only():
    """Erratum PE-20: an above-window candidate is close to definitionally one the corrected
    two-sided reachable-set gate excludes, so requiring one would require a candidate the gate is
    designed to reject. The 0.10*K margin is unchanged and is not tunable to fill a slot."""
    cs = [c for c in _full_set() if c["xi_envelope"]["category"] != "above"]
    sel = vf.select_bridges(cs)
    assert len(sel) == 4
    assert [c["slot"] for c in sel].count("below") == 1
    assert sum(1 for c in sel if c["slot"].startswith("inside")) == 3
    assert "NO_UNAMBIGUOUS_ABOVE_CANDIDATE" not in vf.DESIGN_BLOCKED_REASONS
    assert "NO_UNAMBIGUOUS_ABOVE_CANDIDATE" in vf.RETIRED_DESIGN_BLOCKED_REASONS
    diag = vf.above_window_diagnostics(_full_set())
    assert diag and all(d["role"].startswith("DIAGNOSTIC_ABOVE_WINDOW") for d in diag)
    assert (9, 4) in [(d["w"], d["kz"]) for d in diag]
    assert (9, 4) not in [(c["w"], c["kz"]) for c in vf.select_bridges(_full_set())]


def test_the_frozen_family_is_emitted_as_an_ascending_ordered_ladder():
    sel = vf.select_bridges(_full_set())
    xis = [c["xi_envelope"]["Xi_select"] for c in sel]
    assert xis == sorted(xis)
    assert [c["freeze_order"] for c in sel] == [0, 1, 2, 3]
    assert all(c["slot_provenance"] for c in sel)


def _all_pass_controls():
    return {n: True for n, req, _ in vf.VALIDITY_CONTROLS if req}


def test_every_clause_passing_gives_cross_model_recovery():
    d = vf.decide(_all_pass_controls(), {n: True for n in range(2, 8)})
    assert d["disposition"] == "CROSS_MODEL_RECOVERY"
    assert d["cross_model_transfer_adjudicated"] is True


@pytest.mark.parametrize("control", [n for n, req, _ in vf.VALIDITY_CONTROLS if req])
def test_any_failed_required_control_forces_invalid_execution(control):
    c = _all_pass_controls()
    c[control] = False
    d = vf.decide(c, {n: True for n in range(2, 8)})
    assert d["disposition"] == "INVALID_EXECUTION"
    assert d["primary_cause"] == control
    assert d["cross_model_transfer_adjudicated"] is False
    assert d["evidence_use"] == "DIAGNOSTIC_ONLY_INVALID_EXECUTION"


def test_a_not_evaluated_required_control_is_fail_closed():
    c = _all_pass_controls()
    c["mass_conservation"] = None
    d = vf.decide(c, {n: True for n in range(2, 8)})
    assert d["disposition"] == "INVALID_EXECUTION"
    assert "mass_conservation" in d["not_evaluated_required_controls"]


def test_downstream_clauses_are_non_adjudicative_after_an_invalid_execution():
    c = _all_pass_controls()
    c["convergence"] = False
    d = vf.decide(c, {n: True for n in range(2, 8)})
    for cl in d["clauses"][1:]:
        assert cl["adjudicative"] is False
        assert cl["pass"] is None
        assert cl["status"] == "DIAGNOSTIC_ONLY_NOT_REACHED"
        assert cl["diagnostic_computed_pass"] is True     # preserved, never machine-readable


def test_a_stable_boundary_observable_cannot_rescue_a_failed_componentwise_control():
    """The exact 001 failure mode: every classification was stable and the execution was still
    invalid, because the internal components failed their own forcing-independence requirement."""
    c = _all_pass_controls()
    c["componentwise_creeping_flow_control"] = False
    c["boundary_inference_forcing_stability"] = True
    d = vf.decide(c, {n: True for n in range(2, 8)})
    assert d["disposition"] == "INVALID_EXECUTION"


def test_a_volume_flux_proxy_failure_alone_does_not_invalidate_an_execution():
    c = _all_pass_controls()
    c["volume_flux_uniformity"] = False                  # a DIAGNOSTIC control
    d = vf.decide(c, {n: True for n in range(2, 8)})
    assert d["disposition"] == "CROSS_MODEL_RECOVERY"


def test_too_few_window_cases_is_design_missed_target_and_adjudicates_nothing():
    d = vf.decide(_all_pass_controls(), {2: False, 3: True, 4: True, 5: True, 6: True, 7: True})
    assert d["disposition"] == "DESIGN_MISSED_TARGET"
    assert d["cross_model_transfer_adjudicated"] is False
    assert all(cl["adjudicative"] is False for cl in d["clauses"][2:])


def test_a_factor_of_two_failure_with_correct_ordering_is_mechanism_only():
    d = vf.decide(_all_pass_controls(),
                  {2: True, 3: False, 4: True, 5: True, 6: True, 7: True})
    assert d["disposition"] == "MECHANISM_ONLY"


def test_a_broken_path_swap_is_no_cross_model_transfer():
    d = vf.decide(_all_pass_controls(),
                  {2: True, 3: True, 4: True, 5: True, 6: False, 7: True})
    assert d["disposition"] == "NO_CROSS_MODEL_TRANSFER"


def test_the_disposition_vocabulary_is_the_repository_one():
    assert set(vf.DISPOSITIONS) == {"CROSS_MODEL_RECOVERY", "MECHANISM_ONLY",
                                    "NO_CROSS_MODEL_TRANSFER", "INVALID_EXECUTION",
                                    "DESIGN_MISSED_TARGET"}
    assert vf.DESIGN_BLOCKED not in vf.DISPOSITIONS     # a pre-execution stop, not a disposition


def test_clause_order_and_fail_semantics_are_declared_for_every_clause():
    assert [c["n"] for c in vf.DECISION_CLAUSES] == list(range(1, 8))
    for c in vf.DECISION_CLAUSES:
        for k in ("name", "inputs", "tolerance", "authority", "fail"):
            assert c[k], (c["n"], k)
        assert isinstance(c["later_clauses_adjudicative_after_failure"], bool)
    # execution validity and the window count both terminate adjudication; the rest do not
    stops = [c["n"] for c in vf.DECISION_CLAUSES
             if not c["later_clauses_adjudicative_after_failure"]]
    assert stops == [1, 2]


# ==========================================================================================
# 9. Canonical serialisation, hashing and the execution-authority refusal
# ==========================================================================================

def test_canonical_serialisation_is_stable_and_order_independent():
    a = {"b": 1.0, "a": [3.0, 2.0], "c": {"z": 1, "y": 2}}
    b = {"c": {"y": 2, "z": 1}, "a": [3.0, 2.0], "b": 1.0}
    assert vf.canonical_json(a) == vf.canonical_json(b)
    assert vf.record_hash(a) == vf.record_hash(b)
    assert " " not in vf.canonical_json(a)


def test_serialisation_precision_is_frozen_so_a_hash_cannot_move_on_a_last_binary_digit():
    a = {"x": 1.0000000000001}
    b = {"x": 1.0000000000001 + 1e-15}
    assert vf.record_hash(a) == vf.record_hash(b)
    c = {"x": 1.0000000001}
    assert vf.record_hash(a) != vf.record_hash(c)


def test_the_generated_artifacts_do_not_drift_from_the_module():
    r = vf.verify()
    assert r["ok"], r["problems"]


def test_the_preflight_status_says_nothing_has_been_executed():
    st = vf.preflight_status()
    assert st["status"] == "PRE_EXECUTION_PREFLIGHT_FROZEN_PENDING_EXACT_HEAD_REVIEW"
    assert st["solves_executed"] == 0 and st["lb_solver_invoked"] is False
    assert st["disposition"] is None
    assert st["cross_model_transfer_adjudicated"] is False
    assert st["stage_b_authorised"] is False and st["paper_4_authorised"] is False
    assert st["card_box_5"] == "OPEN"


def test_no_result_or_decision_artifact_exists_that_could_be_mistaken_for_an_executed_one():
    bundle = REPO / vf.BUNDLE_REL
    assert not (bundle / "result.json").exists()
    assert not (bundle / "decision.md").exists()
    assert not (bundle / "summary.csv").exists()


def _config_hashes():
    return vf.config_hashes()


def _manifest(phase, runs):
    doc = {"phase": phase, "correction_version": vf.CORRECTION_VERSION,
           "completed_cases": [{"case_id": "%s.x" % phase, "record_sha256": "a" * 64}]}
    doc.update(_config_hashes())
    (runs / ("manifest_%s.json" % phase)).write_text(json.dumps(doc))
    return doc


def _all_manifests(runs, phases=("P0", "P1a", "P1b", "P2a", "P2b", "P3")):
    return {ph: _manifest(ph, runs) for ph in phases}


def test_authorisation_is_phase_specific_and_empty_at_this_head():
    """Erratum PE-11: one boolean would have authorised the primary experiment and Arm J in the
    same act as the pre-freeze phases."""
    assert drv.AUTHORISED_SOLVING_PHASES == ()
    assert not hasattr(drv, "EXECUTION_AUTHORISED")
    src = (REPO / "puckworks/validation/slow/rp_d_lc_001b.py").read_text()
    assert "AUTHORISED_SOLVING_PHASES = ()" in src          # source-controlled, not a flag
    # and it is not reachable from the process environment or a command-line switch
    tree = ast.parse(src)
    names = {n.attr for n in ast.walk(tree) if isinstance(n, ast.Attribute)}
    names |= {n.id for n in ast.walk(tree) if isinstance(n, ast.Name)}
    assert not (names & {"environ", "getenv"})


@pytest.mark.parametrize("phase", list(drv.SOLVING_MODES))
def test_every_solving_phase_refuses_at_this_head(phase):
    with pytest.raises((drv.ExecutionNotAuthorised, vf.FreezeMissing, vf.ManifestMissing,
                        vf.ExecutionAuthorityError)):
        drv.run_phase(phase)


@pytest.mark.parametrize("phase", ["P3", "P4"])
def test_p3_and_p4_refuse_even_when_the_pre_freeze_phases_are_authorised(phase, tmp_path,
                                                                        monkeypatch):
    """Authorising P0/P1a/P1b/P2a must NOT authorise the primary experiment."""
    monkeypatch.setattr(drv, "AUTHORISED_SOLVING_PHASES", ("P0", "P1a", "P1b", "P2a"))
    _all_manifests(tmp_path)
    with pytest.raises((vf.FreezeMissing, drv.ExecutionNotAuthorised)):
        drv.run_phase(phase, runs_dir=tmp_path)


def test_the_freeze_gate_needs_the_instantiated_matrix_too(tmp_path):
    freeze = {"correction_version": vf.CORRECTION_VERSION,
              "frozen_bridges": [{"w": 3, "kz": 2}] * 5,
              "instantiated_matrix_sha256": "b" * 64}
    freeze.update(_config_hashes())
    fp = tmp_path / "bridge_freeze.json"
    fp.write_text(json.dumps(freeze))
    with pytest.raises(vf.FreezeMissing):
        vf.require_freeze("P3", path=fp, matrix_path=tmp_path / "absent.json")


@pytest.mark.parametrize("mutate,why", [
    ({"protocol_config_sha256": "0" * 64}, "wrong protocol hash"),
    ({"execution_matrix_sha256": "0" * 64}, "wrong matrix hash"),
    ({"correction_version": "PREFLIGHT-C0"}, "superseded correction version"),
    ({"frozen_bridges": []}, "no bridges"),
    ({"frozen_bridges": [{"w": 3, "kz": 2}]}, "too few bridges"),
])
def test_a_freeze_that_does_not_bind_this_configuration_is_refused(mutate, why, tmp_path):
    freeze = {"correction_version": vf.CORRECTION_VERSION,
              "frozen_bridges": [{"w": 3, "kz": 2}] * 5,
              "instantiated_matrix_sha256": "b" * 64}
    freeze.update(_config_hashes())
    freeze.update(mutate)
    fp = tmp_path / "bridge_freeze.json"
    fp.write_text(json.dumps(freeze))
    mp = tmp_path / "instantiated.json"
    mp.write_text(json.dumps({"instantiated_matrix_sha256": "b" * 64}))
    with pytest.raises(vf.FreezeMissing):
        vf.require_freeze("P3", path=fp, matrix_path=mp)


@pytest.mark.parametrize("mutate", [
    {"correction_version": "PREFLIGHT-C0"},
    {"fixture_spec_sha256": "0" * 64},
    {"completed_cases": []},
    {"phase": "P9"},
])
def test_a_manifest_bound_to_a_different_configuration_is_refused(mutate, tmp_path):
    doc = {"phase": "P0", "correction_version": vf.CORRECTION_VERSION,
           "completed_cases": [{"case_id": "x", "record_sha256": "a" * 64}]}
    doc.update(_config_hashes())
    doc.update(mutate)
    (tmp_path / "manifest_P0.json").write_text(json.dumps(doc))
    with pytest.raises(vf.ManifestMissing):
        vf.require_phase_manifests("P1a", runs_dir=tmp_path)


def test_the_execution_authority_fails_closed_rather_than_returning_none():
    with pytest.raises(vf.ExecutionAuthorityError):
        vf.execution_authority("P9")                              # unknown stage
    with pytest.raises(vf.ExecutionAuthorityError):
        vf.execution_authority("P0", backend="taichi")            # unsupported backend
    assert vf.SUPPORTED_BACKENDS == ("reference",)


def test_a_dirty_working_tree_cannot_carry_an_execution_authority(tmp_path, monkeypatch):
    monkeypatch.setattr(vf, "_git", lambda *a: ("M x.py" if a[0] == "status" else "a" * 40))
    with pytest.raises(vf.ExecutionAuthorityError):
        vf.execution_authority("P0")
    # the same authority resolves when the tree is clean
    monkeypatch.setattr(vf, "_git", lambda *a: ("" if a[0] == "status" else "a" * 40))
    auth = vf.execution_authority("P0")
    assert auth["working_tree_clean"] is True and auth["clean_tree_required"] is True


def test_a_missing_input_file_cannot_carry_an_execution_authority(monkeypatch):
    monkeypatch.setattr(vf, "_sha_file", lambda rel: None)
    with pytest.raises(vf.ExecutionAuthorityError):
        vf.execution_authority("P0")


def test_the_execution_authority_records_everything_a_future_stage_must_bind():
    # require_clean=False so the SHAPE of the record is testable from a working checkout; the
    # dirty-tree refusal itself is asserted separately, and is on by default.
    a = vf.execution_authority("P0", require_clean=False)
    assert isinstance(a["working_tree_clean"], bool)   # MEASURED, never asserted True
    for k in ("stage", "correction_version", "source_commit", "source_tree",
              "working_tree_clean", "protocol_sha256", "geometry_spec_sha256", "errata_sha256",
              "protocol_config_sha256", "fixture_spec_sha256", "execution_matrix_sha256",
              "input_file_sha256", "backend", "dependencies", "seed", "solver_config",
              "base_commit", "base_tree", "prerequisites"):
        assert k in a, k
    assert a["seed"] is None
    assert all(v for v in a["input_file_sha256"].values())         # no null hashes
    assert a["backend"] == "reference"
    assert inspect.signature(vf.execution_authority).parameters["require_clean"].default is True


# ==========================================================================================
# 10. No solver runs here, and none can
# ==========================================================================================

def test_the_single_solver_call_site_refuses():
    with pytest.raises(drv.ExecutionNotAuthorised):
        drv.solve(np.ones((4, 4, 4), bool), g=1e-6, phase="P0")


def test_the_driver_has_exactly_one_solver_call_site_and_it_is_guarded():
    src = (REPO / "puckworks/validation/slow/rp_d_lc_001b.py").read_text()
    tree = ast.parse(src)
    calls = [n for n in ast.walk(tree)
             if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
             and n.func.attr == "solve"
             and isinstance(n.func.value, ast.Name) and n.func.value.id == "lb_reference"]
    assert len(calls) == 1
    fn = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "solve"][0]
    guards = [n for n in fn.body if isinstance(n, ast.If)]
    # TWO guards, both ahead of the single call site: the post-freeze hard refusal (PE-76) and
    # the phase allowlist (PE-11). Neither can be reached around.
    dumped = [ast.dump(g.test) for g in guards]
    assert any("POST_FREEZE_EXECUTOR_READY" in d for d in dumped)
    assert any("AUTHORISED_SOLVING_PHASES" in d for d in dumped)
    assert max(g.lineno for g in guards[:2]) < calls[0].lineno


def test_the_analysis_module_never_imports_the_solver():
    """It may NAME the kernel in its frozen configuration; it may not import or call it."""
    src = (REPO / "puckworks/analysis/rp_d_lc_001b_virtual_fixture.py").read_text()
    tree = ast.parse(src)
    imported = set()
    for n in ast.walk(tree):
        if isinstance(n, ast.Import):
            imported.update(a.name for a in n.names)
        elif isinstance(n, ast.ImportFrom):
            imported.add(n.module or "")
            imported.update("%s.%s" % (n.module or "", a.name) for a in n.names)
    assert not any("lb_reference" in m or "brewer2026" in m for m in imported), imported
    called = {n.func.attr for n in ast.walk(tree)
              if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)}
    assert "solve" not in called


def test_no_test_in_this_file_can_reach_the_solver():
    """No preflight test imports or calls the lattice-Boltzmann kernel."""
    tree = ast.parse(pathlib.Path(__file__).read_text())
    imported = set()
    for n in ast.walk(tree):
        if isinstance(n, ast.Import):
            imported.update(a.name for a in n.names)
        elif isinstance(n, ast.ImportFrom):
            imported.add(n.module or "")
    assert not any("lb_reference" in m for m in imported), imported


def test_no_preflight_test_is_marked_slow(request):
    """This whole file must stay in the quick CI lane: it contains no science-heavy work."""
    tree = ast.parse(pathlib.Path(__file__).read_text())
    marks = {d.attr for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)
             for d in n.decorator_list
             if isinstance(d, ast.Attribute)}
    marks |= {d.func.attr for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)
              for d in n.decorator_list
              if isinstance(d, ast.Call) and isinstance(d.func, ast.Attribute)}
    assert marks <= {"parametrize", "fixture"}, marks


# ==========================================================================================
# 10b. Correction regressions — one per erratum, each proving the defect cannot recur
# ==========================================================================================

def _cons_recs(S=vf.S_SMOKE, b=None, ramp=0.0):
    mask, meta, res = _synthetic(S=S, b=b, rho_ramp=ramp, unit_plane_flux=True)
    return [vf.axial_plane_record("cons_%d" % i, x, res["ux"], res["rho"], mask, 1e-6)
            for i, x in enumerate(meta["axial_conservation_planes"])], mask, meta, res


def test_exactly_nine_unique_adjudicative_axial_planes():
    recs, _, meta, _ = _cons_recs()
    assert len(recs) == vf.N_CONSERVATION_PLANES == 9
    assert [r["plane_id"] for r in recs] == list(vf.CONSERVATION_PLANE_IDS)
    assert len({r["index"] for r in recs}) == 9
    assert len(set(meta["axial_conservation_planes"])) == 9
    assert vf.assert_conservation_records(recs) == recs


@pytest.mark.parametrize("bad", ["duplicate", "reordered", "short", "long", "renamed",
                                 "transverse"])
def test_a_conservation_set_that_is_not_the_frozen_nine_is_refused(bad):
    recs, _, _, _ = _cons_recs()
    if bad == "duplicate":
        recs = recs[:-1] + [dict(recs[0], plane_id="cons_8")]
    elif bad == "reordered":
        recs = list(reversed(recs))
    elif bad == "short":
        recs = recs[:-1]
    elif bad == "long":
        recs = recs + [dict(recs[0], plane_id="cons_9")]
    elif bad == "renamed":
        recs = [dict(recs[0], plane_id="x_meas_a")] + recs[1:]
    else:
        recs = [dict(recs[0], orientation="y")] + recs[1:]
    with pytest.raises(ValueError):
        vf.conservation_residuals(recs)


def test_duplicating_a_measurement_plane_cannot_move_the_conservation_verdict():
    """Erratum PE-1 in one assertion: a min/max spread is decided by its extremes, so admitting
    a duplicate of a named plane would move an adjudicative residual with no physics changing.
    The named records are REPORTED and cannot enter the statistic, whatever a caller passes."""
    recs, mask, meta, res = _cons_recs(ramp=1e-3)
    named = drv.named_axial_records(res, mask, meta, 1e-6)
    lanes = drv.lane_records(res, mask, meta, 1e-6)
    base = vf.conservation_residuals(recs)
    with_named = vf.conservation_residuals(recs, named_plane_records=named + lanes)
    doubled = vf.conservation_residuals(recs, named_plane_records=named * 3 + lanes * 2)
    for other in (with_named, doubled):
        assert other["mass_flux_residual"] == base["mass_flux_residual"]
        assert other["volume_flux_residual"] == base["volume_flux_residual"]
        assert other["mass_conservation_pass"] == base["mass_conservation_pass"]
    assert with_named["named_plane_records_admitted_to_verdict"] is False
    assert set(with_named["named_plane_records_reported"]) >= set(drv.NAMED_AXIAL_PLANES)
    # and the named planes really would have moved it, had they been admitted
    contaminated = vf._spread(r["sum_rho_ux"] for r in recs + named)
    assert contaminated != pytest.approx(base["mass_flux_residual"])


def _tv(mass, vol=None, ids=("y_portA_in", "y_duct_a", "y_duct_b", "y_portB_out"), n_fluid=8):
    vol = mass if vol is None else vol
    return [{"plane_id": p, "orientation": "y", "index": i, "n_fluid": n_fluid,
             "sum_uy": v, "sum_rho_uy": m, "footprint_x": (0, 2), "footprint_z": (0, 2),
             "sign_convention": vf.SIGN_CONVENTION_TRANSVERSE}
            for i, (p, m, v) in enumerate(zip(ids, mass, vol))]


def test_four_exact_zeros_at_the_negative_control_pass_rather_than_divide_by_zero():
    """The defining case (erratum PE-2): zero lateral driver means the CORRECT answer is zero
    net transverse mass flux. The superseded mean-normalised metric was undefined here."""
    r = vf.transverse_conservation("open", _tv([0.0, 0.0, 0.0, 0.0]), axial_mass_scale=10.0,
                                   lateral_driver_is_zero=True)
    assert r["status"] == "EVALUATED_ZERO_SAFE_ABSOLUTE"
    assert r["pass"] is True
    assert r["absolute_imbalance_normalised"] == 0.0
    assert r["relative_imbalance"] is None and r["relative_gate_applicable"] is False
    with pytest.raises(ZeroDivisionError):
        vf._spread([0.0, 0.0, 0.0, 0.0])            # what the superseded metric would have done


@pytest.mark.parametrize("noise", [1e-9, -1e-9, 5e-8, -5e-8])
def test_near_zero_signed_round_off_still_passes_the_zero_safe_gate(noise):
    r = vf.transverse_conservation("open", _tv([noise, -noise, noise, -noise]),
                                   axial_mass_scale=10.0, lateral_driver_is_zero=True)
    assert r["pass"] is True
    assert math.isfinite(r["absolute_imbalance_normalised"])
    assert math.isfinite(r["signed_balance"])


def test_a_large_spurious_leakage_at_zero_driver_fails_the_zero_safe_gate():
    r = vf.transverse_conservation("open", _tv([0.05, 0.0, 0.0, -0.05]), axial_mass_scale=10.0,
                                   lateral_driver_is_zero=True)
    assert r["pass"] is False
    assert r["absolute_imbalance_normalised"] > vf.TOL_BRIDGE_LEAKAGE_REL


def test_a_blocked_candidate_reports_not_applicable_and_labels_its_blind_pockets():
    recs = _tv([0.0, 0.0, 0.0, 0.0])
    for r in recs:
        if r["plane_id"] in vf.DUCT_CONTROL_PLANE_IDS:
            r["n_fluid"] = 0                        # the duct row is structurally solid
        else:
            r["sum_rho_uy"] = 1e-6                  # recirculation inside a blind pocket
    out = vf.transverse_conservation("blocked", recs, axial_mass_scale=10.0)
    assert out["status"] == "NOT_APPLICABLE_BLOCKED_CONNECTION"
    assert out["duct_planes_structurally_solid"] is True
    assert out["port_pocket_diagnostics"]["interpretation"] == (
        "BLIND_POCKET_RECIRCULATION_NOT_THROUGH_FLOW")
    assert out["relative_imbalance"] is None


def test_a_blocked_candidate_with_fluid_in_its_duct_planes_is_not_the_fixture_it_claims():
    recs = _tv([0.0, 1e-4, 1e-4, 0.0])
    out = vf.transverse_conservation("blocked", recs, axial_mass_scale=10.0)
    assert out["pass"] is False


def test_a_fixture_with_no_bridge_needs_no_transverse_record_at_all():
    out = vf.transverse_conservation("reference_blocked", [], axial_mass_scale=10.0)
    assert out["status"] == "NOT_APPLICABLE_NO_BRIDGE"
    assert out["pass"] is None


def test_a_driven_bridge_with_consistent_flux_passes_both_halves_of_the_hybrid_gate():
    q = 0.5                                          # far above the frozen floor
    out = vf.transverse_conservation("open", _tv([q, q * 1.0001, q * 0.9999, q]),
                                     axial_mass_scale=10.0)
    assert out["status"] == "EVALUATED_HYBRID"
    assert out["relative_gate_applicable"] is True
    assert out["pass"] is True


def test_a_driven_bridge_with_one_inconsistent_plane_fails():
    q = 0.5
    out = vf.transverse_conservation("open", _tv([q, q, q * 0.5, q]), axial_mass_scale=10.0)
    assert out["relative_gate_applicable"] is True
    assert out["pass"] is False


def test_below_the_frozen_floor_only_the_absolute_gate_decides():
    """A physically small mean lateral flux must not be converted into a failure by a relative
    statistic. Here the imbalance is comfortably inside the ABSOLUTE gate while the relative one
    would read 10 % — which is exactly why the relative gate is not admitted below the floor."""
    scale = 10.0
    floor = vf.LATERAL_FLUX_FLOOR_FACTOR * vf.TOL_BRIDGE_LEAKAGE_REL * scale
    mass = [0.05, 0.05, 0.045, 0.05]
    out = vf.transverse_conservation("open", _tv(mass), axial_mass_scale=scale)
    assert abs(sum(mass) / len(mass)) < floor
    assert out["relative_gate_applicable"] is False
    assert out["relative_imbalance"] is None
    assert out["absolute_imbalance_normalised"] <= vf.TOL_BRIDGE_LEAKAGE_REL
    assert out["pass"] is True
    assert out["lateral_flux_floor"] == pytest.approx(floor)
    # the relative statistic the floor suppresses would have failed
    assert 0.005 / (sum(mass) / len(mass)) > vf.TOL_MASS_REL


def test_a_zero_normalisation_scale_is_refused_rather_than_dividing_by_it():
    with pytest.raises(ValueError):
        vf.transverse_conservation("open", _tv([0.0] * 4), axial_mass_scale=0.0)


@pytest.mark.parametrize("bad", [float("nan"), float("inf"), float("-inf")])
def test_canonical_serialisation_rejects_every_non_finite_number(bad):
    for payload in ({"x": bad}, {"a": [1.0, bad]}, {"a": {"b": {"c": bad}}}):
        with pytest.raises(vf.NonFiniteValue):
            vf.canonical_json(payload)
        with pytest.raises(vf.NonFiniteValue):
            vf.record_hash(payload)


def test_a_finite_payload_round_trips_through_the_canonical_writer():
    payload = {"b": 1.5, "a": [3.0, {"z": -2.25}], "s": "ok", "n": None, "t": True}
    doc = json.loads(vf.canonical_json(payload))
    assert doc == payload
    assert vf.record_hash(payload) == vf.record_hash(json.loads(vf.canonical_json(payload)))


def test_non_applicability_is_a_status_string_with_null_numerics_not_a_nan():
    out = vf.transverse_conservation("reference_blocked", [], axial_mass_scale=10.0)
    assert isinstance(out["status"], str) and out["relative_imbalance"] is None
    vf.canonical_json(out)                            # must serialise without raising


def _vel(mask, ux=0.0, uy=0.0, uz=0.0):
    a = [np.zeros(mask.shape) for _ in range(3)]
    for arr, v in zip(a, (ux, uy, uz)):
        arr[~mask] = v
    return a


def test_every_velocity_component_contributes_to_the_measured_mach_number():
    mask, _ = vf.build_fixture(vf.S_SMOKE, bridge={"w": 3, "kz": 2}, connected=True)
    base = vf.mach_record(*_vel(mask, ux=0.001), mask)["max_mach"]
    for comp in ("ux", "uy", "uz"):
        m = vf.mach_record(*_vel(mask, **{comp: 0.002}), mask)
        assert m["max_mach"] > base, comp
        assert m["components_used"] == ["ux", "uy", "uz"]


def test_a_nonzero_uz_alone_can_determine_the_maximum_mach_number():
    """Erratum PE-4: uz is NOT assumed to vanish from nominal symmetry, and the superseded
    driver never even retained it."""
    mask, _ = vf.build_fixture(vf.S_SMOKE, bridge={"w": 3, "kz": 2}, connected=True)
    ux, uy, uz = _vel(mask, ux=0.001, uy=0.001)
    idx = tuple(int(v) for v in np.argwhere(~mask)[0])
    uz[idx] = 0.02
    m = vf.mach_record(ux, uy, uz, mask)
    assert m["argmax_index"] == idx
    assert m["uz_at_max"] == pytest.approx(0.02)
    assert m["max_mach"] == pytest.approx(math.sqrt(3.0) * math.sqrt(0.001 ** 2 + 0.001 ** 2
                                                                    + 0.02 ** 2))
    assert m["pass"] is False


def test_solid_nodes_are_excluded_from_the_mach_maximum():
    """The kernel leaves g/2 in ux at solid nodes, so counting them would be wrong."""
    mask, _ = vf.build_fixture(vf.S_SMOKE, bridge={"w": 3, "kz": 2}, connected=True)
    ux, uy, uz = _vel(mask, ux=0.001)
    solid = tuple(int(v) for v in np.argwhere(mask)[0])
    ux[solid] = 99.0
    m = vf.mach_record(ux, uy, uz, mask)
    assert m["argmax_index"] != solid
    assert m["max_mach"] == pytest.approx(math.sqrt(3.0) * 0.001)
    assert m["solid_nodes_excluded"] is True
    assert m["n_fluid"] == int((~mask).sum())


@pytest.mark.parametrize("missing", ["ux", "uy", "uz"])
def test_the_mach_record_fails_closed_on_an_absent_component(missing):
    mask, _ = vf.build_fixture(vf.S_SMOKE, bridge={"w": 3, "kz": 2}, connected=True)
    arrays = dict(zip(("ux", "uy", "uz"), _vel(mask, ux=0.001)))
    arrays[missing] = None
    with pytest.raises(ValueError):
        vf.mach_record(arrays["ux"], arrays["uy"], arrays["uz"], mask)


def test_the_mach_record_fails_closed_on_a_non_finite_fluid_value():
    mask, _ = vf.build_fixture(vf.S_SMOKE, bridge={"w": 3, "kz": 2}, connected=True)
    ux, uy, uz = _vel(mask, ux=0.001)
    ux[tuple(int(v) for v in np.argwhere(~mask)[0])] = float("nan")
    with pytest.raises(vf.NonFiniteValue):
        vf.mach_record(ux, uy, uz, mask)


def test_the_case_record_fails_closed_without_the_required_fields():
    mask, meta, res = _synthetic()
    for drop in ("rho", "uy", "uz"):
        partial = {k: v for k, v in res.items() if k != drop}
        with pytest.raises(ValueError):
            drv.case_record(partial, mask, meta, 1e-6, stage="unit")
    assert drv.REQUIRED_FIELDS == ("rho", "uy", "uz")


def test_the_required_fields_are_all_exportable_without_any_solver_change():
    from puckworks.models.brewer2026 import lb_reference
    assert set(drv.REQUIRED_FIELDS) <= set(lb_reference.EXPORTABLE_FIELDS)


def test_every_pre_freeze_forcing_ladder_is_complete_at_both_resolutions():
    """Erratum PE-5: no quantity may inform admission, classification or selection before its own
    forcing-invariance evidence exists."""
    rows = vf.execution_matrix()["rows"]
    want = {lv for lv in vf.FORCING_LEVELS}
    families = {
        "reference_blocked_ladder": lambda r: True,
        "axial_coupon": lambda r: True,
        "identical_path_control": lambda r: True,
        "bridge_coupon": lambda r: True,
        "candidate_blocked_mirror": lambda r: True,
    }
    for kind, keep in families.items():
        sub = [r for r in rows if r["kind"] == kind and keep(r)]
        assert sub, kind
        for S in vf.SCIENTIFIC_RESOLUTIONS:
            got = {r["forcing_level"] for r in sub if r["S"] == S}
            assert got == want, (kind, S, got)


def test_both_coupon_orientations_are_present_over_the_whole_ladder():
    rows = [r for r in vf.execution_matrix()["rows"] if r["kind"] == "axial_coupon"]
    normal = [r for r in rows if r["run_mode"] == "NORMAL"]
    combos = {(r["S"], r["forcing_level"], r["coupon_level"], r["coupon_orientation"])
              for r in normal}
    assert len(combos) == len(normal) == 2 * 3 * 2 * 2
    assert {c[3] for c in combos} == {"x", "y"}
    assert all(r["coupon_orientation"] is not None for r in rows)
    assert len(rows) == 2 * len(normal)          # each paired with its own fixed-step audit


def test_no_selection_bearing_quantity_is_first_validated_after_the_freeze():
    rows = vf.execution_matrix()["rows"]
    pre = {"P0", "P1a", "P1b", "P2a"}
    for kind in ("identical_path_control", "bridge_coupon", "candidate_blocked_mirror",
                 "axial_coupon", "reference_blocked_ladder"):
        phases = {r["phase"] for r in rows if r["kind"] == kind}
        assert phases & pre, kind
    # the artifact and the contrast are measured before anything is selected
    assert {r["phase"] for r in rows if r["kind"] == "candidate_blocked_mirror"} == {"P2a"}
    for kind in vf.SELECTION_BEARING_KINDS:
        normal = [r for r in rows if r["kind"] == kind and r["run_mode"] == "NORMAL"]
        audits = [r for r in rows if r["kind"] == kind
                  and r["run_mode"] == "FIXED_STEP_REEXECUTION_1P5X"]
        assert len(audits) == len(normal), kind


def test_every_matrix_row_carries_a_unique_case_id_and_a_complete_configuration():
    rows = vf.execution_matrix()["rows"]
    ids = [r["case_id"] for r in rows]
    assert len(set(ids)) == len(ids)
    required = ("phase", "kind", "S", "forcing_level", "forcing_repr", "forcing_exact",
                "tau_plus", "state", "variant", "backend", "record_schema", "class")
    for r in rows:
        for k in required:
            assert r[k] is not None, (r["case_id"], k)
        assert r["record_schema"] in vf.RECORD_SCHEMAS
        assert r["backend"] in vf.SUPPORTED_BACKENDS


def test_no_two_matrix_rows_are_canonically_identical_once_the_case_id_is_removed():
    rows = vf.execution_matrix()["rows"]
    canon = [json.dumps({k: v for k, v in sorted(r.items()) if k != "case_id"},
                        sort_keys=True, default=str) for r in rows]
    assert len(set(canon)) == len(canon)


def test_every_conditional_row_declares_a_prerequisite():
    for r in vf.execution_matrix()["rows"]:
        if r["class"].startswith("conditional") or r["phase"] != "P0":
            assert r["prerequisite"], r["case_id"]


def test_every_row_resolves_to_exactly_one_fixture_and_solver_configuration():
    for r in vf.execution_matrix()["rows"]:
        if r["kind"] in ("axial_coupon", "bridge_coupon"):
            continue
        if not isinstance(r["bridge"], dict):
            continue
        mask, _ = vf.build_fixture(r["S"], bridge=r["bridge"],
                                   connected=(r["state"] == "open"),
                                   variant=r["variant"] if r["variant"] in ("mirror",
                                                                            "identical")
                                   else "mirror",
                                   swapped=bool(r["swapped"]),
                                   perturbation=r["perturbation"])
        assert mask is not None
        assert vf.row_forcing(r) == vf.forcing_ladder(r["S"])[r["forcing_level"]]


def test_the_tau_cross_check_is_scheduled_rather_than_merely_asserted():
    rows = [r for r in vf.execution_matrix()["rows"] if r["kind"] == "tau_cross_check"]
    assert len(rows) == len(vf.SCIENTIFIC_RESOLUTIONS)
    assert all(r["tau_plus"] == vf.TAU_CROSS_CHECK for r in rows)
    assert {r["S"] for r in rows} == set(vf.SCIENTIFIC_RESOLUTIONS)


def test_the_p3_p4_matrix_is_instantiated_only_after_selection_is_known():
    m = vf.execution_matrix()
    assert m["post_freeze_rows_are_templates"] is True
    tpl = [r for r in m["rows"] if r["phase"] in ("P3", "P4")]
    assert tpl and all(isinstance(r["bridge"], str) and r["bridge"].startswith("frozen_slot_")
                       for r in tpl)
    sel = [{"w": w, "kz": k} for w, k in ((3, 2), (3, 3), (5, 2), (5, 3))]
    inst = vf.instantiate_post_freeze_matrix(sel)
    assert len(inst) == len(tpl)
    assert all(isinstance(r["bridge"], dict) for r in inst)
    assert len({r["case_id"] for r in inst}) == len(inst)
    assert all(r["bridge_slot"].startswith("frozen_slot_") for r in inst)


def test_the_artifact_gate_is_an_upper_bound_not_a_point_estimate():
    """Erratum PE-6: a 5e-4 point estimate with a 1e-3 uncertainty must FAIL."""
    ok = vf.artifact_metrics(1.0, 1.0, 1.0 + 5e-4, numerical_uncertainty=1e-4)
    assert ok["within_budget"] is True and ok["artifact_upper_bound"] == pytest.approx(6e-4)
    bad = vf.artifact_metrics(1.0, 1.0, 1.0 + 5e-4, numerical_uncertainty=1e-3)
    assert bad["pressure_normalised_R_change"] == pytest.approx(5e-4)
    assert bad["pressure_normalised_R_change"] < vf.ARTIFACT_BUDGET_R_ABS
    assert bad["within_budget"] is False        # the POINT estimate alone would have passed


def test_a_negative_signed_artifact_is_bounded_by_its_absolute_magnitude():
    neg = vf.artifact_metrics(1.0, 1.0, 1.0 - 9e-4, numerical_uncertainty=2e-4)
    assert neg["pressure_normalised_R_change"] < 0
    assert neg["artifact_upper_bound"] == pytest.approx(9e-4 + 2e-4)
    assert neg["within_budget"] is False


@pytest.mark.parametrize("u", [float("nan"), float("inf"), -1e-6, None])
def test_a_missing_or_non_finite_uncertainty_fails_closed(u):
    with pytest.raises(ValueError):
        vf.artifact_metrics(1.0, 1.0, 1.0004, numerical_uncertainty=u)


def test_the_numerical_discrepancy_method_reports_every_term_separately():
    d = vf.numerical_discrepancy_R(R=1.001, C_open=25.5, C_blocked=25.47,
                                   C_open_continued=25.5051, C_blocked_continued=25.4725,
                                   R_node_offsets=[1.0012, 1.0009])
    for k in ("u_continuation_open_rel", "u_continuation_blocked_rel", "u_continuation_R_abs",
              "u_node_offset_R_abs", "u_serialisation_R_abs", "safety_factor", "u_R_abs"):
        assert k in d and math.isfinite(d[k])
    assert d["kind"].endswith("NOT_A_RIGOROUS_ERROR_BOUND")
    assert d["u_R_abs"] == pytest.approx(
        d["safety_factor"] * (d["u_continuation_R_abs"] + d["u_node_offset_R_abs"]
                              + d["u_serialisation_R_abs"]))


def test_the_candidate_contrast_bound_is_measured_not_an_asserted_allowance():
    """Erratum PE-7: the fixed 5 % allowance is gone."""
    assert not hasattr(vf, "C_FIELD_GATE_ALLOWANCE")
    b = vf.candidate_c_bounds([0.320, 0.318, 0.324, 0.322], resolution_tolerance=0.02,
                              numerical_rel=1e-3, surface_rel=2e-3)
    assert b["c_lower"] < min(b["c_measurements"]) <= max(b["c_measurements"]) < b["c_upper"]
    assert b["u_rel_total"] == pytest.approx(0.02 + 1e-3 + 2e-3)
    assert "no open mirror" in b["source"]
    with pytest.raises(ValueError):
        vf.candidate_c_bounds([], resolution_tolerance=0.02, numerical_rel=0.0)


def test_a_wider_contrast_interval_admits_less():
    tight = vf.reachable_set_admission(0.320, 0.324, 1.0, 1e-3)
    wide = vf.reachable_set_admission(0.300, 0.344, 1.0, 1e-3)
    assert wide["headroom"] < tight["headroom"]
    assert wide["max_admissible_Xi"] < tight["max_admissible_Xi"]


def test_the_admission_terms_are_kept_separate_so_none_is_counted_twice():
    a = vf.reachable_set_admission(0.31, 0.33, 1.0, artifact_upper=1e-3,
                                   other_numerical_upper=0.0)
    assert a["other_nonoverlapping_numerical_upper"] == 0.0
    assert "artifact_upper already contains u_R" in a["double_counting_prohibited"]
    b = vf.reachable_set_admission(0.31, 0.33, 1.0, artifact_upper=1e-3,
                                   other_numerical_upper=1e-3)
    assert b["lhs"] == pytest.approx(a["lhs"] + 1e-3)


def test_both_bridge_width_and_depth_enter_the_resolution_tolerance():
    """Erratum PE-8: w is SMALLER than kz over part of the family, so a kz-only model could omit
    the smallest feature governing the bridge entirely."""
    base = vf.resolution_consistency_tolerance("Xi_field", {"w": 5, "kz": 3})
    assert vf.resolution_consistency_tolerance("Xi_field", {"w": 3, "kz": 3}) != base
    assert vf.resolution_consistency_tolerance("Xi_field", {"w": 5, "kz": 2}) != base
    feats = vf.RESOLUTION_GOVERNING_FEATURES["Xi_field"]
    for f in ("bridge_w", "bridge_kz", "port_depth", "duct_traverse", "h_low", "h_high"):
        assert f in feats
    # w = 3 with kz = 4 is governed by w, which the superseded kz-only model would have missed
    assert vf._feature_base_size("bridge_w", {"w": 3, "kz": 4}) < vf._feature_base_size(
        "bridge_kz", {"w": 3, "kz": 4})


def test_open_and_blocked_quantities_have_different_resolution_tolerances():
    b = {"w": 5, "kz": 3}
    assert (vf.resolution_consistency_tolerance("R_open", b)
            > vf.resolution_consistency_tolerance("R_reference_blocked"))
    assert (vf.resolution_consistency_tolerance("s_open", b)
            > vf.resolution_consistency_tolerance("s_reference_blocked"))
    # erratum PE-33: the CANDIDATE blocked fixture carries the common-mode ports, so it is not
    # lane-only and its tolerance is strictly larger than the reference fixture's
    assert (vf.resolution_consistency_tolerance("c_field", b)
            > vf.resolution_consistency_tolerance("R_reference_blocked"))
    tbl = vf.resolution_consistency_table(b)
    assert tbl["R_reference_blocked"]["family"] == "reference_blocked_lane_only"
    assert tbl["R_blocked"]["family"] == "candidate_blocked_common_mode_ports"
    assert tbl["R_open"]["family"] == "open_bridge_carrying"


def test_the_reference_forcing_is_an_exact_rational_not_a_binary_float():
    """Erratum PE-12: Fraction(2.0e-6) is the exact rational of an already-rounded float."""
    from fractions import Fraction
    assert vf.G_REF_EXACT == Fraction(1, 500_000) == Fraction("0.000002")
    assert vf.G_REF == float(vf.G_REF_EXACT)
    assert vf.G_REF_EXACT != Fraction(vf.G_REF)          # the two are genuinely different
    src = inspect.getsource(vf.forcing_ladder) + inspect.getsource(vf.forcing_central)
    assert "Fraction(G_REF)" not in src and "Fraction(forcing_central" not in src


def test_the_correction_version_is_stamped_on_every_generated_artifact():
    for fn in (vf.protocol_config, vf.fixture_spec_config, vf.execution_matrix,
               vf.preflight_status):
        assert fn()["correction_version"] == vf.CORRECTION_VERSION == "PREFLIGHT-C5"


def test_every_superseded_generation_is_retained_not_overwritten():
    """C0 and C1 hashes are both kept, so anything bound to either stays traceable."""
    revs = vf.SUPERSEDED_REVIEWS
    assert [r["correction_version"] for r in revs] == ["PREFLIGHT-C0", "PREFLIGHT-C1",
                                                      "PREFLIGHT-C2", "PREFLIGHT-C3",
                                                      "PREFLIGHT-C4"]
    assert revs[0]["reviewed_head"] == "bbf2304665d09cb78c117353947ce8c6cf2e5d24"
    assert revs[1]["reviewed_head"] == "2cf0b63ba2670de423a39f9563822563a3cb59b5"
    assert revs[1]["disposition"].endswith("C2_AND_PREFREEZE_EXECUTOR_REQUIRED")
    assert revs[2]["reviewed_head"] == "c66670770d6b34b355fe29dba384102fc59827d7"
    assert revs[2]["disposition"].endswith("C3_EXECUTOR_AND_ASSEMBLER_CORRECTION_REQUIRED")
    assert revs[3]["reviewed_head"] == "39533ade0fd74dc5fa10470710ec672041e62526"
    assert revs[3]["disposition"].endswith("C4_INTEGRATION_AND_AUTHORITY_CORRECTION_REQUIRED")
    assert revs[4]["reviewed_head"] == "e455c678a2fdd511ce9a30f1d15164f73b9a4481"
    assert revs[4]["reviewed_tree"] == "72eda81e3ddea54ad4714f10c6bb4b347cd6a15a"
    assert revs[4]["disposition"].endswith(
        "C5_DECISION_PATH_AND_LINEAGE_CORRECTION_REQUIRED")
    assert revs[4]["errata"] == ["PE-%d" % i for i in range(60, 77)]
    # the superseded C4 counts are recorded so no C4 number can be quietly carried forward
    assert revs[4]["superseded_counts"]["adaptive_maximum"] == 703
    assert revs[4]["superseded_counts"]["planned_pressure_plane_diagnostic_rows"] == 0
    for r in revs:
        assert len(r["superseded_artifact_sha256"]) == 4
        assert all(len(h) == 64 for h in r["superseded_artifact_sha256"].values())
    # the superseded C1 counts are recorded so no C1 number can be quietly carried forward
    assert revs[1]["superseded_counts"]["n_frozen_bridges"] == 5
    assert revs[1]["superseded_counts"]["adaptive_maximum"] == 407
    st = vf.preflight_status()
    assert st["superseded_reviews"] == [dict(r) for r in revs]


def test_the_errata_record_exists_and_names_every_corrected_blocker():
    txt = (REPO / vf.ERRATA_PATH).read_text()
    for pe in ["PE-%d" % i for i in range(0, 13)]:
        assert pe in txt, pe
    assert "ACCEPTED" in txt and "common-mode-port apparatus" in txt
    assert "047d55f4dcd222b79f20f3d08e04b8de0dd13e7ddb8438cb74bf35ee6461cbe7" in txt


# ==========================================================================================
# 11. The planned matrix, Arm J and the bundle documents
# ==========================================================================================

def test_the_execution_matrix_reports_zero_executed_solves_and_an_exact_total():
    m = vf.execution_matrix()
    assert m["solves_executed"] == 0
    assert m["n_rows"] == m["adaptive_maximum"] == len(m["rows"])
    assert sum(m["by_class"].values()) == m["n_rows"]
    # PE-41: node-offset summaries are extracted from existing fields, so every row is a solve
    assert m["planned_pressure_plane_diagnostic_rows"] == 0
    assert m["planned_normal_solves"] + m["planned_fixed_step_audits"] == m["n_rows"]
    assert m["planned_solver_invocations"] == m["n_rows"]
    for phase in ("P0", "P1a", "P1b", "P2a", "P3", "P4"):
        assert m["by_phase"][phase] > 0
    assert "P2b" not in m["by_phase"]                     # P2b does arithmetic, not solving
    central = [r for r in m["rows"] if r["kind"] == "identical_path_control"
               and r["forcing_level"] == "central" and r["run_mode"] == "NORMAL"]
    assert len(central) == 2 * 2 * len(SCI) == 48

    assert m["by_phase"]["P4"] == vf.ARM_J["planned_solves"]
    assert m["mandatory_minimum"] + m["refused_after_earliest_stop"] == m["n_rows"]
    assert m["diagnostic_replicates"] == 3


def test_arm_j_is_preserved_with_its_purpose_matrix_and_decision_status():
    assert vf.ARM_J["status"] == "decision_bearing"
    assert vf.ARM_J["gate"] == {"R_rel": 1e-3, "s_abs": 5e-4}
    assert vf.ARM_J["planned_solves"] == vf.N_FROZEN_BRIDGES * 2 * 2 == 16
    for k in ("purpose", "relationship_to_corrected_geometry", "ordering", "fail_semantics",
              "matrix"):
        assert vf.ARM_J[k]


def test_every_phase_is_marked_unauthorised_and_the_ordering_is_declared():
    assert [p["id"] for p in vf.EXECUTION_PHASES] == ["P0", "P1a", "P1b", "P2a", "P2b",
                                                      "P3", "P4"]
    assert all(p["authorised_now"] is False for p in vf.EXECUTION_PHASES)
    assert "P0 -> P1a -> P1b -> P2a -> P2b" in vf.execution_matrix()["ordering"]
    # every phase after the first declares what it depends on
    for p in vf.EXECUTION_PHASES[1:]:
        assert p["prerequisite"] in [q["id"] for q in vf.EXECUTION_PHASES]


def test_p1_never_reveals_a_mirror_recovery_case():
    m = vf.execution_matrix()
    p1 = [r for r in m["rows"] if r["phase"] in ("P1a", "P1b")]
    assert p1 and all(r["variant"] == "identical" for r in p1)


def test_no_open_mirror_case_is_scheduled_before_the_freeze():
    """The whole blindness argument: P2a may characterise a candidate's BLOCKED mirror, but no
    OPEN mirror recovery case exists until P3 (errata PE-5, PE-7)."""
    m = vf.execution_matrix()
    pre = [r for r in m["rows"] if r["phase"] in ("P0", "P1a", "P1b", "P2a")]
    assert pre
    for r in pre:
        assert not (r["variant"] == "mirror" and r["state"] == "open"), r["case_id"]


def test_the_bundle_documents_exist_and_carry_the_claim_ceiling():
    for name in ("README.md", "PROTOCOL.md", "VIRTUAL_FIXTURE_SPEC.md",
                 "PRE_EXECUTION_REVIEW.md", "EXECUTION_MATRIX.md"):
        p = REPO / vf.BUNDLE_REL / name
        assert p.exists(), name
    for name in ("README.md", "PROTOCOL.md"):
        txt = (REPO / vf.BUNDLE_REL / name).read_text()
        assert "box 5" in txt and "Paper 4" in txt
        assert "INVALID_EXECUTION" in txt


def test_the_bundle_states_it_is_not_an_insight_foundry_screen():
    txt = (REPO / vf.BUNDLE_REL / "README.md").read_text()
    assert "Insight Foundry" in txt
    reg = json.loads((REPO / "docs/insights/ID_REGISTRY.json").read_text())
    assert "RP-D-LC-001B" not in json.dumps(reg)


def test_the_protocol_declares_an_append_only_erratum_policy():
    txt = (REPO / vf.BUNDLE_REL / "PROTOCOL.md").read_text()
    assert "erratum" in txt.lower()
    assert "append" in txt.lower()


# ==========================================================================================
# 12. C2 correction regressions — one per erratum PE-13 … PE-21
# ==========================================================================================

def _tvm(mass, ids=("y_portA_in", "y_duct_a", "y_duct_b", "y_portB_out"), n_fluid=8):
    return [{"plane_id": p, "orientation": "y", "index": i, "n_fluid": n_fluid,
             "sum_uy": m, "sum_rho_uy": m, "footprint_x": (0, 2), "footprint_z": (0, 2),
             "sign_convention": vf.SIGN_CONVENTION_TRANSVERSE}
            for i, (p, m) in enumerate(zip(ids, mass))]


# ---- PE-14: zero-driver MAGNITUDE, not merely consistency ---------------------------------

def test_four_exact_zeros_pass_both_zero_driver_gates():
    r = vf.transverse_conservation("open", _tvm([0.0] * 4), 10.0, lateral_driver_is_zero=True)
    assert r["magnitude_pass"] is True and r["consistency_pass"] is True and r["pass"] is True
    assert r["max_abs_lateral_mass_flux_rel"] == 0.0 and r["plane_range_mass_rel"] == 0.0


@pytest.mark.parametrize("q", [1e-9, -1e-9, 1e-6, -1e-6])
def test_small_equal_numerical_noise_below_the_ceiling_passes(q):
    r = vf.transverse_conservation("open", _tvm([q] * 4), 10.0, lateral_driver_is_zero=True)
    assert r["pass"] is True
    assert r["max_abs_lateral_mass_flux_rel"] <= vf.TOL_BRIDGE_LEAKAGE_REL


def test_four_EQUAL_material_fluxes_fail_although_their_range_is_exactly_zero():
    """Erratum PE-14, the false green: the superseded gate tested only max-min, which is exactly
    zero here, so a large but perfectly consistent lateral current passed the negative control."""
    q = 0.05                                          # 5e-3 of the axial scale: 5x the ceiling
    r = vf.transverse_conservation("open", _tvm([q] * 4), 10.0, lateral_driver_is_zero=True)
    assert r["plane_range_mass"] == 0.0               # consistency alone would have passed
    assert r["consistency_pass"] is True
    assert r["magnitude_pass"] is False
    assert r["pass"] is False
    assert r["max_abs_lateral_mass_flux_rel"] > vf.TOL_BRIDGE_LEAKAGE_REL


def test_unequal_leakage_fails_the_consistency_gate():
    r = vf.transverse_conservation("open", _tvm([0.0, 0.05, 0.0, -0.05]), 10.0,
                                   lateral_driver_is_zero=True)
    assert r["consistency_pass"] is False and r["pass"] is False


def test_alternating_signed_round_off_is_judged_on_magnitude_and_range():
    r = vf.transverse_conservation("open", _tvm([1e-9, -1e-9, 1e-9, -1e-9]), 10.0,
                                   lateral_driver_is_zero=True)
    assert r["pass"] is True
    assert r["signed_balance"] == pytest.approx(2e-9)
    assert math.isfinite(r["abs_mean_lateral_mass_flux_rel"])


def test_the_two_zero_driver_gates_are_reported_separately():
    r = vf.transverse_conservation("open", _tvm([0.05] * 4), 10.0, lateral_driver_is_zero=True)
    assert set(("magnitude_pass", "consistency_pass")) <= set(r)
    for k in ("max_abs_lateral_mass_flux", "max_abs_lateral_mass_flux_rel",
              "mean_lateral_mass_flux", "abs_mean_lateral_mass_flux_rel",
              "plane_range_mass", "plane_range_mass_rel", "signed_balance",
              "plane_sums_mass", "plane_sums_volume", "normalisation_scale"):
        assert r[k] is not None, k
    for k in ("max_abs_lateral_mass_flux_rel", "plane_range_mass_rel",
              "abs_mean_lateral_mass_flux_rel"):
        assert math.isfinite(r[k])


def test_a_driven_bridge_is_never_required_to_carry_zero_lateral_flux():
    """The magnitude gate applies ONLY to an expected-zero-driver case: for a driven bridge the
    lateral flux is the physics under test."""
    q = 0.5
    r = vf.transverse_conservation("open", _tvm([q] * 4), 10.0, lateral_driver_is_zero=False)
    assert r["magnitude_pass"] is None                # recorded as a signal, not gated
    assert r["max_abs_lateral_mass_flux_rel"] > vf.TOL_BRIDGE_LEAKAGE_REL
    assert r["pass"] is True
    assert r["relative_gate_applicable"] is True


def test_the_leakage_ceiling_is_not_loosened():
    assert vf.TOL_BRIDGE_LEAKAGE_REL == 1.0e-3 == vf.ARTIFACT_BUDGET_R_ABS


# ---- PE-15: the MEASURED lateral pressure gap ---------------------------------------------

def _face_case(S=vf.S_SMOKE, b=None, variant="identical", bump=0.0, connected=True):
    b = b or {"w": 3, "kz": 2}
    mask, meta = vf.build_fixture(S, bridge=b, connected=connected, variant=variant)
    nx = mask.shape[0]
    g = vf.forcing_central(S)
    ux = np.zeros(mask.shape)
    for x in range(nx):
        n = int((~mask[x]).sum())
        if n:
            ux[x][~mask[x]] = 1.0 / n
    rho = np.ones(mask.shape) + 3.0 * g * (nx - np.arange(nx))[:, None, None]
    if bump:
        rho[:, meta["y_face2"], :] += bump
    z = np.zeros(mask.shape)
    return mask, meta, {"ux": ux, "uy": z.copy(), "uz": z.copy(), "rho": rho, "steps": 3000}, g


def test_both_lateral_pressure_faces_are_retained_with_the_frozen_fields():
    mask, meta, res, g = _face_case()
    faces = drv.pressure_face_records(res, mask, meta, g)
    assert [f["plane_id"] for f in faces] == list(vf.PRESSURE_FACE_IDS)
    for f in faces:
        assert set(f) == set(vf.PRESSURE_FACE_FIELDS)
        assert f["orientation"] == "y"
        assert f["footprint_x"] == tuple(int(v) for v in meta["bridge_x"])
        assert f["footprint_z"] == tuple(int(v) for v in meta["bridge_z"])
        assert f["mask_sha256"] == meta["mask_sha256"]
        assert f["n_fluid"] > 0


def test_the_effective_pressure_subtracts_the_body_force_potential_nodewise():
    """p_eff = rho/3 - g*x, evaluated BEFORE averaging, so a multi-x footprint is handled."""
    mask, meta, res, g = _face_case(b={"w": 9, "kz": 2})
    f = drv.pressure_face_records(res, mask, meta, g)[0]
    xs, xe = meta["bridge_x"]
    y = meta["y_face1"]
    zs, ze = meta["bridge_z"]
    sub = ~mask[xs:xe, y, zs:ze]
    xc = np.arange(xs, xe, dtype=float)[:, None]
    expect = ((res["rho"][xs:xe, y, zs:ze] / 3.0 - g * xc)[sub]).mean()
    assert f["p_mean"] == pytest.approx(float(expect), rel=1e-12)
    assert xe - xs > 1                                 # genuinely a multi-x footprint


def test_pressure_faces_average_fluid_nodes_only():
    mask, meta, res, g = _face_case()
    f = drv.pressure_face_records(res, mask, meta, g)[0]
    xs, xe = meta["bridge_x"]
    zs, ze = meta["bridge_z"]
    assert f["n_fluid"] == int((~mask[xs:xe, meta["y_face1"], zs:ze]).sum())
    res["rho"][mask] = 1e6                             # poison every solid node
    f2 = drv.pressure_face_records(res, mask, meta, g)[0]
    assert f2["p_mean"] == pytest.approx(f["p_mean"], rel=1e-12)


def test_a_symmetric_identical_fixture_measures_a_zero_lateral_gap_and_screens_clean():
    """Erratum PE-61: a point PASS is a screen, never an admission."""
    mask, meta, res, g = _face_case()
    rec = drv.case_record(res, mask, meta, g, stage="unit")
    lp = rec["lateral_pressure"]
    assert lp["delta_p_lateral"] == pytest.approx(0.0, abs=1e-15)
    assert lp["expected_zero_driver"] is True
    assert lp["measured_zero_driver_point_pass"] is True
    # the point screen may NEVER admit: the final verdict is null until the audit exists
    assert lp["measured_zero_driver_pass"] is None
    assert lp["measured_zero_driver_upper_bound_pass"] is None
    assert lp["measured_zero_driver_status"] == "INCOMPLETE_PENDING_FIXED_STEP_AUDIT"
    assert lp["measured_zero_driver_point_role"].startswith("PRELIMINARY_POINT_ESTIMATE_SCREEN")


def test_a_MEASURED_nonzero_gap_fails_an_expected_zero_driver_case():
    """A geometry label may never certify the premise of the negative control (erratum PE-15).

    A point FAILURE may still reject immediately: every omitted uncertainty term is
    non-negative, so no additional evidence can rescue it (erratum PE-61).
    """
    mask, meta, res, g = _face_case(bump=1e-3)
    rec = drv.case_record(res, mask, meta, g, stage="unit")
    lp = rec["lateral_pressure"]
    assert lp["expected_zero_driver"] is True          # the LABEL still says identical
    assert abs(lp["delta_p_lateral"]) > 0
    assert lp["measured_zero_driver_point_pass"] is False   # the MEASUREMENT overrules it
    verdict = vf.case_decision_verdict(
        {"kind": "identical_path_control"}, {"lateral_pressure": lp}, "CONVERGED")
    assert verdict["pass"] is False
    assert verdict["reason"] == "MEASURED_LATERAL_DRIVER_NONZERO"


def test_the_common_axial_gradient_cancels_in_the_pointwise_gap():
    mask, meta, res, g = _face_case(b={"w": 9, "kz": 4})
    rec = drv.case_record(res, mask, meta, g, stage="unit")
    d = rec["lateral_pressure"]["delta_pointwise"]
    assert d["faces_share_footprint"] is True and d["masks_pair_exactly"] is True
    assert d["n_fluid_face1"] == d["n_fluid_face2"] == d["n_paired_fluid"]
    assert d["spatial_sd_delta_p"] == pytest.approx(0.0, abs=1e-15)
    assert d["spatial_sd_role"].startswith("SPATIAL_NONUNIFORMITY_DIAGNOSTIC")
    # the individual faces DO vary strongly across the footprint; that is common-mode
    assert rec["lateral_pressure"]["face_nonuniformity_rel"] > 0
    assert rec["lateral_pressure"]["face_nonuniformity_role"] == (
        "SPATIAL_NONUNIFORMITY_DIAGNOSTIC_NOT_A_NUMERICAL_ERROR_BOUND")
    # PE-44: no standard-error term survives anywhere in the adjudicative path
    assert "face_uncertainty_rel" not in rec["lateral_pressure"]


def test_forcing_normalised_lateral_quantities_are_retained():
    mask, meta, res, g = _face_case()
    rec = drv.case_record(res, mask, meta, g, stage="unit")
    lp = rec["lateral_pressure"]
    assert "delta_p_lateral_over_g" in lp and "q_lat_mass_over_g" in lp
    assert lp["delta_p_lateral_over_g"] == pytest.approx(lp["delta_p_lateral"] / g)


def test_a_non_finite_face_value_fails_closed():
    mask, meta, res, g = _face_case()
    xs, _ = meta["bridge_x"]
    zs, _ = meta["bridge_z"]
    res["rho"][xs, meta["y_face1"], zs] = float("nan")   # inside the bridge footprint
    with pytest.raises(vf.NonFiniteValue):
        drv.pressure_face_records(res, mask, meta, g)


def test_the_driven_case_records_the_gap_without_a_zero_driver_verdict():
    mask, meta, res, g = _face_case(variant="mirror")
    rec = drv.case_record(res, mask, meta, g, stage="unit")
    lp = rec["lateral_pressure"]
    assert lp["expected_zero_driver"] is False
    assert lp["measured_zero_driver_pass"] is None


# ---- PE-16: a REAL fixed-step re-execution -------------------------------------------------

@pytest.mark.parametrize("base", [2000, 3000, 4200, 4201, 5999, 12345])
def test_the_audit_target_rounds_up_to_check_and_exceeds_the_base(base):
    tgt = vf.fixed_step_audit_target(base)
    assert tgt % vf.CHECK == 0
    assert tgt > base
    assert tgt >= vf.CONVERGENCE_AUDIT_FACTOR * base - vf.CHECK


def test_the_audit_pins_min_steps_equal_to_max_steps_so_it_cannot_stop_early():
    plan = vf.fixed_step_audit_plan(4200, "NORMAL_CONVERGED")
    assert plan["min_steps"] == plan["max_steps"] == plan["target_steps"] == 6400
    assert plan["run_mode"] == "FIXED_STEP_REEXECUTION_1P5X"
    assert plan["exceeds_base"] is True and plan["aligned_to_check"] is True
    assert "continuation" in plan["naming_note"]      # explicitly says it is NOT one


def test_an_unconverged_base_can_never_be_rescued_by_an_audit():
    with pytest.raises(ValueError):
        vf.fixed_step_audit_plan(60000, "NORMAL_UNCONVERGED")


def test_normal_convergence_and_audit_completion_are_distinct_statuses():
    assert vf.run_status("NORMAL", 4200) == "NORMAL_CONVERGED"
    assert vf.run_status("NORMAL", vf.MAX_STEPS) == "NORMAL_UNCONVERGED"
    assert vf.run_status("FIXED_STEP_REEXECUTION_1P5X", 6400, 6400) == "FIXED_STEP_AUDIT_COMPLETED"
    assert vf.run_status("FIXED_STEP_REEXECUTION_1P5X", 6399, 6400) == "FIXED_STEP_AUDIT_INCOMPLETE"
    assert set(vf.RUN_STATUSES) == {"NORMAL_CONVERGED", "NORMAL_UNCONVERGED",
                                    "FIXED_STEP_AUDIT_COMPLETED", "FIXED_STEP_AUDIT_INCOMPLETE"}


def test_an_audit_that_stops_early_is_incomplete_not_converged():
    """Precisely the superseded no-op: the solver returns at its own convergence point."""
    assert vf.run_status("FIXED_STEP_REEXECUTION_1P5X", 4200, 6400) == "FIXED_STEP_AUDIT_INCOMPLETE"


def test_the_frozen_audit_maximum_covers_the_rule():
    assert vf.MAX_STEPS_AUDIT % vf.CHECK == 0
    assert vf.MAX_STEPS_AUDIT >= vf.CONVERGENCE_AUDIT_FACTOR * vf.MAX_STEPS
    # the guard covers a base case that ran to the normal maximum, and refuses anything beyond
    assert vf.fixed_step_audit_target(vf.MAX_STEPS) == vf.MAX_STEPS_AUDIT
    with pytest.raises(ValueError):
        vf.fixed_step_audit_target(vf.MAX_STEPS + vf.CHECK)


# ---- PE-17: candidate-specific coverage ----------------------------------------------------

def test_every_artifact_combination_has_its_own_fixed_step_evidence():
    rows = vf.execution_matrix()["rows"]
    ident = [r for r in rows if r["kind"] == "identical_path_control"]
    normal = {(tuple(sorted(r["bridge"].items())), r["S"], r["forcing_level"], r["state"])
              for r in ident if r["run_mode"] == "NORMAL"}
    audit = {(tuple(sorted(r["bridge"].items())), r["S"], r["forcing_level"], r["state"])
             for r in ident if r["run_mode"] == "FIXED_STEP_REEXECUTION_1P5X"}
    assert normal == audit
    assert len(normal) == len(SCI) * 2 * 3 * 2       # candidates x S x forcing x state


def test_no_unproved_smallest_largest_extrapolation_remains():
    src = inspect.getsource(vf)
    assert "smallest and largest" not in src
    assert "SELECTION_BEARING_KINDS" in src


def test_p1a_may_reject_but_never_admit():
    src = inspect.getsource(vf.p1a_triage)
    assert "may NEVER ADMIT" in src
    assert "may_admit" in src


def test_the_artifact_is_a_property_of_the_pair_not_of_one_member():
    """A pair with no fixed-step evidence yields a point estimate that may only REJECT."""
    pair = {"blocked": _fake_rec(C=25.0), "open": _fake_rec(C=25.01)}
    art = vf.artifact_from_pair(pair)
    assert art["upper"] is None and art["within_budget"] is None
    assert art["point"] == pytest.approx(0.01 / 25.0, rel=1e-9)
    pair["audit_blocked"] = _fake_rec(C=25.0005)
    pair["audit_open"] = _fake_rec(C=25.0105)
    art2 = vf.artifact_from_pair(pair)
    assert art2["u_R"] > 0 and art2["upper"] == pytest.approx(art2["point"] + art2["u_R"])
    assert art2["fixed_step_case_ids"]


def _fake_rec(C, case_id="x", kind="identical_path_control", S=2, level="central",
              state="blocked", bridge=(3, 2), phase="P1a"):
    return {"case_id": case_id, "kind": kind, "run_mode": "NORMAL",
            "row": {"S": S, "forcing_level": level, "state": state, "phase": phase,
                    "bridge": {"w": bridge[0], "kz": bridge[1]}, "case_id": case_id},
            "scientific": {"Q_volume": C, "dP": 1.0}}


def test_a_candidate_missing_a_required_combination_is_not_admitted():
    recs = {}
    for S in vf.SCIENTIFIC_RESOLUTIONS:
        for lv in vf.FORCING_LEVELS:
            for st in ("blocked", "open"):
                cid = "c.%d.%s.%s" % (S, lv, st)
                recs[cid] = _fake_rec(25.0 if st == "blocked" else 25.0001, cid, S=S,
                                      level=lv, state=st)
    adm = vf.artifact_admission_from_records(recs)
    assert adm[(3, 2)]["admitted"] is False           # no fixed-step evidence yet
    assert "fixed-step" in adm[(3, 2)]["reason"]
    recs.pop("c.2.low.open")
    adm2 = vf.artifact_admission_from_records(recs)
    assert "2.low" in adm2[(3, 2)]["missing"]


# ---- PE-21: exact forcing identity ---------------------------------------------------------

@pytest.mark.parametrize("S", list(vf.SCIENTIFIC_RESOLUTIONS))
@pytest.mark.parametrize("level", list(vf.FORCING_LEVELS))
def test_the_exact_rational_reproduces_the_frozen_ladder(S, level):
    ex = vf.forcing_exact_dict(S, level)
    assert vf.forcing_from_exact(ex) == vf.forcing_ladder(S)[level]
    from fractions import Fraction
    assert Fraction(ex["numerator"], ex["denominator"]) == vf.forcing_exact(S, level)


def test_every_forcing_bearing_row_carries_the_exact_rational_and_a_lossless_float():
    for r in vf.execution_matrix()["rows"]:
        ex = r["forcing_exact"]
        assert set(ex) == {"numerator", "denominator"}
        assert float(r["forcing_repr"]) == vf.forcing_from_exact(ex)
        assert vf.row_forcing(r) == float(r["forcing_repr"])


def test_twelve_decimal_rounding_would_have_destroyed_the_identity():
    """Why the float is not the identity (erratum PE-21): the canonical writer rounds to twelve
    DECIMAL PLACES, which for a forcing of order 1e-7 keeps only about six significant digits —
    so a round-tripped float is no longer the number that was frozen."""
    for level in vf.FORCING_LEVELS:
        g = vf.forcing_ladder(3)[level]
        assert g > 0
        assert round(g, vf._RECORD_DP) != g           # the identity does not survive the writer
    row = [r for r in vf.execution_matrix()["rows"] if r["S"] == 3][0]
    assert vf.row_forcing(row) == vf.forcing_ladder(3)[row["forcing_level"]]   # exact, via Fraction
    # and a record round-tripped through the canonical writer still yields the exact float
    doc = json.loads(vf.canonical_json(row))
    assert vf.forcing_from_exact(doc["forcing_exact"]) == vf.row_forcing(row)


def test_the_row_hash_changes_when_the_exact_rational_changes():
    row = dict(vf.execution_matrix()["rows"][0])
    h = vf.row_sha256(row)
    row["forcing_exact"] = {"numerator": 1, "denominator": 999999}
    assert vf.row_sha256(row) != h


def test_the_case_id_carries_the_exact_rational():
    rows = vf.execution_matrix()["rows"]
    assert any("g1ov1000000" in r["case_id"] for r in rows)


def test_no_fraction_is_ever_built_from_a_binary_float():
    src = inspect.getsource(vf)
    assert "Fraction(G_REF)" not in src
    assert "Fraction(forcing_central" not in src
    assert "Fraction(float(" not in src


# ---- PE-18: records, manifests and the record-derived freeze --------------------------------

@pytest.fixture()
def executed_p0(tmp_path):
    """A complete, validated P0 phase from the PRIVATE TEST_ONLY seam (erratum PE-34)."""
    auth = vf.execution_authority("P0", require_clean=False)
    man = drv._test_only_execute("P0", tmp_path, _fake_provider, auth)
    return tmp_path, auth, man


def _fake_provider(mask, g, phase, row, tau=None, audit=None, backend="reference"):
    """A deterministic stand-in for the solver. The real kernel is never reached."""
    nx = mask.shape[0]
    ux = np.zeros(mask.shape)
    for x in range(nx):
        n = int((~mask[x]).sum())
        if n:
            ux[x][~mask[x]] = 1.0 / n
    z = np.zeros(mask.shape)
    steps = 3000 if audit is None else audit["target_steps"]
    return {"ux": ux, "uy": z.copy(), "uz": z.copy(), "rho": np.ones(mask.shape), "steps": steps}


def test_the_executor_completes_a_whole_phase_into_validated_records(executed_p0):
    runs, auth, man = executed_p0
    assert man["terminal_status"] == "PHASE_COMPLETE"
    assert man["counts"]["completed"] == man["counts"]["universe"] > 0
    assert man["counts"]["failed"] == 0
    doc = vf.validate_phase_manifest("P0", runs, authority=auth, require_production=False)
    assert len(doc["_records"]) == man["counts"]["completed"]
    assert man["counts"]["universe"] == (man["counts"]["completed"] + man["counts"]["refused"]
                                         + man["counts"]["failed"])


def test_a_case_record_is_immutable_and_a_resume_needs_an_exact_match(executed_p0):
    runs, auth, man = executed_p0
    cid = man["completed"][0]["case_id"]
    rec, path = vf.read_case_record(runs, cid)
    again = vf.write_case_record(runs, rec)
    assert again[1] == "REUSED_EXACT_MATCH"
    tampered = dict(rec, completed_steps=rec["completed_steps"] + 1)
    with pytest.raises(ValueError):
        vf.write_case_record(runs, tampered)
    with pytest.raises(FileExistsError):
        vf.write_case_record(runs, rec, allow_resume=False)


def test_the_record_filename_is_derived_from_the_case_id(executed_p0):
    runs, auth, man = executed_p0
    cid = man["completed"][0]["case_id"]
    assert (runs / vf.case_record_filename(cid)).exists()
    assert vf.case_record_filename(cid) != vf.case_record_filename(cid + "x")


@pytest.mark.parametrize("mutate", [
    {"phase": "P1a"}, {"case_id": "other"}, {"row_sha256": "0" * 64},
    {"source_tree": "0" * 40}, {"correction_version": "PREFLIGHT-C1"},
    {"status": "SOMETHING_ELSE"},
])
def test_a_tampered_case_record_is_refused(executed_p0, mutate):
    runs, auth, man = executed_p0
    rec, _ = vf.read_case_record(runs, man["completed"][0]["case_id"])
    bad = dict(rec, **mutate)
    with pytest.raises(ValueError):
        vf.validate_case_record(bad, authority=auth, phase="P0")


def test_a_missing_record_breaks_its_manifest(executed_p0):
    runs, auth, man = executed_p0
    (runs / vf.case_record_filename(man["completed"][0]["case_id"])).unlink()
    with pytest.raises(vf.ManifestMissing):
        vf.validate_phase_manifest("P0", runs, authority=auth, require_production=False)


def test_a_wrong_record_hash_breaks_its_manifest(executed_p0):
    runs, auth, man = executed_p0
    doc = json.loads((runs / "manifest_P0.json").read_text())
    doc["completed"][0]["record_sha256"] = "0" * 64
    (runs / "manifest_P0.json").write_text(vf.canonical_json(doc) + "\n")
    with pytest.raises(vf.ManifestMissing):
        vf.validate_phase_manifest("P0", runs, authority=auth, require_production=False)


def test_a_nonempty_but_incomplete_manifest_fails(executed_p0):
    """The superseded check passed on a NONEMPTY list (erratum PE-18)."""
    runs, auth, man = executed_p0
    doc = json.loads((runs / "manifest_P0.json").read_text())
    doc["completed"] = doc["completed"][:1]
    doc["counts"]["completed"] = 1
    (runs / "manifest_P0.json").write_text(vf.canonical_json(doc) + "\n")
    assert doc["completed"]                            # nonempty...
    with pytest.raises(vf.ManifestMissing):            # ...and still not a phase
        vf.validate_phase_manifest("P0", runs, authority=auth, require_production=False)


def test_an_extra_case_not_in_the_plan_is_refused(executed_p0):
    runs, auth, man = executed_p0
    doc = json.loads((runs / "manifest_P0.json").read_text())
    doc["completed"].append(dict(doc["completed"][0], case_id="not.in.the.plan"))
    doc["counts"]["completed"] += 1
    (runs / "manifest_P0.json").write_text(vf.canonical_json(doc) + "\n")
    with pytest.raises(vf.ManifestMissing):
        vf.validate_phase_manifest("P0", runs, authority=auth, require_production=False)


def test_a_duplicate_completed_case_is_refused(executed_p0):
    runs, auth, man = executed_p0
    doc = json.loads((runs / "manifest_P0.json").read_text())
    doc["completed"].append(dict(doc["completed"][0]))
    doc["counts"]["completed"] += 1
    (runs / "manifest_P0.json").write_text(vf.canonical_json(doc) + "\n")
    with pytest.raises(vf.ManifestMissing):
        vf.validate_phase_manifest("P0", runs, authority=auth, require_production=False)


def test_one_record_hash_cannot_be_cited_for_two_physically_distinct_rows(executed_p0):
    runs, auth, man = executed_p0
    doc = json.loads((runs / "manifest_P0.json").read_text())
    a, b = doc["completed"][0], doc["completed"][1]
    b["record_sha256"] = a["record_sha256"]
    (runs / "manifest_P0.json").write_text(vf.canonical_json(doc) + "\n")
    with pytest.raises(vf.ManifestMissing):
        vf.validate_phase_manifest("P0", runs, authority=auth, require_production=False)


def test_a_manifest_from_a_superseded_correction_version_is_refused(executed_p0):
    runs, auth, man = executed_p0
    doc = json.loads((runs / "manifest_P0.json").read_text())
    doc["correction_version"] = "PREFLIGHT-C1"
    (runs / "manifest_P0.json").write_text(vf.canonical_json(doc) + "\n")
    with pytest.raises(vf.ManifestMissing):
        vf.validate_phase_manifest("P0", runs, authority=auth, require_production=False)


def test_a_manifest_whose_plan_hash_does_not_match_the_derived_plan_is_refused(executed_p0):
    runs, auth, man = executed_p0
    doc = json.loads((runs / "manifest_P0.json").read_text())
    doc["phase_plan_sha256"] = "0" * 64
    (runs / "manifest_P0.json").write_text(vf.canonical_json(doc) + "\n")
    with pytest.raises(vf.ManifestMissing):
        vf.validate_phase_manifest("P0", runs, authority=auth, require_production=False)


def test_p1b_expectations_are_derived_from_predecessor_records_not_supplied():
    rows = vf.execution_matrix()["rows"]
    recs = {}
    for S in vf.SCIENTIFIC_RESOLUTIONS:               # one candidate fails its triage screen
        for st, C in (("blocked", 25.0), ("open", 26.0)):
            cid = "p1a.%d.%s" % (S, st)
            recs[cid] = _fake_rec(C, cid, S=S, level="central", state=st, bridge=(3, 2))
    keep, adaptive = vf.derive_expected_rows("P1b", rows, predecessor_records=recs)
    assert adaptive["rule"].startswith("candidates surviving")
    assert (3, 2) not in [tuple(s) for s in adaptive["surviving"]]
    assert all(r["bridge"]["w"] != 3 or r["bridge"]["kz"] != 2
               for r in keep if isinstance(r["bridge"], dict))


def test_the_p2b_assembler_accepts_no_free_form_input():
    src = inspect.signature(vf.assemble_p2b_from_runs).parameters
    assert set(src) == {"runs_dir", "backend"}
    assert not hasattr(vf, "build_freeze")
    body = inspect.getsource(vf._p2b_decision_core)
    for call in ("field_contrast(", "xi_envelope(", "reachable_set_admission(",
                 "select_bridges(", "candidate_forcing_gates(", "candidate_resolution_gates(",
                 "fixed_step_discrepancy(", "actual_xi_discrepancy(",
                 "candidate_admission_from_records(", "_atomic_write_json("):
        assert call in body, call
    # the two wrappers have NON-OVERLAPPING provenance and neither takes an override
    assert set(inspect.signature(vf._test_only_assemble_p2b_from_runs).parameters) == {
        "runs_dir", "authority", "backend"}


def test_the_assembler_recomputes_rather_than_trusting_stored_values():
    """c and Xi are rebuilt from the raw compact scalars, so an altered stored value cannot pass
    unnoticed — there is no stored c_field or Xi to alter."""
    sci = {"p_node_in": 1.0, "p_node_out": 0.0, "p_face1": 0.7, "p_face2": 0.3,
           "q1_volume": 2.0, "q2_volume": 2.0}
    fc = vf.field_contrast(sci)
    assert fc["c_field"] == pytest.approx((2.0 / 0.3 - 2.0 / 0.7) / (2.0 / 0.3 + 2.0 / 0.7))
    assert fc["A1"] > 0 and fc["A2"] > 0


# ---- PE-19: the executor -------------------------------------------------------------------

def test_every_matrix_row_resolves_to_exactly_one_fixture_or_coupon():
    seen = {}
    for r in vf.execution_matrix()["rows"]:
        if not isinstance(r["bridge"], dict) and r["bridge"] is not None:
            continue                                   # a P3/P4 template slot
        mask, meta, kind = drv.resolve_row(r)
        assert kind in ("fixture", "coupon")
        seen.setdefault(meta["mask_sha256"], set()).add(kind)
    assert seen


def test_p2b_makes_no_solver_call_and_has_its_own_authority_gate():
    body = inspect.getsource(drv.execute_phase)
    assert "assemble_p2b_from_runs" in body
    assert "require_assembly_authorisation" in body
    assert drv.AUTHORISED_ASSEMBLY_PHASES == ()
    assert drv.AUTHORISED_SOLVING_PHASES == ()
    assert "solver_records" in inspect.getsource(vf._p2b_decision_core)


def test_a_failed_case_stops_the_phase(tmp_path, monkeypatch):
    auth = vf.execution_authority("P0", require_clean=False)

    calls = {"n": 0}

    def failing(mask, g, phase, row, tau=None, audit=None, backend="reference"):
        calls["n"] += 1
        res = _fake_provider(mask, g, phase, row, tau, audit, backend)
        if calls["n"] == 3:
            res["steps"] = vf.MAX_STEPS               # NORMAL_UNCONVERGED
        return res

    man = drv._test_only_execute("P0", tmp_path, failing, auth)
    assert man["terminal_status"] == "PHASE_STOPPED_UNCONVERGED"
    assert man["terminal_stop_reason"] == "NORMAL_UNCONVERGED"
    assert man["counts"]["failed"] == 1
    assert man["counts"]["refused"] > 0               # every later row refused, not run


def test_the_cli_exposes_no_arbitrary_solver_callback():
    src = (REPO / "puckworks/validation/slow/rp_d_lc_001b.py").read_text()
    tree = ast.parse(src)
    main = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "main"][0]
    dump = ast.dump(main)
    assert "result_provider" not in dump
    assert "provider" not in dump


def test_the_production_api_has_no_provider_or_authority_override():
    """Erratum PE-34: the superseded signature took BOTH a solver callback and an authority."""
    params = inspect.signature(drv.execute_phase).parameters
    assert list(params) == ["phase", "runs_dir", "backend"]
    assert "result_provider" not in params and "authority" not in params
    # the seam exists, is private, and marks everything it writes
    assert drv._test_only_execute.__name__.startswith("_")
    assert "TEST_ONLY" in inspect.getsource(drv._test_only_execute)


def test_a_test_only_record_cannot_enter_a_production_manifest(executed_p0):
    runs, auth, man = executed_p0
    assert man["provenance_mode"] == "TEST_ONLY"
    with pytest.raises(vf.ManifestMissing):
        vf.validate_phase_manifest("P0", runs, authority=auth, require_production=True)
    rec, _ = vf.read_case_record(runs, man["completed"][0]["case_id"])
    with pytest.raises(vf.ManifestMissing):
        vf.assert_production_record(rec)


def test_the_real_solver_is_never_reached_by_any_test(monkeypatch):
    """Instrumentation: the guarded call site refuses, and lb_reference.solve is not called."""
    from puckworks.models.brewer2026 import lb_reference
    calls = []
    monkeypatch.setattr(lb_reference, "solve",
                        lambda *a, **k: calls.append(1) or (_ for _ in ()).throw(
                            AssertionError("the real solver was reached")))
    with pytest.raises(drv.ExecutionNotAuthorised):
        drv.solve(np.ones((4, 4, 4), bool), g=1e-6, phase="P0")
    for phase in drv.SOLVING_MODES:
        with pytest.raises((drv.ExecutionNotAuthorised, vf.FreezeMissing, vf.ManifestMissing,
                            vf.ExecutionAuthorityError)):
            drv.run_phase(phase)
    assert calls == []


def test_all_phases_refuse_at_this_head():
    assert drv.AUTHORISED_SOLVING_PHASES == ()
    for phase in drv.SOLVING_MODES + ("P2b",):
        with pytest.raises((drv.ExecutionNotAuthorised, vf.FreezeMissing, vf.ManifestMissing,
                            vf.ExecutionAuthorityError)):
            drv.run_phase(phase)


# ==========================================================================================
# 13. C3 correction regressions — PE-22 … PE-39
# ==========================================================================================

# ---- the physically coherent TEST_ONLY field generator (erratum PE-69) ----------------------
# A 1D Stokes network solved on the ACTUAL mask, so the synthetic fields obey the relations the
# gates test rather than accidentally satisfying them:
#
#   per-plane conductance density   k(x) = SCALE * W(x) * H(x)^3      (the plane-channel law)
#   band resistance                 R    = sum_x 1/k(x)
#   body-force head over one period dPbox= g * nx
#   band flux                       q    = dPbox / (12*nu*R)          -> q proportional to g
#   effective pressure              p(x) = 1/3 - dPbox * cumfrac(x)   -> rho = 3(p + g x) ~ 1
#
# Consequences the gates actually consume: every flux is proportional to g; every conductance,
# outlet share, contrast, area and actual Xi is forcing-independent; Q ~ S, dP ~ S^-2 and C ~ S^3
# under the frozen g(S) = G_REF (S_REF/S)^3, matching the frozen resolution comparison
# coordinate; the two lanes of a MIRROR fixture split the drop asymmetrically, so c_field is
# nondegenerate; the two lanes of an IDENTICAL fixture are exactly equal, so the lateral pressure
# gap is exactly zero and R_identical is exactly 1.
#
# SYNTH_LANE_CONDUCTANCE_SCALE is a TEST-FIXTURE prefactor on the lane conductance only. It
# exists so the synthetic candidate family straddles the frozen Xi window and exercises the
# one-below/three-inside selection. It is a property of this test fixture, NOT of the apparatus:
# it alters no scientific constant, no tolerance, no window and no gate.
SYNTH_NU = 12.0 * vf.NU
SYNTH_LANE_CONDUCTANCE_SCALE = 3.0
#: The candidate the synthetic P1a triage screen prunes.
SYNTH_PRUNED_CANDIDATE = (9, 2)


def _band_profile(mask, y0, y1, scale=1.0):
    """(W(x), H(x), n(x), k(x)) for one y-band, derived from the mask alone."""
    nx = mask.shape[0]
    W = np.zeros(nx)
    H = np.zeros(nx)
    n = np.zeros(nx)
    fl = ~mask[:, y0:y1, :]
    cols = fl.sum(axis=2)                       # (x, y) fluid depth in z
    W[:] = (cols > 0).sum(axis=1)
    H[:] = cols.max(axis=1)
    n[:] = fl.sum(axis=(1, 2))
    k = scale * W * H ** 3
    return W, H, n, k


def _band_solution(mask, g, y0, y1, scale=1.0):
    """The 1D Stokes network solution for one band: flux, per-plane p_eff, node counts."""
    nx = mask.shape[0]
    W, H, n, k = _band_profile(mask, y0, y1, scale=scale)
    if not (k > 0).all():
        return None
    r = 1.0 / k
    R = float(r.sum())
    dP_box = g * nx
    q = dP_box / (SYNTH_NU * R)
    frac = np.cumsum(r) / R
    p_eff = 1.0 / 3.0 - dP_box * frac
    return {"q": q, "p_eff": p_eff, "n": n, "R": R}


def _coherent_fields(mask, meta, g, kind, lane_gain=(1.0, 1.0)):
    """ux and rho for one case, from the 1D network above."""
    ux = np.zeros(mask.shape)
    rho = np.ones(mask.shape)
    ny = mask.shape[1]
    if kind == "coupon":
        bands = [(0, ny, 1.0, 1.0)]
    else:
        y1a, y1b = meta["lane1_y"]
        y2a, y2b = meta["lane2_y"]
        bands = [(y1a, y1b, SYNTH_LANE_CONDUCTANCE_SCALE, lane_gain[0]),
                 (y2a, y2b, SYNTH_LANE_CONDUCTANCE_SCALE, lane_gain[1])]
    p_sum = np.zeros(mask.shape[0])
    solved = 0
    for y0, y1, scale, gain in bands:
        sol = _band_solution(mask, g, y0, y1, scale=scale)
        if sol is None:                                    # pragma: no cover - degenerate band
            continue
        solved += 1
        sub = ~mask[:, y0:y1, :]
        with np.errstate(invalid="ignore", divide="ignore"):
            per = np.where(sol["n"] > 0, sol["q"] * gain / np.maximum(sol["n"], 1), 0.0)
        ux[:, y0:y1, :] = np.where(sub, per[:, None, None], 0.0)
        rho[:, y0:y1, :] = 3.0 * (sol["p_eff"][:, None, None]
                                  + g * np.arange(mask.shape[0], dtype=float)[:, None, None])
        p_sum += sol["p_eff"]
    if kind != "coupon" and solved:
        # the divider/plenum region is a common node: it carries no net axial flow here, and its
        # density is the mean of the two lanes' effective pressures
        mid = p_sum / solved
        y1b, y2a = meta["lane1_y"][1], meta["lane2_y"][0]
        rho[:, y1b:y2a, :] = 3.0 * (mid[:, None, None]
                                    + g * np.arange(mask.shape[0], dtype=float)[:, None, None])
        rho[:, :meta["lane1_y"][0], :] = rho[:, meta["lane1_y"][0]:meta["lane1_y"][0] + 1, :]
        rho[:, meta["lane2_y"][1]:, :] = rho[:, meta["lane2_y"][1] - 1:meta["lane2_y"][1], :]
    return ux, rho


def _pipeline_provider(prune=SYNTH_PRUNED_CANDIDATE):
    """Deterministic, physically coherent TEST_ONLY stand-in. One candidate is given a 1 % axial
    artifact so the P1a triage screen prunes it. The real kernel is never reached."""
    def provider(mask, g, phase, row, tau=None, audit=None, backend="reference"):
        kind = "coupon" if row["kind"] in ("axial_coupon", "bridge_coupon") else "fixture"
        if kind == "coupon":
            meta = {}
        else:
            _, meta = drv.resolve_row(row)[0], drv.resolve_row(row)[1]
        gain = (1.0, 1.0)
        b = row.get("bridge")
        if (kind == "fixture" and isinstance(b, dict) and row["state"] == "open"
                and (prune == "all" or (b["w"], b["kz"]) == prune)):
            gain = (1.01, 1.01)
        ux, rho = _coherent_fields(mask, meta, g, kind, lane_gain=gain)
        z = np.zeros(mask.shape)
        steps = 3000 if audit is None else audit["target_steps"]
        return {"ux": ux, "uy": z.copy(), "uz": z.copy(), "rho": rho, "steps": steps}
    return provider


@pytest.fixture(scope="module")
def synthetic_prefreeze(tmp_path_factory):
    """P0 -> P1a -> adaptive P1b -> adaptive P2a, end to end, with NO solver."""
    d = tmp_path_factory.mktemp("prefreeze")
    auth = vf.execution_authority("P0", require_clean=False)
    prov = _pipeline_provider()
    mans, recs, out = {}, {}, {}
    for phase in ("P0", "P1a", "P1b", "P2a"):
        out[phase] = drv._test_only_execute(phase, d, prov, auth, manifests=dict(mans),
                                            records=dict(recs))
        doc = vf.validate_phase_manifest(phase, d, authority=auth,
                                         predecessor_records=dict(recs),
                                         require_production=False)
        recs.update(doc.pop("_records", {}))
        mans[phase] = doc
    return d, auth, out, recs


def test_the_whole_pre_freeze_pipeline_runs_with_no_solver(synthetic_prefreeze):
    d, auth, out, recs = synthetic_prefreeze
    for phase in ("P0", "P1a", "P1b", "P2a"):
        m = out[phase]
        assert m["terminal_status"] == "PHASE_COMPLETE", phase
        c = m["counts"]
        assert c["universe"] == c["completed"] + c["refused"] + c["failed"], phase
    assert out["P1b"]["counts"]["refused"] > 0        # a candidate really was pruned
    assert out["P2a"]["counts"]["refused"] > 0
    assert len(recs) > 400


def test_p1a_prunes_a_candidate_and_the_refused_rows_stay_in_the_universe(synthetic_prefreeze):
    d, auth, out, recs = synthetic_prefreeze
    triage = vf.p1a_triage(recs)
    rejected = [k for k, v in triage.items() if v["rejected"]]
    assert SYNTH_PRUNED_CANDIDATE in rejected
    assert all(v["may_admit"] is False for v in triage.values())
    m = out["P1b"]
    for entry in m["refused"]:
        assert entry["reason"] in vf.REFUSAL_REASONS
    ids = set(m["phase_universe_case_ids"])
    assert {e["case_id"] for e in m["refused"]} <= ids     # refused rows remain MEMBERS


def test_every_adaptive_ledger_is_an_exact_disjoint_partition(synthetic_prefreeze):
    d, auth, out, recs = synthetic_prefreeze
    for phase in ("P0", "P1a", "P1b", "P2a"):
        m = out[phase]
        comp = {e["case_id"] for e in m["completed"]}
        ref = {e["case_id"] for e in m["refused"]}
        fail = {e["case_id"] for e in m["failed"]}
        uni = set(m["phase_universe_case_ids"])
        assert comp | ref | fail == uni, phase
        assert not (comp & ref) and not (comp & fail) and not (ref & fail), phase


def test_the_artifact_evidence_schema_is_flat_and_plural(synthetic_prefreeze):
    """Erratum PE-23/PE-24: the superseded assembler raised KeyError then TypeError here."""
    d, auth, out, recs = synthetic_prefreeze
    adm = vf.artifact_admission_from_records(recs)
    assert adm and len(adm) == len(SCI)
    checked = 0
    for key, e in adm.items():
        for combo, ev in e["combinations"].items():
            vf.assert_artifact_evidence(ev)              # flat + plural, or it raises
            for k in ("normal_record_sha256", "audit_record_sha256",
                      "pressure_plane_record_sha256"):
                assert all(isinstance(h, str) and len(h) == 64 for h in ev[k])
            assert not set(ev["normal_case_ids"]) & set(ev["audit_case_ids"])
            if e["admitted"]:
                assert ev["audit_case_ids"], "fixed-step evidence must be present"
                assert ev["pressure_plane_case_ids"], "paired node-offset evidence required"
                # PE-42: the ratio is formed from an EXACT open/blocked pair
                assert ev["node_offset_R"]["method"].startswith("R_offset_j = C_open_offset_j")
                assert ev["node_offset_R"]["open_case_id"] != ev["node_offset_R"][
                    "blocked_case_id"]
                checked += 1
    assert checked > 0
    pruned = adm[SYNTH_PRUNED_CANDIDATE]["combinations"]
    assert not pruned[list(pruned)[0]]["audit_case_ids"]   # the pruned candidate has none


def test_eleven_of_twelve_candidates_are_admitted_and_the_pruned_one_is_not(synthetic_prefreeze):
    d, auth, out, recs = synthetic_prefreeze
    adm = vf.artifact_admission_from_records(recs)
    assert adm[SYNTH_PRUNED_CANDIDATE]["admitted"] is False
    assert sum(1 for v in adm.values() if v["admitted"]) == len(SCI) - 1


def test_the_node_offset_term_is_measured_and_not_silently_zero(synthetic_prefreeze):
    """Erratum PE-32: the superseded term was always exactly 0.0 because nothing was passed."""
    d, auth, out, recs = synthetic_prefreeze
    adm = vf.artifact_admission_from_records(recs)
    ev = list(adm[(3, 2)]["combinations"].values())[0]
    assert ev["evidence_complete"] is True
    assert ev["node_offset_R"] is not None
    assert ev["u_artifact_R"] == pytest.approx(ev["u_fixed_step_R"] + ev["u_pressure_plane_R"]
                                               + ev["u_serialization_R"])
    # the ratio comes from an exact open/blocked pair, never a same-state normalisation
    assert len(ev["node_offset_R"]["R_offsets"]) == len(ev["node_offset_R"]["offsets"])
    assert ev["node_offset_R"]["R_offsets"][0]["offset"] == 0


def test_missing_node_offset_evidence_fails_rather_than_contributing_zero(synthetic_prefreeze):
    d, auth, out, recs = synthetic_prefreeze
    stripped = {k: dict(v, scientific=dict(v.get("scientific") or {}, node_offsets=None))
                for k, v in recs.items()}
    adm = vf.artifact_admission_from_records(stripped)
    assert adm[(3, 2)]["admitted"] is False
    ev = list(adm[(3, 2)]["combinations"].values())[0]
    assert ev["evidence_complete"] is False and ev["pass"] is False
    assert "node-offset" in ev["reason"]


def test_audits_are_paired_evidence_and_never_independent_observations(synthetic_prefreeze):
    """Erratum PE-30: coupon selection matched on `kind`, which is identical for a normal row and
    its audit, so re-runs entered estimates as new observations."""
    d, auth, out, recs = synthetic_prefreeze
    normals = vf._normal_only(recs, "bridge_coupon", (3, 2))
    audits = vf._audits_for(recs, "bridge_coupon", (3, 2))
    assert normals and audits
    assert not set(normals) & set(audits)
    assert all(r["run_mode"] == "NORMAL" for r in normals.values())
    pairs = vf._pair_normal_with_audit(normals, audits)
    assert pairs and set(pairs) <= set(normals)
    for base_id, pr in pairs.items():
        assert pr["audit"]["row"]["audit_of_case_id"] == base_id
        assert pr["audit"]["status"] == "FIXED_STEP_AUDIT_COMPLETED"


def test_c_and_xi_uncertainty_come_from_their_own_families(synthetic_prefreeze):
    """Erratum PE-31: the superseded assembler reused the artifact's u_R for both."""
    d, auth, out, recs = synthetic_prefreeze
    key = (3, 2)
    u_c = vf.fixed_step_discrepancy(
        vf._pair_normal_with_audit(vf._normal_only(recs, "candidate_blocked_mirror", key),
                                   vf._audits_for(recs, "candidate_blocked_mirror", key)),
        lambda r: vf.field_contrast(r["scientific"])["c_field"] if r.get("scientific") else None,
        "c_field")
    u_xi = vf.fixed_step_discrepancy(
        vf._pair_normal_with_audit(vf._normal_only(recs, "bridge_coupon", key),
                                   vf._audits_for(recs, "bridge_coupon", key)),
        lambda r: (r.get("scientific") or {}).get("G_bridge_coupon"), "G_bridge_coupon")
    for u in (u_c, u_xi):
        assert u["n_pairs"] > 0
        assert u["normal_case_ids"] and u["audit_case_ids"]
        assert not set(u["normal_case_ids"]) & set(u["audit_case_ids"])
        assert u["overlaps"] == "none; this family's own pairs only"
    assert set(u_c["normal_case_ids"]) != set(u_xi["normal_case_ids"])


def test_the_forcing_and_resolution_gates_actually_execute(synthetic_prefreeze):
    d, auth, out, recs = synthetic_prefreeze
    fg = vf.candidate_forcing_gates(recs, (3, 2))
    rg = vf.candidate_resolution_gates(recs, (3, 2), {"w": 3, "kz": 2})
    assert fg["n_gates"] > 0 and rg["n_gates"] > 0
    for g in fg["gates"]:
        assert g["status"] in vf.FORCING_GATE_STATUS
        assert g["case_ids"] and g["record_sha256"]
    for g in rg["gates"]:
        assert g["kind"].endswith("NOT_A_CONVERGENCE_ORDER_ESTIMATE")
        assert g["case_ids"] and g["record_sha256"]
        assert g["status"] in ("PASS", "FAIL")
    # the gates produce real verdicts with real lineage; whether a SYNTHETIC field passes them is
    # not the point, and a failure here would correctly make the candidate unavailable
    assert isinstance(fg["pass"], bool) and isinstance(rg["pass"], bool)
    assert {g["quantity"].split("@")[0] for g in fg["gates"]} & set(vf.COMPONENTWISE_QUANTITIES)


def test_p2b_is_durable_and_immutable(synthetic_p2b):
    """Erratum PE-25: the superseded assembler returned a dict and wrote nothing.

    Erratum PE-71: this runs the PRIVATE TEST_ONLY wrapper. The production wrapper is never
    reached by monkeypatching away its guards.
    """
    d, auth, man = synthetic_p2b
    assert man["phase_kind"] == "ARITHMETIC_ASSEMBLY_NO_SOLVER_CALL"
    assert man["solver_records"] == []
    assert (d / "candidate_ledger.json").exists()
    assert (d / "manifest_P2b.json").exists()
    ledger = json.loads((d / "candidate_ledger.json").read_text())
    assert ledger["n_declared"] == len(SCI)
    assert man["selection_status"] == "SELECTED"
    fz = json.loads((d / "proposed_bridge_freeze.json").read_text())
    assert len(fz["frozen_bridges"]) == vf.N_FROZEN_BRIDGES
    assert fz["status"] == "PROPOSED_PENDING_SECOND_EXACT_HEAD_REVIEW"
    assert fz["p3_p4_authorised"] is False
    # a P2b artifact is immutable: re-running must reuse the exact match, never overwrite
    again = vf._test_only_assemble_p2b_from_runs(d, auth)
    assert again["terminal_status"] == man["terminal_status"]


def test_a_p2b_artifact_cannot_be_overwritten_with_different_content(tmp_path):
    doc = {"a": 1}
    path = tmp_path / "x.json"
    assert vf._atomic_write_json(path, doc)[1] == "WRITTEN"
    assert vf._atomic_write_json(path, doc)[1] == "REUSED_EXACT_MATCH"
    with pytest.raises(ValueError):
        vf._atomic_write_json(path, {"a": 2})


# ---- PE-27: predecessor success ------------------------------------------------------------

def test_a_stopped_predecessor_cannot_satisfy_the_next_phase(synthetic_prefreeze, tmp_path):
    d, auth, out, recs = synthetic_prefreeze
    import shutil
    work = tmp_path / "w"
    shutil.copytree(d, work)
    doc = json.loads((work / "manifest_P0.json").read_text())
    doc["terminal_status"] = "PHASE_STOPPED_UNCONVERGED"
    (work / "manifest_P0.json").write_text(vf.canonical_json(doc) + "\n")
    with pytest.raises(vf.ManifestMissing) as exc:
        vf.require_phase_manifests("P1a", runs_dir=work, authority=auth,
                                   require_production=False)
    assert "PHASE_COMPLETE" in str(exc.value)


def test_the_exact_predecessor_key_set_is_required(synthetic_prefreeze, tmp_path):
    d, auth, out, recs = synthetic_prefreeze
    import shutil
    work = tmp_path / "w2"
    shutil.copytree(d, work)
    doc = json.loads((work / "manifest_P1b.json").read_text())
    doc["predecessor_manifests"] = {}
    (work / "manifest_P1b.json").write_text(vf.canonical_json(doc) + "\n")
    with pytest.raises(vf.ManifestMissing):
        vf.require_phase_manifests("P2a", runs_dir=work, authority=auth)


# ---- PE-35: exact per-case solver configuration ---------------------------------------------

@pytest.mark.parametrize("tau", [2.0, 1.2])
def test_the_effective_solver_configuration_is_per_row(tau):
    rows = [r for r in vf.execution_matrix()["rows"] if r["tau_plus"] == tau]
    assert rows
    cfg = vf.effective_solver_config(rows[0])
    assert cfg["tau_plus"] == tau
    assert cfg["return_fields"] == list(vf.RETURN_FIELDS)
    assert cfg["min_steps"] == vf.MIN_STEPS and cfg["max_steps"] == vf.MAX_STEPS


def test_a_fixed_step_row_pins_min_and_max_to_its_target():
    row = [r for r in vf.execution_matrix()["rows"]
           if r["run_mode"] == "FIXED_STEP_REEXECUTION_1P5X"][0]
    plan = vf.fixed_step_audit_plan(3000, "NORMAL_CONVERGED")
    cfg = vf.effective_solver_config(row, audit=plan)
    assert cfg["min_steps"] == cfg["max_steps"] == cfg["fixed_step_target"] == plan["target_steps"]


def test_a_record_whose_configuration_is_not_the_rows_is_refused(executed_p0):
    runs, auth, man = executed_p0
    rec, _ = vf.read_case_record(runs, man["completed"][0]["case_id"])
    for mutate in ({"tau_plus": 1.2}, {"min_steps": 1}, {"return_fields": ["rho"]},
                   {"backend": "taichi"}):
        bad = dict(rec, solver_config=dict(rec["solver_config"], **mutate))
        with pytest.raises(ValueError):
            vf.validate_case_record(bad, row=rec["row"], phase="P0")


# ---- PE-36: Arm J is physically resolvable ---------------------------------------------------

@pytest.mark.parametrize("S", [vf.S_SMOKE, vf.S_COARSE, vf.S_FINE])
def test_the_obstruction_changes_only_the_plenum_and_preserves_the_relationship(S):
    b = {"w": 5, "kz": 3}
    nom, meta = vf.build_fixture(S, bridge=b, connected=True)
    obs, meta_o = vf.build_fixture(S, bridge=b, connected=True, obstructed=True)
    r = vf.obstruction_report(nom, obs, meta)
    assert r["differs_from_nominal"] and r["n_changed_voxels"] > 0
    assert r["all_changes_in_plenum"] and r["lane_and_bridge_unchanged"]
    assert r["relationship_preserved"]
    c = vf.connectivity(obs, meta_o)
    assert c["single_connected"] and c["no_lateral_bypass"]
    assert meta_o["obstructed"] is True and meta_o["obstruction"]["kind"] == "PLENUM_SLAB_001B"


def test_an_obstructed_row_resolves_to_an_obstructed_mask():
    inst = vf.instantiate_post_freeze_matrix([{"w": w, "kz": k}
                                              for w, k in ((3, 2), (3, 3), (5, 2), (5, 3))])
    p4 = [r for r in inst if r["obstructed"]]
    assert p4
    row = p4[0]
    mask, meta, kind = drv.resolve_row(row)
    assert meta["obstructed"] is True
    nominal = dict(row, obstructed=False)
    nmask, _, _ = drv.resolve_row(nominal)
    assert vf.mask_hash(mask) != vf.mask_hash(nmask)


def test_resolution_is_deterministic_and_an_unresolved_template_is_refused():
    rows = [r for r in vf.execution_matrix()["rows"] if r["phase"] == "P3"]
    tpl = [r for r in rows if isinstance(r["bridge"], str)][0]
    with pytest.raises(ValueError) as exc:
        drv.resolve_row(tpl)
    assert "UNRESOLVED placeholder" in str(exc.value)
    row = [r for r in vf.execution_matrix()["rows"] if r["kind"] == "identical_path_control"][0]
    a = drv.resolve_row(row)[1]["mask_sha256"]
    b = drv.resolve_row(row)[1]["mask_sha256"]
    assert a == b


@pytest.mark.parametrize("bad", [{"kind": "not_a_kind"}, {"variant": "nope"},
                                 {"state": "nope"}])
def test_an_unknown_row_attribute_fails_closed(bad):
    row = dict([r for r in vf.execution_matrix()["rows"]
                if r["kind"] == "identical_path_control"][0], **bad)
    with pytest.raises(ValueError):
        drv.resolve_row(row)


# ---- PE-37: replicates ------------------------------------------------------------------------

def test_a_determinism_replicate_must_reproduce_its_base_payload(synthetic_prefreeze):
    d, auth, out, recs = synthetic_prefreeze
    reps = out["P0"]["replicates"]
    assert reps
    for r in reps:
        assert r["pass"] is True
        assert r["scientific_payload_sha256"] == r["base_scientific_payload_sha256"]
        assert len(r["scientific_payload_sha256"]) == 64


def test_a_replicate_that_does_not_reproduce_its_base_breaks_the_manifest(synthetic_prefreeze,
                                                                         tmp_path):
    d, auth, out, recs = synthetic_prefreeze
    import shutil
    work = tmp_path / "w3"
    shutil.copytree(d, work)
    doc = json.loads((work / "manifest_P0.json").read_text())
    doc["replicates"][0]["pass"] = False
    (work / "manifest_P0.json").write_text(vf.canonical_json(doc) + "\n")
    with pytest.raises(vf.ManifestMissing):
        vf.validate_phase_manifest("P0", work, authority=auth, require_production=False)


# ---- PE-38/PE-39: CLI and authority ------------------------------------------------------------

@pytest.mark.parametrize("jobs", [0, 2, 6])
def test_only_one_job_is_accepted(jobs):
    with pytest.raises(ValueError) as exc:
        drv.run_phase("plan", jobs=jobs)
    assert "--jobs" in str(exc.value)


def test_a_non_reference_backend_fails_before_execution():
    with pytest.raises(ValueError):
        drv.run_phase("plan", backend="taichi")


def test_an_unknown_phase_fails_closed():
    with pytest.raises(ValueError):
        drv.run_phase("P9")
    with pytest.raises(ValueError):
        drv.execute_phase("P9", "/tmp")


def test_the_output_directory_is_the_runs_directory_actually_used(tmp_path, monkeypatch):
    seen = {}
    monkeypatch.setattr(drv, "execute_phase",
                        lambda phase, runs_dir, backend="reference": seen.setdefault(
                            "runs_dir", pathlib.Path(runs_dir)))
    drv.run_phase("P0", out_dir=tmp_path)
    assert seen["runs_dir"] == tmp_path


def test_solving_and_assembly_authority_are_separate_and_both_empty():
    assert drv.AUTHORISED_SOLVING_PHASES == ()
    assert drv.AUTHORISED_ASSEMBLY_PHASES == ()
    src = (REPO / "puckworks/validation/slow/rp_d_lc_001b.py").read_text()
    assert "AUTHORISED_ASSEMBLY_PHASES = ()" in src
    assert "AUTHORISED_SOLVING_PHASES = ()" in src
    body = inspect.getsource(drv.require_assembly_authorisation)
    assert "AUTHORISED_ASSEMBLY_PHASES" in body and "AUTHORISED_SOLVING_PHASES" not in body


def test_every_phase_including_p2b_refuses_at_this_head():
    for phase in drv.SOLVING_MODES + drv.ASSEMBLY_MODES:
        with pytest.raises((drv.ExecutionNotAuthorised, vf.FreezeMissing, vf.ManifestMissing,
                            vf.ExecutionAuthorityError)):
            drv.run_phase(phase)


def test_the_real_solver_call_count_is_zero_across_the_whole_pipeline(monkeypatch,
                                                                     synthetic_prefreeze):
    from puckworks.models.brewer2026 import lb_reference
    calls = []
    monkeypatch.setattr(lb_reference, "solve", lambda *a, **k: calls.append(1))
    with pytest.raises(drv.ExecutionNotAuthorised):
        drv.solve(np.ones((4, 4, 4), bool), g=1e-6, phase="P0")
    for phase in drv.SOLVING_MODES + drv.ASSEMBLY_MODES:
        with pytest.raises((drv.ExecutionNotAuthorised, vf.FreezeMissing, vf.ManifestMissing,
                            vf.ExecutionAuthorityError)):
            drv.run_phase(phase)
    assert calls == []


# ---- PE-24 unit: flat hash lists ---------------------------------------------------------------

@pytest.mark.parametrize("bad", [[["a" * 64]], ["short"], ["A" * 64], ["a" * 64, "a" * 64],
                                 "notalist", [None]])
def test_a_nested_short_uppercase_or_duplicate_hash_list_is_refused(bad):
    with pytest.raises(ValueError):
        vf.assert_flat_hash_list(bad, "test")


def test_a_valid_flat_hash_list_passes():
    vals = ["%064x" % i for i in range(3)]
    assert vf.assert_flat_hash_list(vals, "test") == vals


# ==========================================================================================
# 14. C4 correction regressions — PE-40 … PE-59
# ==========================================================================================

def test_no_diagnostic_row_survives_and_every_row_is_a_solve():
    """Erratum PE-41: C3 scheduled 144 rows that each went through the result provider, for
    offsets that are re-reads of a field already computed."""
    m = vf.execution_matrix()
    assert not [r for r in m["rows"] if r["kind"] == "pressure_plane_diagnostic"]
    assert m["planned_pressure_plane_diagnostic_rows"] == 0
    assert m["planned_solver_invocations"] == m["n_rows"]
    assert m["planned_normal_solves"] + m["planned_fixed_step_audits"] == m["n_rows"]
    assert "pressure_plane" not in vf.RECORD_SCHEMAS


def test_the_node_offset_summary_is_extracted_without_a_provider_call():
    mask, meta, res, g = _face_case()
    summary = vf.node_offset_summary(res["ux"], res["rho"], mask, meta, g, case_id="x")
    assert summary["offsets"] == [0] + list(meta["node_offsets"])
    assert summary["quantity"] == "CONDUCTANCE_PER_OFFSET_NOT_A_RATIO"
    for row in summary["per_offset"]:
        for k in ("inlet_plane_id", "inlet_index", "outlet_plane_id", "outlet_index",
                  "flux_plane_id", "flux_index", "Q_volume", "p_in", "p_out", "delta_P",
                  "conductance", "n_fluid_inlet", "n_fluid_outlet", "n_fluid_flux",
                  "finite", "delta_P_nonzero"):
            assert k in row, k
    tree = ast.parse(inspect.getsource(vf.node_offset_summary).lstrip())
    fn = tree.body[0]
    calls = {n.func.attr for n in ast.walk(fn)
             if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)}
    calls |= {n.func.id for n in ast.walk(fn)
              if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)}
    assert not (calls & {"solve", "provider", "_guarded_result_provider"})


def test_offset_zero_reproduces_the_case_conductance():
    mask, meta, res, g = _face_case()
    rec = drv.case_record(res, mask, meta, g, stage="unit")
    zero = rec["node_offsets"]["per_offset"][0]
    assert zero["offset"] == 0
    assert zero["conductance"] == pytest.approx(rec["Q_volume"] / rec["dP"], rel=1e-12)


def _offset_rec(case_id, state, cond, S=2, level="central", bridge=(3, 2), offsets=(0, 1, 2)):
    per = [{"offset": o, "inlet_plane_id": "x_node_in_off%d" % o, "inlet_index": 10 - o,
            "outlet_plane_id": "x_node_out_off%d" % o, "outlet_index": 100 + o,
            "flux_plane_id": "x_meas_a", "flux_index": 99, "Q_volume": 1.0, "p_in": 1.0,
            "p_out": 0.0, "delta_P": 1.0, "conductance": c, "n_fluid_inlet": 8,
            "n_fluid_outlet": 8, "n_fluid_flux": 8, "finite": True, "delta_P_nonzero": True}
           for o, c in zip(offsets, cond)]
    return {"case_id": case_id, "kind": "identical_path_control", "run_mode": "NORMAL",
            "row": {"S": S, "forcing_level": level, "state": state, "phase": "P1a",
                    "tau_plus": 2.0, "variant": "identical", "perturbation": None,
                    "obstructed": False, "swapped": False, "run_mode": "NORMAL",
                    "coupon_orientation": None,
                    "bridge": {"w": bridge[0], "kz": bridge[1]}, "case_id": case_id},
            "scientific": {"Q_volume": cond[0], "dP": 1.0,
                           "node_offsets": {"offsets": list(offsets), "per_offset": per,
                                            "all_finite": True}}}


def test_a_same_state_normalised_conductance_is_not_R():
    """Erratum PE-42, the regression the brief asks for: same-state C_j/C_0 is stable while the
    correctly paired open/blocked R_j moves. The superseded calculation would have reported no
    node-offset sensitivity at all."""
    # both states drift by the SAME factor across offsets, so C_j/C_0 is identical in each
    blocked = _offset_rec("b", "blocked", [10.0, 10.5, 11.0])
    opened = _offset_rec("o", "open", [10.0, 11.0, 12.0])
    for rec in (blocked, opened):
        per = rec["scientific"]["node_offsets"]["per_offset"]
        same_state = [p["conductance"] / per[0]["conductance"] for p in per]
        assert same_state[0] == 1.0
    b_ratio = [p["conductance"] / blocked["scientific"]["node_offsets"]["per_offset"][0][
        "conductance"] for p in blocked["scientific"]["node_offsets"]["per_offset"]]
    o_ratio = [p["conductance"] / opened["scientific"]["node_offsets"]["per_offset"][0][
        "conductance"] for p in opened["scientific"]["node_offsets"]["per_offset"]]
    out = vf.node_offset_R(opened, blocked)
    assert out["R_nominal"] == pytest.approx(1.0)
    # the CORRECT ratio moves; neither same-state sequence on its own reveals it
    assert out["max_abs_movement"] > 0.03
    assert out["u_pressure_plane_R"] == pytest.approx(
        vf.NUMERICAL_DISCREPANCY_SAFETY_FACTOR * out["max_abs_movement"])
    assert out["max_abs_movement"] == pytest.approx(12.0 / 11.0 - 1.0, rel=1e-9)
    # neither same-state sequence alone equals the correctly paired movement
    assert max(abs(v - 1.0) for v in o_ratio) != pytest.approx(out["max_abs_movement"])
    assert max(abs(v - 1.0) for v in b_ratio) != pytest.approx(out["max_abs_movement"])


@pytest.mark.parametrize("mutate", [{"S": 3}, {"forcing_level": "high"}, {"tau_plus": 1.2},
                                    {"obstructed": True}, {"perturbation": "one_voxel_plug"}])
def test_a_mismatched_configuration_cannot_be_paired(mutate):
    blocked = _offset_rec("b", "blocked", [10.0, 10.1, 10.2])
    opened = _offset_rec("o", "open", [10.0, 10.1, 10.2])
    opened["row"].update(mutate)
    with pytest.raises(ValueError):
        vf.node_offset_R(opened, blocked)


def test_mismatched_offsets_or_planes_cannot_be_paired():
    blocked = _offset_rec("b", "blocked", [10.0, 10.1], offsets=(0, 1))
    opened = _offset_rec("o", "open", [10.0, 10.1, 10.2])
    with pytest.raises(ValueError):
        vf.node_offset_R(opened, blocked)
    blocked2 = _offset_rec("b", "blocked", [10.0, 10.1, 10.2])
    blocked2["scientific"]["node_offsets"]["per_offset"][1]["inlet_index"] = 999
    with pytest.raises(ValueError):
        vf.node_offset_R(opened, blocked2)


def test_a_missing_node_offset_summary_fails_rather_than_contributing_zero():
    blocked = _offset_rec("b", "blocked", [10.0, 10.1, 10.2])
    opened = _offset_rec("o", "open", [10.0, 10.1, 10.2])
    opened["scientific"]["node_offsets"] = None
    with pytest.raises(ValueError):
        vf.node_offset_R(opened, blocked)


def test_a_wrong_state_pair_is_refused():
    a = _offset_rec("a", "blocked", [10.0, 10.1, 10.2])
    b = _offset_rec("b", "blocked", [10.0, 10.1, 10.2])
    with pytest.raises(ValueError):
        vf.node_offset_R(a, b)


# ---- PE-43 … PE-46: the pressure control ----------------------------------------------------

def test_the_faces_must_pair_exactly_not_merely_intersect():
    mask, meta, res, g = _face_case()
    d = vf.lateral_pressure_delta_record(res["rho"], mask, meta, g)
    assert d["masks_pair_exactly"] is True
    assert d["n_fluid_face1"] == d["n_fluid_face2"] == d["n_paired_fluid"] > 0
    assert len(d["paired_mask_sha256"]) == 64
    src = inspect.getsource(vf.lateral_pressure_delta_record)
    body = src.split('"""')[2]                       # code only, excluding the docstring
    assert "m1 & m2" not in body                     # an intersection is not a pairing
    assert "np.array_equal(m1, m2)" in body


def test_a_face_mask_mismatch_fails_closed():
    mask, meta, res, g = _face_case()
    xs, _ = meta["bridge_x"]
    zs, _ = meta["bridge_z"]
    holed = mask.copy()
    holed[xs, meta["y_face1"], zs] = True             # solidify one node on face 1 only
    with pytest.raises(ValueError) as exc:
        vf.lateral_pressure_delta_record(res["rho"], holed, meta, g)
    assert "pair exactly" in str(exc.value)


def test_the_paired_statistics_include_the_maximum_not_only_the_mean():
    mask, meta, res, g = _face_case()
    d = vf.lateral_pressure_delta_record(res["rho"], mask, meta, g)
    for k in ("mean_delta_p", "abs_mean_delta_p", "max_abs_delta_p", "min_delta_p",
              "max_delta_p", "spatial_sd_delta_p", "n_paired_fluid"):
        assert k in d, k
    assert d["spatial_sd_role"] == (
        "SPATIAL_NONUNIFORMITY_DIAGNOSTIC_NOT_A_NUMERICAL_ERROR_BOUND")


def _delta(mean, mx, sd=0.0):
    return {"mean_delta_p": mean, "abs_mean_delta_p": abs(mean), "max_abs_delta_p": mx,
            "spatial_sd_delta_p": sd,
            "spatial_sd_role": "SPATIAL_NONUNIFORMITY_DIAGNOSTIC_NOT_A_NUMERICAL_ERROR_BOUND"}


def test_a_zero_mean_produced_by_cancellation_cannot_pass():
    """Erratum PE-45: alternating paired differences with a zero mean passed the superseded
    control however large the individual differences were."""
    out = vf.lateral_pressure_upper_bounds(_delta(0.0, 1.0), axial_pressure_scale=1.0,
                                           audit_delta=_delta(0.0, 1.0),
                                           expected_zero_driver=True)
    assert out["mean_pass"] is True                   # the mean alone would have passed
    assert out["max_pass"] is False
    assert out["pass"] is False


def test_a_small_mean_and_maximum_pass():
    out = vf.lateral_pressure_upper_bounds(_delta(1e-6, 2e-6), axial_pressure_scale=1.0,
                                           audit_delta=_delta(1e-6, 2e-6),
                                           expected_zero_driver=True)
    assert out["mean_pass"] and out["max_pass"] and out["pass"]


def test_the_fixed_step_discrepancy_can_change_the_pressure_verdict():
    ok = vf.lateral_pressure_upper_bounds(_delta(1e-4, 2e-4), axial_pressure_scale=1.0,
                                          audit_delta=_delta(1e-4, 2e-4),
                                          expected_zero_driver=True)
    assert ok["pass"] is True
    drift = vf.lateral_pressure_upper_bounds(_delta(1e-4, 2e-4), axial_pressure_scale=1.0,
                                             audit_delta=_delta(1e-3, 2e-3),
                                             expected_zero_driver=True)
    assert drift["u_mean_gap"] > 0 and drift["pass"] is False


def test_missing_audit_evidence_yields_no_upper_bound_verdict():
    out = vf.lateral_pressure_upper_bounds(_delta(0.0, 0.0), axial_pressure_scale=1.0,
                                           audit_delta=None, expected_zero_driver=True)
    assert out["evidence_complete"] is False
    assert out["pass"] is None and "no fixed-step evidence" in out["reason"]


def test_no_standard_error_term_is_used_adjudicatively():
    src = inspect.getsource(vf.lateral_pressure_upper_bounds)
    assert "sqrt" not in src and "standard_error" not in src


# ---- PE-47 … PE-49: gate completeness --------------------------------------------------------

def test_the_forcing_verdict_requires_the_exact_quantity_set():
    """Erratum PE-47: a nonempty intersection with an allowlist is not completeness."""
    partial = [vf.componentwise_forcing_gate(
        "Q_open@S2", [{"forcing_level": lv, "g": 1.0, "value": 1.0, "case_id": "c%s" % lv,
                       "record_sha256": "%064x" % i}
                      for i, lv in enumerate(vf.FORCING_LEVELS)])]
    v = vf.forcing_invariance_verdict(partial)
    assert v["pass"] is False and v["complete"] is False
    assert set(v["missing_quantities"]) == set(vf.REQUIRED_FORCING_QUANTITIES) - {"Q_open"}


def test_the_resolution_gate_uses_actual_xi_not_raw_g_bridge():
    src = inspect.getsource(vf.candidate_resolution_gates)
    assert "ACTUAL_XI_DEFINITION" in src
    assert vf.ACTUAL_XI_DEFINITION.startswith("Xi = G_bridge_coupon * (1/A1 + 1/A2)")
    assert "area_case_ids" in src
    # erratum PE-62: raw G_bridge is gated too, under its OWN name, and never as Xi
    assert "G_bridge_coupon" in vf.CANDIDATE_RESOLUTION_QUANTITIES
    assert "Xi_actual" in vf.CANDIDATE_RESOLUTION_QUANTITIES


def test_the_mass_flux_zero_gate_uses_a_mass_scale():
    """Erratum PE-48: q_lat is a MASS flux and was normalised by a volume-flux quantity."""
    src = inspect.getsource(vf.candidate_forcing_gates)
    assert "Q_mass_diagnostic" in src
    assert 'lambda r: (r.get("scientific") or {}).get("Q_volume")) if s["S"] == S)' not in src


# ---- PE-58/PE-59: shared verdict and explicit binding ---------------------------------------

def test_one_shared_function_classifies_a_case():
    assert drv._decision_bearing_ok.__doc__ and "shared" in drv._decision_bearing_ok.__doc__
    v = vf.case_decision_verdict({}, {}, "NORMAL_UNCONVERGED")
    assert v["pass"] is False and v["reason"] == "NORMAL_UNCONVERGED"
    assert v["effect"] == "STOPS_THE_PHASE"
    ok = vf.case_decision_verdict({}, {"mach": {"pass": True}}, "NORMAL_CONVERGED")
    assert ok["pass"] is True and ok["reason"] is None


def test_a_manifest_cannot_relabel_a_failed_case_as_completed(executed_p0):
    """Erratum PE-58: validation rehashed records but never recomputed their verdict."""
    runs, auth, man = executed_p0
    cid = man["completed"][0]["case_id"]
    rec, path = vf.read_case_record(runs, cid)
    bad = dict(rec, scientific=dict(rec["scientific"],
                                    mach=dict(rec["scientific"]["mach"], **{"pass": False})))
    path.unlink()
    payload = vf.canonical_json(bad) + "\n"
    path.write_text(payload)
    doc = json.loads((runs / "manifest_P0.json").read_text())
    for e in doc["completed"]:
        if e["case_id"] == cid:
            e["record_sha256"] = hashlib.sha256(path.read_bytes()).hexdigest()
    (runs / "manifest_P0.json").write_text(vf.canonical_json(doc) + "\n")
    with pytest.raises(vf.ManifestMissing) as exc:
        vf.validate_phase_manifest("P0", runs, authority=auth, require_production=False)
    assert "recomputes as failed" in str(exc.value)


def test_every_replicate_and_audit_row_names_its_exact_base():
    """Erratum PE-55/PE-59: the base was inferred by searching for the first row that shared a
    few fields, and P3 audits carried audit_of_case_id = None."""
    rows = vf.execution_matrix()["rows"]
    by_id = {r["case_id"]: r for r in rows}
    reps = [r for r in rows if r["kind"] == "determinism_replicate"]
    assert reps
    for r in reps:
        assert r["replicate_of_case_id"], r["case_id"]
        vf.assert_replicate_compatible(r, by_id[r["replicate_of_case_id"]])
    audits = [r for r in rows if r["run_mode"] == "FIXED_STEP_REEXECUTION_1P5X"]
    assert audits
    for a in audits:
        assert a["audit_of_case_id"], a["case_id"]
        vf.assert_audit_compatible(a, by_id[a["audit_of_case_id"]])


@pytest.mark.parametrize("mutate", [{"S": 3}, {"state": "open"}, {"obstructed": True},
                                    {"perturbation": "one_voxel_plug"},
                                    {"bridge": {"w": 9, "kz": 4}}])
def test_an_incompatible_base_is_refused(mutate):
    rows = vf.execution_matrix()["rows"]
    rep = [r for r in rows if r["kind"] == "determinism_replicate"][1]
    base = dict({r["case_id"]: r for r in rows}[rep["replicate_of_case_id"]], **mutate)
    with pytest.raises(ValueError):
        vf.assert_replicate_compatible(rep, base)


def test_the_instantiated_matrix_rebinds_every_reference():
    inst = vf.instantiate_post_freeze_matrix([{"w": w, "kz": k}
                                              for w, k in ((3, 2), (3, 3), (5, 2), (5, 3))])
    ids = {r["case_id"] for r in inst}
    assert len(ids) == len(inst)
    for r in inst:
        assert not isinstance(r["bridge"], str)
        for k in ("audit_of_case_id", "replicate_of_case_id"):
            if r.get(k):
                assert r[k] in ids, (r["case_id"], k)
        mask, meta, kind = drv.resolve_row(r)
        assert meta["obstructed"] == bool(r["obstructed"])


# ---- PE-51 … PE-56: P2b schema, validator, runs_dir, promotion ------------------------------

def test_the_freeze_gate_uses_the_runs_directory_it_is_given(tmp_path):
    assert "runs_dir" in inspect.signature(vf.require_freeze).parameters
    with pytest.raises(vf.FreezeMissing) as exc:
        vf.require_freeze("P3", runs_dir=tmp_path)
    assert str(tmp_path) in str(exc.value)
    body = inspect.getsource(drv.require_execution_authorisation)
    assert "require_freeze(phase, runs_dir=runs_dir)" in body


def test_a_proposed_freeze_never_satisfies_the_p3_gate(tmp_path):
    inst = {"rows": [], "rows_sha256": "a" * 64}
    (tmp_path / "instantiated_p3_p4_matrix.json").write_text(vf.canonical_json(inst) + "\n")
    fz = {"rows_sha256": "a" * 64, "frozen_bridges": [{"w": 3, "kz": 2}] * 4,
          "correction_version": vf.CORRECTION_VERSION, "provenance_mode": "PRODUCTION",
          "status": "PROPOSED_PENDING_SECOND_EXACT_HEAD_REVIEW",
          "instantiated_matrix_file_sha256": hashlib.sha256(
              (tmp_path / "instantiated_p3_p4_matrix.json").read_bytes()).hexdigest()}
    fz.update(vf.config_hashes())
    (tmp_path / "bridge_freeze.json").write_text(vf.canonical_json(fz) + "\n")
    with pytest.raises(vf.FreezeMissing) as exc:
        vf.require_freeze("P3", runs_dir=tmp_path)
    assert "APPROVED" in str(exc.value)


def test_the_promotion_wrapper_binds_evidence_and_authorises_nothing():
    src = inspect.getsource(vf.make_approved_freeze)
    for k in ("proposed_bridge_freeze_file_sha256", "manifest_P2b_file_sha256",
              "candidate_ledger_file_sha256", "instantiated_matrix_file_sha256",
              "rows_sha256", "review_commit", "review_tree", "authorises_p3_p4"):
        assert k in src, k
    assert vf.APPROVED_FREEZE_STATUS == "APPROVED_BY_EXACT_HEAD_REVIEW"
    assert "changes no scientific value" in " ".join(src.replace("**", "").split())


def test_the_p2b_validator_reopens_everything(tmp_path):
    assert "validate_p2b_manifest" in inspect.getsource(vf.require_phase_manifests)
    with pytest.raises(vf.ManifestMissing):
        vf.validate_p2b_manifest(tmp_path)


def test_the_p2b_manifest_is_not_mutated_after_persistence():
    src = inspect.getsource(vf._p2b_decision_core)
    assert 'manifest["artifacts_written"] = written' not in src
    assert "no in-memory mutation after persistence" in src
    assert '"rows_sha256"' in src and "content_sha256" not in src


# ==========================================================================================
# 15. C5 correction regressions — PE-60 … PE-76
# ==========================================================================================

# ---- A. the pressure decision path (errata PE-60, PE-61) ------------------------------------

def _pressure_ev(records, key):
    return vf.lateral_pressure_evidence_from_records(records, key)


def test_the_pressure_upper_bound_is_functionally_reached_by_the_candidate_path(
        synthetic_prefreeze):
    """Erratum PE-60: a helper-unit test is not enough — the PRODUCTION candidate path must
    call the same pure calculation. Proved by instrumenting the real function."""
    d, auth, out, recs = synthetic_prefreeze
    calls = []
    real = vf.lateral_pressure_upper_bounds

    def spy(normal_delta, axial_pressure_scale, audit_delta=None, expected_zero_driver=False):
        calls.append({"has_audit": audit_delta is not None,
                      "expected_zero_driver": bool(expected_zero_driver)})
        return real(normal_delta, axial_pressure_scale, audit_delta=audit_delta,
                    expected_zero_driver=expected_zero_driver)

    vf.lateral_pressure_upper_bounds = spy
    try:
        adm = vf.candidate_admission_from_records(recs)
    finally:
        vf.lateral_pressure_upper_bounds = real
    assert calls, "the candidate admission path never reached lateral_pressure_upper_bounds()"
    assert all(c["expected_zero_driver"] for c in calls)
    assert all(c["has_audit"] for c in calls)
    # and the verdict it produced is what admission consumed
    assert any(v["admitted"] for v in adm.values())
    for key, entry in adm.items():
        if entry["admitted"]:
            assert entry["pressure"], key
            for ev in entry["pressure"].values():
                assert ev["mean_pass"] is True and ev["max_pass"] is True


def test_the_final_pressure_verdict_needs_both_mean_and_maximum(synthetic_prefreeze):
    d, auth, out, recs = synthetic_prefreeze
    key = (3, 2)
    ev = _pressure_ev(recs, key)
    assert ev, "no pressure evidence was built"
    for combo, e in ev.items():
        vf.assert_pressure_evidence(e)
        assert e["evidence_complete"] is True, combo
        assert e["audit_case_id"] and e["audit_case_id"] != e["normal_case_id"]
        assert e["normal_record_sha256"] and e["audit_record_sha256"]
        assert e["face_ids"] == list(vf.PRESSURE_FACE_IDS)
        assert e["paired_mask_sha256"]
        assert e["tolerance"] == vf.TOL_LATERAL_DRIVER_REL
        assert e["pass"] is (e["mean_pass"] and e["max_pass"])
        assert e["spatial_sd_role"].startswith("SPATIAL_NONUNIFORMITY_DIAGNOSTIC")


@pytest.mark.parametrize("field,bad", [("max_abs_delta_p", 1.0), ("mean_delta_p", 1.0)])
def test_a_point_pass_with_a_failed_bound_rejects(synthetic_prefreeze, field, bad):
    """A small point mean can coexist with an excessive maximum or an excessive audit
    movement; either one must reject (errata PE-45, PE-46, PE-61)."""
    d, auth, out, recs = synthetic_prefreeze
    key = (3, 2)
    target = None
    for cid, r in vf._normal_only(recs, "identical_path_control", key).items():
        if r["row"]["state"] == "open":
            target = cid
            break
    assert target
    broken = dict(recs)
    rec = json.loads(json.dumps(recs[target]))
    lp = rec["scientific"]["lateral_pressure"]
    assert lp["measured_zero_driver_point_pass"] is True       # the POINT screen still passes
    lp["delta_pointwise"][field] = bad
    broken[target] = rec
    ev = _pressure_ev(broken, key)
    combo = "%d.%s" % (rec["row"]["S"], rec["row"]["forcing_level"])
    assert ev[combo]["pass"] is False
    assert vf.candidate_admission_from_records(broken)[key]["admitted"] is False


def test_a_missing_pressure_audit_makes_the_combination_unavailable(synthetic_prefreeze):
    d, auth, out, recs = synthetic_prefreeze
    key = (3, 2)
    dropped = {cid: r for cid, r in recs.items()
               if not (r.get("kind") == "identical_path_control"
                       and r["run_mode"] != "NORMAL" and vf._bridge_key(r) == key)}
    ev = _pressure_ev(dropped, key)
    assert ev and all(e["pass"] is False for e in ev.values())
    assert all(e["evidence_complete"] is False for e in ev.values())
    assert all("no fixed-step audit" in e["reason"] for e in ev.values())
    assert vf.candidate_admission_from_records(dropped)[key]["admitted"] is False


def test_a_mismatched_pressure_face_footprint_is_refused(synthetic_prefreeze):
    d, auth, out, recs = synthetic_prefreeze
    key = (3, 2)
    audit_id = next(cid for cid, r in vf._audits_for(recs, "identical_path_control", key).items()
                    if recs[r["row"]["audit_of_case_id"]]["row"]["state"] == "open")
    tampered = dict(recs)
    rec = json.loads(json.dumps(recs[audit_id]))
    rec["scientific"]["pressure_faces"][0]["footprint_x"] = [0, 1]
    tampered[audit_id] = rec
    ev = _pressure_ev(tampered, key)
    bad = [e for e in ev.values() if e["pass"] is False]
    assert bad and any("footprints or mask hashes differ" in e["reason"] for e in bad)


def test_no_spatial_standard_error_appears_in_an_adjudicative_pressure_bound():
    src = inspect.getsource(vf.lateral_pressure_upper_bounds)
    assert "sqrt" not in src and "/ math.sqrt" not in src
    src2 = inspect.getsource(vf.lateral_pressure_evidence_from_records)
    assert "spatial_sd" in src2                       # retained...
    for line in src2.splitlines():                    # ...but never in a bound
        if "spatial_sd" in line:
            assert "upper" not in line and "_pass" not in line


def test_p1a_may_still_only_triage_and_never_admit(synthetic_prefreeze):
    d, auth, out, recs = synthetic_prefreeze
    triage = vf.p1a_triage(recs)
    assert all(v["may_admit"] is False for v in triage.values())
    src = inspect.getsource(vf.derive_expected_rows)
    assert "candidate_admission_from_records" in src


def test_p2a_eligibility_is_the_complete_p1b_verdict_not_the_artifact_alone(synthetic_prefreeze):
    d, auth, out, recs = synthetic_prefreeze
    keep, adaptive = vf.derive_expected_rows("P2a", vf.execution_matrix()["rows"],
                                             predecessor_records=recs)
    assert "BOTH pressure upper bounds" in adaptive["rule"]
    assert "candidate_admission" in adaptive
    admitted = set(adaptive["admitted"])
    assert admitted == {k for k, v in vf.candidate_admission_from_records(recs).items()
                        if v["admitted"]}


# ---- B. forcing completeness (errata PE-62 … PE-65) -----------------------------------------

def test_the_p0_aggregate_verdict_is_durable_complete_and_passing(synthetic_prefreeze):
    d, auth, out, recs = synthetic_prefreeze
    doc = json.loads((d / "manifest_P0.json").read_text())
    sci = doc["phase_science"]
    assert sci is not None and doc["phase_science_sha256"] == vf.record_hash(sci)
    assert sci["complete"] is True and sci["pass"] is True
    assert sci["failed_families"] == []
    assert sci["n_families"] == sci["expected_families"]
    # and it RECOMPUTES from the records rather than being taken on trust
    p0_recs = {c["case_id"]: vf.read_case_record(d, c["case_id"])[0] for c in doc["completed"]}
    assert vf.record_hash(vf.p0_aggregate_science(p0_recs)) == doc["phase_science_sha256"]


def test_the_exact_p0_required_sets_are_adjudicated(synthetic_prefreeze):
    d, auth, out, recs = synthetic_prefreeze
    sci = json.loads((d / "manifest_P0.json").read_text())["phase_science"]
    ref = sci["reference_blocked_forcing"]
    assert ref["required_quantities"] == sorted(vf.P0_REFERENCE_FORCING_QUANTITIES)
    assert ref["present_quantities"] == ref["required_quantities"]
    assert ref["missing_quantities"] == [] and ref["unexpected_quantities"] == []
    assert ref["missing_resolutions"] == [] and ref["missing_levels"] == {}
    assert sci["reference_blocked_resolution"]["required_quantities"] == sorted(
        vf.P0_REFERENCE_RESOLUTION_QUANTITIES)
    want = {"%s.%s" % (lv, o) for lv in vf.P0_COUPON_LEVELS for o in vf.P0_COUPON_ORIENTATIONS}
    assert set(sci["axial_coupon_forcing"]) == want
    assert set(sci["axial_coupon_resolution"]) == want
    for v in sci["axial_coupon_forcing"].values():
        assert v["required_quantities"] == sorted(vf.P0_COUPON_FORCING_QUANTITIES)
        assert v["pass"] is True
    # the empty reference contrast/area set is a RECORDED fact, not an omission
    assert sci["reference_contrast_quantities"] == []
    assert "no bridge" in sci["reference_contrast_applicability"]


def test_p1a_refuses_a_p0_whose_aggregate_verdict_does_not_pass(synthetic_prefreeze, tmp_path):
    d, auth, out, recs = synthetic_prefreeze
    import shutil
    work = tmp_path / "w"
    shutil.copytree(d, work)
    doc = json.loads((work / "manifest_P0.json").read_text())
    sci = dict(doc["phase_science"])
    sci["pass"] = False
    sci["failed_families"] = ["forcing:reference_blocked"]
    doc["phase_science"] = sci
    doc["phase_science_sha256"] = vf.record_hash(sci)
    (work / "manifest_P0.json").write_text(vf.canonical_json(doc) + "\n")
    with pytest.raises(vf.ManifestMissing):        # it no longer recomputes...
        vf.validate_phase_manifest("P0", work, authority=auth, require_production=False)
    with pytest.raises(vf.ManifestMissing):        # ...and P1a refuses either way
        vf.require_phase_manifests("P1a", runs_dir=work, require_production=False)


def test_a_p0_manifest_without_an_aggregate_verdict_is_refused(synthetic_prefreeze, tmp_path):
    d, auth, out, recs = synthetic_prefreeze
    import shutil
    work = tmp_path / "w2"
    shutil.copytree(d, work)
    doc = json.loads((work / "manifest_P0.json").read_text())
    doc["phase_science"] = None
    doc["phase_science_sha256"] = None
    (work / "manifest_P0.json").write_text(vf.canonical_json(doc) + "\n")
    with pytest.raises(vf.ManifestMissing) as exc:
        vf.validate_phase_manifest("P0", work, authority=auth, require_production=False)
    assert "aggregate scientific verdict" in str(exc.value)


def test_the_exact_candidate_component_and_boundary_sets(synthetic_prefreeze):
    d, auth, out, recs = synthetic_prefreeze
    fg = vf.candidate_forcing_gates(recs, (5, 3))
    assert fg["component"]["required_quantities"] == sorted(
        vf.CANDIDATE_COMPONENT_FORCING_QUANTITIES)
    assert fg["boundary"]["required_quantities"] == sorted(
        vf.CANDIDATE_BOUNDARY_FORCING_QUANTITIES)
    for v in (fg["component"], fg["boundary"]):
        assert v["present_quantities"] == v["required_quantities"]
        assert v["missing_quantities"] == [] and v["unexpected_quantities"] == []
        assert v["missing_resolutions"] == [] and v["missing_levels"] == {}
        assert v["pass"] is True
    # every gate really carries all three levels at BOTH resolutions
    for S in vf.SCIENTIFIC_RESOLUTIONS:
        for q in vf.CANDIDATE_BOUNDARY_FORCING_QUANTITIES:
            g = next(x for x in fg["boundary"]["gates"] if x["quantity"] == "%s@S%d" % (q, S))
            assert sorted(g["levels"]) == sorted(vf.FORCING_LEVELS)
            assert g["forcing_independent"] is True
            assert g["reduction_rule"] == "FROZEN_DIRECT_RELATIVE_SPREAD_NOT_DIVIDED_BY_g"


@pytest.mark.parametrize("drop", ["R_identical", "s_blocked", "s_open", "A1", "A2",
                                  "A_field", "A_series_inverse", "Xi_actual", "c_field"])
def test_a_missing_boundary_quantity_fails_the_exact_set(drop):
    gates = [vf.componentwise_forcing_gate(
        "%s@S%d" % (q, S),
        [{"forcing_level": lv, "g": 1.0, "value": 1.0, "case_id": "c%s%s%s" % (q, S, lv),
          "record_sha256": vf.record_hash([q, S, lv])} for lv in vf.FORCING_LEVELS],
        forcing_independent=True)
        for q in vf.CANDIDATE_BOUNDARY_FORCING_QUANTITIES if q != drop
        for S in vf.SCIENTIFIC_RESOLUTIONS]
    v = vf.forcing_invariance_verdict(gates, vf.CANDIDATE_BOUNDARY_FORCING_QUANTITIES)
    assert v["pass"] is False and v["complete"] is False
    assert v["missing_quantities"] == [drop]


def test_a_quantity_at_one_resolution_or_two_levels_is_not_completeness():
    one_res = [vf.componentwise_forcing_gate(
        "%s@S%d" % (q, vf.S_COARSE),
        [{"forcing_level": lv, "g": 1.0, "value": 1.0, "case_id": "c%s%s" % (q, lv),
          "record_sha256": vf.record_hash([q, lv])} for lv in vf.FORCING_LEVELS],
        forcing_independent=True)
        for q in vf.CANDIDATE_BOUNDARY_FORCING_QUANTITIES]
    v = vf.forcing_invariance_verdict(one_res, vf.CANDIDATE_BOUNDARY_FORCING_QUANTITIES)
    assert v["pass"] is False
    assert v["missing_per_resolution"]["S%d" % vf.S_FINE]
    two_levels = vf.componentwise_forcing_gate(
        "R_identical@S2", [{"forcing_level": lv, "g": 1.0, "value": 1.0, "case_id": "c" + lv,
                            "record_sha256": vf.record_hash(lv)}
                           for lv in ("low", "central")], forcing_independent=True)
    assert two_levels["pass"] is False and two_levels["missing_levels"] == ["high"]


def test_a_similarly_named_surrogate_is_unexpected_not_accepted():
    gates = [vf.componentwise_forcing_gate(
        "%s@S%d" % (q, S),
        [{"forcing_level": lv, "g": 1.0, "value": 1.0, "case_id": "c%s%s%s" % (q, S, lv),
          "record_sha256": vf.record_hash([q, S, lv])} for lv in vf.FORCING_LEVELS],
        forcing_independent=True)
        for q in tuple(vf.CANDIDATE_BOUNDARY_FORCING_QUANTITIES) + ("A_field_like",)
        for S in vf.SCIENTIFIC_RESOLUTIONS]
    v = vf.forcing_invariance_verdict(gates, vf.CANDIDATE_BOUNDARY_FORCING_QUANTITIES)
    assert v["unexpected_quantities"] == ["A_field_like"]
    assert v["complete"] is False and v["pass"] is False


def test_one_failed_component_cannot_be_cancelled_by_another(synthetic_prefreeze):
    good = vf.componentwise_forcing_gate(
        "Q_open@S2", [{"forcing_level": lv, "g": {"low": 0.5, "central": 1.0, "high": 2.0}[lv],
                       "value": {"low": 0.5, "central": 1.0, "high": 2.0}[lv],
                       "case_id": "g" + lv, "record_sha256": vf.record_hash("g" + lv)}
                      for lv in vf.FORCING_LEVELS])
    bad = vf.componentwise_forcing_gate(
        "Q_blocked@S2", [{"forcing_level": lv, "g": {"low": 0.5, "central": 1.0, "high": 2.0}[lv],
                          "value": {"low": 0.4, "central": 1.0, "high": 2.4}[lv],
                          "case_id": "b" + lv, "record_sha256": vf.record_hash("b" + lv)}
                         for lv in vf.FORCING_LEVELS])
    assert good["pass"] is True and bad["pass"] is False
    v = vf.forcing_invariance_verdict([good, bad], ("Q_open", "Q_blocked"),
                                      resolutions=(vf.S_COARSE,))
    assert v["pass"] is False and v["failed_quantities"] == ["Q_blocked@S2"]


def test_mass_quantities_use_a_mass_scale(synthetic_prefreeze):
    d, auth, out, recs = synthetic_prefreeze
    fg = vf.candidate_forcing_gates(recs, (5, 3))
    for S in vf.SCIENTIFIC_RESOLUTIONS:
        g = next(x for x in fg["component"]["gates"]
                 if x["quantity"] == "q_lat_mass@S%d" % S)
        assert g["expected_zero"] is True
        assert "MASS" in g["zero_scale_source"] and "Q_volume" in g["zero_scale_source"]


def test_the_pressure_component_gate_requires_the_final_upper_bounds(synthetic_prefreeze):
    """Erratum PE-60 §6.2: three small point means may not substitute for a failed bound."""
    d, auth, out, recs = synthetic_prefreeze
    fg = vf.candidate_forcing_gates(recs, (5, 3))
    g = next(x for x in fg["component"]["gates"] if x["quantity"] == "delta_p_lateral@S2")
    assert g["pressure_upper_bound_prerequisite"]["failed_or_missing"] == []
    stripped = {cid: r for cid, r in recs.items()
                if not (r.get("kind") == "identical_path_control"
                        and r["run_mode"] != "NORMAL" and vf._bridge_key(r) == (5, 3))}
    fg2 = vf.candidate_forcing_gates(stripped, (5, 3))
    g2 = next(x for x in fg2["component"]["gates"] if x["quantity"] == "delta_p_lateral@S2")
    assert g2["pass"] is False
    assert "cannot substitute" in g2["reason"]


def test_the_tau_cross_check_is_diagnostic_only_with_no_invented_tolerance():
    dsp = vf.TAU_CROSS_CHECK_DISPOSITION
    assert dsp["status"] == "DIAGNOSTIC_ONLY"
    assert dsp["exact_frozen_rule_exists"] is False
    assert dsp["tolerance"] is None and dsp["may_alter"] == []
    for forbidden in ("admission", "uncertainty", "classification", "selection"):
        assert forbidden in dsp["may_not_alter"]
    assert dsp["retained_in_matrix"] is True
    rows = [r for r in vf.execution_matrix()["rows"] if r["kind"] == "tau_cross_check"]
    assert len(rows) == len(vf.SCIENTIFIC_RESOLUTIONS)   # still visible in the matrix
    assert all(r["tau_plus"] == vf.TAU_CROSS_CHECK for r in rows)


# ---- C. resolution completeness (erratum PE-66) ----------------------------------------------

def test_the_exact_candidate_resolution_set_is_adjudicated(synthetic_prefreeze):
    d, auth, out, recs = synthetic_prefreeze
    rg = vf.candidate_resolution_gates(recs, (5, 3), {"w": 5, "kz": 3})
    assert rg["required_quantities"] == sorted(vf.CANDIDATE_RESOLUTION_QUANTITIES)
    assert rg["present_quantities"] == rg["required_quantities"]
    assert rg["missing_quantities"] == [] and rg["unexpected_quantities"] == []
    assert rg["pass"] is True
    fams = {g["quantity"]: g["family"] for g in rg["gates"]}
    for q in ("c_field", "A1", "A2", "A_field", "A_series_inverse", "C_blocked", "s_blocked"):
        assert fams[q] == "candidate_blocked_common_mode_ports", q
    feats = next(g for g in rg["gates"] if g["quantity"] == "c_field")["features"]
    for f in ("h_low", "h_high", "bridge_w", "bridge_kz", "port_depth", "duct_traverse"):
        assert f in feats
    assert fams["Xi_actual"] == "actual_xi_derived"
    assert fams["G_bridge_coupon"] == "bridge_coupon"


def test_the_frozen_comparison_coordinate_makes_extensive_quantities_comparable(
        synthetic_prefreeze):
    d, auth, out, recs = synthetic_prefreeze
    rg = vf.candidate_resolution_gates(recs, (5, 3), {"w": 5, "kz": 3})
    by = {g["quantity"]: g for g in rg["gates"]}
    assert by["C_blocked"]["scaling_exponent"] == 3
    assert by["A_series_inverse"]["scaling_exponent"] == -3
    assert by["c_field"]["scaling_exponent"] == 0
    # a dimensionless quantity is untouched; an extensive one really is rescaled
    assert by["c_field"]["value_coarse"] == by["c_field"]["raw_value_coarse"]
    assert by["C_blocked"]["value_coarse"] == pytest.approx(
        by["C_blocked"]["raw_value_coarse"] / vf.S_COARSE ** 3)
    assert "not fitted, not tunable" in by["C_blocked"]["comparison_coordinate_provenance"]


def test_actual_xi_is_built_from_matched_g_bridge_and_areas(synthetic_prefreeze):
    d, auth, out, recs = synthetic_prefreeze
    xs = vf.actual_xi_samples(recs, (5, 3))
    assert xs
    for s in xs:
        assert s["value"] == pytest.approx(s["G_bridge_coupon"] * s["A_series_inverse"])
        assert s["case_id"] != s["area_case_id"]
        assert s["definition"].startswith("Xi = G_bridge_coupon * (1/A1 + 1/A2)")
    rg = vf.candidate_resolution_gates(recs, (5, 3), {"w": 5, "kz": 3})
    xi = next(g for g in rg["gates"] if g["quantity"] == "Xi_actual")
    assert len(xi["area_case_ids"]) == 2 and len(xi["area_record_sha256"]) == 2


@pytest.mark.parametrize("drop", list(vf.CANDIDATE_RESOLUTION_QUANTITIES))
def test_one_missing_resolution_quantity_excludes_the_candidate(drop):
    coarse = {"value": 1.0, "case_id": "a", "record_sha256": "%064x" % 1}
    fine = {"value": 1.0, "case_id": "b", "record_sha256": "%064x" % 2}
    gates = [vf.resolution_consistency_gate(q, coarse, fine, {"w": 5, "kz": 3})
             for q in vf.CANDIDATE_RESOLUTION_QUANTITIES if q != drop]
    v = vf.resolution_consistency_verdict(gates)
    assert v["pass"] is False and v["missing_quantities"] == [drop]


def test_a_failed_resolution_gate_is_never_absorbed_into_an_interval(synthetic_prefreeze):
    v = vf.resolution_consistency_verdict([
        vf.resolution_consistency_gate("c_field",
                                       {"value": 1.0, "case_id": "a",
                                        "record_sha256": "%064x" % 1},
                                       {"value": 5.0, "case_id": "b",
                                        "record_sha256": "%064x" % 2},
                                       {"w": 5, "kz": 3})])
    assert v["pass"] is False
    assert "never absorbed" in v["rule"] and "UNAVAILABLE" in v["rule"]


# ---- D. the actual-Xi discrepancy (erratum PE-67) --------------------------------------------

XI_KEY = (5, 3)


def _copy_recs(recs):
    return {k: json.loads(json.dumps(v)) for k, v in recs.items()}


def _audit_of(recs, kind, key, state=None):
    for cid, r in recs.items():
        if (r.get("kind") == kind and r["run_mode"] != "NORMAL"
                and vf._bridge_key(r) == key
                and (state is None or r["row"]["state"] == state)):
            return cid
    raise AssertionError("no audit found for %r/%r" % (kind, key))


def test_the_actual_xi_discrepancy_pairs_four_matched_records(synthetic_prefreeze):
    d, auth, out, recs = synthetic_prefreeze
    u = vf.actual_xi_discrepancy(recs, XI_KEY)
    assert u["complete"] is True and u["value"] is not None
    assert u["quantity"] == "Xi_actual"
    assert sorted(u["combinations"]) == u["required_combinations"]
    for combo, c in u["combinations"].items():
        assert c["complete"] is True, combo
        for k in ("coupon_normal_case_id", "coupon_audit_case_id",
                  "blocked_mirror_normal_case_id", "blocked_mirror_audit_case_id",
                  "coupon_normal_record_sha256", "coupon_audit_record_sha256",
                  "blocked_mirror_normal_record_sha256", "blocked_mirror_audit_record_sha256",
                  "G_bridge_normal", "G_bridge_audit", "A1_normal", "A2_normal",
                  "A1_audit", "A2_audit", "Xi_normal", "Xi_audit",
                  "relative_movement", "safety_factor", "u_fixed_step_Xi"):
            assert c.get(k) is not None, (combo, k)
        assert c["Xi_normal"] == pytest.approx(
            c["G_bridge_normal"] * (1 / c["A1_normal"] + 1 / c["A2_normal"]))
        assert c["Xi_audit"] == pytest.approx(
            c["G_bridge_audit"] * (1 / c["A1_audit"] + 1 / c["A2_audit"]))
        assert c["u_fixed_step_Xi"] == pytest.approx(
            vf.NUMERICAL_DISCREPANCY_SAFETY_FACTOR * c["relative_movement"])
    assert "never added again" in u["overlaps"]


def test_an_area_movement_alone_makes_u_xi_nonzero(synthetic_prefreeze):
    """Erratum PE-67: a G-only discrepancy is blind to exactly this."""
    d, auth, out, recs = synthetic_prefreeze
    work = _copy_recs(recs)
    mid = _audit_of(work, "candidate_blocked_mirror", XI_KEY)
    sci = work[mid]["scientific"]
    for k in ("q1_volume", "q2_volume"):
        sci[k] = sci[k] * 1.02                       # A1, A2 move; G_bridge does not
    u = vf.actual_xi_discrepancy(work, XI_KEY)
    assert u["complete"] is True
    assert u["value"] > 0.0
    moved = [c for c in u["combinations"].values()
             if c["blocked_mirror_audit_case_id"] == mid][0]
    assert moved["G_bridge_normal"] == pytest.approx(moved["G_bridge_audit"])
    assert moved["A1_audit"] != pytest.approx(moved["A1_normal"])
    assert moved["relative_movement"] > 1e-3
    # a G-only method would have reported exactly zero for this pair
    g_only = vf.fixed_step_discrepancy(
        vf._pair_normal_with_audit(vf._normal_only(work, "bridge_coupon", XI_KEY),
                                   vf._audits_for(work, "bridge_coupon", XI_KEY)),
        lambda r: (r.get("scientific") or {}).get("G_bridge_coupon"), "G_bridge_coupon")
    assert g_only["value"] == pytest.approx(0.0, abs=1e-12)


def test_a_compensating_g_and_area_movement_leaves_actual_xi_unchanged(synthetic_prefreeze):
    d, auth, out, recs = synthetic_prefreeze
    work = _copy_recs(recs)
    mid = _audit_of(work, "candidate_blocked_mirror", XI_KEY)
    S, level = work[mid]["row"]["S"], work[mid]["row"]["forcing_level"]
    cid = next(c for c, r in work.items()
               if r.get("kind") == "bridge_coupon" and r["run_mode"] != "NORMAL"
               and vf._bridge_key(r) == XI_KEY and r["row"]["S"] == S
               and r["row"]["forcing_level"] == level)
    for k in ("q1_volume", "q2_volume"):             # areas up 2 %  -> 1/A1 + 1/A2 down 2 %
        work[mid]["scientific"][k] *= 1.02
    work[cid]["scientific"]["G_bridge_coupon"] *= 1.02        # G up 2 % -> Xi unchanged
    u = vf.actual_xi_discrepancy(work, XI_KEY)
    combo = "%d.%s" % (S, level)
    c = u["combinations"][combo]
    assert c["G_bridge_audit"] != pytest.approx(c["G_bridge_normal"])
    assert c["A1_audit"] != pytest.approx(c["A1_normal"])
    assert c["Xi_audit"] == pytest.approx(c["Xi_normal"], rel=1e-12)
    assert c["relative_movement"] == pytest.approx(0.0, abs=1e-12)
    assert c["diagnostic_decomposition"]["G_relative_movement"] > 1e-3
    assert c["diagnostic_decomposition"]["role"].startswith("DIAGNOSTIC_ONLY")


def test_a_wrong_blocked_mirror_audit_is_rejected(synthetic_prefreeze):
    d, auth, out, recs = synthetic_prefreeze
    work = _copy_recs(recs)
    mid = _audit_of(work, "candidate_blocked_mirror", XI_KEY)
    other = next(c for c, r in work.items()
                 if r.get("kind") == "candidate_blocked_mirror" and r["run_mode"] == "NORMAL"
                 and vf._bridge_key(r) == XI_KEY
                 and r["row"]["forcing_level"] != work[mid]["row"]["forcing_level"])
    work[mid]["row"]["audit_of_case_id"] = other
    u = vf.actual_xi_discrepancy(work, XI_KEY)
    assert u["complete"] is False
    assert any("missing blocked-mirror audit" in (v.get("reason") or "")
               or "not compatible" in (v.get("reason") or "")
               for v in u["combinations"].values())


def test_one_missing_audit_makes_the_xi_evidence_incomplete(synthetic_prefreeze):
    d, auth, out, recs = synthetic_prefreeze
    work = _copy_recs(recs)
    work.pop(_audit_of(work, "bridge_coupon", XI_KEY))
    u = vf.actual_xi_discrepancy(work, XI_KEY)
    assert u["complete"] is False
    assert any("bridge-coupon audit" in (v.get("reason") or "")
               for v in u["combinations"].values())


def test_fixed_step_records_never_enter_xi_select_as_independent_estimates(synthetic_prefreeze):
    d, auth, out, recs = synthetic_prefreeze
    xs = vf.actual_xi_samples(recs, XI_KEY)
    audit_ids = set(vf._audits_for(recs, "bridge_coupon", XI_KEY))
    audit_ids |= set(vf._audits_for(recs, "candidate_blocked_mirror", XI_KEY))
    assert audit_ids
    assert not {s["case_id"] for s in xs} & audit_ids
    assert not {s["area_case_id"] for s in xs} & audit_ids
    u = vf.actual_xi_discrepancy(recs, XI_KEY)
    assert u["fixed_step_records_are_never_independent_estimates"] is True
    env = vf.xi_envelope([{"S": s["S"], "forcing_level": s["forcing_level"],
                           "coupon_source": "bridge_coupon", "Xi": s["value"]} for s in xs],
                         0.0)
    assert env["n_estimates"] == len(xs)


# ---- E/F. the selected P2b branch and the provenance boundary (errata PE-69 … PE-73) ---------

@pytest.fixture(scope="module")
def synthetic_p2b(tmp_path_factory):
    """The SUCCESSFUL P2b endpoint, end to end, through the PRIVATE TEST_ONLY wrapper.

    P0 -> P1a -> adaptive P1b -> adaptive P2a -> P2b, real private orchestration arithmetic
    throughout, zero solver calls, and a one-below / three-inside selection.
    """
    d = tmp_path_factory.mktemp("p2b")
    auth = vf.execution_authority("P0", require_clean=False)
    prov = _pipeline_provider()
    mans, recs = {}, {}
    for phase in ("P0", "P1a", "P1b", "P2a"):
        drv._test_only_execute(phase, d, prov, auth, manifests=dict(mans), records=dict(recs))
        doc = vf.validate_phase_manifest(phase, d, authority=auth,
                                         predecessor_records=dict(recs),
                                         require_production=False)
        recs.update(doc.pop("_records", {}))
        mans[phase] = doc
    p2b_auth = vf.execution_authority("P2b", require_clean=False)
    man = vf._test_only_assemble_p2b_from_runs(d, p2b_auth)
    return d, p2b_auth, man


@pytest.fixture(scope="module")
def synthetic_design_block(tmp_path_factory):
    """The DESIGN-BLOCK endpoint: ledger and manifest only, no freeze, no instantiated matrix."""
    d = tmp_path_factory.mktemp("p2b_blocked")
    auth = vf.execution_authority("P0", require_clean=False)
    prov = _pipeline_provider(prune="all")
    mans, recs = {}, {}
    for phase in ("P0", "P1a", "P1b", "P2a"):
        drv._test_only_execute(phase, d, prov, auth, manifests=dict(mans), records=dict(recs))
        doc = vf.validate_phase_manifest(phase, d, authority=auth,
                                         predecessor_records=dict(recs),
                                         require_production=False)
        recs.update(doc.pop("_records", {}))
        mans[phase] = doc
    p2b_auth = vf.execution_authority("P2b", require_clean=False)
    man = vf._test_only_assemble_p2b_from_runs(d, p2b_auth)
    return d, p2b_auth, man


def test_the_successful_p2b_branch_selects_one_below_and_three_inside(synthetic_p2b):
    """Erratum PE-69: this branch had never executed and sat under `pragma: no cover`."""
    d, auth, man = synthetic_p2b
    assert man["selection_status"] == "SELECTED"
    assert man["terminal_status"] == "PHASE_COMPLETE"
    assert man["terminal_stop_reason"] is None
    fz = json.loads((d / "proposed_bridge_freeze.json").read_text())
    slots = [b["slot"] for b in fz["frozen_bridges"]]
    cats = [b["category"] for b in fz["frozen_bridges"]]
    assert sorted(slots) == ["below", "inside_0", "inside_1", "inside_2"]
    assert cats.count("below") == 1 and cats.count("inside") == 3
    keys = [(b["w"], b["kz"]) for b in fz["frozen_bridges"]]
    assert len(set(keys)) == vf.N_FROZEN_BRIDGES
    for name in vf.P2B_ARTIFACTS:
        assert (d / name).exists(), name
    # the adaptive pruning really happened, and P3/P4 stay unauthorized
    assert fz["p3_p4_authorised"] is False
    assert drv.AUTHORISED_SOLVING_PHASES == ()
    assert drv.AUTHORISED_ASSEMBLY_PHASES == ()


def test_the_successful_branch_reopens_and_revalidates_every_artifact(synthetic_p2b):
    d, auth, man = synthetic_p2b
    doc = vf.validate_p2b_manifest(d, require_production=False)
    assert doc["selection_status"] == "SELECTED"
    assert doc["_freeze"]["rows_sha256"] == doc["_instantiated"]["rows_sha256"]
    assert doc["_instantiated"]["rows_sha256"] == vf.record_hash(doc["_instantiated"]["rows"])
    assert set(doc["_predecessor_manifests"]) == set(vf.PHASE_PREREQUISITES["P2b"])
    assert doc["_predecessor_records"]


def test_selected_evidence_includes_every_audit_hash(synthetic_p2b):
    """Erratum PE-68: C4 reported audit-derived uncertainties and bound only the normals."""
    d, auth, man = synthetic_p2b
    fz = json.loads((d / "proposed_bridge_freeze.json").read_text())
    ledger = json.loads((d / "candidate_ledger.json").read_text())
    for b in fz["frozen_bridges"]:
        bound = set(b["candidate_specific_record_sha256"])
        entry = ledger["candidates"]["w%d_kz%d" % (b["w"], b["kz"])]
        cited = set()
        for combo in entry["u_fixed_step_Xi"]["combinations"].values():
            for k in ("coupon_normal_record_sha256", "coupon_audit_record_sha256",
                      "blocked_mirror_normal_record_sha256",
                      "blocked_mirror_audit_record_sha256"):
                cited.add(combo[k])
        for k in ("normal_record_sha256", "audit_record_sha256"):
            cited |= set(entry["u_fixed_step_c"][k])
        for ev in entry["pressure_upper_bounds"].values():
            cited |= {ev["normal_record_sha256"], ev["audit_record_sha256"]}
        for v in entry["artifact"]["combinations"].values():
            cited |= set(v["audit_record_sha256"]) | set(v["normal_record_sha256"])
        assert cited <= bound, sorted(cited - bound)[:3]
        assert entry["evidence"]["complete"] is True
        assert entry["evidence"]["unbound_cited_hashes"] == []


def test_four_distinct_candidate_evidence_sets_and_a_separate_common_reference(synthetic_p2b):
    d, auth, man = synthetic_p2b
    fz = json.loads((d / "proposed_bridge_freeze.json").read_text())
    sets = [set(b["candidate_specific_record_sha256"]) for b in fz["frozen_bridges"]]
    assert len(sets) == vf.N_FROZEN_BRIDGES and all(sets)
    for i, a in enumerate(sets):
        for b in sets[i + 1:]:
            assert not (a & b), "candidate evidence sets must be distinct"
    common = fz["common_reference_evidence"]
    assert "reference_blocked_ladder" in common["role_names"]
    assert any(r.startswith("axial_coupon[") for r in common["role_names"])
    # the common reference is bound ONCE, never duplicated into a candidate set
    for s in sets:
        assert not (s & set(common["record_sha256"]))
    ledger = json.loads((d / "candidate_ledger.json").read_text())
    assert ledger["common_reference_evidence"]["record_sha256"] == common["record_sha256"]


def test_the_design_block_pipeline_writes_no_freeze_and_no_matrix(synthetic_design_block):
    d, auth, man = synthetic_design_block
    assert man["selection_status"] == "DESIGN_BLOCKED"
    assert man["terminal_status"] == "PHASE_STOPPED_DESIGN_BLOCKED"
    assert man["terminal_stop_reason"] in vf.DESIGN_BLOCKED_REASONS
    assert (d / "candidate_ledger.json").exists()
    assert (d / "manifest_P2b.json").exists()
    assert not (d / "proposed_bridge_freeze.json").exists()
    assert not (d / "instantiated_p3_p4_matrix.json").exists()
    doc = vf.validate_p2b_manifest(d, require_production=False)
    assert doc["terminal_status"] == "PHASE_STOPPED_DESIGN_BLOCKED"


@pytest.mark.parametrize("pattern", ["freeze_differs", "matrix_key_differs", "all_three_differ"])
def test_every_rows_sha256_mismatch_pattern_is_caught(synthetic_p2b, tmp_path, pattern):
    """Erratum PE-70: `a != b != c` is `a != b and b != c`, so `a == c` with `b` different
    slipped through the superseded chained comparison."""
    import shutil
    d, auth, man = synthetic_p2b
    work = tmp_path / pattern
    shutil.copytree(d, work)
    fz = json.loads((work / "proposed_bridge_freeze.json").read_text())
    inst = json.loads((work / "instantiated_p3_p4_matrix.json").read_text())
    if pattern == "freeze_differs":
        fz["rows_sha256"] = "0" * 64            # freeze != wrapper, wrapper == actual
    elif pattern == "matrix_key_differs":
        inst["rows_sha256"] = "1" * 64          # freeze == actual, wrapper differs from both
    else:
        fz["rows_sha256"] = "0" * 64
        inst["rows_sha256"] = "1" * 64          # all three differ
    (work / "proposed_bridge_freeze.json").write_text(vf.canonical_json(fz) + "\n")
    (work / "instantiated_p3_p4_matrix.json").write_text(vf.canonical_json(inst) + "\n")
    doc = json.loads((work / "manifest_P2b.json").read_text())
    doc["proposed_freeze_sha256"] = vf.record_hash(fz)
    doc["instantiated_matrix_file_sha256"] = hashlib.sha256(
        (work / "instantiated_p3_p4_matrix.json").read_bytes()).hexdigest()
    fz["instantiated_matrix_file_sha256"] = doc["instantiated_matrix_file_sha256"]
    (work / "proposed_bridge_freeze.json").write_text(vf.canonical_json(fz) + "\n")
    doc["proposed_freeze_sha256"] = vf.record_hash(fz)
    (work / "manifest_P2b.json").write_text(vf.canonical_json(doc) + "\n")
    with pytest.raises(vf.ManifestMissing) as exc:
        vf.validate_p2b_manifest(work, require_production=False)
    assert "disagree" in str(exc.value) or "stale" in str(exc.value)


def test_a_test_only_predecessor_set_can_never_produce_production_p2b_artifacts(synthetic_p2b):
    d, auth, man = synthetic_p2b
    assert man["provenance_mode"] == "TEST_ONLY"
    for name in vf.P2B_ARTIFACTS:
        art = json.loads((d / name).read_text())
        assert art["provenance_mode"] == "TEST_ONLY", name
    assert man["assembly_authority"]["provenance_mode"] == "TEST_ONLY"
    with pytest.raises(vf.ManifestMissing):
        vf.validate_p2b_manifest(d, require_production=True)


def test_the_production_p2b_validator_recursively_rejects_test_only_predecessors(synthetic_p2b,
                                                                                tmp_path):
    """Erratum PE-72: a correct predecessor FILE hash proves nothing about the file's contents."""
    import shutil
    d, auth, man = synthetic_p2b
    work = tmp_path / "prod"
    shutil.copytree(d, work)
    for name in vf.P2B_ARTIFACTS:
        art = json.loads((work / name).read_text())
        art["provenance_mode"] = "PRODUCTION"
        if "assembly_authority" in art:
            art["assembly_authority"]["provenance_mode"] = "PRODUCTION"
        (work / name).write_text(vf.canonical_json(art) + "\n")
    with pytest.raises(vf.ManifestMissing) as exc:
        vf.validate_p2b_manifest(work, require_production=True)
    # it fails on the recursively revalidated TEST_ONLY predecessors, not on a file hash
    assert "PRODUCTION" in str(exc.value) or "provenance" in str(exc.value)
    assert "validate_phase_manifest" in inspect.getsource(vf.validate_p2b_manifest)


def test_the_p2b_assembly_authority_is_complete_and_load_bearing(synthetic_p2b):
    """Erratum PE-73: C4 accepted an `authority` parameter and never read it."""
    d, auth, man = synthetic_p2b
    aa = man["assembly_authority"]
    for k in vf.P2B_ASSEMBLY_AUTHORITY_FIELDS:
        assert k in aa, k
    assert aa["phase"] == "P2b"
    assert aa["correction_version"] == vf.CORRECTION_VERSION
    assert set(aa["predecessor_manifest_file_sha256"]) == set(vf.PHASE_PREREQUISITES["P2b"])
    assert aa["pre_freeze_matrix_sha256"] == vf.pre_freeze_matrix_sha256()
    # the expected-authority parameter is used, not decorative
    vf.validate_p2b_manifest(
        d, require_production=False,
        expected_assembly_authority_sha256=aa["assembly_authority_sha256"])
    with pytest.raises(vf.ManifestMissing) as exc:
        vf.validate_p2b_manifest(d, require_production=False,
                                 expected_assembly_authority_sha256="0" * 64)
    assert "not the expected one" in str(exc.value)
    assert "authority=None" not in inspect.getsource(vf.validate_p2b_manifest)


def test_the_production_wrapper_exposes_no_override(synthetic_p2b):
    sig = inspect.signature(vf.assemble_p2b_from_runs)
    assert list(sig.parameters) == ["runs_dir", "backend"]
    src = inspect.getsource(vf.assemble_p2b_from_runs)
    assert "require_production=True" in src
    assert "provenance_mode=\"PRODUCTION\"" in src
    # the TEST_ONLY wrapper is private and never calls the production one
    tsrc = inspect.getsource(vf._test_only_assemble_p2b_from_runs)
    assert "assemble_p2b_from_runs(" not in tsrc.split("def _test_only", 1)[1].split('"""')[-1]
    assert 'provenance_mode="TEST_ONLY"' in tsrc


# ---- G. true pre-solve resume (errata PE-74, PE-75) ------------------------------------------

class _CountingProvider:
    """Wraps the coherent TEST_ONLY provider and counts every call."""

    def __init__(self, prune=SYNTH_PRUNED_CANDIDATE):
        self._inner = _pipeline_provider(prune)
        self.calls = 0

    def __call__(self, **kw):
        self.calls += 1
        return self._inner(**kw)


@pytest.fixture(scope="module")
def resumable_p0(tmp_path_factory):
    d = tmp_path_factory.mktemp("resume")
    auth = vf.execution_authority("P0", require_clean=False)
    prov = _CountingProvider()
    man = drv._test_only_execute("P0", d, prov, auth)
    return d, auth, man, prov.calls


def test_a_fresh_phase_calls_the_provider_once_per_newly_executed_row(resumable_p0):
    d, auth, man, calls = resumable_p0
    ec = man["execution_counts"]
    assert ec["n_provider_calls"] == ec["n_newly_executed"] == calls
    assert ec["n_reused"] == 0
    assert ec["n_completed"] + ec["n_failed"] + ec["n_refused"] == man["counts"]["universe"]


def test_an_exact_manifest_is_reused_with_zero_provider_calls(resumable_p0, tmp_path):
    import shutil
    d, auth, man, _ = resumable_p0
    work = tmp_path / "manifest_resume"
    shutil.copytree(d, work)
    prov = _CountingProvider()
    again = drv._test_only_execute("P0", work, prov, auth)
    assert prov.calls == 0
    assert again["terminal_status"] == "PHASE_COMPLETE"
    assert again["phase_universe_sha256"] == man["phase_universe_sha256"]


def test_a_partial_phase_runs_only_the_missing_rows(resumable_p0, tmp_path):
    import shutil
    d, auth, man, _ = resumable_p0
    work = tmp_path / "partial"
    shutil.copytree(d, work)
    (work / "manifest_P0.json").unlink()
    dropped = [e["case_id"] for e in man["completed"][:3]]
    for cid in dropped:
        (work / vf.case_record_filename(cid)).unlink()
    prov = _CountingProvider()
    again = drv._test_only_execute("P0", work, prov, auth)
    ec = again["execution_counts"]
    assert prov.calls == len(dropped) == ec["n_provider_calls"] == ec["n_newly_executed"]
    assert ec["n_reused"] == man["counts"]["completed"] - len(dropped)
    assert ec["n_completed"] == man["counts"]["completed"]
    # a resumed phase legitimately has FEWER provider calls than completed rows
    assert ec["n_provider_calls"] < ec["n_completed"]


@pytest.mark.parametrize("mutate", [
    {"provenance_mode": "PRODUCTION"},
    {"mask_sha256": "0" * 64},
    {"execution_authority_sha256": "0" * 64},
    {"predecessor_manifest_sha256": {"P0": "0" * 64}},
    {"status": "NORMAL_UNCONVERGED"},
])
def test_a_mismatched_existing_record_fails_before_the_provider(resumable_p0, tmp_path, mutate):
    import shutil
    d, auth, man, _ = resumable_p0
    work = tmp_path / ("mismatch_%s" % sorted(mutate)[0])
    shutil.copytree(d, work)
    (work / "manifest_P0.json").unlink()
    cid = man["completed"][0]["case_id"]
    rec, path = vf.read_case_record(work, cid)
    rec.update(mutate)
    if "mask_sha256" in mutate:
        rec["geometry"]["mask_sha256"] = mutate["mask_sha256"]
    path.write_text(vf.canonical_json(rec) + "\n")
    prov = _CountingProvider()
    with pytest.raises((vf.ResumeMismatch, ValueError)):
        drv._test_only_execute("P0", work, prov, auth)
    assert prov.calls == 0, "the provider was called before the mismatch was discovered"


def test_a_mismatched_existing_manifest_fails_closed(resumable_p0, tmp_path):
    import shutil
    d, auth, man, _ = resumable_p0
    work = tmp_path / "bad_manifest"
    shutil.copytree(d, work)
    doc = json.loads((work / "manifest_P0.json").read_text())
    doc["counts"]["completed"] += 1
    (work / "manifest_P0.json").write_text(vf.canonical_json(doc) + "\n")
    prov = _CountingProvider()
    with pytest.raises(vf.ManifestMissing):
        drv._test_only_execute("P0", work, prov, auth)
    assert prov.calls == 0


def test_the_record_path_is_derived_before_any_provider_call():
    src = inspect.getsource(drv._orchestrate)
    before, after = src.split("load_resumable_case_record", 1)
    assert "provider(" not in before, "the provider is reached before the record is discovered"
    assert "resolve_row(row)" in before
    assert "_atomic_write_json" in src            # PE-75: no unconditional manifest overwrite
    assert "tmp.replace(mpath)" not in src


def test_an_audit_record_resumes_only_against_its_exact_base(synthetic_prefreeze, tmp_path):
    import shutil
    d, auth, out, recs = synthetic_prefreeze
    work = tmp_path / "audit_resume"
    shutil.copytree(d, work)
    (work / "manifest_P1b.json").unlink()
    prov = _CountingProvider()
    again = drv._test_only_execute("P1b", work, prov, auth,
                                   manifests={"P0": None, "P1a": None},
                                   records=dict(recs))
    assert prov.calls == 0
    ec = again["execution_counts"]
    assert ec["n_reused"] == ec["n_completed"] > 0
    audits = [e for e in again["completed"]
              if e["case_id"].endswith("fixedstep")]
    assert audits and all(e["write_mode"] == "REUSED_EXACT_MATCH" for e in audits)


# ---- H. the deferred post-freeze executor (erratum PE-76) ------------------------------------

@pytest.mark.parametrize("phase", ["P3", "P4"])
def test_p3_p4_refuse_even_with_the_solving_allowlist_patched(monkeypatch, tmp_path, phase):
    monkeypatch.setattr(drv, "AUTHORISED_SOLVING_PHASES", ("P0", "P1a", "P1b", "P2a", "P3", "P4"))
    assert drv.POST_FREEZE_EXECUTOR_READY is False
    with pytest.raises(drv.PostFreezeExecutorNotReady) as exc:
        drv.require_execution_authorisation(phase, runs_dir=tmp_path)
    assert "instantiated-matrix loader has not yet passed exact-head review" in str(exc.value)
    with pytest.raises(drv.PostFreezeExecutorNotReady):
        drv.execute_phase(phase, tmp_path)
    with pytest.raises(drv.PostFreezeExecutorNotReady):
        drv.solve(None, 1.0, phase)


def test_no_unresolved_post_freeze_template_can_reach_a_provider(tmp_path):
    tpls = [r for r in vf.post_freeze_row_templates() if isinstance(r["bridge"], str)]
    assert tpls
    with pytest.raises(ValueError):
        drv.resolve_row(tpls[0])
    src = inspect.getsource(drv._orchestrate)
    assert '_refuse_post_freeze(row["phase"])' in src
    guard = src.split("_refuse_post_freeze")[0]
    assert "provider(" not in guard


def test_the_post_freeze_deferral_is_explicit_and_names_the_reserved_work():
    assert drv.POST_FREEZE_PHASES == ("P3", "P4")
    note = drv.POST_FREEZE_NOT_READY_NOTE
    for phrase in ("exact-head review", "planning TEMPLATES", "unresolved placeholder",
                   "phase universe", "later authorization tranche"):
        assert phrase in note, phrase
    assert drv.AUTHORISED_SOLVING_PHASES == () and drv.AUTHORISED_ASSEMBLY_PHASES == ()


# ---- negative end-to-end cases (§10.3) -------------------------------------------------------

def _drifted(recs, key, kind, state, level, S, field, factor):
    """Apply a relative drift to ONE forcing level of one configuration."""
    work = _copy_recs(recs)
    for cid, r in work.items():
        if (r.get("kind") == kind and r["run_mode"] == "NORMAL"
                and vf._bridge_key(r) == key and r["row"]["S"] == S
                and r["row"]["forcing_level"] == level
                and (state is None or r["row"]["state"] == state)):
            r["scientific"][field] = r["scientific"][field] * factor
            return work, cid
    raise AssertionError("no record matched %r" % ((kind, state, level, S),))


@pytest.mark.parametrize("quantity,kind,state,field", [
    ("R_identical", "identical_path_control", "open", "Q_volume"),
    ("s_blocked", "identical_path_control", "blocked", "q1_volume"),
    ("c_field", "candidate_blocked_mirror", "blocked", "p_face1"),
])
def test_a_boundary_forcing_drift_above_the_tolerance_fails(synthetic_prefreeze, quantity,
                                                            kind, state, field):
    d, auth, out, recs = synthetic_prefreeze
    key = (5, 3)
    clean = vf.candidate_forcing_gates(recs, key)
    assert clean["boundary"]["pass"] is True
    work, _ = _drifted(recs, key, kind, state, "high", vf.S_COARSE, field, 1.0 + 1.0e-3)
    fg = vf.candidate_forcing_gates(work, key)
    assert fg["boundary"]["pass"] is False
    assert any(g.startswith(quantity) for g in fg["boundary"]["failed_quantities"]), (
        quantity, fg["boundary"]["failed_quantities"])
    assert fg["pass"] is False


def test_an_actual_xi_forcing_drift_above_the_tolerance_fails(synthetic_prefreeze):
    d, auth, out, recs = synthetic_prefreeze
    key = (5, 3)
    work = _copy_recs(recs)
    for cid, r in work.items():
        if (r.get("kind") == "bridge_coupon" and r["run_mode"] == "NORMAL"
                and vf._bridge_key(r) == key and r["row"]["S"] == vf.S_COARSE
                and r["row"]["forcing_level"] == "low"):
            r["scientific"]["G_bridge_coupon"] *= 1.0 + 1.0e-3
    fg = vf.candidate_forcing_gates(work, key)
    assert fg["boundary"]["pass"] is False
    assert any(g.startswith("Xi_actual") for g in fg["boundary"]["failed_quantities"])


def test_a_p0_axial_coupon_forcing_failure_fails_the_aggregate(synthetic_prefreeze):
    d, auth, out, recs = synthetic_prefreeze
    p0 = {cid: r for cid, r in recs.items() if r["row"]["phase"] == "P0"}
    assert vf.p0_aggregate_science(p0)["pass"] is True
    work = _copy_recs(p0)
    target = next(cid for cid, r in work.items()
                  if r.get("kind") == "axial_coupon" and r["run_mode"] == "NORMAL"
                  and r["row"]["coupon_level"] == "low"
                  and r["row"]["coupon_orientation"] == "y"
                  and r["row"]["forcing_level"] == "high"
                  and r["row"]["S"] == vf.S_COARSE)
    work[target]["scientific"]["Q_volume"] *= 1.0 + 1.0e-3
    sci = vf.p0_aggregate_science(work)
    assert sci["pass"] is False
    assert "forcing:axial_coupon[low,y]" in sci["failed_families"]


def test_an_actual_xi_resolution_failure_excludes_the_candidate(synthetic_prefreeze):
    d, auth, out, recs = synthetic_prefreeze
    key, bridge = (5, 3), {"w": 5, "kz": 3}
    assert vf.candidate_resolution_gates(recs, key, bridge)["pass"] is True
    work = _copy_recs(recs)
    for cid, r in work.items():
        if (r.get("kind") == "bridge_coupon" and vf._bridge_key(r) == key
                and r["row"]["S"] == vf.S_FINE and r["row"]["forcing_level"] == "central"):
            r["scientific"]["G_bridge_coupon"] *= 2.0
    rg = vf.candidate_resolution_gates(work, key, bridge)
    assert rg["pass"] is False
    assert "Xi_actual" in rg["failed_quantities"] or "G_bridge_coupon" in rg["failed_quantities"]


def test_a_tampered_candidate_ledger_breaks_the_p2b_manifest(synthetic_p2b, tmp_path):
    import shutil
    d, auth, man = synthetic_p2b
    work = tmp_path / "tampered_ledger"
    shutil.copytree(d, work)
    ledger = json.loads((work / "candidate_ledger.json").read_text())
    ledger["n_eligible"] = ledger["n_eligible"] + 1
    (work / "candidate_ledger.json").write_text(vf.canonical_json(ledger) + "\n")
    with pytest.raises(vf.ManifestMissing):
        vf.validate_p2b_manifest(work, require_production=False)


def test_a_tampered_proposed_freeze_breaks_the_p2b_manifest(synthetic_p2b, tmp_path):
    import shutil
    d, auth, man = synthetic_p2b
    work = tmp_path / "tampered_freeze"
    shutil.copytree(d, work)
    fz = json.loads((work / "proposed_bridge_freeze.json").read_text())
    fz["frozen_bridges"][0]["w"] = 99
    (work / "proposed_bridge_freeze.json").write_text(vf.canonical_json(fz) + "\n")
    with pytest.raises(vf.ManifestMissing):
        vf.validate_p2b_manifest(work, require_production=False)


def test_a_duplicate_selected_candidate_is_refused(synthetic_p2b, tmp_path):
    import shutil
    d, auth, man = synthetic_p2b
    work = tmp_path / "duplicate"
    shutil.copytree(d, work)
    fz = json.loads((work / "proposed_bridge_freeze.json").read_text())
    fz["frozen_bridges"][1] = dict(fz["frozen_bridges"][0], slot="inside_0")
    (work / "proposed_bridge_freeze.json").write_text(vf.canonical_json(fz) + "\n")
    doc = json.loads((work / "manifest_P2b.json").read_text())
    doc["proposed_freeze_sha256"] = vf.record_hash(fz)
    (work / "manifest_P2b.json").write_text(vf.canonical_json(doc) + "\n")
    with pytest.raises(vf.ManifestMissing) as exc:
        vf.validate_p2b_manifest(work, require_production=False)
    assert "twice" in str(exc.value) or "disagree" in str(exc.value) or "stale" in str(exc.value)


def _envelope(xi, lo_hi=None):
    return {"Xi_select": xi, "Xi_lower": xi * 0.99, "Xi_upper": xi * 1.01,
            "category": ("below" if xi * 1.01 < vf.XI_WINDOW_LO else "inside"),
            "categorically_usable": True}


def test_fewer_than_three_inside_candidates_is_a_design_block():
    cands = [{"w": 3, "kz": 2, "eligible": True, "xi_envelope": _envelope(0.05)},
             {"w": 5, "kz": 2, "eligible": True, "xi_envelope": _envelope(0.5)},
             {"w": 7, "kz": 2, "eligible": True, "xi_envelope": _envelope(1.5)}]
    with pytest.raises(vf.DesignBlocked) as exc:
        vf.select_bridges(cands)
    assert exc.value.reason == "INSUFFICIENT_UNAMBIGUOUS_INSIDE_CANDIDATES"


def test_no_below_candidate_is_a_design_block():
    cands = [{"w": w, "kz": 2, "eligible": True, "xi_envelope": _envelope(x)}
             for w, x in ((3, 0.5), (5, 1.0), (7, 2.0), (9, 3.0))]
    with pytest.raises(vf.DesignBlocked) as exc:
        vf.select_bridges(cands)
    assert exc.value.reason == "NO_UNAMBIGUOUS_BELOW_CANDIDATE"


# ---- machine-derived counts (§15) ------------------------------------------------------------

def test_every_count_is_regenerated_from_one_machine_authority():
    m = vf.execution_matrix()
    rows = m["rows"]
    assert m["n_rows"] == len(rows)
    n_audit = sum(1 for r in rows if r["run_mode"] == "FIXED_STEP_REEXECUTION_1P5X")
    assert m["planned_fixed_step_audits"] == n_audit
    assert m["planned_normal_solves"] == len(rows) - n_audit
    assert m["planned_solver_invocations"] == (m["planned_normal_solves"]
                                               + m["planned_fixed_step_audits"])
    assert m["planned_pressure_plane_diagnostic_rows"] == 0
    assert m["same_field_node_offset_summaries"] == sum(
        1 for r in rows if r["kind"] not in ("axial_coupon", "bridge_coupon"))
    pre = [r for r in rows if r["phase"] in ("P0", "P1a", "P1b", "P2a")]
    assert m["pre_freeze_rows"] == len(pre)
    assert m["provider_calls_fresh_full_pre_freeze_run"] == len(pre)
    assert m["provider_calls_on_exact_resume"] == 0
    assert m["arithmetic_only_phases"] == ["P2b"] and m["arithmetic_only_solver_calls"] == 0
    assert m["p3_p4_planning_template_rows"] == m["n_post_freeze_template_rows"]
    assert m["post_freeze_executor_ready"] is False
    assert m["solves_executed"] == 0
    assert "no separate pressure-diagnostic row" in m["pressure_diagnostic_rows_policy"]


def test_observed_provider_calls_equal_newly_executed_rows(resumable_p0):
    d, auth, man, calls = resumable_p0
    ec = man["execution_counts"]
    assert calls == ec["n_provider_calls"] == ec["n_newly_executed"]
    m = vf.execution_matrix()
    p0_rows = [r for r in m["rows"] if r["phase"] == "P0"]
    assert ec["n_newly_executed"] == len(p0_rows)      # a fresh full P0 run


def test_the_documented_plan_command_actually_runs():
    """A defect found by RUNNING the documented `--mode plan` command at the C5 head: the C4 CLI
    read `planned_pressure_plane_diagnostics`, a key the matrix never carried, and the whole
    body sat under `pragma: no cover`. The summary is now a covered function."""
    summary = drv.plan_summary(vf.execution_matrix())
    assert summary["mode"] == "plan"
    for k in drv.PLAN_SUMMARY_KEYS:
        assert k in summary, k
    assert summary["solves_executed"] == 0
    assert summary["post_freeze_executor_ready"] is False
    assert summary["authorised_solving_phases"] == []
    assert summary["authorised_assembly_phases"] == []
    assert summary["planned_solver_invocations"] == (summary["planned_normal_solves"]
                                                     + summary["planned_fixed_step_audits"])
    with pytest.raises(KeyError):
        drv.plan_summary({"n_rows": 1})
