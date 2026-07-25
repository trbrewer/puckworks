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

NOTE (blocked, owed): the phi-split-vs-Cameron discriminating gate (compute phi from Cameron's EK43
PSD, compare to Cameron's fitted fast population) needs Cameron's measured BINNED PSD, which the
registry does not yet hold (only a two-size-class idealisation) -- deferred.
"""
from __future__ import annotations

from puckworks import data as d

_D_C_M = 45e-6            # coffee cell diameter (card Parameters; SEM range 20-60 um)


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
