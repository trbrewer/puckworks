"""gagne2021 apparent-resistance decline vs the liquor-viscosity hypothesis — DISCRIMINATION.

Records a bounded degeneracy from machine-logged traces; it does NOT validate a mechanism.
"""
from puckworks.analysis import gagne2021_resistance as gr
from puckworks.validation.gates import gate_gagne2021_viscosity_discrimination


def test_observed_resistance_declines_across_all_shots():
    obs = gr.observed_resistance_decline()
    assert obs["n_shots"] == 11
    assert obs["lo"] > 1.0                 # every shot's post-bloom resistance declines
    assert obs["median"] > 1.3             # a large, robust decline


def test_viscosity_is_admissible_but_degenerate():
    r = gr.discrimination()
    # the observed decline is quantitatively matched by mu(TDS) at Gagne's ~15% early first-drip TDS
    assert r["viscosity_admissible"]
    assert abs(r["mu_ratio_early"] - r["observed"]["median"]) < 0.5 * r["observed"]["median"]
    # bulk-TDS mu is a smaller (partial) contribution — the decline needs the high-early-TDS regime
    assert r["mu_ratio_bulk"] < r["mu_ratio_early"]
    # ...but the same magnitude is reachable by a bed mechanism; the traces do not discriminate
    assert r["degenerate_with_bed"]


def test_gate_passes():
    assert gate_gagne2021_viscosity_discrimination()["passed"]
