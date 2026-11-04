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

**Shape:** FA underpredicts each lowest retained flow by 64–96%. Data m=0.645–1.279 versus matched m_FA=1.529–2.270; every paired m−m_FA reading interval is negative. C-360's m interval includes 1. These Q-space exponents summarize each retained grid; 1 and m_FA are references, not bands. Resolved departures from linearity differ from D0's strong suppression; they do not identify pressure-only permeability or fresh-bed entry.

**Diagnostics (two parameters each):** L1 P0=−0.906 to +0.254 bar (nine negative offset diagnostics); L2 exponents above; FA-S Pstar=1.021–3.041 bar versus frozen 24.397. L1/L2 contain L0: lower residual alone establishes no new law. No fits selected a boundary; central scalar profiles each had one minimum.

**Qualifications:** 108 means; three beds/series. A-480 has seven markers (lowest 1.412 bar); C/D-360 have ten despite nine described steps. No bed trajectories reconstructed. SD, reading and instrument/correction uncertainty remain separate. Recovery absorbed into amplitude, pressure-coordinate substitution, descending-sweep history and unverified thesis-calibration reuse limit transfer.

**Table 2:** consolidated-height normalization implies μ=0.263–0.416 mPa·s; source numerical viscosity/individual heights are unrecovered, so absolute reconstructed k remains unavailable. This is normalization, not viscosity estimation or validation. Poor transfer rejects this frozen shape/mapping, not all form A parameterizations; coffee, preparation and measurement remain competing explanations.

[Figure](comparison.svg) · [readings/SD](DIGITIZED.csv) · [fits/units](MODELS.csv) · [signed residuals](RESIDUALS.csv) · [dimensional contrasts](PAIRED_DIMENSIONAL.csv) · [D/exponents](CONTRASTS.csv) · [Table 2](TABLE2_CHECK.csv) · [source qualifications](SOURCE_RECONCILIATION.md) · [verification](VERIFICATION.md).
'''
    (OUTPUT/'SUMMARY.md').write_text(text)


if __name__=='__main__':
    main()
