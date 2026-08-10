"""RP-D-LC-001b preflight tests.

Every test here is geometry, configuration, serialisation, hashing or decision-contract. NONE
runs a lattice-Boltzmann solve, and one of them proves that none can: the driver's single solver
call site refuses while the tranche is pre-execution.
"""

import ast
import inspect
import json
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
    assert vf.NUMERICAL_UNCERTAINTY_R_ABS == vf.TOL_MASS_REL


def test_the_001_artifact_would_have_failed_the_budget_by_more_than_an_order_of_magnitude():
    m = vf.artifact_metrics(C_open=1.0143, C_blocked=1.0,
                            R_identical=1.0 + vf.PREDECESSOR[
                                "axial_artifact_at_zero_lateral_driver"])
    assert m["within_budget"] is False
    assert m["pressure_normalised_R_change"] / vf.ARTIFACT_BUDGET_R_ABS > 14


def test_artifact_metrics_report_every_required_form_and_name_the_adjudicative_one():
    m = vf.artifact_metrics(C_open=25.5, C_blocked=25.4, R_identical=1.0004,
                            R_identical_mass=1.0005)
    assert m["adjudicative_metric"] == "pressure_normalised_R_change"
    assert m["signed_conductance_change"] == pytest.approx(0.1)
    assert m["absolute_conductance_change"] == pytest.approx(0.1)
    assert m["relative_conductance_change"] == pytest.approx(0.1 / 25.4)
    assert m["mass_flux_R_change"] == pytest.approx(5e-4)
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
    a = vf.reachable_set_admission(c_field_reference=0.3218, Xi_predicted=1.0,
                                   artifact_bound=5e-4)
    assert a["lhs"] == pytest.approx(a["predicted_signal"] + a["axial_artifact_bound"]
                                     + a["numerical_uncertainty_bound"])
    assert a["rhs"] == pytest.approx(a["reachable_ceiling"] - a["safety_margin"])
    assert a["admitted"] is True
    # the margin is a fixed fraction of the ceiling, not a microscopic point-estimate pass
    assert a["safety_margin"] == pytest.approx(0.10 * a["reachable_ceiling"])
    assert a["safety_margin"] > 20 * a["axial_artifact_bound"]
    # the gate uses a conservatively REDUCED contrast
    assert a["c_gate"] < abs(0.3218)


def test_the_admission_test_rejects_a_candidate_that_saturates_the_model():
    a = vf.reachable_set_admission(c_field_reference=0.3218, Xi_predicted=50.0,
                                   artifact_bound=5e-4)
    assert a["admitted"] is False
    assert a["headroom"] < 0


def test_a_large_artifact_alone_can_close_the_admission_gate():
    a = vf.reachable_set_admission(c_field_reference=0.3218, Xi_predicted=1.0,
                                   artifact_bound=0.5)
    assert a["admitted"] is False


def test_the_whole_wp6_window_is_admissible_at_the_expected_contrast():
    """An ex-ante feasibility check: if no candidate could satisfy the gate the tranche would be
    design-blocked before any computation, which is a legitimate outcome — it is not the case."""
    for Xi in (vf.XI_WINDOW_LO, 1.0, vf.XI_WINDOW_HI):
        a = vf.reachable_set_admission(0.3218, Xi, vf.ARTIFACT_BUDGET_R_ABS)
        assert a["admitted"], Xi
    assert vf.max_admissible_Xi(0.3218 * 0.95, vf.ARTIFACT_BUDGET_R_ABS) > vf.XI_WINDOW_HI


def test_the_artifact_budget_costs_less_than_a_quarter_of_the_factor_of_two_criterion():
    j = vf.artifact_budget_justification(0.3218)
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
    tol_R = vf.resolution_consistency_tolerance("R", b)
    tol_Xi = vf.resolution_consistency_tolerance("Xi_field", b)
    assert tol_Xi > tol_R > 0
    # derived, not chosen: R's tolerance is kappa times the two slot-height error differences
    expect = vf.KAPPA_RES * sum(
        abs(vf.element_error(f * vf.S_COARSE) - vf.element_error(f * vf.S_FINE))
        for f in (vf.BASE["h_low"], vf.BASE["h_high"]))
    assert tol_R == pytest.approx(expect, rel=1e-15)
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

def _cands(xis):
    return [{"w": w, "kz": kz, "Xi_coupon": x, "admitted": True}
            for (w, kz), x in zip([(c["w"], c["kz"]) for c in SCI], xis)]


def test_bridge_selection_is_deterministic_and_reads_coupon_output_only():
    xis = [0.05, 0.09, 0.15, 0.3, 0.6, 1.1, 1.9, 2.8, 3.6, 4.2, 5.5, 8.0]
    a = vf.select_bridges(_cands(xis))
    b = vf.select_bridges(_cands(xis))
    assert [(c["w"], c["kz"]) for c in a] == [(c["w"], c["kz"]) for c in b]
    assert len(a) == vf.N_LOG_TARGETS + 2
    src = inspect.getsource(vf.select_bridges)
    for forbidden in ("R", "Xi_hat", "c_hat", "s_"):
        assert '"%s"' % forbidden not in src


def test_an_inadmissible_candidate_can_never_be_selected():
    xis = [0.05, 0.09, 0.15, 0.3, 0.6, 1.1, 1.9, 2.8, 3.6, 4.2, 5.5, 8.0]
    cs = _cands(xis)
    for c in cs:
        c["admitted"] = c["Xi_coupon"] < 1.0
    sel = vf.select_bridges(cs)
    assert all(c["Xi_coupon"] < 1.0 for c in sel)


def test_selection_ties_break_on_the_integer_geometry():
    cs = [{"w": 9, "kz": 2, "Xi_coupon": 1.0, "admitted": True},
          {"w": 3, "kz": 4, "Xi_coupon": 1.0, "admitted": True}]
    sel = vf.select_bridges(cs)
    assert sel[0]["w"] == 3


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


def test_the_execution_authority_records_everything_a_future_stage_must_bind():
    a = vf.execution_authority("p3")
    for k in ("stage", "source_commit", "source_tree", "protocol_sha256",
              "geometry_spec_sha256", "protocol_config_sha256", "fixture_spec_sha256",
              "execution_matrix_sha256", "input_file_sha256", "backend", "dependencies",
              "seed", "solver_config", "base_commit", "base_tree"):
        assert k in a, k
    assert a["seed"] is None
    assert a["dependencies"]["numpy"]


def test_the_primary_driver_refuses_without_a_freeze_artifact():
    assert not (REPO / vf.FREEZE_REL).exists()
    with pytest.raises(vf.FreezeMissing):
        vf.require_freeze("p3")
    with pytest.raises(vf.FreezeMissing):
        drv.run_phase("p3")


def test_the_primary_driver_refuses_a_freeze_that_does_not_match_the_execution_authority(tmp_path):
    good = {"protocol_config_sha256": vf.record_hash(vf.protocol_config()),
            "fixture_spec_sha256": vf.record_hash(vf.fixture_spec_config()),
            "execution_matrix_sha256": vf.record_hash(vf.execution_matrix()),
            "frozen_bridges": [{"w": 5, "kz": 2}]}
    p = tmp_path / "bridge_freeze.json"
    p.write_text(json.dumps(good))
    assert vf.require_freeze("p3", path=p)["frozen_bridges"]
    bad = dict(good, protocol_config_sha256="0" * 64)
    p.write_text(json.dumps(bad))
    with pytest.raises(vf.FreezeMissing):
        vf.require_freeze("p3", path=p)
    empty = dict(good, frozen_bridges=[])
    p.write_text(json.dumps(empty))
    with pytest.raises(vf.FreezeMissing):
        vf.require_freeze("p3", path=p)


# ==========================================================================================
# 10. No solver runs here, and none can
# ==========================================================================================

@pytest.mark.parametrize("mode", list(drv.SOLVING_MODES))
def test_every_solving_mode_refuses_while_the_tranche_is_pre_execution(mode):
    assert drv.EXECUTION_AUTHORISED is False
    with pytest.raises((drv.ExecutionNotAuthorised, vf.FreezeMissing)):
        drv.run_phase(mode)


def test_the_single_solver_call_site_refuses():
    with pytest.raises(drv.ExecutionNotAuthorised):
        drv.solve(np.ones((4, 4, 4), bool), g=1e-6)


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
    assert "EXECUTION_AUTHORISED" in ast.dump(guard.test)


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


def test_no_preflight_test_is_marked_slow(request):
    """This whole file must stay in the quick CI lane: it contains no science-heavy work."""
    tree = ast.parse(pathlib.Path(__file__).read_text())
    marks = {d.attr for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)
             for d in n.decorator_list
             if isinstance(d, ast.Attribute)}
    marks |= {d.func.attr for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)
              for d in n.decorator_list
              if isinstance(d, ast.Call) and isinstance(d.func, ast.Attribute)}
    assert marks <= {"parametrize"}, marks


# ==========================================================================================
# 11. The planned matrix, Arm J and the bundle documents
# ==========================================================================================

def test_the_execution_matrix_reports_zero_executed_solves_and_an_exact_total():
    m = vf.execution_matrix()
    assert m["solves_executed"] == 0
    assert m["n_rows"] == m["maximum_possible"] == len(m["rows"])
    assert m["mandatory_scheduled"] + m["conditional"] + m["diagnostic_only"] == m["n_rows"]
    for phase in ("P0", "P1", "P2", "P3", "P4"):
        assert m["by_phase"][phase] > 0
    p1 = [r for r in m["rows"] if r["kind"] == "identical_path_control"]
    assert len(p1) == 2 * 2 * len(SCI) == 48
    assert m["by_phase"]["P4"] == vf.ARM_J["planned_solves"]


def test_arm_j_is_preserved_with_its_purpose_matrix_and_decision_status():
    assert vf.ARM_J["status"] == "decision_bearing"
    assert vf.ARM_J["gate"] == {"R_rel": 1e-3, "s_abs": 5e-4}
    assert vf.ARM_J["planned_solves"] == 20
    for k in ("purpose", "relationship_to_corrected_geometry", "ordering", "fail_semantics",
              "matrix"):
        assert vf.ARM_J[k]


def test_every_phase_is_marked_unauthorised_and_the_ordering_is_declared():
    assert [p["id"] for p in vf.EXECUTION_PHASES] == ["P0", "P1", "P2", "P3", "P4"]
    assert all(p["authorised_now"] is False for p in vf.EXECUTION_PHASES)
    assert "P0 -> P1 -> P2" in vf.execution_matrix()["ordering"]


def test_p1_never_reveals_a_mirror_recovery_case():
    m = vf.execution_matrix()
    p1 = [r for r in m["rows"] if r["phase"] == "P1"]
    assert p1 and all(r["variant"] == "identical" for r in p1)


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
