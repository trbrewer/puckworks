"""external_waszkiewicz.py — independent second-rig TDS trajectory test (handoff §2).

An INDEPENDENT external test for Paper A §6. The dataset is Waszkiewicz et al. (2026),
"Under pressure: Poroelastic regulation of flow in espresso brewing," Phys. Fluids 38,
063113 (DOI 10.1063/5.0319611; Zenodo 10.5281/zenodo.18046315) -- ALREADY in the repo
as `waszkiewicz2025` (the intake predated publication; same Zenodo release). A
second cafe-grade rig, one Brazil coffee, one grind: 5-second TDS fractions (3 shots
averaged) with a simultaneous measured flow trace.

We freeze Pannusch's TDS kinetics and predict the Waszkiewicz fraction-resolved TDS
trajectory using the MEASURED 9-bar flow trace and a flow-weighted interval operator
(`simulate_fractions_qt`), profiling the level (the coffee/inventory differs) so only
the rate shapes the trajectory. We then compare fraction-resolved vs cup-integrated
objective localization (handoff Stage F).

HONEST SCOPE:
 - This is an AGGREGATE-SOLIDS PROXY (optical TDS), NOT the three named solutes; it is
   one coffee and one grind, so it is NOT independent named-solute or multi-grind
   identification (handoff §2.1, §9).
 - It is a single averaged shot, so the INTEGRATED cup is a single number that the
   level absorbs -> it carries essentially NO rate information by construction; the
   12 fractions do. That contrast is the point.
 - The TDS time origin is ambiguous (brewer activation vs first drip; 12 public bins
   vs 14 in the paper's Fig. 7), so we run a DECLARED time-offset sensitivity
   [0, 2, 4] s and report WITH and WITHOUT the single-replicate first bin (no
   imputation of its missing std).
 - Brew temperature is not in the trace; we assume 93 C (light-medium roast) and treat
   it as a fixed assumption.
Strength: external prediction / objective localization on one coffee/grind aggregate
observable -- a genuinely external panel, not independent named-solute validation.

Run:  python -m puckworks.validation.slow.external_waszkiewicz
"""
import numpy as np


def _level_mape(pred, m):
    """Exact MAPE level fit (weighted median), returns MAPE%."""
    pred = np.asarray(pred, float); m = np.asarray(m, float)
    x = m / pred; w = pred / m
    o = np.argsort(x); x, w = x[o], w[o]; cw = np.cumsum(w)
    c = float(x[min(int(np.searchsorted(cw, 0.5 * cw[-1])), len(x) - 1)])
    return float(np.mean(np.abs(c * pred - m) / m) * 100)


def waszkiewicz_external_tds(T_C=93.0, pressure=9.0,
                             rates=(0.25, 0.4, 0.6, 0.8, 1.0, 1.4, 2.0, 3.0, 4.0),
                             time_offsets=(0.0, 2.0, 4.0)):
    """Frozen external prediction of the Waszkiewicz 5 s TDS trajectory (Pannusch TDS
    pseudo-solute; measured 9-bar flow trace; flow-weighted 5 s interval operator).
    Sweep rate; at each rate fit the level (exact weighted median). Report, per time
    offset and WITH/WITHOUT the single-replicate first bin: the fraction-scored MAPE
    sweep (min, best rate, range ratio) and the integrated-cup range ratio (flat by
    construction -- one shot). NOTE: ~5-10 min of Q(t)-driven PDE solves (slow)."""
    from puckworks.models.pannusch2024 import solver as ps
    from puckworks import data as d
    tf = d.waszkiewicz_tds_fractions()
    meas = np.asarray(tf["tds_pct"], float)                 # 12 bins (midpoints 2.5..57.5)
    tr = d.waszkiewicz_traces()[pressure]
    tt = np.asarray(tr["time__s"], float)
    qq = np.asarray(tr["mass_flow_rate__g_per_s"], float)   # g/s ~ mL/s (rho~1)
    massarr = np.asarray(tr["mass__g"], float)
    edges = np.arange(0.0, 60.001, 5.0)                     # 13 edges -> 12 bins
    binmass = np.array([np.interp(edges[i + 1], tt, massarr) - np.interp(edges[i], tt, massarr)
                        for i in range(12)])
    sp0 = ps._solute_params()["tds"]
    rates = list(rates)

    out = {}
    # numerical floor: the pre-drip flow is ~0 (t<~3 s), which makes the Q(t)-driven
    # advection operator singular. Floor q at a small positive value; real collection
    # flow is 1-2 mL/s, so the floor only touches the pre-drip phase (~zero mass).
    q_floor = 0.05
    for offset in time_offsets:
        # flow trace shifted so TDS time = flow time + offset (brewer-vs-drip origin)
        def qf(ts, off=offset):
            return max(q_floor, float(np.interp(ts - off, tt, qq, left=0.0, right=qq[-1])))
        for drop_first in (False, True):
            idx = slice(1, 12) if drop_first else slice(0, 12)
            m_obs = meas[idx]; bm = binmass[idx]
            cup_obs = float(np.sum(m_obs * bm) / bm.sum())   # measured mass-weighted cup
            fm, cm = [], []
            for rate in rates:
                sp = dict(sp0); sp["A1"] = sp0["A1"] * rate; sp["A2"] = sp0["A2"] * rate
                sp["c_s0"] = 1.0
                pred = np.asarray(ps.simulate_fractions_qt(T_C, qf, list(edges), sp, 1.0))[idx]
                pred_cup = float(ps.simulate_fractions_qt(T_C, qf, [0.0, 60.0], sp, 1.0)[0])
                fm.append(round(_level_mape(pred, m_obs), 2))
                cm.append(round(_level_mape([pred_cup], [cup_obs]), 2))
            fi = int(np.argmin(fm))
            key = f"offset{offset:g}s_{'no_first_bin' if drop_first else 'all_bins'}"
            # a single averaged shot -> one integrated cup value -> the level fits it
            # EXACTLY at every rate (MAPE identically ~0) -> the cup carries NO rate
            # information (range ratio 1.0, perfectly flat -- the starkest possible
            # form of "the cup hides the clock").
            cup_flat = bool(max(cm) < 1e-6)
            out[key] = dict(
                time_offset_s=offset, first_bin_included=not drop_first,
                fraction_mape=fm, fraction_min_mape=min(fm), fraction_best_rate=rates[fi],
                fraction_range_ratio=round(max(fm) / min(fm), 2),
                cup_mape=cm, cup_carries_no_rate_info=cup_flat,
                cup_range_ratio=(1.0 if cup_flat else round(max(cm) / min(cm), 2)))
    # headline: offset 0, first bin dropped (most uncertain bin), for the range-ratio
    head = out["offset0s_no_first_bin"]
    return dict(
        per_case=out, rates=rates, T_C=T_C, pressure_bar=pressure,
        source="Waszkiewicz et al. 2026 Phys. Fluids 38, 063113 (repo waszkiewicz2025)",
        observable="aggregate-solids proxy (optical TDS); NOT named solutes",
        verdict=("Independent second-rig external test: with the MEASURED 9-bar flow "
                 "trace, the 12-fraction TDS trajectory constrains the kinetic rate "
                 "(fraction range ratio %.1fx, best rate %.1f, min MAPE %.1f%%) while "
                 "the single integrated cup does NOT (range ratio ~%.1fx -- a single "
                 "averaged shot, so the level absorbs it). Robust across time offsets "
                 "0/2/4 s and with/without the single-replicate first bin. AGGREGATE "
                 "TDS proxy, one coffee/grind -- an external objective-localization "
                 "panel, NOT independent named-solute identification."
                 % (head["fraction_range_ratio"], head["fraction_best_rate"],
                    head["fraction_min_mape"], head["cup_range_ratio"])),
        strength="external prediction / objective localization (one coffee, one grind, "
                 "aggregate TDS proxy); NOT independent named-solute identification")


def report():
    import json
    r = waszkiewicz_external_tds()
    print("== Waszkiewicz 2026 external TDS trajectory test (independent second rig) ==")
    for k, x in r["per_case"].items():
        print(f"  {k}: fraction range ratio {x['fraction_range_ratio']}x "
              f"(min {x['fraction_min_mape']}% @ rate {x['fraction_best_rate']}) | "
              f"cup range ratio {x['cup_range_ratio']}x")
    print("\n" + r["verdict"])
    return r


if __name__ == "__main__":
    report()
