"""Cross-pressure heterogeneity, pressure domains and provenance graph (Paper B2 P1.1/P1.2/P1.3).

Also binds Table 3 to its producers. Every static and phi value in that table already matched the
producers exactly while all three rc3b values were stale by ~0.009 -- a one-column transcription
that survived because nothing checked it. These tests make that class of drift fail.
"""
import pathlib
import re

import numpy as np
import pytest

from puckworks import harness as h
from puckworks.analysis import waszkiewicz_cross_pressure as X

_ROOT = pathlib.Path(__file__).resolve().parents[1]
_DRAFT = _ROOT / "docs/PAPER_B2_TEMPORAL_DRAFT.md"


@pytest.fixture(scope="module")
def het():
    return X.cross_pressure_heterogeneity()


# --- P1.1 ------------------------------------------------------------------------------------
def test_every_pressure_is_scored_and_ranked(het):
    assert het["n_pressures"] == 11
    for p, row in het["per_pressure"].items():
        assert row["best"] in row["rmse"], p
        assert sorted(row["rank"].values()) == list(range(1, len(row["rmse"]) + 1)), p
        assert row["n_shots"] > 0, p


def test_the_best_branch_is_not_constant_across_pressure(het):
    """The finding the macro mean hides. If this ever becomes True, the manuscript's localisation
    caveat is wrong and must be revisited rather than left standing."""
    assert het["best_branch_is_constant_across_pressure"] is False
    assert len(het["branch_wins"]) >= 3, het["branch_wins"]


def test_phi_wins_the_band_containing_the_primary_analysis(het):
    """The primary 9-bar result sits inside the band Phi(t) wins, which is why the paper must not
    generalise it across pressure."""
    assert het["per_pressure"][9.0]["best"] == "phi"
    neighbours = [het["per_pressure"][p]["best"] for p in (7.0, 8.0, 9.0, 11.0)]
    assert set(neighbours) == {"phi"}, neighbours
    assert het["per_pressure"][4.0]["best"] != "phi"


def test_the_averaging_scheme_changes_the_ordering(het):
    """Equal-pressure and shot-weighted means answer different questions; the paper reports both
    because they disagree below first place."""
    assert het["averaging_scheme_changes_order"] is True
    assert het["equal_pressure_order"][0] == het["shot_weighted_order"][0] == "phi"


def test_shot_counts_are_uneven_enough_for_the_weighting_to_matter(het):
    lo, hi = het["n_shots_range"]
    assert hi >= 2 * lo, (lo, hi)


# --- Table 3 bound to its producers -----------------------------------------------------------
def _table3_rows():
    text = _DRAFT.read_text(encoding="utf-8")
    block = text[text.index("**Table 3."):]
    rows = {}
    for line in block.splitlines():
        m = re.match(r"\|\s*(LOPO-EC[^|]*|Shared calibration[^|]*)\|\s*([\d.]+)\s*\|"
                     r"\s*([\d.]+)\s*\|\s*([\d.]+)\s*\|", line)
        if m:
            rows[m.group(1).strip()] = tuple(float(m.group(i)) for i in (2, 3, 4))
        elif rows and line.strip() == "":
            break
    return rows


def test_table3_matches_its_producers():
    """All three columns, all three rows. rc3b was wrong in every row before this test existed."""
    rows = _table3_rows()
    assert len(rows) == 3, sorted(rows)
    lo = h.cross_pressure_loco()
    disc = h.cross_pressure_discrimination()
    per = disc["per_pressure"]
    off9 = [p for p in per if abs(float(p) - 9.0) > 1e-9]
    expected = {
        "LOPO-EC (equilibrium calibration withheld), all 11 pressures": lo["heldout_mean"],
        "Shared calibration, all 11 pressures": lo["shared_calibration_mean"],
        "Shared calibration, 10 off-9-bar pressures":
            {b: float(np.mean([per[p][b] for p in off9 if b in per[p]]))
             for b in ("static", "phi", "rc3b")},
    }
    for label, (s, phi, rc) in rows.items():
        want = expected[label]
        for got, key in ((s, "static"), (phi, "phi"), (rc, "rc3b")):
            assert abs(got - want[key]) < 5e-4, (label, key, got, want[key])


# --- P1.2 ------------------------------------------------------------------------------------
def test_pressure_domains_separate_the_four_quantities():
    d = X.pressure_domains()
    assert d["model_valid_pressure_range_bar"] == [1.0, 13.0]
    # recorded basket pressure is BELOW nominal at every setting -- the conflation hazard
    gaps = d["nominal_minus_recorded_bar"]
    assert all(v > 0 for v in gaps.values()), gaps
    assert d["primary_analysis_recorded_bar"] < d["primary_analysis_pressure_bar"]
    # P_c is a fitted parameter, not a rig setting, and is barely exercised
    assert d["n_pressures_at_or_above_P_c"] <= 2


def test_manuscript_states_the_recorded_pressure_gap():
    text = _DRAFT.read_text(encoding="utf-8")
    d = X.pressure_domains()
    assert "%.2f bar" % d["primary_analysis_recorded_bar"] in text
    assert "%.2f bar" % d["fitted_equilibrium_P_c_bar"] in text


# --- P1.3 ------------------------------------------------------------------------------------
def test_zero_free_parameters_does_not_imply_held_out():
    """The distinction P1.3 exists to make. Phi(t) has no coefficient fitted to the scored trace
    and is still not held out, because its sigmoid channel reuses the target."""
    g = X.provenance_graph()
    phi = g["branches"]["rung4_phi_of_t"]
    assert phi["free_params_fitted_to_scored_trace"] == 0
    assert phi["is_held_out"] is False
    assert phi["most_target_proximal_access"] == "indirect_target"


def test_only_the_null_comparator_is_held_out():
    g = X.provenance_graph()
    held = {b for b, v in g["branches"].items() if v["is_held_out"]}
    assert held == {"penalized_spline_loso"}, held


def test_every_branch_declares_its_inputs_with_known_access_levels():
    g = X.provenance_graph()
    for b, v in g["branches"].items():
        assert v["inputs"], b
        for inp in v["inputs"]:
            assert inp["access"] in g["access_levels"], (b, inp)
            assert inp["why"], (b, inp)
