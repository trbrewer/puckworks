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


# ── extraction figures + phi-split-vs-Cameron (Figs 4.6-4.10 + Cameron Fig 2 drop) ──
def test_extraction_curves_load_all_five_analytes():
    rows = d.maille_extraction_curves()
    analytes = {r["analyte"] for r in rows}
    assert analytes == {"Caffeine", "3-CQA", "Citric acid", "Malic acid", "Quinic acid"}
    assert len(rows) > 250                                   # ~99+60+56+48+56 digitized points
    for r in rows:
        assert 0.0 <= r["C_over_Cinf"] <= 1.2 and r["time_s"] > 0


def test_two_regime_reproduces_omega_a_curves():
    r = m.two_regime_reproduction()
    assert r["passed"] and r["worst_mape_pct"] < 15.0       # tabulated params ~ the reported MPE
    for an in ("Caffeine", "3-CQA", "Citric acid", "Malic acid", "Quinic acid"):
        assert r["per_analyte"][an]["mape_pct"] < 15.0


def test_cameron_psd_loads_four_grinds():
    rows = d.cameron2020_psd()
    assert len(rows) > 400
    cols = [c for c in rows[0] if c.startswith("volume_percent_Gs_")]
    assert set(cols) == {"volume_percent_Gs_1.0", "volume_percent_Gs_1.5",
                         "volume_percent_Gs_2.0", "volume_percent_Gs_2.5"}


def test_phi_split_vs_cameron_semantics():
    p = m.phi_split_vs_cameron()
    assert p["passed"] and not p["commensurable"]
    # both fast-fractions decrease as grind coarsens (sign agreement)
    assert p["both_decrease_with_coarser_grind"]
    # maille phi on Cameron's espresso PSD is an EXTRAPOLATION above maille's own coarse-grind range
    assert min(p["maille_phi_on_cameron_range"]) > max(p["maille_own_phi_range"])
    # magnitudes differ several-fold (definitional gap), everywhere > 1
    assert min(p["ratio_range"]) > 3.0


def test_cross_model_timescale_cameron_two_regime_does_not_port():
    g = m.cross_model_timescale_cameron()
    # cameron-only half; roman-corrochano half stays rights-deferred
    assert g["roman_corrochano_half"].startswith("deferred")
    assert len(g["per_grind"]) == 4
    # the gate's finding: NO grind reproduces maille's fast timescale (lambda_fast > 19.1 s)
    assert g["passed"] and g["no_maille_fast_component"]
    assert not g["two_regime_ports_to_cameron"]
    for row in g["per_grind"]:
        assert not row["fast_in_maille_band"]          # fitted lambda_fast is above maille's fast band
        assert row["lambda_fast_s"] > 19.1
        assert row["r2"] > 0.98                         # a single-timescale form fits cameron well
