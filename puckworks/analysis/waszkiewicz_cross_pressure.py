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
    per pressure, so weighting by shot count can reorder the branches. Both are reported.

    IMPORTANT (third review P0.4). The shot-count-weighted value here is a weighted mean of
    PRESSURE-LEVEL MEAN-CURVE RMSEs. It is NOT the expected RMSE of a randomly drawn shot, because
    RMSE is nonlinear:

        RMSE(mean curve) != mean[ RMSE(individual shots) ]

    This docstring previously said it answered "what happens to a randomly drawn shot", which is
    wrong. For the genuine shot-level estimand see `per_shot_cross_pressure()`.

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
        # Adjacent transitions along the pressure axis, NOT the number of distinct winners.
        # `len(set(winners)) - 1` gave 2 for the actual sequence
        #   RC-3b, RC-3b, static x4, Phi x4, RC-3b
        # which has THREE transitions; it undercounts whenever a winner reappears later, and it is
        # not a transition count at all (fourth review 5.4). A verification manifest had confirmed
        # the wrong value against the bundle because both carried the same definition.
        n_rank_changes=sum(a != b for a, b in zip(winners, winners[1:])),
        best_branch_is_constant_across_pressure=bool(len(set(winners)) == 1),
        equal_pressure_mean={b: (round(v, 4) if v is not None else None)
                             for b, v in equal.items()},
        shot_weighted_mean={b: (round(v, 4) if v is not None else None)
                            for b, v in shotw.items()},
        equal_pressure_order=equal_order,
        shot_weighted_order=shotw_order,
        averaging_scheme_changes_order=bool(equal_order != shotw_order),
        note=("Both schemes average PRESSURE-LEVEL MEAN-CURVE RMSEs. The equal-pressure mean is "
              "the manuscript's headline scheme and weights a 3-shot pressure the same as a "
              "10-shot one; the shot-count-weighted variant weights by shot count but is still an "
              "average of mean-curve scores, NOT the expected error of a randomly drawn shot "
              "(RMSE is nonlinear). The shot-level estimand is per_shot_cross_pressure()."))


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
        # Fifth review P0.2. This was recorded as 0 parameters fitted to the scored trace, with
        # `same_shot` access ("outside the scored window") and "the scored window, but not the
        # shot" held out. All three are FALSE. `harness.py` defines the late interval as
        # `hi - 10` to `hi`, and the scored window is 15-95 s, so the level is fitted on 85-95 s --
        # the final eighth OF the scored interval. It is an in-sample subset fit with one free
        # parameter and direct access to the trace it is scored on, and nothing is held out.
        "free_params_fitted_to_scored_trace": 1,
        "inputs": [("long-run flow level", "direct_target",
                    "the mean over 85-95 s, which lies INSIDE the scored 15-95 s window")],
        "literature_inputs": [],
        "held_out": "nothing; 85-95 s is a subset of the scored interval",
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


# --------------------------------------------------------------------------------------------
# P0.4 (third review) -- the genuine shot-level cross-pressure estimand
# --------------------------------------------------------------------------------------------
def per_shot_cross_pressure(window=WINDOW):
    """Score every INDIVIDUAL included shot, at every pressure, against every branch.

    Third review P0.4. The manuscript reported equal-pressure and shot-count-weighted averages of
    pressure-level MEAN-CURVE RMSEs and read the second as "the expected error for a randomly
    selected shot". That is mathematically wrong: RMSE is nonlinear, so

        RMSE(mean curve)  !=  mean[ RMSE(individual shots) ]

    and a weighted average of mean-curve scores is not the expectation over shots. The mean curve
    has variance averaged out of it, so scores against it are systematically optimistic relative to
    scores against real shots.

    Four estimands are returned, each named exactly, so the manuscript can no longer describe one
    as another:

    ``equal_pressure_macro_mean_of_mean_curve``
        Every pressure counts once; the score at each pressure is against that pressure's mean
        curve. The manuscript's headline scheme.
    ``shot_weighted_macro_mean_of_mean_curve``
        The same mean-curve scores, weighted by shot count. Reported because it appeared in the
        manuscript, labelled as what it is.
    ``mean_of_individual_shot_rmse``
        The expected RMSE of a randomly drawn shot -- the quantity the manuscript meant.
    ``pooled_shot_time_rmse``
        Root mean square over all shot x time observations pooled.

    The three branches are all zero-free-parameter at the shot level: `static` is flat in time,
    and `phi`/`rc3b` depend on time and pressure only, so each shot at a given pressure is scored
    against the same prediction its pressure-level mean curve was scored against. Nothing is
    refitted here.

    The source campaign is described as 60 brews; the committed processed deposit contains 57
    trace RECORDS after source-side exclusions, of which 56 are distinct trajectories -- see
    `exclusion_note`. Because the shot is the experimental unit here, the declared alias is
    EXCLUDED: counting it twice would give the 13-bar condition seven units where it has six, and
    would understate shot-level spread. All three counts are returned.

    Strength: descriptive. Within-campaign; not independent validation.
    """
    import numpy as np
    from puckworks import data as d
    from puckworks.models.waszkiewicz2025 import poroelastic as wz
    from puckworks.models.cameron2020 import extraction_bdf as cam

    lo, hi = window
    P_c, Q_c = wz.published_calibration()
    k_s, l_s, m_s = wz._solids_params()
    dose = d.waszkiewicz_constants()["dose__g"]

    # Distinct physical brews only: this function's unit is the shot (fourth review P0.1).
    by_pressure = d.waszkiewicz_traces_per_brew(include_aliases=False)
    pressures = sorted(by_pressure)

    per_shot, per_pressure = {}, {}
    pooled_sq = {b: [] for b in BRANCHES}

    for p in pressures:
        shots = by_pressure[p]
        # One prediction per branch per pressure, evaluated on each shot's own time grid.
        sh = cam.simulate_shot(1.9, p_bar=p, m_in=dose / 1000, m_out=0.040,
                               t_shot=100.0, n_save=150)
        rows = {}
        for sid in sorted(shots):
            t = np.asarray(shots[sid]["time__s"], float)
            q = np.asarray(shots[sid]["mass_flow_rate__g_per_s"], float)
            sel = (t >= lo) & (t <= hi)
            ts, qs = t[sel], q[sel]
            if ts.size == 0:
                continue
            scores = {}
            scores["static"] = float(np.sqrt(np.nanmean((wz.q_static(p, P_c, Q_c) - qs) ** 2)))
            q_phi = wz.q_dynamic(ts, p, P_c, Q_c, k_s, l_s, m_s, dose)
            scores["phi"] = float(np.sqrt(np.nanmean((q_phi - qs) ** 2)))
            md = np.interp(ts, sh.t, sh.m_cup * 1000.0)
            if md[-1] <= 0:
                scores["rc3b"] = float("nan")
            else:
                q_rc = wz.q_dynamic_from_md(p, P_c, Q_c, md, dose)
                scores["rc3b"] = float(np.sqrt(np.nanmean((q_rc - qs) ** 2)))
            rows[sid] = {b: round(v, 4) for b, v in scores.items()}
            for b in BRANCHES:
                v = scores.get(b)
                if v is not None and np.isfinite(v):
                    pooled_sq[b].append(v ** 2 * ts.size)
            per_shot[f"{p}:{sid}"] = dict(pressure_bar=float(p), shot_id=sid,
                                          n_points=int(ts.size), rmse=rows[sid])
        per_pressure[float(p)] = dict(
            n_shots=len(rows),
            mean_of_individual_shot_rmse={
                b: round(float(np.nanmean([rows[s][b] for s in rows])), 4) for b in BRANCHES},
            individual_shot_rmse=rows)

    n_points_total = sum(v["n_points"] for v in per_shot.values())

    def _shot_mean(branch):
        vals = [v["rmse"][branch] for v in per_shot.values()
                if np.isfinite(v["rmse"].get(branch, np.nan))]
        return round(float(np.mean(vals)), 4) if vals else None

    def _pooled(branch):
        if not pooled_sq[branch]:
            return None
        return round(float(np.sqrt(sum(pooled_sq[branch]) / n_points_total)), 4)

    het = cross_pressure_heterogeneity(window)
    shot_level = {b: _shot_mean(b) for b in BRANCHES}
    pooled = {b: _pooled(b) for b in BRANCHES}
    order_mean_curve = het["shot_weighted_order"]
    order_shot = sorted((b for b in shot_level if shot_level[b] is not None),
                        key=lambda b: shot_level[b])

    return dict(
        window_s=tuple(window),
        n_pressures=len(pressures),
        n_shots_included=len(per_shot),
        n_trace_records_in_deposit=57,
        n_distinct_trajectories=56,
        # The common grid every trace is interpolated onto. Exposed so the manuscript's statement
        # that the duplicate pair agrees "at all 1000 time rows" is a producer-backed claim rather
        # than an unchecked numeral.
        n_time_rows_per_trace=int(d.WASZ_PER_BREW_NGRID),
        n_brews_reported_by_source=60,
        aliases_excluded=dict(d.WASZ_TRACE_ALIASES),
        exclusion_note=("The source campaign is described as 60 brews. The committed processed "
                        "deposit contains 57 trace RECORDS after source-side exclusions; the "
                        "three excluded brews are not identified in the released deposit, so the "
                        "exclusion provenance is recorded as incomplete rather than "
                        "reconstructed. Of those 57 records only 56 are distinct: in the source "
                        "archive `12-8-6.txt` is an exact line-for-line prefix of "
                        "`12-8-6_alt.txt`, whose 42 extra samples lie past the 100 s truncation "
                        "and record the scale being cleared (mass runs to -175 g), so the pair is "
                        "one physical brew stored twice. It is counted ONCE here, because the "
                        "shot is the experimental unit. Note separately that the source's own "
                        "published per-pressure means average both copies, so the deposited "
                        "13-bar mean curve is a mean over seven records covering six brews."),
        per_shot=per_shot,
        per_pressure=per_pressure,
        # --- the four estimands, each named ---
        equal_pressure_macro_mean_of_mean_curve=het["equal_pressure_mean"],
        shot_weighted_macro_mean_of_mean_curve=het["shot_weighted_mean"],
        mean_of_individual_shot_rmse=shot_level,
        pooled_shot_time_rmse=pooled,
        order_by_mean_curve_shot_weighted=order_mean_curve,
        order_by_individual_shot_mean=order_shot,
        ordering_agrees_across_estimands=bool(order_mean_curve == order_shot),
        note=("Four DIFFERENT estimands. Only `mean_of_individual_shot_rmse` is the expected error "
              "of a randomly drawn shot. The two macro means average pressure-level MEAN-CURVE "
              "scores and are systematically lower, because averaging shots removes variance the "
              "branches were never required to predict. All three branches are evaluated, so the "
              "ordering statement is not finalised on two of them."))
