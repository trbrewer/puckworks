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
