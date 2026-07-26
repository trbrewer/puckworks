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
        note="Partial cross-fit: the equilibrium channel IS withheld, the solids-sigmoid "
             "channel is not. Do NOT describe this as a leave-one-shot-out validation of Phi(t).")


# --- P0.3: shot-level paired uncertainty -------------------------------------------------------
def paired_shot_uncertainty(window=WINDOW, seed=0):
    """Primary uncertainty on the SHOT, not on the time point (Paper B2 review P0.3).

    The published intervals resample time BLOCKS of the residual sequence of ONE derived mean
    curve with every fit held fixed, so they condition on that mean and on those fits. This
    replaces them as the primary statement: the unit is the shot, every branch's own free
    parameters are re-optimized inside each unit, and the paired per-shot differences are reported
    in full rather than summarized by an interval alone.

    With **five** experimental units a percentile bootstrap is not credible, so the primary
    statement is EXACT rather than asymptotic: over the 2**5 = 32 sign assignments of the paired
    differences we compute the exact two-sided randomization p-value, and we report the full list
    of five differences alongside it. A bootstrap over five units is reported too, explicitly
    labelled coarse, because readers will ask; it is not the primary claim.

    Strength: descriptive / exact randomization on five units. It bounds ORDERING, not accuracy,
    and it says nothing about the channels of Phi(t) that are not cross-fitted."""
    import itertools

    lad = per_shot_ladder(window)
    ids = lad["shot_ids"]
    n = len(ids)

    def _diff(a, b):
        return np.array([lad["per_shot"][k][a] - lad["per_shot"][k][b] for k in ids], float)

    signs = np.array(list(itertools.product((-1.0, 1.0), repeat=n)))     # 2**n assignments

    def _exact(d):
        """Exact two-sided randomization test on the paired differences under the sign-symmetry
        null. Returns (mean, p, n_negative). Deterministic: the full sign group is enumerated."""
        obs = float(np.abs(d.mean()))
        null = np.abs((signs * d).mean(axis=1))
        return (round(float(d.mean()), 4),
                round(float((null >= obs - 1e-15).mean()), 4),
                int((d < 0).sum()))

    rng = np.random.default_rng(seed)
    out = {}
    for label, a, b in (("phi_vs_const", "rung4_phi_of_t", "rung1_const"),
                        ("phi_vs_static", "rung4_phi_of_t", "rung3_static"),
                        ("phi_vs_cubic", "rung4_phi_of_t", "flexible_cubic"),
                        ("static_vs_const", "rung3_static", "rung1_const")):
        d = _diff(a, b)
        mean, p, n_neg = _exact(d)
        boot = np.array([rng.choice(d, size=n, replace=True).mean() for _ in range(20000)])
        out[label] = dict(
            per_shot_difference_g_per_s={k: round(float(v), 4) for k, v in zip(ids, d)},
            mean_difference_g_per_s=mean,
            shots_favouring_first="%d/%d" % (n_neg, n),
            exact_randomization_p=p,
            exact_test="two-sided sign-symmetry randomization over all 2**%d assignments" % n,
            coarse_bootstrap_95_g_per_s=[round(float(np.percentile(boot, 2.5)), 4),
                                         round(float(np.percentile(boot, 97.5)), 4)],
            bootstrap_caveat="five units: a percentile interval here is indicative only",
        )
    return dict(
        pressure_bar=PRESSURE_BAR, window_s=tuple(window), n_shots=n, shot_ids=ids,
        comparisons=out, seed=int(seed),
        shot_noise_floor_rmse_g_per_s=lad["shot_noise_floor_rmse_g_per_s"],
        supersedes="within-curve block resampling of the mean trace, which is retained only as a "
                   "secondary within-curve sensitivity",
        note="Free parameters are re-optimized per shot for the constant and the cubic. Phi(t) and "
             "the static curve carry no free parameters here, but their upstream calibration is "
             "only partially cross-fitted (see leave_one_shot_out_phi).")


# --- P0.4: a flexible temporal comparator scored out of sample -----------------------------------
_SPLINE_KNOTS = 12                 # prespecified, not tuned on any held-out shot
_SPLINE_DEGREE = 3
_LAMBDA_GRID = np.geomspace(1e-6, 1e3, 40)


def _penalized_spline_basis(t, n_knots=_SPLINE_KNOTS, degree=_SPLINE_DEGREE):
    """Cubic B-spline design matrix on `n_knots` interior knots, with a second-difference penalty
    matrix. Prespecified: the knot count and degree are fixed constants, never chosen per fold."""
    from scipy.interpolate import BSpline
    lo, hi = float(t[0]), float(t[-1])
    interior = np.linspace(lo, hi, n_knots + 2)[1:-1]
    knots = np.r_[[lo] * (degree + 1), interior, [hi] * (degree + 1)]
    B = np.asarray(BSpline.design_matrix(t, knots, degree, extrapolate=True).todense())
    D = np.diff(np.eye(B.shape[1]), 2, axis=0)          # second-difference penalty
    return B, D.T @ D


def _fit_penalized_spline(B, P, y, lam_grid=_LAMBDA_GRID):
    """Ridge-penalized least squares with the smoothing weight chosen by generalized
    cross-validation ON THE SUPPLIED DATA ONLY. Returns (coefficients, lambda)."""
    BtB = B.T @ B
    Bty = B.T @ y
    n = len(y)
    best = None
    for lam in lam_grid:
        A = BtB + lam * P
        try:
            c = np.linalg.solve(A, Bty)
        except np.linalg.LinAlgError:
            continue
        H_trace = float(np.trace(np.linalg.solve(A, BtB)))
        rss = float(((B @ c - y) ** 2).sum())
        denom = (1.0 - H_trace / n) ** 2
        gcv = (rss / n) / denom if denom > 1e-12 else np.inf
        if best is None or gcv < best[0]:
            best = (gcv, c, float(lam))
    return best[1], best[2]


def held_out_flexible_comparator(window=WINDOW, n_segments=5):
    """A flexible temporal comparator scored OUT OF SAMPLE (Paper B2 review P0.4).

    NAMING. This paper's surface retires the evidentiary phrase that was previously applied to a
    mechanistic branch whose temporal construction was in fact retained (see
    puckworks.paper_b.evidence_ontology.RETIRED_LANGUAGE). That retirement stands and is not
    loosened here. This comparator is a different object -- it is a NULL -- and what is withheld
    from it is stated per protocol below rather than asserted.

    The degree-3 polynomial null is fitted to the very trace it is scored on, so it establishes
    only that a smooth curve can interpolate the data -- it is not a predictive comparator. This
    adds a prespecified penalized cubic B-spline (%d interior knots, second-difference penalty,
    smoothing weight by GCV) under two protocols that withhold the scored points entirely:

      * LEAVE-ONE-SHOT-OUT -- fit on the other four shots, predict the excluded shot. The
        constant null is refitted the same way, so both nulls are withheld identically.
      * LEAVE-SEGMENT-OUT -- within each shot, hold out contiguous time segments in turn and
        predict them from the remaining segments of the SAME shot. This asks the different
        question of whether a smooth interpolator can fill a temporal gap.

    Neither protocol lets the comparator see the points it is scored on. If the spline still beats
    the mechanistic branch out of sample, the mechanism has not earned a temporal claim; if it does
    not, the same-trace cubic was flattering it. Strength: held-out prediction (flexible
    comparator); the mechanistic branches remain only partially cross-fitted upstream.""" % _SPLINE_KNOTS
    from puckworks import data as d
    from puckworks.models.waszkiewicz2025 import poroelastic as wz

    ids, t, Q = _shots(window)
    B, P = _penalized_spline_basis(t)
    P_c, Q_c = wz.published_calibration()
    k_s, l_s, m_s = wz._solids_params()
    dose = d.waszkiewicz_constants()["dose__g"]
    q_phi = wz.q_dynamic(t, PRESSURE_BAR, P_c, Q_c, k_s, l_s, m_s, dose)
    lvl_static = float(wz.q_static(PRESSURE_BAR, P_c, Q_c))

    # Phi(t) is also evaluated under its OWN cross-fit (equilibrium channel withheld per shot), so
    # the comparison is like-for-like: neither comparator is scored on a calibration that saw the
    # held-out shot through a channel that could be withheld.
    phi_cf = leave_one_shot_out_phi(window)["per_shot"]

    # --- protocol 1: leave one SHOT out ---------------------------------------------------------
    loso = {}
    for i, k in enumerate(ids):
        train = np.delete(Q, i, axis=0)
        y_train = train.mean(axis=0)                       # the other four shots
        c, lam = _fit_penalized_spline(B, P, y_train)
        pred = B @ c
        held = Q[i]
        loso[k] = dict(
            spline_heldout_rmse=round(float(np.sqrt(((pred - held) ** 2).mean())), 4),
            const_heldout_rmse=round(float(np.sqrt(((y_train.mean() - held) ** 2).mean())), 4),
            phi_rmse=round(float(np.sqrt(np.nanmean((q_phi - held) ** 2))), 4),
            phi_crossfit_rmse=phi_cf[k]["heldout_rmse"],
            static_rmse=round(float(np.sqrt(((lvl_static - held) ** 2).mean())), 4),
            spline_lambda=round(lam, 6))

    # --- protocol 2: leave one contiguous SEGMENT out, within each shot -------------------------
    # NOTE the first and last segments require the spline to EXTRAPOLATE beyond its support, where
    # a penalized smoother is not defined in any useful sense. Those segments are computed and
    # reported, but the headline is the INTERIOR-segment mean, where the task is interpolation --
    # which is the question "can a smooth curve fill a temporal gap?" actually asks.
    edges = np.linspace(0, len(t), n_segments + 1).astype(int)
    lso, interior = {}, [s for s in range(n_segments) if 0 < s < n_segments - 1]
    for i, k in enumerate(ids):
        y = Q[i]
        per_seg = {}
        for s in range(n_segments):
            hold = np.zeros(len(t), bool)
            hold[edges[s]:edges[s + 1]] = True
            c, _ = _fit_penalized_spline(B[~hold], P, y[~hold])
            per_seg[s] = dict(
                spline=float(np.sqrt(((B[hold] @ c - y[hold]) ** 2).mean())),
                phi=float(np.sqrt(np.nanmean((q_phi[hold] - y[hold]) ** 2))),
                const=float(np.sqrt(((y[~hold].mean() - y[hold]) ** 2).mean())),
                extrapolating=bool(s not in interior))

        def _m(key, segs):
            return round(float(np.mean([per_seg[s][key] for s in segs])), 4)

        lso[k] = dict(
            per_segment={s: {kk: round(vv, 4) if isinstance(vv, float) else vv
                             for kk, vv in per_seg[s].items()} for s in per_seg},
            interior_spline_rmse=_m("spline", interior), interior_phi_rmse=_m("phi", interior),
            interior_const_rmse=_m("const", interior),
            all_segments_spline_rmse=_m("spline", range(n_segments)))

    def _mean(dct, key):
        return round(float(np.mean([dct[k][key] for k in ids])), 4)

    floor = shot_level_noise_floor(window)["noise_floor_rmse_g_per_s"]
    spline_mean = _mean(loso, "spline_heldout_rmse")
    phi_mean = _mean(loso, "phi_rmse")
    phi_cf_mean = _mean(loso, "phi_crossfit_rmse")
    return dict(
        pressure_bar=PRESSURE_BAR, window_s=tuple(window), n_shots=len(ids), shot_ids=ids,
        comparator=dict(kind="penalized cubic B-spline", interior_knots=_SPLINE_KNOTS,
                        degree=_SPLINE_DEGREE, penalty="second difference",
                        smoothing_selection="GCV on the training data only",
                        prespecified=True),
        leave_one_shot_out=loso,
        leave_one_shot_out_mean=dict(
            spline=spline_mean, const=_mean(loso, "const_heldout_rmse"),
            phi=phi_mean, phi_equilibrium_crossfit=phi_cf_mean,
            static=_mean(loso, "static_rmse")),
        leave_segment_out=lso, n_segments=int(n_segments),
        leave_segment_out_interior_mean=dict(
            spline=_mean(lso, "interior_spline_rmse"), phi=_mean(lso, "interior_phi_rmse"),
            const=_mean(lso, "interior_const_rmse")),
        leave_segment_out_all_segments_spline=_mean(lso, "all_segments_spline_rmse"),
        leave_segment_out_caveat=("the first and last segments require the spline to extrapolate "
                                  "beyond its support, where it is unstable; the interior mean is "
                                  "the interpolation question and is the headline"),
        shot_noise_floor_rmse_g_per_s=floor,
        phi_minus_spline_heldout_g_per_s=round(phi_mean - spline_mean, 4),
        phi_crossfit_minus_spline_heldout_g_per_s=round(phi_cf_mean - spline_mean, 4),
        phi_beats_heldout_spline=bool(phi_mean < spline_mean),
        difference_exceeds_shot_noise_floor=bool(abs(phi_mean - spline_mean) > floor),
        note="The spline never sees the points it is scored on under either protocol. The "
             "leave-one-shot-out spline is trained on the mean of the other four shots, which is "
             "the same object the manuscript scores, so the protocols are comparable.")


# --- P0.7: residual diagnostics at ONE declared resolution --------------------------------------

def _acf_by_lag(centred, max_lag):
    """Sample autocorrelation at lags 1..max_lag of an already-centred series."""
    import numpy as np
    x = np.asarray(centred, dtype=float)
    denom = float((x ** 2).sum())
    if denom == 0 or max_lag < 1:
        return []
    return [round(float((x[:-k] * x[k:]).sum() / denom), 4) for k in range(1, int(max_lag) + 1)]


def _periodogram(centred, dt_s, keep=12):
    """One-sided periodogram of an already-centred residual series.

    Reported as (period_s, relative_power) for the strongest components, and normalised so the
    powers sum to 1. Absolute power in (g/s)^2 would invite comparison between branches with very
    different residual magnitudes -- the question here is WHERE each branch's structure sits, not
    how large it is; magnitude is already reported as RMSE.
    """
    import numpy as np
    x = np.asarray(centred, dtype=float)
    n = x.size
    if n < 8 or dt_s <= 0:
        return dict(period_s=[], relative_power=[], dominant_period_s=None,
                    power_in_slowest_quarter=None)
    power = np.abs(np.fft.rfft(x)) ** 2
    freq = np.fft.rfftfreq(n, d=dt_s)
    power, freq = power[1:], freq[1:]                 # drop the zero-frequency (mean) term
    total = float(power.sum())
    if total == 0:
        return dict(period_s=[], relative_power=[], dominant_period_s=None,
                    power_in_slowest_quarter=None)
    rel = power / total
    order = np.argsort(rel)[::-1][:keep]
    order = order[np.argsort(freq[order])]
    # "slowest quarter" = the lowest-frequency quarter of the spectrum; a residual dominated by it
    # is drifting rather than oscillating.
    q = max(1, len(freq) // 4)
    return dict(
        period_s=[round(float(1.0 / f), 3) for f in freq[order]],
        relative_power=[round(float(v), 4) for v in rel[order]],
        dominant_period_s=round(float(1.0 / freq[int(np.argmax(rel))]), 3),
        power_in_slowest_quarter=round(float(rel[:q].sum()), 4),
    )


def residual_diagnostics(window=WINDOW, resolution_s=1.0):
    """Serial-dependence diagnostics for EVERY branch at ONE declared resolution (review P0.7).

    The published summary mixed an autocorrelation computed at the native sample spacing with a
    Durbin-Watson statistic computed on a different series, so the two described different
    sampling scales and could not be read together. Here every branch is decimated to the SAME
    declared resolution (default 1 s), and lag-1 autocorrelation, the Durbin-Watson statistic and
    the residual scale are reported for each on that one grid.

    Both statistics are reported against the SHOT-TO-SHOT scale as well, because a residual that is
    strongly autocorrelated but smaller than the between-shot spread is a different situation from
    one that is both autocorrelated and large. Strength: descriptive diagnostic."""
    from puckworks import data as d
    from puckworks.models.waszkiewicz2025 import poroelastic as wz

    ids, t, Q = _shots(window)
    step = max(1, int(round(resolution_s / float(np.median(np.diff(t))))))
    td = t[::step]
    Qd = Q[:, ::step]
    mean_curve = Qd.mean(axis=0)
    P_c, Q_c = wz.published_calibration()
    k_s, l_s, m_s = wz._solids_params()
    dose = d.waszkiewicz_constants()["dose__g"]
    branches = {
        "rung1_const": np.full_like(td, float(mean_curve.mean())),
        "rung3_static": np.full_like(td, float(wz.q_static(PRESSURE_BAR, P_c, Q_c))),
        "rung4_phi_of_t": wz.q_dynamic(td, PRESSURE_BAR, P_c, Q_c, k_s, l_s, m_s, dose),
    }
    Xc = np.column_stack([td ** k for k in range(4)])
    cc, *_ = np.linalg.lstsq(Xc, mean_curve, rcond=None)
    branches["flexible_cubic"] = Xc @ cc

    pointwise_sd = Qd.std(axis=0, ddof=1)
    out = {}
    for name, pred in branches.items():
        r = mean_curve - pred
        r = r[np.isfinite(r)]
        rc = r - r.mean()
        acf1 = float((rc[:-1] * rc[1:]).sum() / (rc ** 2).sum())
        dw = float((np.diff(r) ** 2).sum() / (r ** 2).sum())
        rmse = float(np.sqrt((r ** 2).mean()))
        out[name] = dict(
            lag1_autocorrelation=round(acf1, 4),
            durbin_watson=round(dw, 4),
            # review P1.5: one scalar is not complete evidence -- report the error MAGNITUDE
            # (RMSE, MAE), its DIRECTION (mean bias), and its SCALE relative to shot-to-shot
            # variability, so a branch cannot look adequate on a single summary.
            rmse_g_per_s=round(rmse, 4),
            mae_g_per_s=round(float(np.abs(r).mean()), 4),
            mean_bias_g_per_s=round(float(r.mean()), 4),
            residual_over_between_shot_sd=round(rmse / float(pointwise_sd.mean()), 3),
            standardized_residual_sd=round(float(r.std(ddof=1)
                                                 / pointwise_sd.mean()), 3),
            residual_vs_time_g_per_s=[round(float(x), 4) for x in r],
            # review 4.7: lag-1 alone cannot distinguish "slowly drifting" from "oscillating".
            # The ACF across lags and the periodogram show WHERE the structure sits, which is
            # what makes the residuals a first-class result rather than a single number.
            acf_by_lag=_acf_by_lag(rc, max_lag=min(20, len(rc) // 4)),
            spectrum=_periodogram(rc, float(resolution_s)),
        )
    return dict(
        pressure_bar=PRESSURE_BAR, window_s=tuple(window), n_shots=len(ids),
        declared_resolution_s=float(resolution_s), decimation_step=int(step),
        n_points_at_resolution=int(len(td)), time_s=[round(float(x), 3) for x in td],
        branches=out,
        between_shot_sd_mean_g_per_s=round(float(pointwise_sd.mean()), 4),
        note="ACF and Durbin-Watson are computed on the SAME decimated series for every branch. "
             "Durbin-Watson near 2 indicates no lag-1 structure AT THIS RESOLUTION; the value "
             "changes with resolution, which is why the resolution is declared rather than "
             "implied.")


def recorded_pressure_robustness(window=(15.0, 95.0), pressure_bar=9.0):
    """Re-score the static and Phi(t) branches against the RECORDED basket-pressure history
    instead of the nominal setpoint (Paper 2 review 4.9 / §5.2).

    The manuscript printed six full-precision values for this check that were transcribed from a
    reviewer's independent table rather than computed here — the claim-coverage audit (review
    4.13) flagged them as having no producer. This is that producer.

    The substitution is point-by-point: at each retained sample the branch is evaluated at the
    measured basket pressure at that instant rather than at the nominal 9 bar. Everything else —
    window, calibration, dissolution parameters, dose — is held fixed, so the only difference
    between the two columns is the pressure argument.

    Returns nominal and recorded RMSE for both branches, their differences, and whether the branch
    ordering is unchanged. It is a ROBUSTNESS result: it says the reported rise is not an artifact
    of the small measured pressure drift. It is not evidence for any mechanism.
    """
    import numpy as np

    from puckworks import data as d
    from puckworks.models.waszkiewicz2025 import poroelastic as wz

    lo, hi = window
    tr = d.waszkiewicz_traces()
    rec = tr[pressure_bar]
    t = np.asarray(rec["time__s"], dtype=float)
    q = np.asarray(rec["mass_flow_rate__g_per_s"], dtype=float)
    p_recorded = np.asarray(rec["basket_pressure__bar"], dtype=float)
    sel = (t >= lo) & (t <= hi)
    td, qd, pd = t[sel], q[sel], p_recorded[sel]

    P_c, Q_c = wz.published_calibration()
    k_s, l_s, m_s = wz._solids_params()
    dose = d.waszkiewicz_constants()["dose__g"]

    def _rmse(pred):
        return float(np.sqrt(np.nanmean((np.asarray(pred, dtype=float) - qd) ** 2)))

    static_nominal = _rmse(wz.q_static(pressure_bar, P_c, Q_c))
    static_recorded = _rmse([wz.q_static(float(p), P_c, Q_c) for p in pd])
    phi_nominal = _rmse(wz.q_dynamic(td, pressure_bar, P_c, Q_c, k_s, l_s, m_s, dose))
    phi_recorded = _rmse(np.array(
        [wz.q_dynamic(np.array([ti]), float(pi), P_c, Q_c, k_s, l_s, m_s, dose)[0]
         for ti, pi in zip(td, pd)]))

    d_static = static_recorded - static_nominal
    d_phi = phi_recorded - phi_nominal
    return dict(
        pressure_bar=pressure_bar, window_s=(lo, hi), n_points=int(sel.sum()),
        recorded_pressure_mean_bar=round(float(np.mean(pd)), 4),
        recorded_pressure_range_bar=[round(float(np.min(pd)), 4), round(float(np.max(pd)), 4)],
        static_nominal_rmse_g_per_s=round(static_nominal, 6),
        static_recorded_rmse_g_per_s=round(static_recorded, 6),
        static_delta_g_per_s=round(d_static, 6),
        phi_nominal_rmse_g_per_s=round(phi_nominal, 6),
        phi_recorded_rmse_g_per_s=round(phi_recorded, 6),
        phi_delta_g_per_s=round(d_phi, 6),
        max_abs_delta_g_per_s=round(max(abs(d_static), abs(d_phi)), 6),
        both_shifts_below_0p001=bool(max(abs(d_static), abs(d_phi)) < 0.001),
        ordering_unchanged=bool((phi_recorded < static_recorded) == (phi_nominal < static_nominal)),
        note=("Point-by-point substitution of the recorded basket pressure for the nominal "
              "setpoint; window, calibration, dissolution parameters and dose held fixed. A "
              "robustness result, not evidence for any mechanism."),
    )
