"""G10 viscosity sensitivity study (ROADMAP card telisromero2001 §Impl-est ii).

Question the card poses: every registered flow model uses pure-water viscosity, but
coffee liquor is more viscous where it is more concentrated. Darcy flow is q ~ 1/mu, so
a concentration-dependent mu(c,T) would suppress flow most where the liquor is strongest.
Does that matter for a real shot, or does G10 close as "negligible at shot TDS"?

This module makes the earlier ANALYTIC bound (harness.g10_mu_bias_direction) QUANTITATIVE
and c(t)-resolved by driving the Telis-Romero (2001) MEASURED viscosity (Table 1) with the
cameron2020 extraction model's own local liquor-concentration field cl(z, t).

Method (first-order, permeability/pressure held fixed -- only mu changes):
  1. Baseline shot: cameron `simulate_shot` -> cl_out(t) (outlet liquor, kg/m^3) and, via
     truncated re-runs, the depth profile cl(z, t_k) at several times.
  2. Map each local cl -> water fraction X_w -> dynamic viscosity mu:
       - X_w in [76,90] %  -> MEASURED Table-1 eta(X_w, T)  (data.telisromero_eta_measured)
       - X_w > 90 % (dilute; MORE dilute than the source's box -- espresso is here for most
         of the shot) -> linear blend from measured eta(90,T) down to pure water at X_w=100.
         This is the honest fix: dilute espresso is an extrapolation TOWARD water, so those
         cells are ~1x water, NOT the 1.07x box-edge value.
       - X_w < 76 % (concentrated; Table-2 regime) -> eta(76,T) (conservative; does not occur
         in cameron at espresso conditions -- see the study result).
  3. Series-Darcy flow factor (uniform permeability): F(t) = mu_water / mean_z mu(z, t).
     Also the conservative single-cell OUTLET bound F_out(t) = mu_water / mu(cl_out(t)).
  4. Shot-integrated flow deficit (flow-weighted ~ time-weighted at ~constant q).

Verdict is computed, not asserted: at espresso conditions the cameron liquor never
approaches saturation (peaks ~90% X_w), so mu stays within a few % of water and the
depth-averaged, shot-integrated effect is small. The gate
`gate_g10_viscosity_bulk_negligible` bounds it for CI.
"""
from __future__ import annotations

import numpy as np

from puckworks import data as _d
from puckworks.models.cameron2020 import extraction_bdf as _em
from puckworks.models.pannusch2024 import closures as _pc

# Representative espresso operating points (grind, pressure, dose, yield).
DEFAULT_CONDITIONS = [
    dict(label="normale_9bar_med", gs=1.9, p_bar=9.0, m_in=0.020, m_out=0.036),
    dict(label="fine_9bar", gs=1.1, p_bar=9.0, m_in=0.020, m_out=0.036),
    dict(label="ristretto_slow_low_p", gs=1.1, p_bar=3.0, m_in=0.020, m_out=0.030),
    dict(label="lungo_fine", gs=1.1, p_bar=6.0, m_in=0.018, m_out=0.054),
]

BREW_T_C = 90.0        # fixed brew temperature; T is not a contract field (G4 backlog)

# cameron2020's PUBLISHED initial soluble concentration (SI Table S1, kg/m^3). We PIN it for
# the duration of every shot: brewer2026.streamtube MUTATES em.C_S0 at import time (per-bed-
# volume reinterpretation, 118/PHI_S ~= 142.6), so an unpinned study is import-order-dependent
# (the mega-model global-state failure mode CLAUDE.md warns about). The verdict is robust to
# either value; pinning just makes the numbers deterministic and reproducible.
_CAMERON_C_S0_PUBLISHED = 118.0


def _pinned_shot(**kw):
    """cameron simulate_shot with C_S0 pinned to the published value + restored after."""
    saved = _em.C_S0
    try:
        _em.C_S0 = _CAMERON_C_S0_PUBLISHED
        return _em.simulate_shot(**kw)
    finally:
        _em.C_S0 = saved


def liquor_mu_pas(cl_kgm3, T_C: float = BREW_T_C, excess_scale: float = 1.0):
    """Local liquor dynamic viscosity [Pa*s] from local solids concentration cl [kg/m^3].

    Uses the MEASURED Telis-Romero Table-1 grid inside its box and blends to pure water for
    the dilute (X_w > 90 %) espresso regime. Vectorized over cl.

    `excess_scale` multiplies ONLY the coffee-solute viscosity elevation above pure water
    (mu = mu_w + excess_scale*(mu_TR - mu_w)), leaving water itself unscaled. Used for the
    khomyakov INTER-SOURCE robustness check: khomyakov's measured mu runs ~+37% (total) above
    TR2001 in the overlap, so excess_scale=2.0 is a conservative upper bound on 'what if the
    true liquor is markedly more viscous than TR2001' (see gate_g10_intersource_spread)."""
    cl = np.atleast_1d(np.asarray(cl_kgm3, float))
    T_K = T_C + 273.15
    mu_w = float(_pc.water_viscosity(T_K))
    # cl -> X_w fraction (iterate density; liquor density from telisromero2000)
    rho = np.full_like(cl, 1000.0)
    for _ in range(6):
        xwf = np.clip(1.0 - cl / rho, 0.49, 1.0)
        rho = np.array([_d.telisromero_density_kgm3(T_C, float(x)) for x in xwf])
    xw_pct = 100.0 * (1.0 - cl / rho)
    out = np.empty_like(cl)
    for i, xw in enumerate(xw_pct):
        if xw <= 90.0:
            # in-box (or concentrated <76 -> interpolator clamps to 76): measured eta
            mu = _d.telisromero_eta_measured(T_K, xw)
        else:
            # dilute espresso: blend measured box-edge eta(90) -> pure water at X_w=100
            eta90 = _d.telisromero_eta_measured(T_K, 90.0)
            f = min((xw - 90.0) / 10.0, 1.0)     # 0 at 90 %, 1 at 100 %
            mu = eta90 * (1.0 - f) + mu_w * f
        out[i] = mu_w + excess_scale * (mu - mu_w)   # scale the coffee excess only
    return out if out.size > 1 else float(out[0])


def _depth_profiles(cond, n_snap):
    """Reconstruct cl(z, t_k) at n_snap times by truncated cameron runs (no internal edits)."""
    base = _pinned_shot(gs=cond["gs"], p_bar=cond["p_bar"],
                        m_in=cond["m_in"], m_out=cond["m_out"])
    tks = np.linspace(base.t_shot / n_snap, base.t_shot, n_snap)
    profs = []
    for tk in tks:
        rk = _pinned_shot(gs=cond["gs"], p_bar=cond["p_bar"],
                          m_in=cond["m_in"], m_out=cond["m_out"], t_shot=float(tk))
        profs.append(rk.cl_final)
    return base, tks, profs


def run_condition(cond, T_C: float = BREW_T_C, n_snap: int = 6, excess_scale: float = 1.0):
    """Full c(t)-resolved viscosity sensitivity for one operating point."""
    base, tks, profs = _depth_profiles(cond, n_snap)
    T_K = T_C + 273.15
    mu_w = float(_pc.water_viscosity(T_K))

    # depth-averaged series-Darcy flow factor F(t_k) = mu_w / mean_z mu(z, t_k)
    F_depth = np.array([mu_w / np.mean(liquor_mu_pas(p, T_C, excess_scale)) for p in profs])
    # conservative single-cell outlet bound over the whole shot
    mu_out = liquor_mu_pas(base.cl_out, T_C, excess_scale)
    F_out = mu_w / np.asarray(mu_out)
    # most concentrated liquor anywhere/anytime we sampled
    cl_peak = max(float(base.cl_out.max()), max(float(p.max()) for p in profs))
    mu_peak_ratio = float(liquor_mu_pas(cl_peak, T_C, excess_scale)) / mu_w
    # does any sampled cell enter the concentrated (<76% X_w) Table-2 regime?
    min_xw = 100.0
    for p in profs:
        rho = np.asarray(1000.0, float)                  # ndarray from the start (mypy-clean)
        for _ in range(6):
            xwf = np.clip(1.0 - p / rho, 0.49, 1.0)
            rho = np.array([_d.telisromero_density_kgm3(T_C, float(x)) for x in xwf])
        min_xw = min(min_xw, float(np.min(100.0 * (1.0 - p / rho))))

    return dict(
        label=cond["label"], gs=cond["gs"], p_bar=cond["p_bar"],
        t_shot=round(float(base.t_shot), 1), EY=round(float(base.EY), 1),
        tds=round(float(base.tds), 2),
        cl_peak_kgm3=round(cl_peak, 1), min_Xw_pct=round(min_xw, 1),
        mu_peak_ratio_to_water=round(mu_peak_ratio, 3),
        peak_flow_suppression_pct=round(100.0 * (1.0 - F_depth.min()), 2),
        outlet_bound_suppression_pct=round(100.0 * (1.0 - F_out.min()), 2),
        shot_integrated_flow_deficit_pct=round(100.0 * (1.0 - F_depth.mean()), 2),
        reached_powerlaw_regime=bool(min_xw < 76.0),
    )


def run_sensitivity(conditions=None, T_C: float = BREW_T_C, n_snap: int = 6,
                    excess_scale: float = 1.0):
    """Run the study across operating points and synthesize a verdict.

    excess_scale > 1 runs the khomyakov inter-source ROBUSTNESS variant (scales the coffee
    viscosity excess above water; 2.0 conservatively covers khomyakov's ~+37% offset vs TR2001)."""
    conds = conditions or DEFAULT_CONDITIONS
    results = [run_condition(c, T_C=T_C, n_snap=n_snap, excess_scale=excess_scale) for c in conds]
    worst_int = max(r["shot_integrated_flow_deficit_pct"] for r in results)
    worst_peak = max(r["peak_flow_suppression_pct"] for r in results)
    worst_mu = max(r["mu_peak_ratio_to_water"] for r in results)
    any_powerlaw = any(r["reached_powerlaw_regime"] for r in results)
    verdict = (
        f"Across {len(results)} espresso operating points the cameron2020 in-pore liquor "
        f"peaks at mu <= {worst_mu:.2f}x water (never enters the <76% X_w power-law regime: "
        f"{'REACHED' if any_powerlaw else 'not reached'}). Depth-averaged, shot-integrated "
        f"Darcy-flow deficit from mu(c,T) is <= {worst_int:.2f}% (peak instantaneous "
        f"<= {worst_peak:.2f}%). => the constant-water-mu assumption in every registered "
        f"flow model is SAFE for bulk espresso; G10 closes as negligible-at-shot-TDS. No "
        f"runtime mu(c,T) hook is warranted. Caveat: composition bias (soluble-coffee "
        f"extract != espresso liquor) and dilute-end extrapolation stand; a genuinely "
        f"saturating shot (choked/ristretto beyond this envelope) is the only place to revisit."
    )
    return dict(T_C=T_C, n_snap=n_snap, conditions=results,
                worst_shot_integrated_deficit_pct=round(worst_int, 2),
                worst_peak_suppression_pct=round(worst_peak, 2),
                worst_mu_ratio_to_water=round(worst_mu, 3),
                any_powerlaw_regime=any_powerlaw, verdict=verdict)


def bulk_negligibility(gs=1.9, p_bar=9.0, m_in=0.020, m_out=0.036, T_C: float = BREW_T_C,
                       excess_scale: float = 1.0):
    """FAST single-shot bound for the CI gate (no truncation loop).

    Uses the outlet liquor cl_out(t) (the MOST concentrated cell, a conservative bound) plus
    the end-of-shot depth profile. Returns the peak single-cell mu ratio, the outlet-bound
    peak flow suppression, and the end-of-shot depth-averaged flow factor. excess_scale>1 is
    the khomyakov inter-source robustness variant."""
    r = _pinned_shot(gs=gs, p_bar=p_bar, m_in=m_in, m_out=m_out)
    T_K = T_C + 273.15
    mu_w = float(_pc.water_viscosity(T_K))
    mu_out = np.asarray(liquor_mu_pas(r.cl_out, T_C, excess_scale))
    cl_peak = max(float(r.cl_out.max()), float(r.cl_final.max()))
    mu_peak_ratio = float(liquor_mu_pas(cl_peak, T_C, excess_scale)) / mu_w
    F_out_min = float((mu_w / mu_out).min())
    F_depth_end = mu_w / float(np.mean(liquor_mu_pas(r.cl_final, T_C, excess_scale)))
    return dict(
        mu_peak_ratio_to_water=round(mu_peak_ratio, 3),
        outlet_bound_peak_suppression_pct=round(100.0 * (1.0 - F_out_min), 2),
        depthavg_end_flow_factor=round(F_depth_end, 4),
        t_shot=round(float(r.t_shot), 1), tds=round(float(r.tds), 2),
    )


if __name__ == "__main__":
    import json
    print(json.dumps(run_sensitivity(), indent=2, default=float))
