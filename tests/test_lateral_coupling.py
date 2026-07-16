"""WP6 / PR10 — the minimal lateral-coupling feasibility model: mass conservation, the
zero-coupling limit (Model 1 -> Model 0), the strong-coupling homogenization limit, monotone
redistribution, and the regime map. Exact linear network -> asserted to machine precision.
"""
import pytest

from puckworks.models.lateral_coupling import (
    model0_uncoupled, model1_two_path, coupling_number, regime)

_P = 9.0e5
# asymmetric paths: path 1 top-heavy (high mid-p), path 2 bottom-heavy (low mid-p)
_G = dict(g1_top=3.0, g1_bot=1.0, g2_top=1.0, g2_bot=3.0)


def test_global_mass_conservation_at_all_coupling():
    for Glat in (0.0, 0.5, 1.0, 4.0, 1e4):
        r = model1_two_path(_P, G_lat=Glat, **_G)
        assert r["Q"] == pytest.approx(r["q_in"], abs=1e-3)   # inflow == outflow


def test_zero_coupling_reduces_to_model0():
    r = model1_two_path(_P, G_lat=0.0, **_G)
    m1 = model0_uncoupled(_P, _G["g1_top"], _G["g1_bot"])
    m2 = model0_uncoupled(_P, _G["g2_top"], _G["g2_bot"])
    assert r["p1"] == pytest.approx(m1["p_mid"])
    assert r["p2"] == pytest.approx(m2["p_mid"])
    assert r["q_lat_1to2"] == pytest.approx(0.0)              # no transverse flux uncoupled


def test_strong_coupling_homogenizes():
    r = model1_two_path(_P, G_lat=1e6, **_G)
    assert abs(r["p1"] - r["p2"]) < 1e-3 * _P                 # pressures equalize


def test_coupling_monotonically_reduces_transverse_gradient():
    gaps = [abs(model1_two_path(_P, G_lat=G, **_G)["p1"] - model1_two_path(_P, G_lat=G, **_G)["p2"])
            for G in (0.0, 0.5, 1.0, 4.0, 20.0)]
    assert all(a > b for a, b in zip(gaps, gaps[1:]))         # strictly decreasing


def test_regime_map():
    g_axial = 2.0
    assert regime(coupling_number(0.01, g_axial)) == "uncoupled"
    assert regime(coupling_number(2.0, g_axial)) == "transitional"
    assert regime(coupling_number(50.0, g_axial)) == "homogenized"
