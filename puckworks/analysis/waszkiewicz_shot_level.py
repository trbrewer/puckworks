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


# --- equilibrium-window provenance (Paper B2 review 4.7 / P0.5) -------------------------------
EQUILIBRIUM_WINDOWS = ("endpoint_100s", "mean_90_100s", "mean_110_120s")


def equilibrium_window_sensitivity(exclude_contaminated=True):
    """Which long-run statistic defines the equilibrium (P_c, Q_c) -- and does it matter?

    THE PROVENANCE MISMATCH (review 4.7): the manuscript attributed a **110-120 s** equilibrium
    statistic to the source, while the repository takes the FINAL point of a 0-100 s grid -- the
    source's own formatter truncates at 100 s, so the published aggregate cannot contain 110-120 s.

    The raw per-brew traces are NOT truncated (all 57 reach >=110 s; median 121 s), so the
    source-faithful window is nominally recoverable. It is nevertheless **not usable as published**:
    shot `9-1` has plainly ended inside it -- falling cup mass gives a large negative flow derivative
    and, through the brewer-calibration subtraction, a nonsensical -106 bar -- which alone drags the
    refit to P_c ~ 82 bar. Dropping it would be an exclusion the authors did not make (their own
    `excluded/` set does not contain `9-1`), so the honest resolution is to report the repository's
    own observable and say so, with this table as the evidence.

    Returns the per-window static refit. Strength: descriptive provenance audit."""
    import numpy as np
    from puckworks import data as d
    from puckworks.models.waszkiewicz2025 import poroelastic as wz

    rows = d.waszkiewicz_equilibrium_windows()
    contaminated = sorted({r["shot_id"] for r in rows
                           if float(r["mass_flow_rate__g_per_s"]) < 0.0
                           or float(r["basket_pressure__bar"]) < 0.0})
    out = {}
    for w in EQUILIBRIUM_WINDOWS:
        for drop in ((), tuple(contaminated)):
            sel = [r for r in rows if r["window"] == w and r["shot_id"] not in drop
                   and int(r["n_samples"]) > 0]
            if not sel:
                continue
            by_p = {}
            for r in sel:
                by_p.setdefault(round(float(r["reference_pressure_round__bar"]), 3),
                                []).append(r)
            P = np.array([np.mean([float(x["basket_pressure__bar"]) for x in v])
                          for _, v in sorted(by_p.items())])
            Q = np.array([np.mean([float(x["mass_flow_rate__g_per_s"]) for x in v])
                          for _, v in sorted(by_p.items())])
            (Pc, Qc), _ = wz.fit_static(P, Q)
            key = w if not drop else f"{w}_excl_contaminated"
            out[key] = dict(P_c_bar=round(float(Pc), 3), Q_c_g_per_s=round(float(Qc), 3),
                            n_pressures=len(P), n_shots=len(sel))
            if not contaminated:
                break
    pub_P, pub_Q = wz.published_calibration()
    used = out["endpoint_100s"]
    return dict(
        windows=out, contaminated_shots=contaminated,
        repository_observable="endpoint_100s",
        published_P_c_bar=round(float(pub_P), 3), published_Q_c_g_per_s=round(float(pub_Q), 3),
        # the repository proxy reproduces the published static fit
        endpoint_matches_published=bool(abs(used["P_c_bar"] - pub_P) < 0.05
                                        and abs(used["Q_c_g_per_s"] - pub_Q) < 0.05),
        # and the choice does not matter WITHIN the clean region
        clean_region_insensitive=bool(
            abs(out["endpoint_100s"]["P_c_bar"] - out["mean_90_100s"]["P_c_bar"]) < 0.05),
        nominal_110_120s_usable=False,
        note="The manuscript must NOT attribute a 110-120 s statistic to this analysis. The "
             "repository's equilibrium observable is the final 100 s value of each preprocessed "
             "pressure mean; it reproduces the published static fit. The nominal 110-120 s window "
             "is unusable from the published raw traces without an exclusion the source did not "
             "make (shot 9-1 has ended inside it).")


def leave_one_shot_out_phi(window=WINDOW):
    """PARTIAL leave-one-shot-out cross-fit of Phi(t) (Paper B2 review 4.2 / P0.2).

    CORRECTION to an earlier assessment in this repository, which recorded 4.2/4.3 as fully
    blocked. Phi(t) reuses the target through TWO channels, and they are not equally blocked:

      (a) the EQUILIBRIUM calibration (P_c, Q_c) is fitted across pressures, and the 9-bar point is
          the mean over the five 9-bar shots -- so it contains the held-out shot. This channel IS
          cross-fittable, and is what this function removes: for each held-out shot the 9-bar
          equilibrium point is rebuilt from the OTHER FOUR, (P_c, Q_c) is refitted, Phi(t) is
          recomputed, and ONLY the held-out shot is scored.
      (b) the DISSOLVED-MASS sigmoid (k, l, m) is fitted from TDS(t) x Q(t). The deposit's TDS is
          three replicates that are NOT shot-matched to the flow traces, so it cannot be rebuilt
          per held-out shot. This channel remains and is reported, not hidden.

    So this is a cross-fit of the equilibrium channel, NOT a full leave-one-shot-out of Phi(t). It
    is strictly better than scoring a fully in-sample Phi(t) and strictly weaker than the review's
    ideal. Strength: partial held-out (equilibrium channel only)."""
    from puckworks import data as d
    from puckworks.models.waszkiewicz2025 import poroelastic as wz

    ids, t, Q = _shots(window)
    rows = d.waszkiewicz_equilibrium_windows()
    eq = [r for r in rows if r["window"] == "endpoint_100s" and int(r["n_samples"]) > 0]
    k_s, l_s, m_s = wz._solids_params()
    dose = d.waszkiewicz_constants()["dose__g"]

    def _fit_without(drop_id):
        by_p = {}
        for r in eq:
            if r["shot_id"] == drop_id:
                continue
            by_p.setdefault(round(float(r["reference_pressure_round__bar"]), 3), []).append(r)
        P, Qe = [], []
        for p, v in sorted(by_p.items()):
            P.append(np.mean([float(x["basket_pressure__bar"]) for x in v]))
            Qe.append(np.mean([float(x["mass_flow_rate__g_per_s"]) for x in v]))
        (Pc, Qc), _ = wz.fit_static(np.array(P), np.array(Qe))
        return float(Pc), float(Qc)

    per, insample = {}, {}
    Pc_in, Qc_in = _fit_without(None)                     # nothing held out
    q_phi_in = wz.q_dynamic(t, PRESSURE_BAR, Pc_in, Qc_in, k_s, l_s, m_s, dose)
    for k, q in zip(ids, Q):
        Pc, Qc = _fit_without(k)                          # THIS shot excluded from the calibration
        q_phi = wz.q_dynamic(t, PRESSURE_BAR, Pc, Qc, k_s, l_s, m_s, dose)
        per[k] = dict(P_c_bar=round(Pc, 4), Q_c_g_per_s=round(Qc, 4),
                      heldout_rmse=round(float(np.sqrt(np.nanmean((q_phi - q) ** 2))), 4))
        insample[k] = round(float(np.sqrt(np.nanmean((q_phi_in - q) ** 2))), 4)

    held = np.array([per[k]["heldout_rmse"] for k in ids])
    ins = np.array([insample[k] for k in ids])
    floor = shot_level_noise_floor(window)["noise_floor_rmse_g_per_s"]
    return dict(
        pressure_bar=PRESSURE_BAR, window_s=tuple(window), n_shots=len(ids),
        per_shot=per, in_sample_rmse=insample,
        heldout_mean_rmse_g_per_s=round(float(held.mean()), 4),
        in_sample_mean_rmse_g_per_s=round(float(ins.mean()), 4),
        optimism_pp_g_per_s=round(float(held.mean() - ins.mean()), 4),
        shot_noise_floor_rmse_g_per_s=floor,
        cross_fitted_channels=["equilibrium_calibration_P_c_Q_c"],
        remaining_target_reuse=["dissolved_mass_sigmoid_k_l_m (TDS replicates are not shot-matched "
                                "to the flow traces, so it cannot be rebuilt per held-out shot)"],
        is_full_cross_fit=False,
        note="Partial cross-fit: the equilibrium channel is genuinely held out, the solids-sigmoid "
             "channel is not. Do NOT describe this as a leave-one-shot-out validation of Phi(t).")
