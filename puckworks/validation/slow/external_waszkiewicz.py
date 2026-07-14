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


def _isotonic_nondecreasing(y):
    """L2 projection onto the nearest NONDECREASING sequence (pool-adjacent-violators).

    A cumulative *collected* mass is physically monotone, but the measured Waszkiewicz
    cumulative-mass trace has small local decreases (sensor noise; ~58 in the 9-bar
    trace). PAVA gives the closest monotone reconstruction so its consecutive
    differences (bin masses) are nonnegative. No SciPy dependency.
    """
    y = np.asarray(y, float)
    val = []      # block means
    size = []     # block sizes
    for yi in y:
        val.append(float(yi)); size.append(1)
        while len(val) > 1 and val[-2] > val[-1]:     # pool the two out-of-order blocks
            nv = (val[-1] * size[-1] + val[-2] * size[-2]) / (size[-1] + size[-2])
            ns = size[-1] + size[-2]
            val.pop(); size.pop()
            val[-1] = nv; size[-1] = ns
    out = np.empty(len(y)); i = 0
    for v, s in zip(val, size):
        out[i:i + s] = v; i += s
    return out


def observed_bin_masses(tt, massarr, edges, offset):
    """Physically admissible 5 s observed-bin masses (review MC29 / A-03).

    Naively differencing the raw (non-monotone) cumulative-mass trace produced a
    NEGATIVE collected-mass bin under the 4 s alignment offset, i.e. a negative
    cup-average weight. We first project the cumulative mass onto the nearest
    nondecreasing sequence (:func:`_isotonic_nondecreasing`), then difference the
    offset-shifted 5 s edges — so every bin mass is ``>= 0`` by construction and the
    bins telescope to the total collected mass over the window. Returns
    ``(binmass[len(edges)-1], diagnostics)`` and asserts nonnegativity.
    """
    massmono = _isotonic_nondecreasing(massarr)
    bm = np.array([np.interp(edges[i + 1] - offset, tt, massmono)
                   - np.interp(edges[i] - offset, tt, massmono)
                   for i in range(len(edges) - 1)])
    total = float(np.interp(edges[-1] - offset, tt, massmono)
                  - np.interp(edges[0] - offset, tt, massmono))
    diag = dict(bin_mass_min_g=float(bm.min()),
                nonnegative=bool(bm.min() >= -1e-9),
                total_collected_g=round(total, 4),
                mass_balance_resid_g=float(abs(bm.sum() - total)),
                n_raw_cumulative_decreases=int(np.sum(np.diff(np.asarray(massarr)) < 0)))
    assert bm.min() >= -1e-9, (
        "negative observed bin mass %.6g g at offset %.3g s (monotone reconstruction "
        "failed)" % (float(bm.min()), offset))
    return bm, diag


def waszkiewicz_external_tds(T_C=93.0, pressure=9.0,
                             rates=(0.25, 0.4, 0.6, 0.8, 1.0, 1.4, 2.0, 3.0, 4.0),
                             time_offsets=(0.0, 2.0, 4.0), q_floor=0.05):
    """Target-profiled external SHAPE test on the Waszkiewicz 5 s TDS trajectory (review
    A3-06/A3-25: NOT a frozen external prediction -- a target-specific level is profiled at
    each rate, so this localizes temporal SHAPE, not absolute concentration). Pannusch TDS
    pseudo-solute; measured 9-bar flow trace; flow-weighted 5 s interval operator.
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
    sp0 = ps._solute_params()["tds"]
    rates = list(rates)

    out = {}
    # numerical floor: the pre-drip flow is ~0 (t<~3 s), which makes the Q(t)-driven
    # advection operator singular. Floor q at a small positive value; real collection
    # flow is 1-2 mL/s, so the floor only touches the pre-drip phase (~zero mass).
    # q_floor is a declared parameter so its influence can be swept (review A2-13b).
    for offset in time_offsets:
        # flow trace shifted so TDS time = flow time + offset (brewer-vs-drip origin)
        def qf(ts, off=offset):
            return max(q_floor, float(np.interp(ts - off, tt, qq, left=0.0, right=qq[-1])))
        # review MAJ-16(1): the observed-cup bin masses MUST use the SAME shifted time
        # origin as the model flow -- collect the mass in flow-time [edge-offset] for
        # each fixed 5 s TDS bin, not the unshifted trace. review MC29/A-03: use a
        # MONOTONE cumulative-mass reconstruction so no bin mass (cup weight) is negative.
        binmass, mass_diag = observed_bin_masses(tt, massarr, edges, offset)
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
                cup_range_ratio=(1.0 if cup_flat else round(max(cm) / min(cm), 2)),
                mass_operator=mass_diag)    # A-03: nonnegative bin masses + mass balance
    # headline: offset 0, first bin dropped (most uncertain bin), for the range-ratio
    head = out["offset0s_no_first_bin"]
    return dict(
        per_case=out, rates=rates, T_C=T_C, pressure_bar=pressure,
        source="Waszkiewicz et al. 2026 Phys. Fluids 38, 063113 (repo waszkiewicz2025)",
        observable="aggregate-solids proxy (optical TDS); NOT named solutes",
        verdict=("Target-profiled external SHAPE test (review A3-06/A3-23): with the "
                 "MEASURED 9-bar flow trace, the 12-fraction TDS trajectory produces a "
                 "SHALLOW rate-dependent MAPE minimum (range ratio only %.1fx, best rate "
                 "%.1f) but the minimum MAPE stays HIGH at ~%.1f%% -- so this is evidence "
                 "that temporal shape moves the objective more than a single aggregate "
                 "under the tested operator, NOT a validated rate estimate. The single "
                 "integrated cup is flat (range ratio ~%.1fx) ALGEBRAICALLY -- one scalar "
                 "paired with one profiled level is exactly matchable at every rate -- so "
                 "this is not an empirical no-information finding. A target-specific level "
                 "is profiled, so absolute concentration is NOT tested; aggregate TDS "
                 "proxy, one coffee/grind, NOT named-solute identification."
                 % (head["fraction_range_ratio"], head["fraction_best_rate"],
                    head["fraction_min_mape"], head["cup_range_ratio"])),
        strength="external-data shape-objective localization (target-specific level "
                 "profiled; shallow high-residual minimum); a target-profiled shape test, "
                 "NOT a frozen absolute-concentration prediction and NOT named-solute "
                 "identification")


def waszkiewicz_sensitivity(temps=(89.0, 91.0, 93.0, 95.0),
                            floors=(0.02, 0.05, 0.10),
                            rates=(0.4, 0.6, 0.8, 1.0, 1.4, 2.0, 3.0)):
    """Review A2-13b: the external panel makes two DECLARED nuisance assumptions -- the
    brew temperature (not in the trace; assumed 93 C) and the pre-drip numerical flow
    floor. Sweep both and report whether the localization conclusion (the 12-fraction
    trajectory constrains the rate; the single cup does not) is invariant. For each
    (T, floor) we take the headline case (offset 0 s, first bin dropped) on a coarse
    7-rate grid and record the best rate, fraction range ratio, min MAPE, and that the
    cup still carries no rate information. NOTE: ~10-20 min of Q(t) PDE solves (slow;
    NOT a CI gate)."""
    cells = []
    for T in temps:
        for fl in floors:
            r = waszkiewicz_external_tds(T_C=T, rates=rates, time_offsets=(0.0,),
                                         q_floor=fl)
            h = r["per_case"]["offset0s_no_first_bin"]
            cells.append(dict(
                T_C=T, q_floor=fl, best_rate=h["fraction_best_rate"],
                fraction_range_ratio=h["fraction_range_ratio"],
                fraction_min_mape=h["fraction_min_mape"],
                cup_carries_no_rate_info=h["cup_carries_no_rate_info"]))
    best_rates = sorted({c["best_rate"] for c in cells})
    rrs = [c["fraction_range_ratio"] for c in cells]
    mins = [c["fraction_min_mape"] for c in cells]
    # the localization is "invariant" if EVERY cell still shows the fraction trajectory
    # discriminating (range ratio comfortably >1) while the cup never does.
    all_localize = all(c["fraction_range_ratio"] > 1.3 for c in cells)
    cup_never = all(c["cup_carries_no_rate_info"] for c in cells)
    return dict(
        cells=cells, temps=list(temps), floors=list(floors), rates=list(rates),
        best_rate_set=best_rates, best_rate_spread=max(best_rates) - min(best_rates),
        fraction_range_ratio_min=min(rrs), fraction_range_ratio_max=max(rrs),
        fraction_min_mape_min=min(mins), fraction_min_mape_max=max(mins),
        localization_invariant=bool(all_localize and cup_never),
        verdict=("Nuisance-assumption sensitivity (temperature 89-95 C x flow floor "
                 "0.02-0.10): across all %d cells the 12-fraction trajectory keeps "
                 "discriminating the rate (range ratio %.1f-%.1fx, min MAPE %.1f-%.1f%%, "
                 "best rate in {%s}) while the single integrated cup NEVER does. The "
                 "localization conclusion is %s to the brew-temperature and flow-floor "
                 "assumptions; the best-rate POINT shifts by %.1f across the grid, which "
                 "is expected (temperature rescales the kinetic level, not the "
                 "cup-vs-fraction contrast)."
                 % (len(cells), min(rrs), max(rrs), min(mins), max(mins),
                    ", ".join(f"{b:g}" for b in best_rates),
                    "INVARIANT" if (all_localize and cup_never) else "SENSITIVE",
                    max(best_rates) - min(best_rates))),
        strength="external-panel robustness (declared nuisance assumptions); NOT "
                 "independent named-solute identification")


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
