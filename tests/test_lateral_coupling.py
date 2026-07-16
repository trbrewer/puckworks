"""WP6 — the minimal lateral-coupling FEASIBILITY model: pressure bounds, per-node and global
mass conservation, the canonical transverse-flux sign, path-swap symmetry, the identical-path
negative control, the strong-coupling analytical limit, monotone gap reduction, nondecreasing
effective conductance, dimensional scaling, the regime map (incl. boundary behaviour), and input
validation. The network is an exact linear solve -> asserted to machine precision. Also covers
the frozen streamtube SHARE proxy helpers (analysis.lateral_proxy).
"""
import pytest

from puckworks.models.lateral_coupling import (
    model0_uncoupled, model1_two_path, strong_coupling_limit,
    g_series, g_axial_reference, coupling_number, regime,
    equalization_number, gap_remaining_fraction, equalization_regime,
    XI_UNCHANGED, XI_HOMOGENIZED)
from puckworks.analysis.lateral_proxy import (
    homogenize_relative_flow, frozen_two_path_proxy)

_P = 9.0e5
# asymmetric paths: path 1 top-heavy (high mid-p), path 2 bottom-heavy (low mid-p)
_G = dict(g1_top=3.0, g1_bot=1.0, g2_top=1.0, g2_bot=3.0)


# --------------------------------------------------------------------------- physical model

def test_pressure_bounds_between_outlet_and_inlet():
    for Glat in (0.0, 0.5, 1.0, 4.0, 1e4):
        r = model1_two_path(_P, G_lat=Glat, **_G)
        for p in (r["p1"], r["p2"]):
            assert 0.0 <= p <= _P                             # P_out=0 gauge, no overshoot


def test_per_node_and_global_mass_conservation():
    for Glat in (0.0, 0.5, 1.0, 4.0, 1e4):
        r = model1_two_path(_P, G_lat=Glat, **_G)
        # node 1: inlet == outlet + transverse-out; node 2: inlet + transverse-in == outlet
        assert r["node1_residual"] == pytest.approx(0.0, abs=1e-6)
        assert r["node2_residual"] == pytest.approx(0.0, abs=1e-6)
        assert r["global_residual"] == pytest.approx(0.0, abs=1e-6)
        assert r["Q"] == pytest.approx(r["q_in"], abs=1e-6)   # inflow == outflow


def test_canonical_transverse_flux_sign():
    # p1 > p2 here (path 1 top-heavy) -> canonical q_lat_1to2 = G_lat*(p1-p2) > 0 (flow 1->2)
    r = model1_two_path(_P, G_lat=1.0, **_G)
    assert r["p1"] > r["p2"]
    assert r["q_lat_1to2"] == pytest.approx(1.0 * (r["p1"] - r["p2"]))
    assert r["q_lat_1to2"] > 0
    # swapping the paths must flip the sign but not the magnitude
    rs = model1_two_path(_P, g1_top=1.0, g1_bot=3.0, g2_top=3.0, g2_bot=1.0, G_lat=1.0)
    assert rs["q_lat_1to2"] == pytest.approx(-r["q_lat_1to2"])


def test_path_swap_symmetry():
    r = model1_two_path(_P, G_lat=1.3, **_G)
    rs = model1_two_path(_P, g1_top=1.0, g1_bot=3.0, g2_top=3.0, g2_bot=1.0, G_lat=1.3)
    assert rs["p1"] == pytest.approx(r["p2"])                 # labels 1<->2 swap
    assert rs["p2"] == pytest.approx(r["p1"])
    assert rs["q1"] == pytest.approx(r["q2"])
    assert rs["q2"] == pytest.approx(r["q1"])
    assert rs["Q"] == pytest.approx(r["Q"])                   # total flow invariant to labelling


def test_zero_coupling_reduces_to_model0():
    r = model1_two_path(_P, G_lat=0.0, **_G)
    m1 = model0_uncoupled(_P, _G["g1_top"], _G["g1_bot"])
    m2 = model0_uncoupled(_P, _G["g2_top"], _G["g2_bot"])
    assert r["p1"] == pytest.approx(m1["p_mid"])
    assert r["p2"] == pytest.approx(m2["p_mid"])
    assert r["q_lat_1to2"] == pytest.approx(0.0)              # no transverse flux uncoupled


def test_identical_paths_negative_control():
    for Glat in (0.0, 0.5, 5.0, 1e6):
        r = model1_two_path(_P, g1_top=3.0, g1_bot=1.0, g2_top=3.0, g2_bot=1.0, G_lat=Glat)
        assert r["p1"] == pytest.approx(r["p2"])              # symmetric -> no transverse gradient
        assert r["q_lat_1to2"] == pytest.approx(0.0)          # ...hence no lateral flow, ever


def test_strong_coupling_matches_analytic_limit():
    lim = strong_coupling_limit(_P, **_G)
    r = model1_two_path(_P, G_lat=1e9, **_G)
    assert abs(r["p1"] - r["p2"]) < 1e-6 * _P                 # pressures equalize
    assert r["p1"] == pytest.approx(lim["p_inf"], rel=1e-4)
    assert r["Q"] == pytest.approx(lim["Q_inf"], rel=1e-4)


def test_coupling_monotonically_reduces_transverse_gradient():
    gaps = [abs(model1_two_path(_P, G_lat=G, **_G)["p1"] - model1_two_path(_P, G_lat=G, **_G)["p2"])
            for G in (0.0, 0.5, 1.0, 4.0, 20.0)]
    assert all(a > b for a, b in zip(gaps, gaps[1:]))         # strictly decreasing


def test_effective_conductance_nondecreasing_in_coupling():
    effs = [model1_two_path(_P, G_lat=G, **_G)["effective_conductance"]
            for G in (0.0, 0.5, 1.0, 4.0, 20.0, 1e4)]
    assert all(b >= a - 1e-9 for a, b in zip(effs, effs[1:]))  # coupling can only help throughput


def test_dimensional_scaling_of_conductances():
    # scaling every conductance by s scales flows by s and leaves pressures/shares invariant
    s = 10.0
    r = model1_two_path(_P, G_lat=0.75, **_G)
    rs = model1_two_path(_P, g1_top=30.0, g1_bot=10.0, g2_top=10.0, g2_bot=30.0, G_lat=0.75 * s)
    assert rs["p1"] == pytest.approx(r["p1"])
    assert rs["p2"] == pytest.approx(r["p2"])
    assert rs["Q"] == pytest.approx(s * r["Q"])


def test_g_series_and_axial_reference():
    assert g_series(3.0, 1.0) == pytest.approx(0.75)
    assert g_series(1.0, 3.0) == pytest.approx(0.75)
    # mirror case: both end-to-end series conductances are 0.75 -> reference 0.75
    assert g_axial_reference(3.0, 1.0, 1.0, 3.0) == pytest.approx(0.75)


def test_regime_map_and_boundaries():
    g_axial = 2.0
    assert regime(coupling_number(0.01, g_axial)) == "uncoupled"
    assert regime(coupling_number(2.0, g_axial)) == "transitional"
    assert regime(coupling_number(50.0, g_axial)) == "homogenized"
    # equality at lo and hi belongs to 'transitional' (documented boundary convention)
    assert regime(0.05) == "transitional"
    assert regime(5.0) == "transitional"
    assert regime(0.05 - 1e-9) == "uncoupled"
    assert regime(5.0 + 1e-9) == "homogenized"


def test_equalization_number_closed_form_matches_solved_gap():
    # gap/gap0 = 1/(1+Xi) exactly, for a case with a nonzero uncoupled gap (mirror is symmetric-
    # gap; use the asymmetric _G whose uncoupled p1 != p2)
    r0 = model1_two_path(_P, G_lat=0.0, **_G)
    gap0 = abs(r0["p1"] - r0["p2"])
    assert gap0 > 0
    for Glat in (0.0, 0.3, 1.0, 4.0, 25.0):
        r = model1_two_path(_P, G_lat=Glat, **_G)
        gap = abs(r["p1"] - r["p2"])
        Xi = equalization_number(Glat, **_G)
        assert gap_remaining_fraction(Xi) == pytest.approx(gap / gap0, rel=1e-9, abs=1e-12)


def test_equalization_regime_thresholds():
    # Xi thresholds are the exact images of the 5%/95% gap-reduction cutoffs
    assert equalization_regime(XI_UNCHANGED - 1e-9) == "pressure_gap_unchanged"
    assert equalization_regime(XI_UNCHANGED) == "pressure_gap_transition"
    assert equalization_regime(1.0) == "pressure_gap_transition"
    assert equalization_regime(XI_HOMOGENIZED - 1e-9) == "pressure_gap_transition"
    assert equalization_regime(XI_HOMOGENIZED) == "pressure_gap_homogenized"
    assert gap_remaining_fraction(XI_UNCHANGED) == pytest.approx(0.95)
    assert gap_remaining_fraction(XI_HOMOGENIZED) == pytest.approx(0.05)


def test_strong_coupling_limit_validates_P_in():
    with pytest.raises(ValueError):
        strong_coupling_limit(-1.0, **_G)                    # negative P_in
    with pytest.raises(ValueError):
        strong_coupling_limit(float("inf"), **_G)            # non-finite P_in
    with pytest.raises(ValueError):
        equalization_number(-1.0, **_G)                      # negative G_lat


def test_invalid_inputs_raise():
    with pytest.raises(ValueError):
        model1_two_path(-1.0, G_lat=1.0, **_G)                # negative P_in
    with pytest.raises(ValueError):
        model1_two_path(_P, g1_top=0.0, g1_bot=1.0, g2_top=1.0, g2_bot=3.0, G_lat=1.0)  # zero g
    with pytest.raises(ValueError):
        model1_two_path(_P, G_lat=-1.0, **_G)                 # negative G_lat
    with pytest.raises(ValueError):
        model1_two_path(float("inf"), G_lat=1.0, **_G)        # non-finite P_in
    with pytest.raises(ValueError):
        coupling_number(1.0, 0.0)                             # zero axial reference
    with pytest.raises(ValueError):
        regime(1.0, lo=0.5, hi=0.5)                           # hi must exceed lo
    with pytest.raises(ValueError):
        regime(-1.0)                                          # negative Lambda


# --------------------------------------------------------------------------- frozen share proxy

def test_homogenize_relative_flow_matches_closed_form():
    rf = [0.5, 1.5]
    assert list(homogenize_relative_flow(rf, 0.0)) == pytest.approx(rf)          # alpha=0 identity
    assert list(homogenize_relative_flow(rf, 1.0)) == pytest.approx([1.0, 1.0])  # alpha=1 uniform
    for a in (0.25, 0.5, 0.75):
        got = homogenize_relative_flow(rf, a)
        assert list(got) == pytest.approx([(1 - a) * x + a for x in rf])


def test_homogenize_relative_flow_validation():
    with pytest.raises(ValueError):
        homogenize_relative_flow([1.0, -0.1], 0.5)            # negative relative flow
    with pytest.raises(ValueError):
        homogenize_relative_flow([1.0, 1.0], 1.5)             # alpha out of [0,1]
    with pytest.raises(ValueError):
        homogenize_relative_flow([1.0, float("nan")], 0.5)    # non-finite


def test_frozen_proxy_is_a_share_homogenizer_only():
    # asymmetric end-to-end conductances so homogenization actually moves the shares
    p = frozen_two_path_proxy(_P, g1_top=3.0, g1_bot=1.0, g2_top=1.0, g2_bot=1.0, alpha=0.5)
    assert p["is_frozen_share_proxy"] is True
    assert p["Q_over_Q0"] == 1.0                              # uncoupled completion retains total flow
    assert p["proxy_inlet_share_1"] == p["proxy_outlet_share_1"]   # one share through whole depth
    assert p["proxy_share_transfer_1"] == 0.0
    # physical observables a share proxy cannot produce are None, never a fabricated 0
    assert p["physical_observables_available"] is False
    for v in p["physical_observables"].values():
        assert v is None


def test_frozen_proxy_validates_P_in():
    with pytest.raises(ValueError):
        frozen_two_path_proxy(-1.0, 3.0, 1.0, 1.0, 3.0, alpha=0.5)   # negative P_in
    with pytest.raises(ValueError):
        frozen_two_path_proxy(float("nan"), 3.0, 1.0, 1.0, 3.0, alpha=0.5)   # non-finite


def test_frozen_proxy_alpha_endpoints():
    kw = dict(g1_top=3.0, g1_bot=1.0, g2_top=1.0, g2_bot=1.0)
    at0 = frozen_two_path_proxy(_P, alpha=0.0, **kw)
    at1 = frozen_two_path_proxy(_P, alpha=1.0, **kw)
    assert at0["homogenized_shares"] == pytest.approx(at0["original_shares"])   # alpha=0: no change
    assert at1["homogenized_shares"] == pytest.approx([0.5, 0.5])               # alpha=1: uniform
