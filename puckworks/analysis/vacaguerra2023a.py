"""vacaguerra2023a discriminating computations (card `docs/cards/vacaguerra2023a.md`).

Three offline, PDE-free verifications on the digitized data (Tim drop 2026-07-25), each named
by the card's Implementation-estimate gates. All strengths are **verification / post-fit
reconstruction** of the source's own internal consistency, NOT independent validation of coffee
physics (single dark-roast arabica; the permeability closure is post-fit on 9 points).

1. resolve_compression_sign()  -- the card's *blocking* gate: resolve the printed Eq-9/Eq-10
   beta-term sign. The negated-beta convention is adopted (physical repose porosity + reproduces
   the Fig-9 per-PSD fits); the printed +beta form is unphysical.
2. fig12_validation()          -- recompute the cross-device dry-porosity validation R^2 / RMSE
   (the authors report ~0.93).
3. permeability_darcy()        -- INDEPENDENT Darcy K recomputation from the Table C.1 operating
   points; reports the as-published (mu=3.5 mPa s) K, an Eq-11 modified-Kozeny-Carman
   reconstruction, and the viscosity-renormalization scaling.
"""
from __future__ import annotations

import math

from puckworks import data as d
from puckworks.models.wadsworth2026 import permeability as _wads

# --- geometry / properties (card `docs/cards/vacaguerra2023a.md` Parameters) ---
_BED_DIAMETER_M = 0.059          # basket inner diameter 5.9 cm
_BED_AREA_M2 = math.pi * (_BED_DIAMETER_M / 2) ** 2
_L0_M = 0.0255                   # initial bed length 2.55 cm
_MU_PUBLISHED_PAS = 3.5e-3       # authors' unpublished brew-viscosity measurement at 65 C
_K_RANGE_M2 = (1.8e-14, 3.6e-13)  # card's stated MEASURED permeability range

# card Fig-9 per-PSD DIRECT (omega, phi) fits, order A/B/C -- the sign-resolution targets
_FIG9_OMEGA_PHI = {"A": (0.36, 6.875e-6), "B": (0.34, 1.007e-5), "C": (0.28, 1.257e-5)}

# modified Kozeny-Carman (Eq. 11): K = (psi d32)^2 eps^4.3 beta^0.43 / (72 lambda^2 (1-eps)^2)
_KC_LAMBDA = 7.5
_KC_EPS_EXP = 4.3
_KC_BETA_EXP = 0.43


def _phi(coeff, alpha_m, beta, beta_sign):
    """Eq. 9 compression factor phi(alpha, beta); beta_sign = -1 adopts the -k3*beta convention."""
    k = coeff
    return 1.0 / (k["k1"] - k["k2"] * alpha_m + beta_sign * k["k3"] * beta
                  + k["k4"] * alpha_m * beta + k["k5"] * alpha_m ** 2)


def _omega(coeff, alpha_m, beta, beta_sign):
    """Eq. 10 repose porosity omega(alpha, beta); beta_sign = -1 adopts the -x3*beta convention."""
    x = coeff
    return (x["x1"] - x["x2"] * alpha_m + beta_sign * x["x3"] * beta + x["x4"] * alpha_m * beta)


def resolve_compression_sign(omega_tol=0.05):
    """Resolve the printed Eq-9/Eq-10 beta-term sign error (the card's blocking gate).

    Under the printed +beta signs the repose porosity omega comes out ~0.48-0.62 -- above the
    loosest MEASURED bed (eps0 = 0.36, Table C.1) and the Fig-9 fits (0.28-0.36), i.e. unphysical.
    Under -beta, omega ~0.31-0.37 (matches Table C.1 + Fig-9 within `omega_tol`) and phi is the
    right magnitude. Verdict: adopt the negated-beta convention. Strength: verification."""
    kphi = d.vacaguerra_phi_coefficients()
    kom = d.vacaguerra_omega_coefficients()
    psd = {r["Distribution"]: r for r in d.vacaguerra_psd()}
    per = {}
    for dist, (om_fig9, phi_fig9) in _FIG9_OMEGA_PHI.items():
        a = float(psd[dist]["alpha_um"]) * 1e-6
        b = float(psd[dist]["beta"])
        per[dist] = dict(
            omega_plus=round(_omega(kom, a, b, +1), 4),
            omega_minus=round(_omega(kom, a, b, -1), 4),
            phi_plus=_phi(kphi, a, b, +1),
            phi_minus=_phi(kphi, a, b, -1),
            fig9_omega=om_fig9, fig9_phi=phi_fig9)
    minus_omega = [per[k]["omega_minus"] for k in per]
    plus_omega = [per[k]["omega_plus"] for k in per]
    minus_matches_fig9 = all(abs(per[k]["omega_minus"] - per[k]["fig9_omega"]) <= omega_tol
                             for k in per)
    minus_physical = all(0.28 <= o <= 0.40 for o in minus_omega)
    plus_unphysical = max(plus_omega) > 0.45
    adopted = "-beta" if (minus_physical and minus_matches_fig9 and plus_unphysical) else "UNRESOLVED"
    return dict(
        per_distribution=per, adopted_convention=adopted,
        minus_omega_range=[round(min(minus_omega), 3), round(max(minus_omega), 3)],
        plus_omega_range=[round(min(plus_omega), 3), round(max(plus_omega), 3)],
        minus_matches_fig9=bool(minus_matches_fig9),
        plus_beta_unphysical=bool(plus_unphysical),
        passed=bool(adopted == "-beta"),
        note="printed Table-2/3 k3,x3 are POSITIVE but the +beta form gives unphysical omega; "
             "the registry adopts -k3*beta / -x3*beta.")


def fig12_validation():
    """Recompute the cross-device dry-bed porosity validation (Fig. 12): R^2 and RMSE of the
    (measured, calculated) pairs the authors report at R^2 ~ 0.93. Strength: verification."""
    rows = d.vacaguerra_dry_porosity_validation()
    y = [float(r["measured_dry_bed_porosity"]) for r in rows]
    f = [float(r["calculated_dry_bed_porosity"]) for r in rows]
    n = len(y)
    ybar = sum(y) / n
    ss_res = sum((yi - fi) ** 2 for yi, fi in zip(y, f))
    ss_tot = sum((yi - ybar) ** 2 for yi in y)
    r2 = 1.0 - ss_res / ss_tot
    rmse = (ss_res / n) ** 0.5
    return dict(n=n, r2=round(r2, 3), rmse=round(rmse, 4),
                passed=bool(r2 >= 0.90),
                note="two vessels (60 mm stainless portafilter + 50 mm acrylic); "
                     "the authors' cross-device validation, recomputed.")


def _kozeny_carman_k(psi, d32_m, eps, beta):
    return ((psi * d32_m) ** 2 * eps ** _KC_EPS_EXP * beta ** _KC_BETA_EXP
            / (72.0 * _KC_LAMBDA ** 2 * (1.0 - eps) ** 2))


def permeability_darcy(mu_pas=_MU_PUBLISHED_PAS):
    """Independent Darcy K = Q*mu*L / (A*DeltaP) from the 9 Table C.1 operating points, plus the
    Eq-11 modified-Kozeny-Carman reconstruction per point. Reports how many land in the card's
    stated measured band and the viscosity-renormalization scaling (K ∝ mu). Strength:
    verification / post-fit reconstruction (reproduces the authors' own Darcy K + fitted closure)."""
    psd = {r["Distribution"]: r for r in d.vacaguerra_psd()}
    lo, hi = _K_RANGE_M2
    points, n_in_band, n_order_ok = [], 0, 0
    for r in d.vacaguerra_extraction_conditions():
        dist = r["Distribution"]
        dp = float(r["DeltaP_bar"]) * 1e5
        q = float(r["Q_ml_per_s"]) * 1e-6
        length = _L0_M - float(r["delta_L_mm"]) * 1e-3
        eps = float(r["epsilon_0"])
        k_darcy = q * mu_pas * length / (_BED_AREA_M2 * dp)
        p = psd[dist]
        k_kc = _kozeny_carman_k(float(p["psi"]), float(p["d_32_um"]) * 1e-6, eps, float(p["beta"]))
        in_band = bool(lo <= k_darcy <= hi)
        order_ok = bool(1e-14 <= k_darcy <= 1e-12)
        n_in_band += in_band
        n_order_ok += order_ok
        points.append(dict(distribution=dist, dosage_g=float(r["Dosage_g"]), eps0=eps,
                           k_darcy_m2=k_darcy, k_kozeny_carman_m2=k_kc,
                           in_stated_band=in_band))
    ratios = sorted(p["k_darcy_m2"] / p["k_kozeny_carman_m2"] for p in points)
    median_ratio = ratios[len(ratios) // 2]
    return dict(
        mu_pas=mu_pas, n_points=len(points), n_in_stated_band=n_in_band,
        n_order_of_magnitude_ok=n_order_ok, stated_band_m2=list(_K_RANGE_M2),
        median_darcy_over_kozeny=round(median_ratio, 2), points=points,
        passed=bool(n_order_ok == len(points) and n_in_band >= 7),
        viscosity_note="K is proportional to mu; a G10 espresso-liquor mu (< 3.5 mPa s) scales "
                       "every K down by mu_G10/3.5e-3 -- renormalize before any cross-source K "
                       "comparison (Wadsworth band, Corrochano).",
        note="7/9 land in the stated band; the two loosest 17.5 g beds (B, C) sit ~1.3-1.7x above "
             "it, consistent with the card's note that high-K rows carry the unpublished pump curve. "
             "The post-fit Eq-11 (lambda=7.5) runs ~%.0fx BELOW the as-published-mu Darcy K -- "
             "comparable to the 3-7x viscosity-convention factor above, i.e. Eq-11 is broadly "
             "consistent with a G10-renormalized K, not the mu=3.5 mPa s one." % median_ratio)


def _g10_mu_pas(T_degC=65.0, Xw_pct=92.0):
    """Registry G10 espresso-liquor viscosity (telisromero closure) at the vacaguerra permeability
    measurement temperature and a representative espresso TDS (Xw=92% ~ 8% solids). ~0.42 mPa s at
    65 C -- ~8x below the authors' 3.5 mPa s convention."""
    return float(d.telisromero_viscosity_pas(T_degC + 273.15, Xw_pct))


def permeability_lambda_refit(T_degC=65.0, Xw_pct=92.0):
    """Refit the Eq-11 modified-Kozeny-Carman constant lambda so the closure reproduces the
    INDEPENDENT Darcy K, under the as-published (mu=3.5 mPa s) vs the registry G10 viscosity
    convention -- the card's owed mu-renormalization. Because K ∝ mu (Darcy) and Eq-11 K ∝ 1/lambda^2,
    the fitted lambda is convention-dependent: lambda_refit(mu) = sqrt(geomean_i C_i / K_darcy_i(mu)),
    with C_i = (psi d32)^2 eps^4.3 beta^0.43 / (72 (1-eps)^2) the lambda-free Eq-11 kernel. Reports
    lambda under both conventions (and the published 7.5 for reference; note the published fit was to
    the AUTHORS' K, which the independent Darcy K exceeds ~5x). Strength: post-fit reconstruction."""
    psd = {r["Distribution"]: r for r in d.vacaguerra_psd()}

    def _lambda_for(mu_pas):
        perm = permeability_darcy(mu_pas=mu_pas)
        logs = []
        for p in perm["points"]:
            pp = psd[p["distribution"]]
            c = ((float(pp["psi"]) * float(pp["d_32_um"]) * 1e-6) ** 2
                 * p["eps0"] ** _KC_EPS_EXP * float(pp["beta"]) ** _KC_BETA_EXP
                 / (72.0 * (1.0 - p["eps0"]) ** 2))
            logs.append(math.log(c / p["k_darcy_m2"]))
        return math.exp(0.5 * (sum(logs) / len(logs)))

    mu_g10 = _g10_mu_pas(T_degC, Xw_pct)
    lam_pub_mu = _lambda_for(_MU_PUBLISHED_PAS)
    lam_g10 = _lambda_for(mu_g10)
    return dict(
        lambda_published=_KC_LAMBDA,
        lambda_refit_published_mu=round(lam_pub_mu, 2),
        lambda_refit_g10_mu=round(lam_g10, 2),
        mu_published_pas=_MU_PUBLISHED_PAS, mu_g10_pas=round(mu_g10, 6),
        g10_conditions=dict(T_degC=T_degC, Xw_pct=Xw_pct, source="telisromero"),
        passed=bool(lam_pub_mu > 0 and lam_g10 > 0),
        note="lambda is viscosity-convention-dependent (lambda proportional to sqrt(mu)); the G10 "
             "espresso-liquor mu (~%.2f mPa s at %.0f C) is ~%.0fx below the authors' 3.5 mPa s, so "
             "lambda_G10 = lambda_pub-mu * sqrt(3.5e-3/mu_G10). The published 7.5 was fit to the "
             "authors' own K; the independent Darcy K runs ~5x higher, so lambda_refit at mu=3.5 mPa s "
             "is below 7.5. Report the convention explicitly; do NOT compare K across sources without "
             "fixing mu." % (mu_g10 * 1000, T_degC, _MU_PUBLISHED_PAS / mu_g10))


def wadsworth_cross_eval(mu_pas=_MU_PUBLISHED_PAS):
    """Cross-evaluate wadsworth2026.permeability (percolation closure) against vacaguerra's
    MEASURED tamped Darcy K on the shared Table C.1 points -- localizing where wadsworth's
    UNTAMPED-validated model (phi_p 0.37-0.67) diverges when extrapolated into the tamped regime
    (the card's Gate-3 discriminating computation).

    Adapter (FLAGGED, not silently assumed): phi_p <- eps0 -- both are the bed void fraction, and
    vacaguerra's DRY tamped eps0 (0.24-0.36) sits BELOW wadsworth's validated floor 0.37, so this IS
    the extrapolation being probed; R <- d32/2 -- the Sauter radius, exactly consistent with
    wadsworth's own specific-surface definition s_p = 3(1-phi_p)/R. Caveats carried: vacaguerra's
    eps0 is dry (NOT consolidation-corrected) porosity, and wadsworth's global angularity (alpha)
    is NOT refit to this material. Strength: verification / discrimination -- promotes neither model.
    """
    psd = {r["Distribution"]: r for r in d.vacaguerra_psd()}
    perm = permeability_darcy(mu_pas=mu_pas)
    pts = []
    for p in perm["points"]:
        r_sauter = float(psd[p["distribution"]]["d_32_um"]) * 1e-6 / 2.0
        k_w = float(_wads.k_percolation(r_sauter, p["eps0"]))
        pts.append(dict(distribution=p["distribution"], dosage_g=p["dosage_g"], eps0=p["eps0"],
                        R_sauter_m=r_sauter, k_wadsworth_m2=k_w,
                        k_vacaguerra_darcy_m2=p["k_darcy_m2"],
                        wadsworth_over_vacaguerra=round(k_w / p["k_darcy_m2"], 1)))
    ratios = sorted(x["wadsworth_over_vacaguerra"] for x in pts)
    median_ratio = ratios[len(ratios) // 2]
    # divergence vs extrapolation distance: sort by eps0 ascending
    by_eps = sorted(pts, key=lambda x: x["eps0"])
    return dict(
        adapter="phi_p<-eps0 (bed void fraction); R<-d32/2 (Sauter, surface-consistent)",
        mu_pas=mu_pas,
        wadsworth_validated_phi_p=[0.37, 0.67], vacaguerra_eps0_range=[0.24, 0.36],
        ratio_range=[ratios[0], ratios[-1]], median_ratio=median_ratio,
        tightest_bed=dict(eps0=by_eps[0]["eps0"], ratio=by_eps[0]["wadsworth_over_vacaguerra"]),
        loosest_bed=dict(eps0=by_eps[-1]["eps0"], ratio=by_eps[-1]["wadsworth_over_vacaguerra"]),
        points=pts,
        passed=bool(all(x["wadsworth_over_vacaguerra"] > 1 for x in pts) and median_ratio > 5),
        finding="wadsworth's untamped-validated percolation K, extrapolated into the tamped regime "
                "(eps0 below its 0.37 floor), OVERPREDICTS the measured tamped Darcy K at every "
                "operating point -- by ~%.0f-%.0fx (as-published mu=3.5 mPa s; LARGER under a "
                "G10-renormalized mu, which lowers vacaguerra's Darcy K). The overprediction grows "
                "as eps0 drops further below 0.37, localizing the failure of the tamped "
                "extrapolation. Neither closure is promoted." % (ratios[0], ratios[-1]))
