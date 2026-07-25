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
