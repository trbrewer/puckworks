"""Residual autocorrelation on the waszkiewicz flow-trace time series.

Per CC's investigation: serial autocorrelation is only meaningful where there is
a time axis. The RSM residuals are ~15 INDEPENDENT design points (no time order
-> autocorrelation undefined). The waszkiewicz traces are 1000-point time series
per pressure -> this is the correct home for a Durbin-Watson / ACF analysis.

What it tests: the dynamic model Q(t) (poroelastic Eq.18, RC-3a empirical
sigmoid) is fit/reconstructed against the measured flow trace. If the residuals
(measured - predicted) are serially UNcorrelated, the model has captured the
temporal structure; strong positive autocorrelation means systematic
lack-of-fit (a shape the model misses), not just noise.

DIAGNOSTIC strength. Durbin-Watson near 2 => little autocorrelation; << 2 =>
positive serial correlation (the usual lack-of-fit signature). Reported per
pressure so a single bad pressure does not hide behind a pooled statistic.
The infiltration transient (t < ~15 s, per gate_waszkiewicz_dynamic_9bar) is
excluded so the metric reflects the extraction regime the model targets.
"""
import numpy as np
from puckworks import data as d


def _durbin_watson(res):
    res = np.asarray(res, float)
    return float(np.sum(np.diff(res)**2) / np.sum(res**2))


def _acf(res, nlags=20):
    res = np.asarray(res, float) - np.mean(res)
    denom = np.sum(res**2)
    return [1.0] + [float(np.sum(res[k:]*res[:-k])/denom) for k in range(1, nlags+1)]


def residual_autocorr_waszkiewicz(t_cut_s=15.0, nlags=20, decimate_dt_s=1.0):
    """Per-pressure DW + ACF of the RC-3a dynamic-model residuals.

    Zero extra parameters: (P_c,Q_c) from the published static fit + the solids
    sigmoid, exactly as gate_waszkiewicz_dynamic_9bar. Residual = measured
    mass_flow_rate - model Q(t), over t >= t_cut_s (skip infiltration transient).

    CRITICAL sampling note: the raw trace is ~10 Hz (dt~0.1 s). On a slow process
    the MEASURED signal already has lag-1 autocorr ~1.0, so DW on the native
    series is dominated by sample spacing, not model fit (it will read ~0 for any
    model). We therefore DECIMATE to `decimate_dt_s` (default 1 s, a physically
    meaningful interval for an espresso shot) before computing DW/ACF, so the
    statistic tests MODEL STRUCTURE rather than sampling density. Raw-series DW is
    also reported as `durbin_watson_raw` for transparency.
    """
    from puckworks.models.waszkiewicz2025 import poroelastic as wz
    tr = d.waszkiewicz_traces()
    P_c, Q_c = wz.published_calibration()
    k_s, l_s, m_s = wz._solids_params()
    dose = d.waszkiewicz_constants()["dose__g"]
    pressures = sorted(k for k in tr if k != "columns")
    out = {}
    for P in pressures:
        t = np.asarray(tr[P]["time__s"], float)
        meas = np.asarray(tr[P]["mass_flow_rate__g_per_s"], float)
        pred = wz.q_dynamic(t, P, P_c, Q_c, k_s, l_s, m_s, dose)
        sel = t >= t_cut_s
        if sel.sum() < 5:
            continue
        res_raw = meas[sel] - pred[sel]
        dw_raw = _durbin_watson(res_raw)
        # decimate to decimate_dt_s before the meaningful DW/ACF
        tt = t[sel]
        step = max(1, int(round(decimate_dt_s / np.median(np.diff(tt)))))
        res = res_raw[::step]
        if len(res) < 5:
            res = res_raw                                # too short to decimate
        dw = _durbin_watson(res)
        acf = _acf(res, nlags=min(nlags, len(res)//2))
        band = 1.96/np.sqrt(len(res))                   # 95% white-noise band
        n_signif = int(sum(abs(a) > band for a in acf[1:]))
        out[float(P)] = dict(
            n_points_raw=int(sel.sum()), n_points_decimated=len(res),
            decimate_dt_s=decimate_dt_s,
            durbin_watson=round(dw, 3), durbin_watson_raw=round(dw_raw, 4),
            acf_lag1=round(acf[1], 3),
            acf_lag5=round(acf[5], 3) if len(acf) > 5 else None,
            n_lags_outside_95pct_band=n_signif,
            resid_std_g_per_s=round(float(res_raw.std()), 4),
            signal_std_g_per_s=round(float(meas[sel].std()), 4),
            interpretation=("near-white after decimation" if dw > 1.6 else
                            "residual serial correlation persists at 1 s spacing "
                            "(genuine slow lack-of-fit)"))
    return out


def summary(t_cut_s=15.0):
    """One-line-per-pressure table + a pooled read."""
    r = residual_autocorr_waszkiewicz(t_cut_s)
    dws = [v["durbin_watson"] for v in r.values()]
    return dict(per_pressure=r,
                mean_durbin_watson=round(float(np.mean(dws)), 3),
                n_pressures=len(r),
                pooled_read=("residuals broadly near-white; model captures the "
                             "temporal shape" if np.mean(dws) > 1.6 else
                             "systematic positive autocorrelation remains; the "
                             "dynamic model misses a temporal feature (report as "
                             "honest lack-of-fit, not noise)"),
                caveat="DW is a diagnostic; the RC-3a model uses zero free params "
                       "here, so residual structure is expected and informative, "
                       "not a pass/fail")


if __name__ == "__main__":
    import json
    print(json.dumps(summary(), indent=2))
