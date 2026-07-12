"""Smoke tests for the P1 extraction comparison harness."""
from puckworks import harness as h


def test_csat_not_silently_merged():
    """The three distinct c_sat values are surfaced, never merged (§5.4)."""
    assert h.csat_values() == [170.0, 212.4, 224.0]
    # every model carries its own inventory reference
    invs = {hz["inventory"] for hz in h.P1_HAZARDS.values()}
    assert len(invs) >= 4


def test_dissolution_speed_discriminator():
    """§5.6: Waszkiewicz TDS fractions favor near-instant dissolution."""
    r = h.dissolution_speed_test()
    assert r["early_to_peak"] > 0.8
    assert r["favors"] == "near-instant dissolution"


def test_p2_kappa_ladder():
    """P2: time-dependent Phi(t) (rung 4) beats the constant-kappa null."""
    L = h.kappa_t_ladder()
    assert L["rung4_beats_floor"]
    assert L["rung4_phi_of_t"] < L["rung1_const_kappa"]
    assert L["improvement_factor"] > 2.0


def test_p2_rung5_rc3b():
    """P2 rung 5: RC-3b (Cameron-coupled Phi) beats the flat null but loses to
    the empirical near-instant rung 4 -> near-instant dissolution favored."""
    L = h.kappa_t_ladder()
    assert L["rung5_rc3b_cameron_coupled"] < L["rung1_const_kappa"]
    assert L["rung5_rc3b_cameron_coupled"] > L["rung4_phi_of_t"]


def test_p2_cross_pressure_separation():
    """P2 cross-pressure: mechanisms separate by regime (no single mechanism
    lowest everywhere) -- Phi(t) lowest transfer-mean, RC-3b lower low-P, static
    lower mid-P."""
    X = h.cross_pressure_discrimination()
    assert X["phi_generalizes"]
    assert X["rc3b_lower_low_p"]
    assert X["static_lower_mid_p"]


def test_lee2023_negative_result():
    """lee2023: imposed rho_c=798 gives a fine-grind decline; physical rho_c=399
    only plateaus (the paper's documented negative result). Never promote."""
    import numpy as np
    from puckworks.models.lee2023 import feedback as lee
    g = np.linspace(1.1, 2.3, 13)
    assert lee.peak_and_fine_decline(g, rho_c=798.0)["fine_side_decline"]
    assert not lee.peak_and_fine_decline(g, rho_c=399.0)["fine_side_decline"]
    assert abs(lee.tau_shot(1.1) - 1.12) < 0.03
    assert abs(lee.tau_shot(2.3) - 0.48) < 0.03


def test_a8_bedstate_fields():
    """A8: BedState carries per-depth-cell porosity + fines inventory fields."""
    from puckworks.contracts import BedState, SCHEMA_VERSION
    assert SCHEMA_VERSION == "0.6"   # 0.6 = A4 SoluteInventory (additive; A8 fields intact)
    b = BedState(dose_kg=0.018, depth_m=0.02, area_m2=2.6e-3, porosity=0.3)
    assert all(hasattr(b, a) for a in
               ("porosity_profile", "fines_mobile", "fines_bound"))


def test_unified_kappa_t_branches():
    """kappa(t) closure: branch signs (compaction/swelling/fines down, extraction
    up) and reduction to unity when neutral."""
    n = h.kappa_branches()
    assert n["f_swelling"] == 1.0 and n["f_extraction"] == 1.0 and n["f_fines"] == 1.0
    assert h.kappa_branches(P_bar=13)["f_compaction"] < h.kappa_branches(P_bar=2)["f_compaction"]
    assert h.kappa_branches(EY=0.3)["f_extraction"] > 1.0
    assert h.kappa_branches(t_swell_s=30)["f_swelling"] < 1.0


def test_coupled_kappa_t():
    """Coupled kappa(t): non-monotone trajectory driven by live cameron EY(t) +
    mo2023_2 swelling (swelling closes early, extraction opens late)."""
    import numpy as np
    r = h.coupled_kappa_t(P_bar=9.0, t_shot_s=30.0)
    k = r["kappa_over_kappa0"]
    assert r["EY"][-1] > r["EY"][2] > 0
    imin = int(np.argmin(k))
    assert 0 < imin < len(k) - 1 and k[-1] > k[imin]


def test_g9_series_resistance():
    """G9: puck resistance (measured tamped kappa) is below the DE1 total, and the
    fitted effective kappa sits below the measured tamped kappa (series residual)."""
    g = h.g9_series_resistance()
    assert g["puck_below_total"] and g["fitted_below_measured"]


def test_coupled_kappa_t_synthesis():
    """brewer2026.coupled_kappa_t: extraction-only reduces to poroelastic rung 4
    exactly; adding swelling over-closes the saturated rig (diagnostic residual)."""
    from puckworks.models.brewer2026 import coupled_kappa_t as ck
    assert ck.degeneracy_rmse(P_bar=9.0) < 0.13            # == rung 4
    c = ck.composition_residual(P_bar=9.0)
    assert c["swelling_closes"] and c["rmse"] > 3 * ck.degeneracy_rmse(9.0)
