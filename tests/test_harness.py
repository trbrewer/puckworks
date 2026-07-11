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


def test_a8_bedstate_fields():
    """A8: BedState carries per-depth-cell porosity + fines inventory fields."""
    from puckworks.contracts import BedState, SCHEMA_VERSION
    assert SCHEMA_VERSION == "0.5"
    b = BedState(dose_kg=0.018, depth_m=0.02, area_m2=2.6e-3, porosity=0.3)
    assert all(hasattr(b, a) for a in
               ("porosity_profile", "fines_mobile", "fines_bound"))
