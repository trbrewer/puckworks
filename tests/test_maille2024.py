"""maille2024 Phase-0 table intake + discriminating-computation smoke tests.

Offline + deterministic. Asserts loader structure/anchors and the three verifications in
`puckworks.analysis.maille2024` (no model/PDE runs here). Data is the 2026-07-25 Tim drop
(thesis tables; the extraction figures follow separately).
"""
from puckworks import data as d
from puckworks.analysis import maille2024 as m


# ── loaders ───────────────────────────────────────────────────────────────────────
def test_material_legend_and_phi_load():
    mats = {r["Sample ID"]: r for r in d.maille_materials()}
    assert len(mats) == 21 and mats["Omega_A"]["Sieve class (um)"] == "1000-1180"
    phi = {r["Sample ID"]: r for r in d.maille_phi()}
    assert len(phi) == 17
    for r in phi.values():
        assert 0.3 < float(r["phi"]) < 0.7


def test_kinetics_tables_load():
    caf = d.maille_kinetics_caffeine_3cqa()
    acids = d.maille_kinetics_organic_acids()
    assert len(caf) == 17 and len(acids) == 16
    a = {r["Sample ID"]: r for r in caf}["Omega_A"]
    assert float(a["Caffeine lambda_fast (s)"]) == 9.2 and float(a["Caffeine lambda_slow (s)"]) == 109


def test_psd_and_equilibrium_load():
    psd = {r["Sample ID"]: r for r in d.maille_psd_hybrid()}
    assert len(psd) == 21 and float(psd["Omega_A"]["Volume Fraction <186um"]) == 0.02
    eq = {r["Sample ID"]: r for r in d.maille_equilibrium()}
    assert len(eq) == 21 and float(eq["Omega_A"]["Caffeine 600s avg (mg per L)"]) == 384


# ── discriminating computations ─────────────────────────────────────────────────────
def test_e1_shell_depth_resolves_to_two_layer():
    e = m.e1_shell_depth_resolution()
    assert e["adopted"] == "two_layer" and e["passed"]
    # two cell layers reproduce Table 6.3; one layer is far off (~10x the error)
    assert e["mean_abs_err_two_layer"] < 0.05
    assert e["mean_abs_err_one_layer"] > 0.15
    assert e["mean_abs_err_two_layer"] < e["mean_abs_err_one_layer"]


def test_phi_closure_internal_consistency():
    c = m.phi_closure_consistency()
    assert c["passed"] and c["eq67_violations"] == []          # phi = fines + coarse exactly
    assert c["theta_v_fines_vs_psd_mean_abs_diff"] < 0.01      # 6.3 fines tracks 5.4 <186um


def test_kinetics_flags_catch_the_two_impossible_cis():
    k = m.kinetics_flags()
    assert k["n_impossible_ci"] == 2
    hits = {(f["sample"], f["compound"], f["regime"]) for f in k["flagged"]}
    assert ("Omega_T", "3-CQA", "lambda_fast") in hits      # upper CI 11.9 < est 12.2
    assert ("Omega_L", "Quinic", "lambda_slow") in hits     # CI [65,54] does not bracket 44
