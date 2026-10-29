# PRESSURE-PEAK Stage B0

**Recommendation: none — stop.** D1's point peak is 8 bar, outside 5–7 despite its interval touching 7. D2 retains a positive slope. D3's refit slope crosses zero; its five parameters also make it exploratory and ineligible. PR #388 was squash-merged after nine successful CI workflows.

**B0a: pressure-robust, window-sensitive, drift untestable.** Raw-pressure slope is −0.0655 [−0.0880, −0.0403] g/s/bar. Scaling all brewer-drop coefficients by ×0.8 or ×1.2 gives −0.0652 and −0.0650, both with intervals wholly negative. The nominal coefficient case gives −0.0651. Every pressure version peaks at 6 [5, 6] bar, so the raw-pressure stop rule is not triggered.

The 90–100 s window retains −0.0700 [−0.0913, −0.0463]. Literal 110–120 s gives +1.6003 [−0.1031, 4.9409]. Brew 9-1 shows pressure collapsing to 2.76 bar and a −111.34 g scale step near 119 s: shutdown plus probable cup removal/reset. The [paper](https://arxiv.org/html/2512.21528v1) specifies each run's last ten seconds, rather than fixed aligned 110–120 s. Actual terminal windows are also contaminated. The last ten seconds before detected terminal events retain −0.0681 [−0.0930, −0.0386], peak 6 [5, 6]. Scoring keeps the original endpoint and 56 brews.

The 61 raw files, headers, filenames and code comments were searched. Current [GitHub measurements](https://github.com/RadostW/espresso) match the originals; the release ZIP matches Zenodo's checksum. Only elapsed milliseconds were found; order, dates and temperature records remain unavailable. The 90°C viscosity reference is a constant. Drift cannot be tested. Filesystem modification times and restart were not used.

**Results:** basket pressure is primary as requested, although Stage A/SCI-MD-010 used line pressure. Its dependence on observed flow makes comparisons conditional. Slopes use unchanged 9/11/13 nominal conditions; peaks identify sampled nominal settings.

| Form | Pressure | RMSE (g/s) | Versus B1 | Refit slope interval (g/s/bar) | Refit peak interval (bar) | PASS |
|---|---|---:|---|---|---|:---:|
| D1 | Basket | 0.236 | BETTER | [-0.2146, -0.1716] | [7, 8] | N |
| D1 | Raw | 0.235 | TIE | [-0.1929, -0.1518] | [7, 8] | N |
| D2 | Basket | 0.214 | BETTER | [0.0077, 0.0205] | [8, 13] | N |
| D2 | Raw | 0.220 | TIE | [0.0038, 0.0385] | [9, 13] | N |
| D3 | Basket | 0.213 | BETTER | [-0.1317, 0.0077] | [8, 13] | N |
| D3 | Raw | 0.228 | TIE | [-0.0140, 0.0077] | [8, 13] | N |
| B1 | Basket | 0.306 | TIE | [-0.3861, -0.3195] | [8, 9] | N |
| B1 | Raw | 0.294 | TIE | [-0.3733, -0.3087] | [8, 9] | N |
| C4 | Basket | 0.206 | BETTER | [-0.1382, -0.1049] | [8, 8] | N |
| C4 | Raw | 0.216 | TIE | [-0.1102, -0.0760] | [8, 8] | N |

Intervals include fitting uncertainty: 200 brew resamples within conditions per row, refitting eleven folds each time, seed 20261029; none omitted. CSV includes no-refit intervals and parameters. Mean fold RMSE and paired comparisons retain Stage A's 1,000-resample procedure and 0.25 g/s tolerance. CAPABILITY is UNRESOLVED for D1/B1/C4 and NOT CAPABLE for D2/D3 under both pressure variables; none is CAPABLE.

D1 fixes Φ=0.122 and transient amplitude=1; first stable pressure proxies unobserved wetting-time pressure. D3 required an optimizer fallback. Full-history checks differ from the fitting grid by ≤0.00108 g/s, below 10% of affected errors/effects. All 28 focused/source/quick-gate checks passed. Charged fitting time was 42.1 minutes, including prior attempts conservatively.

**Solver implications:** no implementation is recommended. A future D1 implementation would touch the wetting-front/saturation transition and WP02 effective-permeability blocks in `espressoWholePullFoam.C`, plus `poroelasticCompaction.H`. It would need irreversible maximum dry-bed stress stored and locked at wetting, and delivered-mass memory distinct from dissolved-solids mass. D2 would add persistent jamming resistance. Brewer pressure loss would need predicted flow. None of these changes was made.

Only CC-BY-4.0 aggregates are committed: [Waszkiewicz et al. (2025), Zenodo 18046315](https://doi.org/10.5281/zenodo.18046315). Source locations and trace evidence are in `DATA_CHECKS.csv`. No successor task was started.
