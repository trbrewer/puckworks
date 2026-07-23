"""gagne2021 apparent-resistance decline vs the liquor-viscosity hypothesis — DISCRIMINATION.

Records a bounded degeneracy from machine-logged traces; it does NOT validate a mechanism.
"""
from puckworks import data as pwdata
from puckworks.analysis import gagne2021_resistance as gr
from puckworks.validation.gates import gate_gagne2021_viscosity_discrimination


def test_observed_resistance_declines_across_all_shots():
    obs = gr.observed_resistance_decline()
    assert obs["n_shots"] == 11
    assert obs["lo"] > 1.0                 # every shot's post-bloom resistance declines
    assert obs["median"] > 1.3             # a large, robust decline


def test_shipping_summary_is_declared_and_matches_the_raw_traces():
    """The gate reads a SHIPPING derived summary (raw .shot stays out of the wheel); the committed
    summary must equal a fresh recompute from the raw traces, and be MANIFEST-declared."""
    import csv
    import os
    summary = {r["shot_id"]: float(r["r_decline_ratio"]) for r in pwdata.gagne2021_resistance_decline()}
    assert len(summary) == 11
    fresh = {sid: round(ratio, 4) for sid, ratio in gr._decline_from_shots()}
    assert set(summary) == set(fresh)
    for sid in summary:
        assert abs(summary[sid] - fresh[sid]) < 1e-4, sid       # committed == recompute
    mp = os.path.join(os.path.dirname(__file__), "..", "puckworks", "data", "MANIFEST.csv")
    with open(mp, newline="", encoding="utf-8") as fh:
        ids = {row["dataset_id"] for row in csv.DictReader(fh)}
    assert "gagne2021/resistance_decline_summary" in ids


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
