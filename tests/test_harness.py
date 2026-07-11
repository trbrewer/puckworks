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
    """P2 cross-pressure: mechanisms separate by regime (no single winner) --
    Phi(t) best on OOS mean, RC-3b wins low-P, static wins mid-P."""
    X = h.cross_pressure_discrimination()
    assert X["phi_generalizes"]
    assert X["rc3b_wins_low_p"]
    assert X["static_wins_mid_p"]


def test_a8_bedstate_fields():
    """A8: BedState carries per-depth-cell porosity + fines inventory fields."""
    from puckworks.contracts import BedState, SCHEMA_VERSION
    assert SCHEMA_VERSION == "0.5"
    b = BedState(dose_kg=0.018, depth_m=0.02, area_m2=2.6e-3, porosity=0.3)
    assert all(hasattr(b, a) for a in
               ("porosity_profile", "fines_mobile", "fines_bound"))
