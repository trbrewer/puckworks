"""vacaguerra2023a Phase-0 data intake + discriminating-computation smoke tests.

Offline + deterministic. Asserts loader structure/anchors and the three verifications in
`puckworks.analysis.vacaguerra2023a` (no model/PDE runs here). Data is the 2026-07-25 Tim drop
digitized from the 2022-09-27 preprint.
"""
from puckworks import data as d
from puckworks.analysis import vacaguerra2023a as v


# ── loaders ───────────────────────────────────────────────────────────────────────
def test_table_c1_nine_operating_points():
    rows = d.vacaguerra_extraction_conditions()
    assert len(rows) == 9
    assert sorted({r["Distribution"] for r in rows}) == ["A", "B", "C"]
    assert sorted({r["Dosage_g"] for r in rows}) == [17.5, 19.86, 22.2]
    for r in rows:
        assert 0.2 < r["epsilon_0"] < 0.4
        assert r["DeltaP_bar"] > 0 and r["Q_ml_per_s"] > 0 and r["delta_L_mm"] > 0


def test_psd_three_distributions_match_card():
    psd = {r["Distribution"]: r for r in d.vacaguerra_psd()}
    assert psd["A"]["alpha_um"] == 224 and psd["A"]["beta"] == 1.95
    assert psd["C"]["alpha_um"] == 427 and psd["C"]["beta"] == 1.40   # widest -> densest
    for r in psd.values():
        assert 0.7 < r["psi"] < 0.85


def test_coefficient_loaders():
    k = d.vacaguerra_phi_coefficients()
    x = d.vacaguerra_omega_coefficients()
    assert set(k) == {"k1", "k2", "k3", "k4", "k5"} and k["k3"] == 6.65e4   # printed POSITIVE
    assert set(x) == {"x1", "x2", "x3", "x4"} and x["x1"] == 0.48


def test_fig12_validation_pairs_load():
    rows = d.vacaguerra_dry_porosity_validation()
    assert len(rows) == 50
    assert {r["series"] for r in rows} == {
        "circle_60mm_stainless_portafilter", "square_50mm_acrylic_vessel"}


# ── discriminating computations ─────────────────────────────────────────────────────
def test_compression_sign_resolves_to_minus_beta():
    s = v.resolve_compression_sign()
    assert s["adopted_convention"] == "-beta" and s["passed"]
    # -beta omega is physical (in the measured porosity range) and matches the Fig-9 fits
    lo, hi = s["minus_omega_range"]
    assert 0.28 <= lo and hi <= 0.40 and s["minus_matches_fig9"]
    # the printed +beta form is unphysical (repose porosity above the loosest measured bed)
    assert s["plus_beta_unphysical"] and s["plus_omega_range"][1] > 0.45


def test_fig12_validation_r2_matches_card():
    f = v.fig12_validation()
    assert f["n"] == 50 and f["passed"]
    assert 0.90 <= f["r2"] <= 0.97          # card reports ~0.93


def test_permeability_darcy_reconstructs_measured_range():
    k = v.permeability_darcy()
    assert k["n_points"] == 9 and k["passed"]
    assert k["n_in_stated_band"] >= 7 and k["n_order_of_magnitude_ok"] == 9
    # the two loosest 17.5 g beds sit above the stated band
    above = [p for p in k["points"] if not p["in_stated_band"]]
    assert {p["distribution"] for p in above} == {"B", "C"}
    assert all(p["dosage_g"] == 17.5 for p in above)


def test_permeability_scales_with_viscosity():
    # K is proportional to mu -- halving mu halves every recomputed K
    base = v.permeability_darcy(mu_pas=3.5e-3)["points"]
    half = v.permeability_darcy(mu_pas=1.75e-3)["points"]
    for b, h in zip(base, half):
        assert abs(h["k_darcy_m2"] - 0.5 * b["k_darcy_m2"]) < 1e-18
