"""maille2024 discriminating computations (card `docs/cards/maille2024.md`).

Offline, PDE-free verifications on the digitized thesis tables (Tim drop 2026-07-25). All strengths
are **verification / post-fit reconstruction** of the source's own internal consistency (single
Colombian origin, batch well-mixed reactor, coarse grind; the two-regime lambda are per-material curve
fits). The time-resolved extraction figures (Figs 4.6-4.10) are a separate digitization to follow.

1. e1_shell_depth_resolution()  -- the card's E1 gate: resolve the printed Eq-6.9 shell depth. The
   one-cell-layer (2 d_c) form is far from Table 6.3; the two-cell-layer (4 d_c) form reproduces it,
   so the registry adopts the two-layer convention (which ~doubles phi).
2. phi_closure_consistency()    -- Eq 6.7 (phi = fines + coarse) internal check + theta_v_fines
   (Table 6.3) vs the < 186 um volume fraction (Table 5.4).
3. kinetics_flags()             -- surface the E5 internally-impossible 95% CIs (unusable rows).
4. two_regime_reproduction()    -- the tabulated two-regime model (Eq 6.2) reproduces the digitized
   Omega_A extraction curves (Figs 4.6-4.10) to ~the model's own MPE.
5. phi_split_vs_cameron()       -- the card's headline gate (now UNBLOCKED by Cameron's digitized
   Fig-2 PSD): maille's phi closure on Cameron's binned PSD vs Cameron's fitted fines fraction --
   sign-agreeing but NOT commensurable (a definitional observable-semantics gap).
6. cross_model_timescale_cameron() -- the cameron HALF of gate 4: fit Eq 6.2 to cameron's
   model-generated (flowing-bed) extraction curve and check maille's lambda bands. No fitted
   lambda_fast enters maille's fast band; the 3 finer settings are single-exponential-like while the
   coarsest returns two separated constants (left to model selection). Non-portable. QUALITATIVE
   (cameron has no well-mixed config; run past its recipe to plateau).
7. cross_model_timescale_roman()   -- the Roman-Corrochano HALF of gate 4: the GENUINE well-mixed
   (stirred-vessel) config. Fit Eq 6.2 to roman's model-generated single-species diffusion curve; the
   fitted dimensionless SHAPE (weight phi ~0.32, ratio ~12.3) is grind-invariant while the ABSOLUTE
   constants vary ~1.9x with diffusivity -- the early/late-time signature of one physical diffusion
   PROCESS, NOT maille's material-varying two-POOL split; the SELECTED 20um fine-class timescales sit
   below maille's bands (coarse class not evaluated). Non-portable (semantic). QUALITATIVE. (Research
   computation; the #100 rights deferral gates only the public Laboratory product lens.)
8. roman_protocol_sensitivity()    -- U8 rigor: the roman shape is grind-invariant, but the exact
   weight/ratio pair drifts with the fit window and bath dilution -> protocol-specific, not intrinsic.
9. timescale_semantics_bundle()    -- U10: producer-bound, machine-readable claim records for the two
   timescale probes (NOT an EVIDENCE_LINKS claim; that needs the maille registration decision).
   The cameron/roman producers also now carry a U9 `portability_vector` (portability as a vector, not
   a Boolean) and cameron a U6 multistart `phi_multistart_span`/`non_identifiable` identifiability flag.
"""
from __future__ import annotations

import math

from puckworks import data as d

_D_C_M = 45e-6            # coffee cell diameter (card Parameters; SEM range 20-60 um)
# tau (extraction delay) is NOT tabulated; the card gives visual-inspection values (0 for the acids)
_TAU_S = {"Caffeine": 4.0, "3-CQA": 3.0, "Citric acid": 0.0, "Malic acid": 0.0, "Quinic acid": 0.0}


def _shell_fraction(diameter_m, n_layers):
    """Coarse-particle outer-shell volume fraction (Eq 6.9 kernel) at a representative diameter,
    removing `n_layers` cell layers (depth = 2*n_layers*d_c off the diameter -- d_c per side per layer)."""
    depth = 2.0 * n_layers * _D_C_M
    inner = diameter_m - depth
    if inner <= 0:
        return 1.0
    return 1.0 - inner ** 3 / diameter_m ** 3


def e1_shell_depth_resolution():
    """Resolve the printed Eq-6.9 shell depth (card E1). Recompute theta_v_coarse from the hybrid
    D[4,3] (Table 5.4, single-diameter approximation -- the per-bin PSD is unpublished, so this is
    the same approximation the thesis used) at ONE- vs TWO-cell-layer depth and compare to Table 6.3.
    Verdict: two layers reproduce Table 6.3 (mean |err| ~0.02) while one layer is far off (~0.2), so
    the registry adopts the two-layer convention. Strength: verification."""
    phi = {r["Sample ID"]: r for r in d.maille_phi()}
    psd = {r["Sample ID"]: r for r in d.maille_psd_hybrid()}
    per, err = {}, {1: [], 2: []}
    for sid, r in phi.items():
        if sid not in psd:
            continue
        d43 = float(psd[sid]["D[4,3] Vol Mean (um)"]) * 1e-6
        coarse_frac = 1.0 - float(psd[sid]["Volume Fraction <186um"])
        tv_coarse = float(r["theta_v_coarse"])
        vals = {}
        for n in (1, 2):
            computed = coarse_frac * _shell_fraction(d43, n)
            err[n].append(abs(computed - tv_coarse))
            vals[n] = round(computed, 3)
        per[sid] = dict(table6_3_theta_v_coarse=tv_coarse,
                        one_layer=vals[1], two_layer=vals[2])
    mean1 = sum(err[1]) / len(err[1])
    mean2 = sum(err[2]) / len(err[2])
    return dict(
        n_materials=len(per), d_c_m=_D_C_M,
        mean_abs_err_one_layer=round(mean1, 3), mean_abs_err_two_layer=round(mean2, 3),
        adopted="two_layer" if (mean2 < 0.05 and mean2 < 0.4 * mean1) else "UNRESOLVED",
        passed=bool(mean2 < 0.05 and mean2 < 0.4 * mean1),
        per_material=per,
        note="the printed Eq-6.9 removes ONE cell layer (2 d_c); Table 6.3 requires TWO (4 d_c). "
             "D[4,3] single-diameter approximation (per-bin PSD unpublished) -- reproduces the "
             "thesis's own E1 evidence; two-layer ~doubles phi vs the printed one-layer form.")


def phi_closure_consistency(tol_phi=0.002):
    """Internal consistency of the phi closure: (a) Eq 6.7 phi = theta_v_fines + theta_v_coarse at
    every material; (b) theta_v_fines (Table 6.3) equals the < 186 um volume fraction (Table 5.4),
    a transcription cross-check across two independently digitized tables. Strength: verification."""
    phi = {r["Sample ID"]: r for r in d.maille_phi()}
    psd = {r["Sample ID"]: r for r in d.maille_psd_hybrid()}
    eq67_bad = [sid for sid, r in phi.items()
                if abs(float(r["phi"]) - (float(r["theta_v_fines"]) + float(r["theta_v_coarse"]))) > tol_phi]
    fines_diffs = [abs(float(phi[s]["theta_v_fines"]) - float(psd[s]["Volume Fraction <186um"]))
                   for s in phi if s in psd]
    mean_fines_diff = sum(fines_diffs) / len(fines_diffs)
    return dict(
        n_materials=len(phi),
        eq67_violations=eq67_bad,
        theta_v_fines_vs_psd_mean_abs_diff=round(mean_fines_diff, 4),
        theta_v_fines_vs_psd_max_abs_diff=round(max(fines_diffs), 3),
        passed=bool(not eq67_bad and mean_fines_diff < 0.01),
        note="phi = fines + coarse (Eq 6.7) exact; theta_v_fines (Table 6.3) tracks the Table-5.4 "
             "sub-186um volume fraction, cross-checking two independently transcribed tables.")


def kinetics_flags():
    """Surface the card's E5 internally-impossible 95% CIs (a lower bound above, or an upper bound
    below, the point estimate) across the caffeine/3-CQA (Table 6.4) and organic-acid (Table 6.5)
    kinetics -- these rows' CIs are unusable and must be flagged, not fitted. Strength: verification."""
    flagged = []
    specs = [(d.maille_kinetics_caffeine_3cqa(), ("Caffeine", "3-CQA")),
             (d.maille_kinetics_organic_acids(), ("Citric", "Malic", "Quinic"))]
    n_rows = 0
    for rows, compounds in specs:
        for r in rows:
            n_rows += 1
            for c in compounds:
                for regime in ("lambda_fast", "lambda_slow"):
                    est = r.get("%s %s (s)" % (c, regime))
                    lo = r.get("%s %s lower 95CI" % (c, regime))
                    hi = r.get("%s %s upper 95CI" % (c, regime))
                    try:                                  # '*' marks unreported cells -> skip
                        est, lo, hi = float(est), float(lo), float(hi)
                    except (TypeError, ValueError):
                        continue
                    if lo > est or hi < est:
                        flagged.append(dict(sample=r["Sample ID"], compound=c, regime=regime,
                                            est=est, lower=lo, upper=hi))
    return dict(
        n_rows_scanned=n_rows, n_impossible_ci=len(flagged), flagged=flagged,
        passed=True,   # a report gate: it always "passes"; the value is the flagged list
        note="E5: rows where a 95%% CI does not bracket its own estimate are internally impossible "
             "(e.g. caffeine table 3-CQA and organic-acid quinic) -- carry as UNUSABLE, do not fit.")


def _two_regime(t, phi, lam_fast, lam_slow, tau):
    """Eq 6.2: C(t)/C_inf = phi(1-e^-(t-tau)/lam_fast) + (1-phi)(1-e^-(t-tau)/lam_slow); 0 for t<=tau."""
    if t <= tau:
        return 0.0
    x = t - tau
    return phi * (1.0 - math.exp(-x / lam_fast)) + (1.0 - phi) * (1.0 - math.exp(-x / lam_slow))


def two_regime_reproduction():
    """Source-curve reproduction (Figs 4.6-4.10, material Omega_A): the TABULATED two-regime model --
    phi (Table 6.3), lambda_fast/lambda_slow (Tables 6.4/6.5), tau per the card's visual values --
    reproduces the digitized early-time extraction curves to ~the model's own reported MPE (4-10%).
    Strength: source_curve_reproduction (not an independent re-fit)."""
    phi_a = float({r["Sample ID"]: r for r in d.maille_phi()}["Omega_A"]["phi"])
    c = {r["Sample ID"]: r for r in d.maille_kinetics_caffeine_3cqa()}["Omega_A"]
    a = {r["Sample ID"]: r for r in d.maille_kinetics_organic_acids()}["Omega_A"]
    lam = {
        "Caffeine": (float(c["Caffeine lambda_fast (s)"]), float(c["Caffeine lambda_slow (s)"])),
        "3-CQA": (float(c["3-CQA lambda_fast (s)"]), float(c["3-CQA lambda_slow (s)"])),
        "Citric acid": (float(a["Citric lambda_fast (s)"]), float(a["Citric lambda_slow (s)"])),
        "Malic acid": (float(a["Malic lambda_fast (s)"]), float(a["Malic lambda_slow (s)"])),
        "Quinic acid": (float(a["Quinic lambda_fast (s)"]), float(a["Quinic lambda_slow (s)"])),
    }
    curves = {}
    for r in d.maille_extraction_curves():
        curves.setdefault(r["analyte"], []).append((r["time_s"], r["C_over_Cinf"]))
    per = {}
    for an, pts in curves.items():
        lf, ls = lam[an]
        tau = _TAU_S[an]
        errs = [abs(_two_regime(t, phi_a, lf, ls, tau) - y) / y * 100.0 for t, y in pts if y > 0]
        per[an] = dict(n=len(errs), mape_pct=round(sum(errs) / len(errs), 1),
                       lambda_fast=lf, lambda_slow=ls, tau_s=tau)
    worst = max(v["mape_pct"] for v in per.values())
    return dict(phi_omega_a=phi_a, per_analyte=per, worst_mape_pct=worst,
                passed=bool(worst < 15.0),
                note="tabulated phi/lambda + the card's visual tau reproduce the digitized Omega_A "
                     "curves to MAPE ~4-10% (~the model's own reported MPE); source-curve "
                     "reproduction, not an independent re-fit.")


def _phi_from_psd(diam_um, vol, fines_cut_um=186.0, n_layers=2):
    """maille phi = theta_v_fines + theta_v_coarse (Eqs 6.7-6.9, E1-resolved n_layers) from a binned
    PSD (diameters [um] + per-bin volume). Returns (phi, theta_fines, theta_coarse)."""
    tot = sum(vol)
    depth_um = 2.0 * n_layers * _D_C_M * 1e6      # d_c per side per layer, in um
    fines = coarse = 0.0
    for dia, v in zip(diam_um, vol):
        frac = v / tot
        if dia < fines_cut_um:
            fines += frac
        else:
            inner = max(dia - depth_um, 0.0)
            coarse += frac * (1.0 - inner ** 3 / dia ** 3)
    return fines + coarse, fines, coarse


def phi_split_vs_cameron():
    """The card's headline gate: apply maille's PSD->fast-fraction phi closure (E1-resolved two cell
    layers) to Cameron 2020's MEASURED binned PSD (Figure 2, 4 grind settings) and compare to Cameron's
    own fitted fines-population fraction PHI_S1/(PHI_S1+PHI_S2) of solid.

    FINDING: both fast-fractions DECREASE as grind coarsens (sign agreement), but maille's phi runs
    ~5-9x Cameron's fines fraction -- a DEFINITIONAL gap: maille 'fast' = fines <186 um + coarse-
    particle outer shells; Cameron 'fast' = the 12 um fines class only. On Cameron's espresso-fine PSD
    maille's phi is ~0.85-0.94 (vs maille's own 0.36-0.65 on coarser drip grinds -- an extrapolation).
    The two 'fast fractions' are NOT commensurable; equating them would be a ~5-9x observable-semantics
    error. Neither model is validated by the other. Strength: verification / discrimination."""
    from puckworks.models.cameron2020.extraction_bdf import GS_GRID, PHI_S1_GRID, PHI_S2_GRID
    rows = d.cameron2020_psd()
    diam = [float(r["particle_diameter_um"]) for r in rows]
    per = []
    for gs, ps1, ps2 in zip(GS_GRID, PHI_S1_GRID, PHI_S2_GRID):
        vol = [float(r["volume_percent_Gs_%.1f" % gs]) for r in rows]
        phi, fines, _coarse = _phi_from_psd(diam, vol)
        cam_fines = float(ps1) / (float(ps1) + float(ps2))
        per.append(dict(gs=float(gs), maille_phi=round(phi, 3),
                        maille_fines_lt186=round(fines, 3),
                        cameron_fines_of_solid=round(cam_fines, 3),
                        ratio_phi_over_cameron=round(float(phi / cam_fines), 1)))
    maille_mono = all(per[i]["maille_phi"] > per[i + 1]["maille_phi"] for i in range(len(per) - 1))
    cam_mono = all(per[i]["cameron_fines_of_solid"] > per[i + 1]["cameron_fines_of_solid"]
                   for i in range(len(per) - 1))
    ratios = [p["ratio_phi_over_cameron"] for p in per]
    return dict(
        per_grind=per, both_decrease_with_coarser_grind=bool(maille_mono and cam_mono),
        ratio_range=[min(ratios), max(ratios)],
        maille_phi_on_cameron_range=[per[-1]["maille_phi"], per[0]["maille_phi"]],
        maille_own_phi_range=[0.356, 0.648], commensurable=False,
        passed=bool(maille_mono and cam_mono and all(r > 1 for r in ratios)),
        finding="maille phi on Cameron's espresso PSD ~0.85-0.94 (vs maille's own 0.36-0.65 -- "
                "extrapolation); BOTH maille phi and Cameron's fitted fines fraction DECREASE as grind "
                "coarsens (sign agreement). Magnitudes differ ~5-9x, but this is DEFINITIONAL (maille "
                "fast = fines<186um + coarse shells; Cameron fast = 12um fines class). NOT commensurable "
                "-- a registry-surfaced observable-semantics disagreement, not a validation of either.")


# maille's observed two-regime timescale bands across all materials/species (card gate 4, from
# Tables 6.4/6.5): lambda_fast in 2.2-19.1 s, lambda_slow in 13-158 s.
_MAILLE_LAM_FAST_RANGE = (2.2, 19.1)
_MAILLE_LAM_SLOW_RANGE = (13.0, 158.0)
_CAMERON_EXHAUST_S = 400.0   # run cameron to solute exhaustion so the curve plateaus (lambda_slow
                             # up to 158 s cannot be identified over the paper's ~30 s recipe window)


def cross_model_timescale_cameron():
    """Cameron-only HALF of the card's gate 4 (cross-model timescale portability).

    The card asks whether maille's two-regime decomposition (Eq 6.2) ports off maille's stirred
    batch: fit Eq 6.2 to an independent rig's extraction curve and check whether lambda_fast lands
    in maille's 2.2-19.1 s band and lambda_slow in 13-158 s. This is the cameron2020 half; the
    Roman-Corrochano stirred-vessel half is a sibling research computation,
    cross_model_timescale_roman() (NOT rights-blocked; the #100 rights deferral gates only the
    public Laboratory product lens).

    THREE STANDING CAVEATS make this a QUALITATIVE probe, never a validation:
      (1) cameron2020 has NO well-mixed configuration -- it is intrinsically a flowing percolation
          bed (advection term q in the liquid balance). The card's literal 'well-mixed cameron
          configuration' does not exist; what is fit here is cameron's MODEL-GENERATED cumulative
          extraction curve m_cup(t)/m_cup(inf).
      (2) to expose lambda_slow up to maille's 158 s, cameron is run to solute exhaustion
          (~400 s) -- FAR beyond its validated ~30 s espresso recipe: an extrapolation of the
          cameron model itself.
      (3) cameron lumps all solute into one species (one C_SAT, one D_S); maille resolves five.
          So cameron yields ONE (lambda_fast, lambda_slow) pair per grind, not per species, and
          tau is fixed to 0 (cameron models no hydration lag).

    FINDING (robust, deterministic): NO cameron fit places its nominal fast constant inside maille's
    2.2-19.1 s fast band, in any of the four EK43 grinds. Additionally, the three FINER settings
    (gs 1.0/1.5/2.0) collapse to a single-exponential-like response -- the two fitted constants
    coincide and a two-exponential fit gains ~0 R2 over one exponential (constants non-identifiable).
    The COARSEST setting (gs 2.5) does NOT collapse: it returns two SEPARATED constants (~23.6 s and
    ~40.0 s) whose two-vs-one adjudication is left to formal model selection and is NOT asserted here
    to be single-timescale. So cameron does not reproduce maille's fast timescale, and is
    single-exponential-like in 3 of 4 settings -- maille's two-regime decomposition does not port to
    cameron's flowing rig. Strength: qualitative. NOTE we report a one- vs two-exponential R2
    comparison per grind, not a heuristic distance threshold; a full identifiability treatment
    (AICc/BIC on deterministic curves, multistart, profile likelihoods) is out of scope for this
    quick probe (see the maille card / review action plan)."""
    import numpy as np
    from scipy.optimize import curve_fit
    from puckworks.models.cameron2020.extraction_bdf import GS_GRID, simulate_shot

    def _f(t, phi, lam_fast, lam_slow):    # Eq 6.2 with tau = 0
        return phi * (1.0 - np.exp(-t / lam_fast)) + (1.0 - phi) * (1.0 - np.exp(-t / lam_slow))

    def _one(t, lam):                      # single exponential (one-timescale null)
        return 1.0 - np.exp(-t / lam)

    fast_lo, fast_hi = _MAILLE_LAM_FAST_RANGE
    slow_lo, slow_hi = _MAILLE_LAM_SLOW_RANGE
    per = []
    for gs in GS_GRID:
        r = simulate_shot(float(gs), t_shot=_CAMERON_EXHAUST_S, n_save=300)
        t = np.asarray(r.t, float)
        y = np.asarray(r.m_cup, float) / float(r.m_cup[-1])
        mask = t > 0.0
        p, _ = curve_fit(_f, t[mask], y[mask], p0=[0.5, 5.0, 40.0],
                         bounds=([0.0, 0.1, 1.0], [1.0, 200.0, 2000.0]), maxfev=20000)
        phi, lf, ls = (float(v) for v in p)
        if lf > ls:                        # order the constants (remove label switching)
            lf, ls, phi = ls, lf, 1.0 - phi
        ss = lambda arr: float(np.sum(arr ** 2))
        ss_tot = ss(y[mask] - y[mask].mean())
        r2_two = 1.0 - ss(y[mask] - _f(t[mask], phi, lf, ls)) / ss_tot
        p1, _ = curve_fit(_one, t[mask], y[mask], p0=[30.0], maxfev=20000)
        r2_one = 1.0 - ss(y[mask] - _one(t[mask], float(p1[0]))) / ss_tot
        # a SETTING-SPECIFIC collapse signal: the two constants coincide (tight) AND a second
        # exponential buys essentially no R2 -- i.e. the bi-exponential is non-identifiable here.
        constants_coincide = abs(lf - ls) / max(ls, 1e-9) < 0.1
        # U6: identifiability via MULTISTART. Fit the bi-exponential from a deterministic grid of
        # starting weights; when the two constants coincide the mixture weight phi is arbitrary, so
        # near-optimal fits span a wide phi range (non-identifiable) while a genuinely two-scale curve
        # pins phi. Report the phi span rather than trusting a single fit's R2.
        phi_starts = []
        for w0 in (0.15, 0.35, 0.5, 0.65, 0.85):
            try:
                pm, _ = curve_fit(_f, t[mask], y[mask], p0=[w0, 3.0, 60.0],
                                  bounds=([0.0, 0.1, 1.0], [1.0, 200.0, 2000.0]), maxfev=20000)
                wm, am, bm = (float(v) for v in pm)
                phi_starts.append(wm if am <= bm else 1.0 - wm)
            except Exception:
                pass
        phi_span = (max(phi_starts) - min(phi_starts)) if phi_starts else 0.0
        # non-identifiable when the two-exp gains ~0 R2 over one-exp AND phi wanders across multistart
        non_identifiable = bool(constants_coincide and (r2_two - r2_one) < 1e-3 and phi_span > 0.3)
        single_exp_like = bool(constants_coincide and (r2_two - r2_one) < 1e-3)
        per.append(dict(gs=float(gs), phi=round(phi, 3), lambda_fast_s=round(lf, 2),
                        lambda_slow_s=round(ls, 2), r2_two=round(r2_two, 5), r2_one=round(r2_one, 5),
                        two_exp_r2_gain=round(r2_two - r2_one, 5),
                        phi_multistart_span=round(phi_span, 3), non_identifiable=non_identifiable,
                        fast_in_maille_band=bool(fast_lo <= lf <= fast_hi),
                        slow_in_maille_band=bool(slow_lo <= ls <= slow_hi),
                        single_exp_like=single_exp_like,
                        needs_model_selection=bool(not constants_coincide)))
    # the robust, deterministic non-portability signal: NO grind reproduces maille's fast timescale
    no_fast_component = all(not row["fast_in_maille_band"] for row in per)
    n_single_exp_like = sum(1 for row in per if row["single_exp_like"])
    n_non_identifiable = sum(1 for row in per if row["non_identifiable"])
    # U9: portability is a VECTOR, not a Boolean.
    portability_vector = {
        "observable_identity": "differ (maille = measured multi-analyte batch concentration; cameron "
                               "= model-generated flowing-bed cumulative cup fraction, run to ~400 s)",
        "mechanism_identity": "differ (maille = geometric two-POOL split; cameron = aggregate "
                              "flowing-bed response: advection + dissolution + intragrain diffusion)",
        "population_identity": "differ (maille = 5 analytes; cameron = 1 lumped solute, one C_SAT/D_S)",
        "estimation_identity": "differ (tau fixed 0; 400 s run-to-exhaustion extrapolation past the "
                               "~30 s recipe; endpoint normalization)",
        "numerical_compatibility": "no_fast_band_match (no fitted lambda_fast in maille's 2.2-19.1 s "
                                   "band in any grind; 3 of 4 settings single-exponential-like)",
        "predictive_transfer": "not_tested",
    }
    return dict(
        per_grind=per,
        roman_corrochano_half="landed as a research computation -- cross_model_timescale_roman(); "
                              "the #100 rights deferral is product-lane (public Laboratory lens) only",
        no_maille_fast_component=no_fast_component,
        n_settings_single_exp_like=n_single_exp_like,
        n_settings_non_identifiable=n_non_identifiable,
        coarsest_needs_model_selection=bool(per[-1]["needs_model_selection"]),
        portability_vector=portability_vector,
        portability_verdict="non_portability_under_declared_mapping",
        two_regime_ports_to_cameron=bool(not no_fast_component),
        passed=bool(no_fast_component),
        finding="Fitting maille's Eq-6.2 to cameron's model-generated run-to-exhaustion (~400 s) "
                "extraction curve, NO fitted lambda_fast enters maille's fast band (2.2-19.1 s) in "
                "any of the four EK43 grinds. The three FINER settings (gs 1.0/1.5/2.0) are "
                "single-exponential-like (constants coincide; a 2nd exponential buys ~0 R2 -> "
                "non-identifiable); the COARSEST (gs 2.5) returns two SEPARATED constants "
                "(~23.6/40.0 s) and is left for formal model selection, NOT asserted single-"
                "timescale. So cameron does not reproduce maille's fast timescale and is single-"
                "exponential-like in 3 of 4 settings -- maille's two-regime decomposition does not "
                "port to cameron's flowing rig. QUALITATIVE: model-generated curve; cameron has no "
                "well-mixed config and is pushed past its validated ~30 s recipe to plateau; NOT a "
                "validation of either model. The Roman-Corrochano stirred-vessel half (a genuine "
                "well-mixed config) is cross_model_timescale_roman().")


_ROMAN_R_FINE_M = 20e-6        # roman's fine size class ~40 um diameter (card: "fine-class mean size
                              # ~40 um (biological cell)"); the ONLY particle size the card states.
                              # The coarse class is "at d[4,3]" but is NOT published in-repo, so it is
                              # not fabricated here -- the roman half runs at the fine class only.
_ROMAN_T_DEGC = 80.0          # roman's Deff table (4.9) reference temperature; deff_of T-corrects.
                              # (maille ran at 91.5 C, which would make roman's release only FASTER.)


def cross_model_timescale_roman():
    """Roman-Corrochano stirred-vessel HALF of the card's gate 4 (cross-model timescale portability)
    -- the genuine WELL-MIXED config that cameron2020 lacks. NOT rights-blocked for this research use:
    romancorrochano2017.extraction is the same published_port/NOT_REVIEWED class as cameron2020, which
    this module already runs; the #100 rights deferral gates only the public Laboratory product lens.

    Roman's raw experimental curves were never published, so (as for cameron) the curve is MODEL-
    generated: `romancorrochano2017.extraction.stirred_vessel` (a Crank-verified spherical-diffusion
    solver) into a finite well-mixed bath, single lumped medium-MW species (the card's headline
    galactomannan-DP20 Deff), dilute bath, roman's fine size class (R ~= 20 um). Fit maille's Eq 6.2
    per grind (Blend-1, PsiA..PsiH) on a time window matched to roman's own diffusion time.

    FINDING (two-fold):
      * SHAPE (scale-invariant): a single-Deff sphere release has a FIXED dimensionless shape -- every
        grind fits to the SAME weight phi ~= 0.32 and the SAME slow/fast RATIO ~= 12.3. Only the
        dimensionless SHAPE is invariant; the ABSOLUTE constants scale with the diffusion time
        (tau ~ R^2/(pi^2 Deff)) and vary ~1.9x across the seven grinds (review comment U2 -- do NOT
        call the absolute constants grind-independent). The two-regime form fits well (R2 ~ 0.999 vs
        ~0.95 for one exponential), but that split is the early/late-time signature of ONE physical
        diffusion PROCESS in one particle/species class -- NOT two physical pools (avoid "single
        mathematical mode"; a sphere solution is many eigenmodes, review comment U4). maille's split,
        by contrast, is a modeled two-POOL (fines < 186 um + coarse-particle shells) structure whose
        phi and separation VARY by material. Same word ("two-regime"), different construct.
      * ABSOLUTE bands (SELECTED fine class only): at roman's card-stated 20 um fine class the fitted
        lambda_fast ~0.03-0.06 s and lambda_slow ~0.36-0.68 s fall below maille's bands (fast
        2.2-19.1 s, slow 13-158 s). This is fine-class-SPECIFIC, not a universal-numeric claim: the
        coarse class (d[4,3], not published in-repo) would raise tau by (R_coarse/R_fine)^2 and could
        enter maille's bands -- it is deliberately NOT fabricated (review comment U3).

    So a shared bi-exponential form is not a shared physical construct; the defensible conclusion is
    SEMANTIC non-equivalence under the tested fine-class mapping, not a universal numerical theorem.
    Strength: qualitative (model-generated curve, single lumped species, fine class only)."""
    import numpy as np
    from scipy.optimize import curve_fit
    from puckworks.models.romancorrochano2017 import extraction as rc

    def _f(t, phi, lam_fast, lam_slow):        # Eq 6.2 with tau = 0
        return phi * (1.0 - np.exp(-t / lam_fast)) + (1.0 - phi) * (1.0 - np.exp(-t / lam_slow))

    def _one(t, lam):
        return 1.0 - np.exp(-t / lam)

    fast_lo, fast_hi = _MAILLE_LAM_FAST_RANGE
    slow_lo, slow_hi = _MAILLE_LAM_SLOW_RANGE
    R, T = _ROMAN_R_FINE_M, _ROMAN_T_DEGC
    K = rc.K_of_T(T)
    grinds = [row["grind"] for row in d.roman_deff() if row["blend"] == "Blend1"]
    per = []
    for g in grinds:
        deff = rc.deff_of(g, "med", T)
        tau = R ** 2 / (math.pi ** 2 * deff)                 # med-MW diffusion time
        t_eval = np.linspace(0.0, 20.0 * tau, 500)
        t, frac = rc.stirred_vessel(deff, R, K, pore_to_bath=0.01, t_eval=t_eval)
        y = np.asarray(frac, float) / float(frac[-1])
        mask = t > 0.0
        p, _ = curve_fit(_f, t[mask], y[mask], p0=[0.5, 0.3 * tau, 2.0 * tau],
                         bounds=([0.0, 1e-4, 1e-3], [1.0, 100.0 * tau, 1000.0 * tau]), maxfev=40000)
        phi, a, b = (float(v) for v in p)
        lf, ls = (a, b) if a <= b else (b, a)
        yhat = _f(t[mask], phi, a, b)
        ss = lambda arr: float(np.sum(arr ** 2))
        r2_two = 1.0 - ss(y[mask] - yhat) / ss(y[mask] - y[mask].mean())
        p1, _ = curve_fit(_one, t[mask], y[mask], p0=[tau], maxfev=20000)
        r2_one = 1.0 - ss(y[mask] - _one(t[mask], float(p1[0]))) / ss(y[mask] - y[mask].mean())
        per.append(dict(grind=g, deff_med_m2_s=deff, tau_diff_s=round(tau, 3),
                        phi=round(phi, 3), lambda_fast_s=round(lf, 4), lambda_slow_s=round(ls, 4),
                        ratio_slow_over_fast=round(ls / lf, 2), r2_two=round(r2_two, 5),
                        r2_one=round(r2_one, 5),
                        fast_in_maille_band=bool(fast_lo <= lf <= fast_hi),
                        slow_in_maille_band=bool(slow_lo <= ls <= slow_hi)))
    ratios = [row["ratio_slow_over_fast"] for row in per]
    phis = [row["phi"] for row in per]
    fasts = [row["lambda_fast_s"] for row in per]
    slows = [row["lambda_slow_s"] for row in per]
    # scale-invariant Crank SHAPE: the fitted ratio and weight (phi) are grind-INDEPENDENT.
    # (NB: only the dimensionless shape is invariant; the ABSOLUTE constants scale with R^2/Deff and
    #  vary across grinds -- see absolute_timescales_are_grind_independent below. Review comment U2.)
    shape_universal = (max(ratios) - min(ratios) < 0.1) and (max(phis) - min(phis) < 0.02)
    absolute_grind_independent = (max(fasts) - min(fasts) < 1e-9) and (max(slows) - min(slows) < 1e-9)
    # a single-Deff Crank curve is two-regime-SHAPED, not a single exponential
    two_regime_beats_one = all(row["r2_two"] > row["r2_one"] + 0.02 for row in per)
    # fine-class miss: no grind lands EITHER timescale in maille's bands (fine class R~20um ONLY;
    # the coarse class d[4,3] is not published in-repo -> not evaluated, review comment U3)
    none_in_maille_bands = all(not row["fast_in_maille_band"] and not row["slow_in_maille_band"]
                               for row in per)
    # the semantic verdict is DERIVED, not hard-coded (review comment U11): a shared bi-exponential
    # form is not a shared physical construct -- the shape is one diffusion process's short/long-time
    # signature, invariant across grinds, and the fine-class bands miss maille's.
    ports_to_roman = not (shape_universal and two_regime_beats_one and none_in_maille_bands)
    # U9: portability is a VECTOR, not a Boolean -- a fitted timescale can fail to port for several
    # independent reasons, and numerical-range overlap alone would not prove semantic portability.
    portability_vector = {
        "observable_identity": "differ (maille = measured multi-analyte batch concentration; roman = "
                               "model-generated single-species stirred-vessel fractional release)",
        "mechanism_identity": "differ (maille = geometric two-POOL fines+coarse-shell split; roman = "
                              "ONE physical diffusion process, early/late-time signature)",
        "population_identity": "differ (maille = 5 analytes over fines+coarse pools; roman = 1 lumped "
                               "medium-MW species, fine class R~20um only, coarse class not evaluated)",
        "estimation_identity": "differ (tau fixed 0; roman window = 20 diffusion times, finite-bath "
                               "normalization -- protocol-specific, see roman_protocol_sensitivity())",
        "numerical_compatibility": "fine_class_miss (both fitted timescales below maille's bands at "
                                   "R~20um; a larger coarse radius could overlap but was not evaluated)",
        "predictive_transfer": "not_tested (no out-of-sample transfer of a donor timescale attempted)",
    }
    portability_verdict = "semantic_non_equivalence_under_tested_mapping"
    return dict(
        per_grind=per, config="well-mixed stirred vessel (genuine config); MODEL-GENERATED (Crank-"
                              "verified solver, no raw roman curves published); single lumped medium-"
                              "MW species; fine size class R~20um ONLY",
        particle_class="fine", radius_m=_ROMAN_R_FINE_M,
        coarse_class_status="not_evaluated_missing_radius",   # d[4,3] not in-repo; not fabricated (U3)
        rights_note="research computation; not rights-blocked (same published_port/NOT_REVIEWED class "
                    "as cameron2020, used here already). #100 deferral is the public product lens only.",
        universal_ratio_slow_over_fast=round(sum(ratios) / len(ratios), 2),
        universal_phi=round(sum(phis) / len(phis), 3),
        shape_is_scale_invariant=bool(shape_universal),
        absolute_timescales_are_grind_independent=bool(absolute_grind_independent),   # False (U2)
        two_regime_shaped_not_single_exp=bool(two_regime_beats_one),
        none_in_maille_bands_fine_class=bool(none_in_maille_bands),
        portability_vector=portability_vector,
        portability_verdict=portability_verdict,
        two_regime_ports_to_roman=bool(ports_to_roman),
        passed=bool(not ports_to_roman),
        finding="Roman's single-species WELL-MIXED (model-generated stirred-vessel) diffusion curve "
                "fits maille's Eq-6.2 to a UNIVERSAL dimensionless SHAPE: the fitted weight (phi "
                "~0.32) and slow/fast RATIO (~12.3) are invariant across grinds, while the ABSOLUTE "
                "constants scale with the diffusion time (R^2/Deff) and vary ~1.9x across the seven "
                "grinds -- shape invariance, NOT absolute-constant invariance. That shape is the "
                "early/late-time signature of ONE physical diffusion process in one particle/species "
                "class, two-regime-SHAPED (R2 ~0.999 vs ~0.95 for one exponential) but NOT maille's "
                "material-varying two-POOL (fines + coarse shells) construct: same word, different "
                "thing. For the SELECTED 20um fine class the timescales are sub-second, below maille's "
                "2.2-19.1 s / 13-158 s bands; the coarse class d[4,3] is not published in-repo and was "
                "NOT fabricated (larger radii would raise tau ~ R^2 and could enter maille's bands -- "
                "so this is a fine-class-specific, not universal-numeric, result). The defensible "
                "conclusion is SEMANTIC: a shared bi-exponential form is not a shared physical "
                "construct. QUALITATIVE (model-generated curve, single lumped species, fine class).")


def roman_protocol_sensitivity(grind="PsiA"):
    """U8: the roman 'universal' shape (weight ~0.32, ratio ~12.3) is real ACROSS GRINDS at fixed
    dimensionless settings, but the exact numeric pair is NOT a protocol-independent constant. Vary
    the fit window and the pore-to-bath dilution (R = 20 um fine class, medium-MW Deff) and report
    how the fitted weight/ratio drift -- so the manuscript can describe the pair as protocol-specific
    rather than intrinsic. Reproduces the review's U8 sensitivity tables from the registered solver."""
    import numpy as np
    from scipy.optimize import curve_fit
    from puckworks.models.romancorrochano2017 import extraction as rc

    def _f(t, phi, lf, ls):
        return phi * (1.0 - np.exp(-t / lf)) + (1.0 - phi) * (1.0 - np.exp(-t / ls))

    R, T = _ROMAN_R_FINE_M, _ROMAN_T_DEGC
    K = rc.K_of_T(T)
    deff = rc.deff_of(grind, "med", T)
    tau = R ** 2 / (math.pi ** 2 * deff)

    def _fit(pore_to_bath, window_taus):
        t_eval = np.linspace(0.0, window_taus * tau, 500)
        t, frac = rc.stirred_vessel(deff, R, K, pore_to_bath=pore_to_bath, t_eval=t_eval)
        y = np.asarray(frac, float) / float(frac[-1])
        m = t > 0.0
        p, _ = curve_fit(_f, t[m], y[m], p0=[0.5, 0.3 * tau, 2.0 * tau],
                         bounds=([0.0, 1e-4, 1e-3], [1.0, 100.0 * tau, 1000.0 * tau]), maxfev=40000)
        phi, a, b = (float(v) for v in p)
        lf, ls = (a, b) if a <= b else (b, a)
        return dict(phi=round(phi, 3), lambda_fast_s=round(lf, 4), lambda_slow_s=round(ls, 4),
                    ratio_slow_over_fast=round(ls / lf, 2))
    window_rows = [dict(window_diffusion_times=w, **_fit(0.01, w))
                   for w in (3.0, 5.0, 10.0, 20.0, 40.0, 100.0)]
    bath_rows = [dict(pore_to_bath=ptb, **_fit(ptb, 20.0))
                 for ptb in (1e-4, 1e-3, 1e-2, 0.1, 1.0, 3.0)]
    ratios_w = [r["ratio_slow_over_fast"] for r in window_rows]
    return dict(
        grind=grind, radius_m=R, temperature_degC=T,
        vs_fit_window=window_rows, vs_pore_to_bath=bath_rows,
        ratio_drifts_with_protocol=bool(max(ratios_w) - min(ratios_w) > 1.0),
        note="shape invariance ACROSS GRINDS at fixed settings is real; the exact weight ~0.32 / "
             "ratio ~12.3 pair is protocol-specific (drifts with fit window and dilution), so the "
             "manuscript describes it as protocol-conditional, not an intrinsic universal constant.")


# U10: two producer-bound, machine-readable claim records for the timescale-semantics result. These
# are NOT added to EVIDENCE_LINKS.json: reconcile() enforces a bijection with REGISTERED registry
# gate wirings, and maille2024 is a data+analysis provider (no registered gate), so a link here would
# be flagged ORPHAN and break --strict. Promoting these to formal EVIDENCE_LINKS claims requires the
# deferred maille component-registration decision. Until then they live as a standalone result bundle.
def timescale_semantics_bundle():
    """Assemble the U10 result bundle: the two gate-4 producers + the roman protocol sensitivity, with
    claim-record metadata (statement / producer / configuration / limitations / not_supported), for a
    generated, source-committable artifact the manuscript can cite. Returns a JSON-serializable dict."""
    cam = cross_model_timescale_cameron()
    rom = cross_model_timescale_roman()
    sens = roman_protocol_sensitivity()
    return {
        "bundle": "paper3.timescale_semantics",
        "note": "Qualitative model-to-model probes of whether maille's two-regime decomposition ports "
                "to cameron2020 / romancorrochano2017. NOT a validation of any model. NOT an "
                "EVIDENCE_LINKS claim (see module note): formal claim-record promotion needs the "
                "maille component-registration decision.",
        "claims": [
            {
                "claim_id": "paper3.timescale_semantics.cameron",
                "statement": "Under the declared 400 s, tau=0 fitting protocol, no cameron2020 grinder "
                             "setting reproduces maille's pooled fast-timescale band (2.2-19.1 s); "
                             "three of four curves are single-exponential-like, while the coarsest "
                             "requires formal two-vs-one model adjudication.",
                "producer": "puckworks.analysis.maille2024.cross_model_timescale_cameron",
                "components": ["maille2024 (analysis provider)", "cameron2020.extraction_bdf"],
                "evidence_relation": "model_to_model_qualitative",
                "outcome_polarity": "non_portability_under_declared_mapping",
                "configuration": {"horizon_s": _CAMERON_EXHAUST_S, "normalization": "simulated_endpoint",
                                  "delay_s": 0},
                "portability_vector": cam["portability_vector"],
                "result": {"no_maille_fast_component": cam["no_maille_fast_component"],
                           "n_settings_single_exp_like": cam["n_settings_single_exp_like"],
                           "coarsest_needs_model_selection": cam["coarsest_needs_model_selection"]},
                "limitations": ["model-generated curve", "cameron extrapolated beyond ~30 s validation",
                                "one lumped cameron solute vs five maille analytes",
                                "identifiability by multistart + one-vs-two-exp, not full profile likelihood"],
                "not_supported": ["external validation",
                                  "that cameron has only one physical extraction mechanism",
                                  "universal non-portability under every fit protocol"],
            },
            {
                "claim_id": "paper3.timescale_semantics.roman_corrochano",
                "statement": "Under the declared fine-class stirred-vessel protocol, the fitted "
                             "dimensionless bi-exponential shape (weight ~0.32, slow/fast ratio ~12.3) "
                             "is invariant across diffusivities while absolute constants vary with the "
                             "diffusion time and remain below maille's bands at R=20 um.",
                "producer": "puckworks.analysis.maille2024.cross_model_timescale_roman",
                "components": ["maille2024 (analysis provider)", "romancorrochano2017.extraction"],
                "evidence_relation": "model_to_model_qualitative",
                "outcome_polarity": rom["portability_verdict"],
                "configuration": {"radius_m": rom["radius_m"], "temperature_degC": _ROMAN_T_DEGC,
                                  "molecular_weight_class": "medium", "pore_to_bath": 0.01,
                                  "fit_window_diffusion_times": 20, "normalization": "finite_window_endpoint"},
                "portability_vector": rom["portability_vector"],
                "result": {"shape_is_scale_invariant": rom["shape_is_scale_invariant"],
                           "absolute_timescales_are_grind_independent":
                               rom["absolute_timescales_are_grind_independent"],
                           "universal_phi": rom["universal_phi"],
                           "universal_ratio_slow_over_fast": rom["universal_ratio_slow_over_fast"],
                           "coarse_class_status": rom["coarse_class_status"]},
                "protocol_sensitivity": {"ratio_drifts_with_protocol": sens["ratio_drifts_with_protocol"]},
                "limitations": ["model-generated curve", "fine class only", "coarse-class radius unavailable",
                                "protocol-sensitive empirical approximation"],
                "not_supported": ["validation against roman experimental time curves",
                                  "absolute-timescale conclusion for the untested coarse class",
                                  "claim that the physical diffusion solution is one mathematical mode"],
            },
        ],
    }
