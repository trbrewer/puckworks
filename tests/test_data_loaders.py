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


# --- schmieder2023 (0.1) ---
def test_schmieder_table_a1_matches_card():
    rows = pwdata.schmieder_kinetics_fit_avg()
    assert len(rows) == 60  # 15 exp x 4 components
    e7 = [r for r in rows if r["exp"] == 7 and r["component"] == "caffeine"][0]
    # card central point: caffeine c0=9.71, lambda=23.09
    assert abs(e7["c0"] - 9.70981) < 1e-4
    assert abs(e7["lambda_g"] - 23.09434) < 1e-4


def test_schmieder_reps_and_cupmasses():
    reps = pwdata.schmieder_kinetics_fit_reps()
    assert len(reps) == 192  # 48 exp-rep x 4 components
    comps = {r["component"] for r in reps}
    assert comps == {"trigonelline", "caffeine", "5-CQA", "TDS"}
    cups = pwdata.schmieder_cup_masses()
    assert len(cups) == 612  # 48 exp-rep x 4 comp x 3 BR
    assert {r["brew_ratio"] for r in cups} == {"1/1", "1/2", "1/3"}


def test_wadsworth_grindmap_table1():
    rows = pwdata.wadsworth_grindmap_table1()
    assert len(rows) == 22  # 2 coffees x 11 settings
    assert {r["coffee"] for r in rows} == {"Guayacan", "Tumba"}
    # S = <R><R2>/<R3> reconstructs the reported S column (moments consistent)
    r = rows[0]
    S = r["R_mean_m"] * r["R2_mean_m2"] / r["R3_mean_m3"]
    assert abs(S - r["S_polydispersivity"]) < 5e-3


def test_liang_figures_load():
    f3 = pwdata.liang_fig3_tds()
    assert len(f3) > 20 and "TDS_percent" in f3[0]
    f4 = pwdata.liang_fig4_E()
    assert {r["measurement"] for r in f4} == {"equilibrium", "oven_drying"}
    assert len(pwdata.liang_fig5_cupping()) > 0


def test_moroney_figures_load():
    f6 = pwdata.moroney_fig6()
    assert len(f6) > 5 and f6[0]["c_h_nondimensional"] > 0.9  # starts saturated
    t1 = {r["symbol"]: r["value"] for r in pwdata.moroney_table1()}
    assert float(t1["a2"]) == 5.139 and float(t1["a3"]) == 0.473


def test_grudeva_data_load():
    p = {r["symbol"]: r for r in pwdata.grudeva_params()}
    assert "kappa" in p and "ADJUDICATED" in p["kappa"]["classification"]
    v = pwdata.grudeva_vial_stats()
    assert len(v) == 16
    total = sum(r["solubles_mean_g"] for r in v)
    assert 2.5 < total < 3.5  # ~3 g total solubles per shot


def test_pannusch_table2_load():
    t = {r["solute"]: r for r in pwdata.pannusch_table2()}
    assert set(t) == {"caffeine", "trigonelline", "5CQA", "tds"}
    assert abs(t["caffeine"]["K_ref"] - 0.81) < 1e-9
    assert t["trigonelline"]["gamma"] == -431


def test_foster_machine_mode():
    from puckworks.models.foster2025 import machine_mode as fm
    p = {r["symbol"]: r for r in pwdata.foster2025_params()}
    assert abs(p["t_shift"]["value"] - 0.796) < 1e-9
    s_p, t_p_model, Q_p = fm.ponding()
    assert 0 < s_p < 1e-3 and Q_p > 0            # ponding front sub-mm, flow>0
    t_p, t_s = fm.reported_times()
    assert abs(t_p - 0.823) < 0.01 and abs(t_s - 6.669) < 0.02


def test_schmieder_raw_fractions_and_rsm():
    frac = pwdata.schmieder_raw_fractions()
    assert len(frac) == 288 and frac[0]["fraction"] == 1.0
    rsm = pwdata.schmieder_rsm()
    assert len(rsm) == 12  # 4 components x 3 BR
    # spot-check a transcribed coefficient (Trigonelline BR 1/1 beta0 = 185.8)
    t11 = [r for r in rsm if r["component"] == "Trigonelline"
           and r["brew_ratio"] == "1/1"][0]
    assert abs(t11["beta0"] - 185.8) < 1e-6
