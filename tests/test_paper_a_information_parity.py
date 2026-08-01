"""Information parity and the M0/M1/M2 ablation (pivot plan §7).

Two things here are easy to get wrong in a way no reader could detect, so both are tested directly:

1. the **oracle bound must never be mistaken for a held-out score** — it is chosen using the
   coarse/fine data it is scored on;
2. the **hydraulic covariate must be the target grind's**, because handing the empirical arm a
   residence time computed at the calibration grind would quietly restore the information gap the
   panel exists to close.
"""
from __future__ import annotations

import json
import pathlib
import sys

import numpy as np
import pytest

REPO = pathlib.Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from puckworks.paper_a import empirical_benchmarks as EB  # noqa: E402

ARCHIVE = REPO / "docs" / "paper1_resource" / "PAPER_A_INFORMATION_PARITY.json"


@pytest.fixture(scope="module")
def archive():
    if not ARCHIVE.exists():
        pytest.skip("run tools/paper_a_information_parity.py --write")
    return json.loads(ARCHIVE.read_text(encoding="utf-8"))


# ── 1. the referee-pinned panel must not have moved ──────────────────────────────────────────
def test_adding_hydraulic_families_did_not_disturb_the_published_panel():
    """`FAMILIES` is frozen: 8.691 % and all six selections are pinned to exactly that list."""
    p = EB.panel()
    assert p["empirical"]["macro_cf_mape"] == pytest.approx(8.691, abs=5e-4)
    assert EB.FAMILIES == ("constant", "temperature", "pressure", "temperature+pressure",
                           "temperature*pressure")


def test_the_hydraulic_family_set_extends_rather_than_replaces():
    assert set(EB.FAMILIES[:-1]).issubset(set(EB.HYDRAULIC_FAMILIES))
    assert any("residence" in f for f in EB.HYDRAULIC_FAMILIES)
    # the interaction family is deliberately dropped, not forgotten
    assert "temperature*pressure" not in EB.HYDRAULIC_FAMILIES


# ── 2. the hydraulic covariate is exogenous and grind-specific ───────────────────────────────
def test_residence_time_is_computed_at_each_row_s_own_granulometry():
    """A residence time computed at the calibration grind would restore the information gap."""
    rows = EB._rows()
    for grind in ("O", "C", "F"):
        sub = [r for r in rows if r.granulometry == grind and r.variety == "Arabica"]
        tau = EB.residence_times(sub)
        assert np.all(tau > 0)
        # the three grinds must not collapse onto one another
        assert len(sub) > 0
    o = EB.residence_times([r for r in rows if r.granulometry == "O" and r.variety == "Arabica"])
    f = EB.residence_times([r for r in rows if r.granulometry == "F" and r.variety == "Arabica"])
    assert f.mean() > o.mean(), "the fine grind must be slower, or the map is not grind-specific"


def test_residence_time_never_depends_on_a_measured_concentration():
    """Perturbing every concentration must leave the covariate identical."""
    rows = EB._rows()
    before = EB.residence_times(rows)

    class Perturbed:
        def __init__(self, row):
            self._row = row
            self.raw = {k: (str(float(v) * 3.0) if k in ("CF", "TR", "5CQA") else v)
                        for k, v in row.raw.items()}

        def __getattr__(self, name):
            return getattr(self._row, name)

    assert np.allclose(before, EB.residence_times([Perturbed(r) for r in rows]))


def test_a_hydraulic_family_refuses_to_build_without_the_covariate():
    """Silently returning a temperature-only matrix would be an invisible information leak."""
    T = np.array([88.0, 93.4, 98.0])
    p = np.array([6.0, 9.0, 12.0])
    with pytest.raises(ValueError):
        EB._design("temperature+log_residence", T, p, None)


# ── 3. the oracle bound must stay quarantined from the held-out score ────────────────────────
def test_the_oracle_bound_is_labelled_as_not_a_held_out_score(archive):
    oracle = archive["information_parity"]["oracle_upper_bound"]
    assert "NOT A HELD-OUT SCORE" in oracle["status"]
    assert "selection on the test set" in oracle["status"]


def test_the_frozen_score_and_the_oracle_bound_are_reported_separately(archive):
    """They differ by more than a percentage point; conflating them would invert the conclusion."""
    ip = archive["information_parity"]
    frozen = ip["frozen_selection"]["macro_cf_mape"]
    oracle = ip["oracle_upper_bound"]["best_macro_cf_mape"]
    assert frozen != oracle
    assert frozen > oracle, (
        "the oracle is chosen on held-out performance, so it cannot be worse than the frozen "
        "selection; if it ever is, the selection paths have diverged")


def test_the_frozen_selection_saw_no_held_out_record(archive):
    """Stated in the archive AND reachable from the code path, not just asserted in prose."""
    assert "calibration conditions only" in archive["information_parity"]["frozen_selection"]["selection"]


def test_perturbing_held_out_concentrations_cannot_change_the_frozen_predictor():
    """The leakage test, re-run for the hydraulic family set."""
    from puckworks.paper_a import source_schema as SS

    rows = SS.parse_rows()
    rng = np.random.default_rng(1)

    class Perturbed:
        def __init__(self, row):
            self._row = row
            if row.granulometry in EB.HELD_OUT_GRINDS:
                raw = dict(row.raw)
                for _s, column in EB.SOLUTE_COLUMNS:
                    raw[column] = str(float(raw[column]) * float(rng.uniform(2.0, 5.0)))
                self.raw = raw
            else:
                self.raw = row.raw

        def __getattr__(self, name):
            return getattr(self._row, name)

    perturbed = [Perturbed(r) for r in rows]
    for variety in EB.VARIETIES:
        for solute, column in EB.SOLUTE_COLUMNS:
            clean = EB.select_and_score(rows, variety, solute, column,
                                        families=EB.HYDRAULIC_FAMILIES)
            dirty = EB.select_and_score(perturbed, variety, solute, column,
                                        families=EB.HYDRAULIC_FAMILIES)
            assert dirty.family == clean.family, (variety, solute, "family leaked")
            assert dirty.train_mape == pytest.approx(clean.train_mape), (variety, solute, "fit leaked")


# ── 4. the extrapolation finding, which explains the frozen result ───────────────────────────
def test_the_target_grinds_are_extrapolative_in_the_hydraulic_covariate(archive):
    """The reason information parity does NOT narrow the margin under frozen selection."""
    report = archive["hydraulic_extrapolation"]["Arabica"]["held_out"]
    assert report["F"]["fraction_outside_calibration_range"] > 0.5
    assert report["F"]["largest_gap_in_calibration_spans"] > 1.0, (
        "if the fine grind ever falls inside the calibration hydraulic range, the extrapolation "
        "explanation for the frozen result no longer applies and must be re-derived")


# ── 5. the ablation ──────────────────────────────────────────────────────────────────────────
def test_the_ablation_arms_are_internally_consistent(archive):
    arms = archive["ablation"]["arms"]
    for arm in ("M0", "M1", "M2"):
        v = arms[arm]
        assert v["pooled"] == pytest.approx((v["coarse"] + v["fine"]) / 2.0, abs=0.002)


def test_m2_reproduces_the_published_mechanistic_arm(archive):
    """M2 is the canonical arm; if it does not recover 8.44/10.17/6.71 the panel is not comparable."""
    m2 = archive["ablation"]["arms"]["M2"]
    assert m2["pooled"] == pytest.approx(8.44, abs=0.01)
    assert m2["coarse"] == pytest.approx(10.17, abs=0.01)
    assert m2["fine"] == pytest.approx(6.71, abs=0.01)


def test_m0_recovers_the_rate_free_score_seen_independently(archive):
    """8.281 % is what the refit tool produced when its rate multiplier was accidentally omitted.

    That bug made the mechanistic arm rate-free — which is exactly what M0 is by construction. Two
    independent routes to the same number is a real check on this arm, and it is why the earlier
    bug's value is worth remembering rather than just fixing.
    """
    assert archive["ablation"]["arms"]["M0"]["pooled"] == pytest.approx(8.281, abs=0.01)


def test_the_contrasts_are_the_stated_differences(archive):
    a = archive["ablation"]
    arms, c = a["arms"], a["contrasts_pp"]
    assert c["M1_to_M2"] == pytest.approx(arms["M1"]["pooled"] - arms["M2"]["pooled"], abs=0.002)
    assert c["M0_to_M2"] == pytest.approx(arms["M0"]["pooled"] - arms["M2"]["pooled"], abs=0.002)
    assert c["M0_to_M1"] == pytest.approx(arms["M0"]["pooled"] - arms["M1"]["pooled"], abs=0.002)


def test_no_equivalence_or_significance_language_in_the_archive(archive):
    """The plan forbids manufacturing a categorical conclusion from this comparison."""
    blob = json.dumps(archive).lower()
    for banned in ("statistically significant", "non-inferior", "equivalent to", "p-value"):
        assert banned not in blob, banned
