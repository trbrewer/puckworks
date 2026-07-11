"""Smoke tests for Phase 0 dataset loaders (DoD: loader smoke tests).

These assert structure and a few card-anchored values; they are NOT validation
gates (no model runs here).
"""
import numpy as np

from puckworks import data as pwdata


def test_waszkiewicz_traces_11_pressures():
    t = pwdata.waszkiewicz_traces()
    pressures = sorted(k for k in t if k != "columns")
    assert pressures == pwdata.WASZ_PRESSURES_BAR
    # each pressure has aligned columns and a plausible flow-rate channel
    for p in pressures:
        q = t[p]["mass_flow_rate__g_per_s"]
        assert q.size > 100 and np.isfinite(q).any()
    assert "basket_pressure__bar" in t["columns"]


def test_waszkiewicz_static_calibration_matches_card():
    c = pwdata.waszkiewicz_static_calibration()
    # card: (Q_c, P_c) = (1.90 g/s, 12 bar)
    assert abs(c["P_c_bar"] - 12.39) < 0.1
    assert abs(c["Q_c_g_per_s"] - 1.897) < 0.01


def test_waszkiewicz_tds_fractions():
    f = pwdata.waszkiewicz_tds_fractions()
    assert f["time_s"].size == 12
    assert f["time_s"][0] == 2.5 and f["time_s"][-1] == 57.5
    assert 0 < np.nanmax(f["tds_pct"]) < 30


def test_waszkiewicz_constants_and_brewer():
    k = pwdata.waszkiewicz_constants()
    assert abs(k["dose__g"] - 18.5) < 0.01
    assert abs(k["mu__Pas"] - 3.15e-4) < 1e-6
    b = pwdata.waszkiewicz_brewer_quadratic()
    assert set(b) == {"a", "b", "c"} and b["a"] > 0


def test_waszkiewicz_psd_shape():
    psd = pwdata.waszkiewicz_psd()
    assert psd["size_um"].size == 48
    assert psd["volume_pct"].shape[1] == 48
    assert psd["volume_pct"].shape[0] >= 1
