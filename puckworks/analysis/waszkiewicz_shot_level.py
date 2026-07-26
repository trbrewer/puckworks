"""Shot-level analysis of the Waszkiewicz 9-bar condition (Paper B2 review item 4.1).

WHY THIS EXISTS. `harness.kappa_t_ladder()` scores every rung against the PUBLISHED per-pressure
mean trace, so its unit of analysis is the TIME POINT, not the shot. The published spread column is
a standard ERROR (the source aggregates with `sem`), so shot-to-shot variability cannot be recovered
from it at all. With the raw per-brew traces now intaken (`data.waszkiewicz_traces_per_brew`), the
SHOT can be the unit: five independent brews at 9 bar.

WHAT THIS DOES AND DOES NOT DO. It re-scores the zero-free-parameter rungs and the constant nulls
against each individual shot, and it measures how far a single shot sits from the mean curve the
paper scores. It does NOT re-fit Phi(t) per shot: Phi(t) is built from TDS(t) x Q(t), and the TDS
replicates are not shot-matched to these flow traces, so a genuine leave-one-shot-out CROSS-FIT
(review items 4.3/4.4) remains blocked on data that was never published. Treating the results here
as a cross-fit would be exactly the overclaim the review is trying to remove.
"""
from __future__ import annotations

import numpy as np

WINDOW = (15.0, 95.0)          # the manuscript's scored saturated-extraction window
PRESSURE_BAR = 9.0


def _shots(window):
    from puckworks import data as d
    shots = d.waszkiewicz_traces_per_brew(PRESSURE_BAR)
    ids = sorted(shots)
    t = shots[ids[0]]["time__s"]
    sel = (t >= window[0]) & (t <= window[1])
    Q = np.vstack([shots[k]["mass_flow_rate__g_per_s"][sel] for k in ids])
    return ids, t[sel], Q


def shot_level_noise_floor(window=WINDOW):
    """The REFERENCE SCALE the published RMSEs should be read against.

    Measures how far an individual 9-bar shot sits from the across-shot mean curve that the
    manuscript scores. This is a descriptive noise floor, NOT a model: it is the residual any model
    would incur predicting a single real shot even if it reproduced the mean trajectory perfectly.

    The comparison it licenses is ORDERING-vs-SEPARATION, not accuracy: an RMSE gap much larger than
    this floor is a real discrimination; a gap comfortably inside it is not resolvable with five
    shots, however reproducible the point estimate looks. Strength: descriptive/diagnostic."""
    ids, t, Q = _shots(window)
    mean_curve = Q.mean(axis=0)
    per_shot_rmse = np.sqrt(((Q - mean_curve) ** 2).mean(axis=1))
    per_shot_mean_q = Q.mean(axis=1)
    pointwise_sd = Q.std(axis=0, ddof=1)
    return dict(
        pressure_bar=PRESSURE_BAR, window_s=tuple(window), n_shots=len(ids),
        n_points=int(Q.shape[1]), shot_ids=ids,
        per_shot_mean_flow_g_per_s={k: round(float(v), 4)
                                    for k, v in zip(ids, per_shot_mean_q)},
        between_shot_sd_of_mean_flow_g_per_s=round(float(per_shot_mean_q.std(ddof=1)), 4),
        per_shot_rmse_vs_mean_curve_g_per_s={k: round(float(v), 4)
                                             for k, v in zip(ids, per_shot_rmse)},
        # THE number: the typical single-shot deviation from the scored mean trajectory
        noise_floor_rmse_g_per_s=round(float(per_shot_rmse.mean()), 4),
        noise_floor_rmse_range_g_per_s=[round(float(per_shot_rmse.min()), 4),
                                        round(float(per_shot_rmse.max()), 4)],
        pointwise_between_shot_sd_mean_g_per_s=round(float(pointwise_sd.mean()), 4),
        pointwise_between_shot_sd_max_g_per_s=round(float(pointwise_sd.max()), 4),
        note="Descriptive shot-to-shot scatter, not a fitted model and not an error bar on any "
             "rung. It is the scale on which RMSE DIFFERENCES between rungs should be judged.")


def per_shot_ladder(window=WINDOW):
    """Review item 4.1: re-score the ladder with the SHOT as the unit of analysis.

    Each rung is evaluated against each of the five individual 9-bar brews:

      rung1  best-in-window constant   1 param, re-optimized PER SHOT (its best case)
      rung3  published static kappa(P) 0 free params, identical prediction for every shot
      rung4  poroelastic Phi(t)        0 free params, identical prediction for every shot
      cubic  degree-3 polynomial       4 params, re-fit PER SHOT (non-mechanistic flexible null)

    Reports per-shot RMSE, the across-shot mean/SD per rung, and how many of the five shots each
    rung wins against the constant null. `shots_rung4_beats_const` is the honest headline: an
    ordering that holds on every individual shot is far stronger than one that holds only on the
    averaged curve. Strength: descriptive (no rung is re-fitted except its own free parameters;
    Phi(t) is NOT cross-fitted -- see the module docstring)."""
    from puckworks import data as d
    from puckworks.models.waszkiewicz2025 import poroelastic as wz

    ids, t, Q = _shots(window)
    P_c, Q_c = wz.published_calibration()
    k_s, l_s, m_s = wz._solids_params()
    dose = d.waszkiewicz_constants()["dose__g"]
    lvl_static = float(wz.q_static(PRESSURE_BAR, P_c, Q_c))
    q_phi = wz.q_dynamic(t, PRESSURE_BAR, P_c, Q_c, k_s, l_s, m_s, dose)
    Xc = np.column_stack([t ** k for k in range(4)])

    rows = {}
    for k, q in zip(ids, Q):
        const = float(q.mean())                       # LS-optimal constant for THIS shot
        cc, *_ = np.linalg.lstsq(Xc, q, rcond=None)   # cubic re-fit to THIS shot
        rows[k] = dict(
            rung1_const=round(float(np.sqrt(((const - q) ** 2).mean())), 4),
            rung1_const_level_g_per_s=round(const, 4),
            rung3_static=round(float(np.sqrt(((lvl_static - q) ** 2).mean())), 4),
            rung4_phi_of_t=round(float(np.sqrt(np.nanmean((q_phi - q) ** 2))), 4),
            flexible_cubic=round(float(np.sqrt(((Xc @ cc - q) ** 2).mean())), 4),
        )

    def _col(name):
        return np.array([rows[k][name] for k in ids], float)

    summary = {}
    for rung in ("rung1_const", "rung3_static", "rung4_phi_of_t", "flexible_cubic"):
        v = _col(rung)
        summary[rung] = dict(mean=round(float(v.mean()), 4), sd=round(float(v.std(ddof=1)), 4),
                             min=round(float(v.min()), 4), max=round(float(v.max()), 4))
    beats_const = int((_col("rung4_phi_of_t") < _col("rung1_const")).sum())
    phi_vs_cubic = _col("rung4_phi_of_t") - _col("flexible_cubic")
    floor = shot_level_noise_floor(window)["noise_floor_rmse_g_per_s"]

    return dict(
        pressure_bar=PRESSURE_BAR, window_s=tuple(window), n_shots=len(ids), shot_ids=ids,
        per_shot=rows, across_shots=summary,
        shots_rung4_beats_const=beats_const,
        shots_rung4_beats_const_fraction="%d/%d" % (beats_const, len(ids)),
        phi_minus_cubic_mean_g_per_s=round(float(phi_vs_cubic.mean()), 4),
        phi_minus_cubic_sd_g_per_s=round(float(phi_vs_cubic.std(ddof=1)), 4),
        shot_noise_floor_rmse_g_per_s=floor,
        # the two comparisons the review asks to be separated
        ordering_survives_per_shot=bool(beats_const == len(ids)),
        phi_vs_cubic_resolvable=bool(abs(float(phi_vs_cubic.mean())) > floor),
        note="rung1 and the cubic get their free parameters re-optimized per shot (their best "
             "case); rung3 and rung4 are zero-free-parameter predictions evaluated as-is. Phi(t) "
             "is NOT re-fitted per shot -- a true leave-one-shot-out cross-fit needs shot-matched "
             "TDS, which was never published (review 4.3/4.4 stays blocked).")
