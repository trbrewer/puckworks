"""Cross-pressure heterogeneity, model domains, and parameter-provenance graph for Paper B2.

Covers second-review items P1.1 (show heterogeneity rather than only macro means), P1.2 (declare
the pressure domains and boundary nodes every analysis uses), and P1.3 (expand parameter provenance
into a dependency graph rather than a flat "target-informed" label).

The common thread is that a macro mean over eleven pressures hides three different things: which
branch wins where, how many shots each pressure contributes, and which pressure a given number even
refers to. Each is reported here rather than summarised away.
"""
from __future__ import annotations

import numpy as np

WINDOW = (15.0, 95.0)
BRANCHES = ("static", "phi", "rc3b")


# --------------------------------------------------------------------------------------------
# P1.1 -- per-pressure heterogeneity
# --------------------------------------------------------------------------------------------
def _shots_per_pressure(window_name="endpoint_100s"):
    from puckworks import data as d
    from collections import Counter
    rows = d.waszkiewicz_equilibrium_windows()
    return dict(Counter(round(float(r["reference_pressure_round__bar"]), 2)
                        for r in rows if r["window"] == window_name))


def cross_pressure_heterogeneity(window=WINDOW):
    """Per-pressure scores, the rank of each branch at each pressure, and how the headline changes
    under two defensible averaging schemes (review P1.1).

    The manuscript's aggregate statement is an EQUAL-PRESSURE mean: every reference pressure counts
    once. That is a choice, not a neutral summary -- the campaign contributes between 3 and 10 shots
    per pressure, so a shot-weighted mean answers a different question (what happens to a randomly
    drawn shot) and can reorder the branches. Both are reported, with the disagreement stated.

    Strength: descriptive. No branch is refitted here; this re-reads the existing cross-pressure
    producer at a finer grain."""
    from puckworks import harness as h

    res = h.cross_pressure_discrimination(window=window)
    per = res["per_pressure"]
    n_shots = _shots_per_pressure()
    pressures = sorted(per, key=float)

    rows, winners = {}, []
    for p in pressures:
        scores = {b: float(per[p][b]) for b in BRANCHES if b in per[p]}
        order = sorted(scores, key=scores.get)
        rows[p] = dict(
            rmse={b: round(v, 4) for b, v in scores.items()},
            rank={b: order.index(b) + 1 for b in scores},
            best=order[0],
            margin_over_second=round(scores[order[1]] - scores[order[0]], 4) if len(order) > 1
            else None,
            n_shots=int(n_shots.get(round(float(p), 2), 0)))
        winners.append(order[0])

    def _mean(branch, weighted):
        vals, wts = [], []
        for p in pressures:
            if branch not in rows[p]["rmse"]:
                continue
            vals.append(rows[p]["rmse"][branch])
            wts.append(rows[p]["n_shots"] if weighted else 1)
        if not vals:
            return None
        return float(np.average(vals, weights=wts))

    equal = {b: _mean(b, False) for b in BRANCHES}
    shotw = {b: _mean(b, True) for b in BRANCHES}
    equal_order = sorted((b for b in equal if equal[b] is not None), key=lambda b: equal[b])
    shotw_order = sorted((b for b in shotw if shotw[b] is not None), key=lambda b: shotw[b])

    from collections import Counter
    win_counts = dict(Counter(winners))
    return dict(
        window_s=tuple(window), n_pressures=len(pressures),
        pressures=[float(p) for p in pressures],
        per_pressure=rows,
        n_shots_per_pressure={float(k): int(v) for k, v in sorted(n_shots.items())},
        n_shots_range=[int(min(n_shots.values())), int(max(n_shots.values()))],
        branch_wins=win_counts,
        n_rank_changes=len(set(winners)) - 1,
        best_branch_is_constant_across_pressure=bool(len(set(winners)) == 1),
        equal_pressure_mean={b: (round(v, 4) if v is not None else None)
                             for b, v in equal.items()},
        shot_weighted_mean={b: (round(v, 4) if v is not None else None)
                            for b, v in shotw.items()},
        equal_pressure_order=equal_order,
        shot_weighted_order=shotw_order,
        averaging_scheme_changes_order=bool(equal_order != shotw_order),
        note=("The equal-pressure mean is the manuscript's headline scheme and weights a 3-shot "
              "pressure the same as a 10-shot one. Neither scheme is 'correct'; they answer "
              "different questions and are reported together."))


# --------------------------------------------------------------------------------------------
# P1.2 -- model domains and boundary nodes
# --------------------------------------------------------------------------------------------
def pressure_domains():
    """Which pressure does each number refer to? (review P1.2).

    Four distinct pressure quantities appear in this paper and are easily conflated: the campaign's
    NOMINAL reference pressure, the RECORDED basket pressure that the rig actually delivered, the
    FITTED equilibrium characteristic pressure P_c, and the range over which the poroelastic closure
    is valid. This producer emits all four from the data and the calibration, plus the measured gap
    between nominal and recorded."""
    from puckworks import data as d
    from puckworks.models.waszkiewicz2025 import poroelastic as wz

    rows = [r for r in d.waszkiewicz_equilibrium_windows() if r["window"] == "endpoint_100s"]
    by = {}
    for r in rows:
        p = round(float(r["reference_pressure_round__bar"]), 2)
        by.setdefault(p, []).append(float(r["basket_pressure__bar"]))
    nominal = sorted(by)
    recorded = {p: float(np.mean(v)) for p, v in by.items()}
    deficit = {p: recorded[p] - p for p in nominal}
    P_c, Q_c = wz.published_calibration()
    return dict(
        nominal_reference_pressures_bar=[float(p) for p in nominal],
        recorded_basket_pressure_mean_bar={float(p): round(recorded[p], 3) for p in nominal},
        nominal_minus_recorded_bar={float(p): round(-deficit[p], 3) for p in nominal},
        max_nominal_recorded_gap_bar=round(float(max(abs(v) for v in deficit.values())), 3),
        fitted_equilibrium_P_c_bar=round(float(P_c), 3),
        fitted_equilibrium_Q_c_g_per_s=round(float(Q_c), 3),
        model_valid_pressure_range_bar=[float(min(nominal)), float(max(nominal))],
        primary_analysis_pressure_bar=9.0,
        primary_analysis_recorded_bar=round(recorded[9.0], 3),
        n_pressures_at_or_above_P_c=int(sum(1 for p in nominal if p >= float(P_c))),
        boundary_note=("P_c = %.2f bar sits just inside the tested range [%.1f, %.1f]: only %d of "
                       "the %d reference pressures reach or exceed it, so the saturating branch of "
                       "the equilibrium curve is exercised by essentially one pressure and the "
                       "rest of the campaign probes the sub-characteristic regime."
                       % (float(P_c), float(min(nominal)), float(max(nominal)),
                          sum(1 for p in nominal if p >= float(P_c)), len(nominal))),
        conflation_hazard=("The recorded basket pressure is systematically BELOW nominal at every "
                           "setting (up to %.2f bar). A statement about '9 bar' therefore means "
                           "the nominal setting, not the delivered pressure of %.2f bar."
                           % (max(abs(v) for v in deficit.values()), recorded[9.0])))


# --------------------------------------------------------------------------------------------
# P1.3 -- parameter-provenance dependency graph
# --------------------------------------------------------------------------------------------
#: Per branch, every input and how it reaches the branch. `access` records the branch's relationship
#: to the SCORED trace, which is the question a reader actually needs answered.
PROVENANCE = {
    "rung1_const": {
        "free_params_fitted_to_scored_trace": 1,
        "inputs": [("in-window mean flow", "direct_target", "the scored trace itself")],
        "literature_inputs": [],
        "held_out": "nothing",
    },
    "rung1b_longrun_const": {
        "free_params_fitted_to_scored_trace": 0,
        "inputs": [("long-run flow level", "same_shot", "the tail of the same shot")],
        "literature_inputs": [],
        "held_out": "the scored window, but not the shot",
    },
    "rung3_static": {
        "free_params_fitted_to_scored_trace": 0,
        "inputs": [("equilibrium (P_c, Q_c)", "same_campaign",
                    "fitted across 11 pressures; the 9-bar point contains the scored shots"),
                   ("universal curve form", "literature", "Waszkiewicz Eq. 16")],
        "literature_inputs": ["poroelastic equilibrium closure"],
        "held_out": "no coefficient fitted to the scored trace; the calibration still sees it",
    },
    "rung4_phi_of_t": {
        "free_params_fitted_to_scored_trace": 0,
        "inputs": [("equilibrium (P_c, Q_c)", "same_campaign",
                    "as above -- cross-fittable, and cross-fitted in the LOSO analysis"),
                   ("dissolved-mass sigmoid (k, l, m)", "indirect_target",
                    "fitted from TDS(t) x Q(t) on this rig; Q(t) is the scored observable"),
                   ("dose, bed constants", "same_campaign", "campaign constants"),
                   ("Phi(t) = m_d(t)/m0 closure", "literature", "Waszkiewicz Eq. 18")],
        "literature_inputs": ["poroelastic time-dependent closure"],
        "held_out": "no fitted coefficient, but the sigmoid channel reuses the target",
    },
    "flexible_cubic": {
        "free_params_fitted_to_scored_trace": 4,
        "inputs": [("polynomial coefficients", "direct_target", "least squares on the scored trace")],
        "literature_inputs": [],
        "held_out": "nothing",
    },
    "penalized_spline_loso": {
        "free_params_fitted_to_scored_trace": 0,
        "inputs": [("spline coefficients", "other_shots", "fitted on the four other brews"),
                   ("knot count, penalty order", "prespecified", "declared before running")],
        "literature_inputs": [],
        "held_out": "the entire scored shot",
    },
}

ACCESS_LEVELS = {
    "direct_target": "fitted to the very trace being scored",
    "indirect_target": "derived from the scored observable through another measurement",
    "same_shot": "taken from the same shot, outside the scored window",
    "same_campaign": "estimated from the same campaign, including the scored shots",
    "other_shots": "estimated from other shots only",
    "literature": "taken from the source publication",
    "prespecified": "declared in advance, not estimated",
}


def provenance_graph():
    """Flatten PROVENANCE into a reportable dependency graph (review P1.3).

    Reports, per branch, the worst (most target-proximal) access level any of its inputs carries --
    because a branch is only as held-out as its most target-informed dependency, and a flat
    'no coefficient fitted to the scored trace' label hides exactly that."""
    order = ["direct_target", "indirect_target", "same_shot", "same_campaign",
             "other_shots", "literature", "prespecified"]
    out = {}
    for branch, spec in PROVENANCE.items():
        accesses = [a for _n, a, _w in spec["inputs"]]
        worst = min(accesses, key=order.index) if accesses else "prespecified"
        out[branch] = dict(
            free_params_fitted_to_scored_trace=spec["free_params_fitted_to_scored_trace"],
            n_inputs=len(spec["inputs"]),
            inputs=[dict(name=n, access=a, why=w) for n, a, w in spec["inputs"]],
            access_levels_present=sorted(set(accesses), key=order.index),
            most_target_proximal_access=worst,
            is_held_out=bool(worst in ("other_shots", "literature", "prespecified")),
            held_out=spec["held_out"],
            literature_inputs=spec["literature_inputs"])
    return dict(access_levels=ACCESS_LEVELS, branches=out,
                note=("A branch is only as held out as its most target-proximal input. Zero free "
                      "parameters fitted to the scored trace is necessary but not sufficient for "
                      "'held out', which is why the count and the access level are reported "
                      "separately rather than collapsed into one label."))
