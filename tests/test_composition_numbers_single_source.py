"""Composition numbers must come from ONE producer (Paper 3 review P0-5).

The same three-value comparison appeared in the manuscript, the Figure-5 caption, the public PV-05
claim and the generated evidence matrix -- and they disagreed:

    manuscript / PV-05      constant 0.573   extraction-only 0.116   composite 0.648
    generated evidence matrix   flat null 0.603   extraction-only 0.113   composite 0.650

Both artifacts were "generated", so both looked authoritative. The architectural cause is that the
evidence graph stores hand-curated claim PROSE, while PV-05 is bound to a packaged snapshot -- so
"generated" never meant "computed" for the evidence text.

Resolved by measurement, not by preference: the flat null on its own stated definition (LS-optimal
constant over 15-95 s) computes to 0.5729, so 0.573 is right and 0.603 was simply a stale literal
that had never been producer-bound. These tests enumerate every place the three values are repeated
and pin each to its producer under a declared rounding policy.
"""
import json
import pathlib
import re

import numpy as np
import pytest

_ROOT = pathlib.Path(__file__).resolve().parents[1]
ROUNDING_DP = 3          # declared policy: all four artifacts quote 3 decimal places


@pytest.fixture(scope="module")
def canonical():
    """The single source of truth: recomputed from the registered producers."""
    from puckworks import data as d
    from puckworks.models.brewer2026 import coupled_kappa_t as ck
    tr = d.waszkiewicz_traces()
    t, q = tr[9.0]["time__s"], tr[9.0]["mass_flow_rate__g_per_s"]
    sel = (t >= 15.0) & (t <= 95.0)
    flat = float(np.mean(q[sel]))
    return {
        "flat_null": round(float(np.sqrt(np.mean((flat - q[sel]) ** 2))), ROUNDING_DP),
        "extraction_only": round(float(ck.degeneracy_rmse(window=(15.0, 95.0))), ROUNDING_DP),
        "composite": round(float(ck.composition_residual(window=(15.0, 95.0))["rmse"]),
                           ROUNDING_DP),
    }


def test_the_canonical_values_are_what_the_manuscript_reports(canonical):
    """Pins the resolution: 0.573 / 0.116 / 0.648, computed -- not 0.603 / 0.113 / 0.650."""
    assert canonical == {"flat_null": 0.573, "extraction_only": 0.116, "composite": 0.648}


def test_the_two_extraction_only_producers_agree(canonical):
    """The coupled model's extraction-only branch must reduce to the ladder's Phi(t) rung. If these
    ever diverge, 0.113-vs-0.116 style drift is back and the 'exact reduction' claim is void."""
    from puckworks import harness as h
    assert h.kappa_t_ladder()["rung4_phi_of_t"] == pytest.approx(
        canonical["extraction_only"], abs=0.002)


def _artifacts():
    return {
        "manuscript": (_ROOT / "docs/PAPER_3_PUCKWORKS_DRAFT.md").read_text(encoding="utf-8"),
        "evidence_links": (_ROOT / "puckworks/paper3/EVIDENCE_LINKS.json").read_text(encoding="utf-8"),
        "gates": (_ROOT / "puckworks/validation/gates.py").read_text(encoding="utf-8"),
        "pv05": (_ROOT / "puckworks/public/data/pv05_model_composition.json").read_text(encoding="utf-8"),
    }


@pytest.mark.parametrize("name", ["manuscript", "evidence_links", "gates", "pv05"])
def test_no_artifact_still_quotes_a_retired_composition_value(name):
    """THE regression guard. Enumerates the repeated claim across artifacts and forbids the stale
    literals anywhere -- this is what let 0.603 survive in 'generated' output."""
    text = _artifacts()[name]
    for dead in ("0.603", "0.650 g", "0.113 g"):
        assert dead not in text, f"{name}: retired composition value {dead!r} is still present"


def test_the_flat_null_definition_is_stated_wherever_it_is_quoted():
    """Review P0-5 item 5: the baseline definition must travel with the number, or 0.573 and 0.603
    look like the same quantity measured twice rather than one right and one wrong."""
    links = _artifacts()["evidence_links"]
    assert "LS-optimal constant on the same 15-95 s window" in links


def test_pv05_matches_the_producers(canonical):
    pv = json.loads(_artifacts()["pv05"])
    blob = json.dumps(pv)
    m = re.search(r'"const_baseline_rmse_g_per_s":\s*([0-9.]+)', blob)
    assert m, "PV-05 no longer exposes the constant baseline"
    assert float(m.group(1)) == pytest.approx(canonical["flat_null"], abs=0.002)


# --- HOW the composition fails, not just that it does -----------------------------------------
def test_the_composite_collapses_to_the_static_limit_rather_than_merely_scoring_worse():
    """The composite RMSE (0.6477) and the static kappa(P) RMSE (0.6477) are the SAME number, and
    the manuscripts previously reported them as two independent facts. They coincide because the
    imported swelling branch drives the shared porosity below its initial value everywhere in the
    scored window, so the dissolved-mass proxy sits on its floor, Phi -> 0, and the flow closure
    returns its own Phi->0 limit -- the static curve. The composite prediction is therefore
    CONSTANT: the composition does not degrade the temporal reconstruction, it removes it.

    If a future change makes the composite genuinely time-varying, this test fails and the
    manuscripts' explanation must be revisited rather than silently left in place."""
    import numpy as np

    from puckworks import data as d
    from puckworks.models.brewer2026 import coupled_kappa_t as ck
    from puckworks.models.waszkiewicz2025 import poroelastic as wz

    W, P = (15.0, 95.0), 9.0
    r = ck.composition_residual(P_bar=P, window=W)
    assert r["swelling_closes"] is True
    assert r["phi_floor_fraction_in_window"] == 1.0, r["phi_floor_fraction_in_window"]
    assert r["reduces_to_static_limit"] is True
    assert r["predicted_flow_spread_g_per_s"] < 1e-9

    # and the coincidence is exact, not a rounding artefact
    tr = d.waszkiewicz_traces()
    t = np.asarray(tr[P]["time__s"], float)
    q = np.asarray(tr[P]["mass_flow_rate__g_per_s"], float)
    sel = (t >= W[0]) & (t <= W[1])
    P_c, Q_c = wz.published_calibration()
    static_rmse = float(np.sqrt(np.nanmean((float(wz.q_static(P, P_c, Q_c)) - q[sel]) ** 2)))
    assert abs(r["rmse"] - static_rmse) < 1e-9, (r["rmse"], static_rmse)


def test_both_manuscripts_explain_the_coincidence_rather_than_reporting_two_numbers():
    """Prose guard: the two 0.648 values must not be presented as independent evidence."""
    for rel in ("docs/PAPER_3_PUCKWORKS_DRAFT.md", "docs/PAPER_B2_TEMPORAL_DRAFT.md"):
        text = (_ROOT / rel).read_text(encoding="utf-8")
        low = text.lower()
        assert "static" in low and "0.648" in low, rel
        assert ("by construction, not by coincidence" in low
                or "structural rather than accidental" in low), rel
