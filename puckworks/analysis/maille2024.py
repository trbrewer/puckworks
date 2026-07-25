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
6. cross_model_timescale_cameron() -- the cameron HALF of gate 4: fit Eq 6.2 to cameron's simulated
   (flowing-bed) extraction curve and check maille's lambda bands. The two-regime split collapses
   (single ~30 s timescale, no maille-fast component) -- non-portable. QUALITATIVE (cameron has no
   well-mixed config; run past its recipe to plateau).
7. cross_model_timescale_roman()   -- the Roman-Corrochano HALF of gate 4: the GENUINE well-mixed
   (stirred-vessel) config. Fit Eq 6.2 to roman's model-generated single-species diffusion curve;
   it fits a UNIVERSAL Crank shape (grind-independent phi ~0.32, ratio ~12.3) that is one diffusion
   mode's short/long-time signature, NOT maille's material-varying two-POOL split; fine-class
   timescales sit ~2 orders below maille's bands. Non-portable. QUALITATIVE. (This is a research
   computation; the #100 rights deferral gates only the public Laboratory product lens.)
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
    in maille's 2.2-19.1 s band and lambda_slow in 13-158 s. The Roman-Corrochano stirred-vessel
    HALF is rights-deferred (product #100), so only the cameron2020 side runs here.

    THREE STANDING CAVEATS make this a QUALITATIVE probe, never a validation:
      (1) cameron2020 has NO well-mixed configuration -- it is intrinsically a flowing percolation
          bed (advection term q in the liquid balance). The card's literal 'well-mixed cameron
          configuration' does not exist; what is fit here is cameron's simulated cumulative
          extraction curve m_cup(t)/m_cup(inf).
      (2) to expose lambda_slow up to maille's 158 s, cameron is run to solute exhaustion
          (~400 s) -- FAR beyond its validated ~30 s espresso recipe: an extrapolation of the
          cameron model itself.
      (3) cameron lumps all solute into one species (one C_SAT, one D_S); maille resolves five.
          So cameron yields ONE (lambda_fast, lambda_slow) pair per grind, not per species, and
          tau is fixed to 0 (cameron models no hydration lag).

    FINDING: across all four EK43 grinds the two-regime fit COLLAPSES -- fitted lambda_fast lands
    at ~23-32 s (ABOVE maille's fast ceiling of 19.1 s) and, for the three finer grinds,
    lambda_fast ~= lambda_slow, so the fast/slow split is unidentifiable and phi is degenerate.
    Cameron's curve is essentially single-timescale (~28-32 s, which happens to sit inside maille's
    broad SLOW band); it has NO distinct maille-fast component. i.e. maille's two-regime
    decomposition does NOT port to cameron's flowing rig -- exactly the 'miss' the card anticipated.
    Strength: qualitative."""
    import numpy as np
    from scipy.optimize import curve_fit
    from puckworks.models.cameron2020.extraction_bdf import GS_GRID, simulate_shot

    def _f(t, phi, lam_fast, lam_slow):    # Eq 6.2 with tau = 0
        return phi * (1.0 - np.exp(-t / lam_fast)) + (1.0 - phi) * (1.0 - np.exp(-t / lam_slow))

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
        yhat = _f(t[mask], phi, lf, ls)
        ss_res = float(np.sum((y[mask] - yhat) ** 2))
        ss_tot = float(np.sum((y[mask] - y[mask].mean()) ** 2))
        r2 = 1.0 - ss_res / ss_tot
        # degenerate (single-timescale) when the two fitted constants nearly coincide
        degenerate = abs(lf - ls) / max(ls, 1e-9) < 0.5
        per.append(dict(gs=float(gs), phi=round(phi, 3), lambda_fast_s=round(lf, 2),
                        lambda_slow_s=round(ls, 2), r2=round(r2, 4),
                        fast_in_maille_band=bool(fast_lo <= lf <= fast_hi),
                        slow_in_maille_band=bool(slow_lo <= ls <= slow_hi),
                        single_timescale=degenerate))
    # the robust, deterministic non-portability signal: NO grind reproduces maille's fast timescale
    no_fast_component = all(not row["fast_in_maille_band"] for row in per)
    return dict(
        per_grind=per,
        roman_corrochano_half="landed as a research computation -- cross_model_timescale_roman(); "
                              "the #100 rights deferral is product-lane (public Laboratory lens) only",
        no_maille_fast_component=no_fast_component,
        two_regime_ports_to_cameron=bool(not no_fast_component),
        passed=bool(no_fast_component),
        finding="Fitting maille's Eq-6.2 to cameron's run-to-exhaustion (~400 s) extraction curve, "
                "the two-regime split COLLAPSES: fitted lambda_fast ~23-32 s lands ABOVE maille's "
                "fast band (2.2-19.1 s) in ALL four grinds and coincides with lambda_slow for the "
                "three finer grinds (phi degenerate). Cameron is single-timescale (~28-32 s, inside "
                "maille's broad slow band) with NO distinct fast component -- maille's two-regime "
                "decomposition does not port to cameron's flowing rig. QUALITATIVE: cameron has no "
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
      * SHAPE (scale-invariant): a single-Deff sphere release has a FIXED shape -- every grind fits to
        the SAME phi ~= 0.32 and the SAME lambda_slow/lambda_fast ~= 12.3; only the absolute timescale
        (tau ~ R^2/(pi^2 Deff)) shifts. The two-regime form fits it well (R2 ~ 0.999 vs ~0.95 for one
        exponential), but that split is the intrinsic short-time (t^1/2) / long-time signature of ONE
        diffusion mode -- NOT two physical pools. maille's split, by contrast, is a modeled two-POOL
        (fines < 186 um + coarse-particle shells) structure whose phi and separation VARY by material.
        Same word ("two-regime"), different construct -- echoes the phi-split observable-semantics gap.
      * ABSOLUTE bands: at roman's card-stated fine class the fitted lambda_fast ~0.03-0.06 s and
        lambda_slow ~0.4-0.7 s -- ~2 orders of magnitude BELOW maille's bands (fast 2.2-19.1 s, slow
        13-158 s). Roman's coarse class (d[4,3], not published in-repo) would raise tau by
        (R_coarse/R_fine)^2 and is deliberately NOT fabricated.

    So maille's two-regime decomposition does not port to roman's well-mixed diffusion physics either.
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
    # scale-invariant Crank shape: the fitted ratio and phi are grind-INDEPENDENT
    shape_universal = (max(ratios) - min(ratios) < 0.1) and (max(phis) - min(phis) < 0.02)
    # a single-Deff Crank curve is two-regime-SHAPED, not a single exponential
    two_regime_beats_one = all(row["r2_two"] > row["r2_one"] + 0.02 for row in per)
    # fine-class miss: no grind lands EITHER timescale in maille's bands
    none_in_maille_bands = all(not row["fast_in_maille_band"] and not row["slow_in_maille_band"]
                               for row in per)
    return dict(
        per_grind=per, config="well-mixed stirred vessel (genuine); model-generated (Crank-verified "
                              "solver); single lumped medium-MW species; fine size class R~20um",
        rights_note="research computation; not rights-blocked (same published_port/NOT_REVIEWED class "
                    "as cameron2020, used here already). #100 deferral is the public product lens only.",
        universal_ratio_slow_over_fast=round(sum(ratios) / len(ratios), 2),
        universal_phi=round(sum(phis) / len(phis), 3),
        shape_is_scale_invariant=bool(shape_universal),
        two_regime_shaped_not_single_exp=bool(two_regime_beats_one),
        none_in_maille_bands_fine_class=bool(none_in_maille_bands),
        two_regime_ports_to_roman=False,
        passed=bool(shape_universal and two_regime_beats_one and none_in_maille_bands),
        finding="Roman's single-species WELL-MIXED (stirred-vessel) diffusion curve fits maille's "
                "Eq-6.2 to a UNIVERSAL shape (phi ~0.32, lambda_slow/lambda_fast ~12.3, grind-"
                "INDEPENDENT) -- the intrinsic short/long-time signature of ONE Crank diffusion mode, "
                "not two physical pools. Two-regime-shaped (R2 ~0.999 vs ~0.95 for one exponential) "
                "but NOT maille's material-varying two-POOL (fines + coarse shells) construct: same "
                "word, different thing. At roman's card-stated fine class the timescales are sub-"
                "second -- ~2 orders below maille's bands (roman's unpublished coarse d[4,3] NOT "
                "fabricated). maille's two-regime decomposition does not port to roman's diffusion "
                "physics. QUALITATIVE (model-generated curve, single lumped species, fine class).")
