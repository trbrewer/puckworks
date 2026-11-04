#!/usr/bin/env python3
"""Reporting-only supplement from committed shape fits; no new fits or data reads."""
import csv
from collections import defaultdict
from itertools import product
import numpy as np

from puckworks.analysis.cor15_shape_001 import read_inputs, write_csv, OUTPUT


def main():
    contract, coords = read_inputs()
    support = []
    for r in coords:
        a = contract['axes'][r['panel']]
        bounds = []
        for value, anchor0, anchor1, span in [('x_px','x0','x1',1.8e-5),('y_px','y0','y1',450000)]:
            vals = [((float(r[value])+d*float(r['mean_guard_px'])-(a[anchor0]+e)) /
                     (a[anchor1]+f-a[anchor0]-e)*span) for d,e,f in product((-1,1),repeat=3)]
            bounds.append((min(vals),max(vals)))
        qlo,qhi = bounds[0]
        status = ('BELOW' if qhi < 3e-6 else 'ABOVE' if qlo > 1.7e-5 else
                  'WITHIN' if qlo >= 3.4e-6 and qhi <= 1.6e-5 else 'AMBIGUOUS')
        support.append(dict(series=r['series'],point_id=r['point_id'],Q_reading_lo_m3_s=qlo,
            Q_reading_hi_m3_s=qhi,P_reading_lo_Pa=bounds[1][0],P_reading_hi_Pa=bounds[1][1],
            conditional_thesis_calibration_support=status,
            qualification='exact_calibration_reuse_in_journal_unverified'))
    write_csv(OUTPUT/'CALIBRATION_SUPPORT.csv',support)

    import json
    result=json.loads((OUTPUT/'RESULT.json').read_text())
    models=list(csv.DictReader((OUTPUT/'MODELS.csv').open()))
    contrasts=list(csv.DictReader((OUTPUT/'CONTRASTS.csv').open()))
    draws = defaultdict(list)
    with (OUTPUT/'READING_REALIZATIONS.csv').open() as f:
        for r in csv.DictReader(f):
            if r['series'] != 'POOLED':
                fa, l0 = float(r['FA_MSE_m6_s2']), float(r['L0_MSE_m6_s2'])
                draws[r['series']].append([fa-l0, np.sqrt(fa)-np.sqrt(l0)])
    dimensional = []
    for c in contrasts:
        s = c['series']
        m = {r['model']: r for r in models if r['series'] == s}
        l0, fa = float(m['L0']['rmse']), float(m['FA']['rmse'])
        di = np.quantile(draws[s], [.025, .975], axis=0)
        dimensional.append(dict(series=s, L0_RMSE_m3_s=l0, FA_RMSE_m3_s=fa,
            FA_minus_L0_MSE_m6_s2=fa**2-l0**2, FA_minus_L0_RMSE_m3_s=fa-l0,
            paired_MSE_difference_reading_lo_m6_s2=di[0, 0],
            paired_MSE_difference_reading_hi_m6_s2=di[1, 0],
            paired_RMSE_difference_reading_lo_m3_s=di[0, 1],
            paired_RMSE_difference_reading_hi_m3_s=di[1, 1]))
    write_csv(OUTPUT/'PAIRED_DIMENSIONAL.csv', dimensional)
    rows=[]
    for c in contrasts:
        s=c['series']; m={r['model']:r for r in models if r['series']==s}
        fmt=lambda x:f'{float(x)*1e6:.3f}'
        rows.append(f"| {s} | {fmt(m['L0']['rmse'])} / {fmt(m['FA']['rmse'])} | "
                    f"{fmt(m['L0']['lowest_signed_residual'])} / {fmt(m['FA']['lowest_signed_residual'])} | "
                    f"{float(c['L2_m']):.3f} / {float(c['FA_grid_m']):.3f} | "
                    f"{float(c['D_series']):.4f} [{float(c['D_series_reading_lo']):.4f}, {float(c['D_series_reading_hi']):.4f}] |")
    text=f'''# PW-COR15-SHAPE-001 — frozen D0 shape comparison

G1 / SOURCE_INTERNAL / TARGET_EXPOSED / DESCRIPTIVE / PHYSICAL_VALIDATION=NOT_ESTABLISHED

**FA loses to L0 in all 12 series: pooled D={result['central_D']:.5f} [{result['D_reading_interval'][0]:.5f}, {result['D_reading_interval'][1]:.5f}].** Positive favors L0. Both have **one amplitude per series** (12 fits each). D uses fixed central S². Intervals: central 95% of 4096 paired reading realizations with shared panel calibration, **not population confidence intervals**.

RMSE and lowest-pressure residual (predicted−observed): **mL/s = 10⁻⁶ m³/s**. Every contrast uses matched observations.

| Series (grind–kg/m³) | RMSE L0 / FA | Lowest residual L0 / FA | Data m / FA-grid m_FA | Paired contrast [reading interval] |
|---|---:|---:|---:|---:|
'''+'\n'.join(rows)+'''

Outcome: resolved curvature in the declared graphical-reading analysis, predominantly sub-linear. The L2 exponent interval lies below 1 in nine series, above 1 in D-360 and D-400, and includes 1 in C-360. Frozen D0 has higher RMSE than L0 in all twelve series, and every paired m−m_FA reading interval is negative. This establishes failure of the specified shape transfer under the declared mapping, not absence of all low-pressure suppression or identification of a fresh-bed mechanism. Experimental spread, instrument/correction uncertainty and descending-sweep history remain separate qualifications.

**Diagnostics (two parameters each):** L1 P0=−0.906 to +0.254 bar (nine negative offsets). L1/L2 contain L0: lower residual alone establishes no new law. No boundary fits; one central minimum per scalar profile.

FA-S's Pstar = 1.0–3.0 bar is compensation within the restricted function (n, Pd frozen), not an identified compaction scale. FA-S fits worse than L0 in 11/12 and worse than L2 in 12/12 series (central RMSEs).

**Qualifications:** 108 means; three beds/series. A-480 has seven markers (lowest 1.412 bar); C/D-360 have ten despite nine described steps. No bed trajectories reconstructed. SD, reading and instrument/correction uncertainty remain separate. Recovery absorbed into amplitude, pressure-coordinate substitution, descending-sweep history and unverified thesis-calibration reuse limit transfer.

The 64–96% lowest-point underprediction is not a common-pressure comparison: A-480's lowest retained point is about 1.41 bar; the others 0.23–0.42 bar.

**Table 2:** The inverse-normalization check gives plausible implied-viscosity magnitudes, but absolute permeability reconstruction remains unresolved. Support for the digitization comes from the marker overlay, axis checks and recorded coordinates, rather than this inverse calculation.

[Figure](comparison.svg) · [readings/SD](DIGITIZED.csv) · [fits/units](MODELS.csv) · [signed residuals](RESIDUALS.csv) · [dimensional contrasts](PAIRED_DIMENSIONAL.csv) · [D/exponents](CONTRASTS.csv) · [Table 2](TABLE2_CHECK.csv) · [source qualifications](SOURCE_RECONCILIATION.md) · [verification](VERIFICATION.md).
'''
    (OUTPUT/'SUMMARY.md').write_text(text)


if __name__=='__main__':
    main()
