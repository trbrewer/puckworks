# PRESSURE-PEAK Stage A

**Recommend C4: whole-bed pressure-set compaction plus W-H2 delivered-mass evolution.** It passes with the lowest held-out error. This is a conditional research lead; no Stage B work was started.

**Step 0: the peak survives.** Across 56 brews, the ≥9-bar slope is **−0.0655 [−0.0880, −0.0403] g/s/bar**. The sampled peak is **6 [5, 6] bar**. Every leave-one-brew-out slope remains negative (−0.0763 to −0.0567), with peaks at 5–6 bar. Per-pressure means and 95% intervals are included in the CSV’s B1 reference row.

Dose (18.50 ± 0.05 g), grind (1.9), basket, tamp and coffee origin/roaster are fixed by the published protocol. No pressure-linked change is documented; **dates, chronological order, randomization and batch IDs are missing**, so confounding cannot be ruled out. Alignment offsets vary (1.53–11.53 s), but aligned and original-clock 90–100 s checks retain negative slopes near −0.070. All brews cover the endpoint. The contaminated 110–120 s window is unsuitable. One duplicate is removed; published means reproduce within 0.000005 g/s. Four author-excluded records were inspected; their two high-pressure brews have lower flows, reinforcing the downturn. Exclusions remain unchanged.

**Step 1:** local quasi-static compaction is disqualified: `Q ∝ ∫₀ᴾ k(σ)dσ` cannot decrease when k ≥ 0. None of C1–C4 reduces to that form. C1 uses whole-bed pressure and can peak. C2 accumulates resistance with delivered flow; it has no positive steady equilibrium and remains monotone at a common age under constant pressure. C3 uses global pressure memory; C4 adds delivered-mass memory. Both approach C1 at constant pressure after relaxation/evolution.

**Results:** exact SCI-MD-010 folds, endpoint and training weights; all stored B1 predictions reproduced. RMSE is the mean of 11 fold RMSEs in g/s; CSV also reports the historical normalized metric. Intervals use 1,000 resamples, seed 20261029: paired condition-then-brew draws for losses, within-condition brew draws for slopes/peaks, without refitting. They exclude parameter-fitting and protocol uncertainty.

| Form | RMSE [95% interval], g/s | Versus B1 | High-pressure slope | Restart | Pass |
|---|---|---|---:|---|:---:|
| C1 exponential | 0.288 [0.192, 0.384] | TIE | −0.0105 | Cannot say | Y |
| C1 power-law limit | 0.288 [0.192, 0.384] | TIE | −0.0105 | Cannot say | Y |
| C2, m=1 | 0.430 [0.295, 0.565] | WORSE | +0.1549 | Lower: inconsistent | N |
| C2, m=2 | 0.377 [0.261, 0.487] | TIE | +0.1088 | Lower: inconsistent | N |
| C3 relaxation | 0.289 [0.192, 0.384] | TIE | −0.0103 | Cannot say | Y |
| C4 combined | 0.215 [0.132, 0.290] | TIE | −0.0908 | Higher: directional consistency | Y |
| B1 reference | 0.294 [0.200, 0.394] | TIE | −0.3400 | Cannot say | N* |
| W-H0A reference | 0.428 [0.289, 0.562] | WORSE | +0.1399 | Cannot say | N* |

*References are not Stage B candidates. Capability is **UNRESOLVED** for C1, C3, C4 and B1; **NOT CAPABLE** for C2 and W-H0A. None is CAPABLE or BETTER. TIE follows the owner's ±0.25 g/s rule. C1/C3 predict sampled peaks at 9 [9, 9] bar, C4/B1 at 8 [8, 8], and C2/W-H0A at 13 [13, 13], versus observed 6 [5, 6]. Every slope interval is in the CSV; C4's is [−0.0915, −0.0902].

C4 uses the lowest-stored-loss evolving form, W-H2, with transient amplitude fixed at one: three fitted parameters. C1 power approaches the exponential limit; finite Pc and n are unidentified. An artificial search ceiling was removed by representing that limit explicitly. C3 instantly recompacts after restart. C1/C3 supply no lasting matched-pressure increase. C4 predicts higher flow through continued delivery, **not a separate benefit of pausing**. The observed restart increase, 1.82 to 3.23–4.31 g/s, remains unexplained in magnitude and cause. C4's smaller error and closer slope make it the strongest lead, despite its misplaced peak.

All fits have ≤3 parameters. Fitting took under one minute, including the boundary correction; grid refinement changes flow by ≤0.0000011 g/s. Synthetic recovery and monotonicity tests pass. Only CC-BY-4.0 aggregates are committed: Waszkiewicz et al. (2025), [Zenodo](https://doi.org/10.5281/zenodo.18046315). Useful sources: `puckworks/data/waszkiewicz2025/`, its identical `/home/tim/Documents/data/` copy, original/restart/excluded records in `/home/tim/wasz-terminal-mass-evidence/upstream/`, the paper in `/home/tim/Documents/data/pdf/06_other_papers/06_other_papers/`, and read-only EWP's SCI-MD-010 contracts/results and dynamic-hydraulics results/core. No restricted-number file was needed.
