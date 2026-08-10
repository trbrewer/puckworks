"""RP-D-LC-001b preflight tests.

Every test here is geometry, configuration, serialisation, hashing or decision-contract. NONE
runs a lattice-Boltzmann solve, and one of them proves that none can: the driver's single solver
call site refuses while the tranche is pre-execution.
"""

import ast
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
    tol_R_blocked = vf.resolution_consistency_tolerance("R_blocked")
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
    guard = fn.body[1]
    assert isinstance(guard, ast.If)
    assert "AUTHORISED_SOLVING_PHASES" in ast.dump(guard.test)


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
            > vf.resolution_consistency_tolerance("R_blocked"))
    assert (vf.resolution_consistency_tolerance("s_open", b)
            > vf.resolution_consistency_tolerance("s_blocked"))
    tbl = vf.resolution_consistency_table(b)
    assert tbl["R_blocked"]["family"] == "lane_only"
    assert tbl["R_open"]["family"] == "bridge_carrying"


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
        assert fn()["correction_version"] == vf.CORRECTION_VERSION == "PREFLIGHT-C2"


def test_every_superseded_generation_is_retained_not_overwritten():
    """C0 and C1 hashes are both kept, so anything bound to either stays traceable."""
    revs = vf.SUPERSEDED_REVIEWS
    assert [r["correction_version"] for r in revs] == ["PREFLIGHT-C0", "PREFLIGHT-C1"]
    assert revs[0]["reviewed_head"] == "bbf2304665d09cb78c117353947ce8c6cf2e5d24"
    assert revs[1]["reviewed_head"] == "2cf0b63ba2670de423a39f9563822563a3cb59b5"
    assert revs[1]["disposition"].endswith("C2_AND_PREFREEZE_EXECUTOR_REQUIRED")
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
    for phase in ("P0", "P1a", "P1b", "P2a", "P3", "P4"):
        assert m["by_phase"][phase] > 0
    assert "P2b" not in m["by_phase"]                     # P2b does arithmetic, not solving
    central = [r for r in m["rows"] if r["kind"] == "identical_path_control"
               and r["forcing_level"] == "central" and r["run_mode"] == "NORMAL"]
    assert len(central) == 2 * 2 * len(SCI) == 48
    assert m["planned_normal_solves"] + m["planned_fixed_step_audits"] == m["n_rows"]
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


def test_a_symmetric_identical_fixture_measures_a_zero_lateral_gap_and_passes():
    mask, meta, res, g = _face_case()
    rec = drv.case_record(res, mask, meta, g, stage="unit")
    lp = rec["lateral_pressure"]
    assert lp["delta_p_lateral"] == pytest.approx(0.0, abs=1e-15)
    assert lp["expected_zero_driver"] is True
    assert lp["measured_zero_driver_pass"] is True


def test_a_MEASURED_nonzero_gap_fails_an_expected_zero_driver_case():
    """A geometry label may never certify the premise of the negative control (erratum PE-15)."""
    mask, meta, res, g = _face_case(bump=1e-3)
    rec = drv.case_record(res, mask, meta, g, stage="unit")
    lp = rec["lateral_pressure"]
    assert lp["expected_zero_driver"] is True          # the LABEL still says identical
    assert abs(lp["delta_p_lateral"]) > 0
    assert lp["measured_zero_driver_pass"] is False    # the MEASUREMENT overrules it


def test_the_common_axial_gradient_cancels_in_the_pointwise_gap():
    mask, meta, res, g = _face_case(b={"w": 9, "kz": 4})
    rec = drv.case_record(res, mask, meta, g, stage="unit")
    d = rec["lateral_pressure"]["delta_pointwise"]
    assert d["faces_share_footprint"] is True
    assert d["delta_sd"] == pytest.approx(0.0, abs=1e-15)
    # the individual faces DO vary strongly across the footprint; that is common-mode
    assert rec["lateral_pressure"]["face_nonuniformity_rel"] > 0
    assert rec["lateral_pressure"]["face_nonuniformity_role"].startswith("diagnostic")


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
    """A complete, validated P0 phase produced by the executor with a FAKE result provider."""
    auth = vf.execution_authority("P0", require_clean=False)
    man = drv._execute_solving_phase("P0", tmp_path, auth, {}, {}, _fake_provider, "reference")
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
    assert man["counts"]["completed"] == man["counts"]["expected"] > 0
    assert man["counts"]["failed"] == 0
    doc = vf.validate_phase_manifest("P0", runs, authority=auth)
    assert len(doc["_records"]) == man["counts"]["completed"]


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
        vf.validate_phase_manifest("P0", runs, authority=auth)


def test_a_wrong_record_hash_breaks_its_manifest(executed_p0):
    runs, auth, man = executed_p0
    doc = json.loads((runs / "manifest_P0.json").read_text())
    doc["completed"][0]["record_sha256"] = "0" * 64
    (runs / "manifest_P0.json").write_text(vf.canonical_json(doc) + "\n")
    with pytest.raises(vf.ManifestMissing):
        vf.validate_phase_manifest("P0", runs, authority=auth)


def test_a_nonempty_but_incomplete_manifest_fails(executed_p0):
    """The superseded check passed on a NONEMPTY list (erratum PE-18)."""
    runs, auth, man = executed_p0
    doc = json.loads((runs / "manifest_P0.json").read_text())
    doc["completed"] = doc["completed"][:1]
    doc["counts"]["completed"] = 1
    (runs / "manifest_P0.json").write_text(vf.canonical_json(doc) + "\n")
    assert doc["completed"]                            # nonempty...
    with pytest.raises(vf.ManifestMissing):            # ...and still not a phase
        vf.validate_phase_manifest("P0", runs, authority=auth)


def test_an_extra_case_not_in_the_plan_is_refused(executed_p0):
    runs, auth, man = executed_p0
    doc = json.loads((runs / "manifest_P0.json").read_text())
    doc["completed"].append(dict(doc["completed"][0], case_id="not.in.the.plan"))
    doc["counts"]["completed"] += 1
    (runs / "manifest_P0.json").write_text(vf.canonical_json(doc) + "\n")
    with pytest.raises(vf.ManifestMissing):
        vf.validate_phase_manifest("P0", runs, authority=auth)


def test_a_duplicate_completed_case_is_refused(executed_p0):
    runs, auth, man = executed_p0
    doc = json.loads((runs / "manifest_P0.json").read_text())
    doc["completed"].append(dict(doc["completed"][0]))
    doc["counts"]["completed"] += 1
    (runs / "manifest_P0.json").write_text(vf.canonical_json(doc) + "\n")
    with pytest.raises(vf.ManifestMissing):
        vf.validate_phase_manifest("P0", runs, authority=auth)


def test_one_record_hash_cannot_be_cited_for_two_physically_distinct_rows(executed_p0):
    runs, auth, man = executed_p0
    doc = json.loads((runs / "manifest_P0.json").read_text())
    a, b = doc["completed"][0], doc["completed"][1]
    b["record_sha256"] = a["record_sha256"]
    (runs / "manifest_P0.json").write_text(vf.canonical_json(doc) + "\n")
    with pytest.raises(vf.ManifestMissing):
        vf.validate_phase_manifest("P0", runs, authority=auth)


def test_a_manifest_from_a_superseded_correction_version_is_refused(executed_p0):
    runs, auth, man = executed_p0
    doc = json.loads((runs / "manifest_P0.json").read_text())
    doc["correction_version"] = "PREFLIGHT-C1"
    (runs / "manifest_P0.json").write_text(vf.canonical_json(doc) + "\n")
    with pytest.raises(vf.ManifestMissing):
        vf.validate_phase_manifest("P0", runs, authority=auth)


def test_a_manifest_whose_plan_hash_does_not_match_the_derived_plan_is_refused(executed_p0):
    runs, auth, man = executed_p0
    doc = json.loads((runs / "manifest_P0.json").read_text())
    doc["phase_plan_sha256"] = "0" * 64
    (runs / "manifest_P0.json").write_text(vf.canonical_json(doc) + "\n")
    with pytest.raises(vf.ManifestMissing):
        vf.validate_phase_manifest("P0", runs, authority=auth)


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
    assert set(src) == {"runs_dir", "authority"}
    assert not hasattr(vf, "build_freeze")
    body = inspect.getsource(vf.assemble_p2b_from_runs)
    assert "field_contrast(" in body                   # c is RECOMPUTED, never read back
    assert "xi_envelope(" in body and "reachable_set_admission(" in body
    assert "select_bridges(" in body


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


def test_p2b_makes_no_solver_call():
    body = inspect.getsource(drv.execute_phase)
    assert "NO solver call" in body
    assert "assemble_p2b_from_runs" in body


def test_a_failed_case_stops_the_phase(tmp_path, monkeypatch):
    auth = vf.execution_authority("P0", require_clean=False)

    calls = {"n": 0}

    def failing(mask, g, phase, row, tau=None, audit=None, backend="reference"):
        calls["n"] += 1
        res = _fake_provider(mask, g, phase, row, tau, audit, backend)
        if calls["n"] == 3:
            res["steps"] = vf.MAX_STEPS               # NORMAL_UNCONVERGED
        return res

    man = drv._execute_solving_phase("P0", tmp_path, auth, {}, {}, failing, "reference")
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


def test_the_result_provider_is_a_python_keyword_only_test_seam():
    params = inspect.signature(drv.execute_phase).parameters
    assert "result_provider" in params
    assert params["result_provider"].default is None


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
