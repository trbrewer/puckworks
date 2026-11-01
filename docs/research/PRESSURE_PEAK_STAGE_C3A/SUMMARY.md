# PRESSURE-PEAK C3a: diagnostics

**capability demonstration, not validation; PHYSICAL_VALIDATION=NOT_ESTABLISHED; TARGET_EXPOSED.** Ungraded; 56 brews, 11 conditions.

Flow became true last in 4/5 one-bar brews, versus zero in every other condition. Their mean x1-minus-x0.5 onset shift was 4.676 s (largest other condition 2.123 s). The pre-declared reading is to **T3-O: carry into C3**. All five one-bar x1.5 onsets were undetected. This supports a detector-limited one-bar onset, not an identified physical onset law.

The x0.5 and x1.5 onset point fits give (Pd, P0, P0+Pd) = (3.648, 0.618, 4.266) bar; (7.342, -5.000, 2.342) bar. The x1.5 fit loses all one-bar targets and pins P0 at -5 bar; all twelve x1.5 fits hit a bound (eleven P0, one t0). The x0.5 fold holding out 1 bar also pins P0 at -5 bar. No training or held-out onset floors were active. Plug-in peaks keep saved flow parameters and do not replace flow refitting.

## Screens

**T2-F objective replay first:** saved 0.0719361259858887; recomputed 0.07193612598588868, agreeing at rtol=1e-12. This checks the C2 mask/grid before comparisons. In-sample screens can mislead and do not replace LOCO + refits.

| Screen | Objective | 100-s flow peak, bar | Low-pressure signed bias, g/s |
|---|---:|---:|---:|
| T3-D primary Pd | 0.073402615 | 7.05 | +0.202 |
| T3-D free Pd | 0.072937008 | 7.05 | +0.208 |
| T3-D x0.5 Pd | 0.073282284 | 7.05 | +0.203 |
| T3-R | 0.071933907 | 6.85 | +0.101 |

All T3-D objectives are worse than T2-F. The x0.5-Pd screen is plug-in only: Pd comes from a sensitivity detection, not the primary onset target. The free-Pd screen converges close to lam=Pd, requiring the series limit; P0_eff is undefined on its lam>=Pd side. No flow-screen parameter is bound-pinned and starts do not disagree under the declared checks.

T3-R fits tau=0.1944 s; its three starts give 0.19437 to 0.19440 s. The objective reduction is only 2.2e-06. Predicted flow at observed onset differs from T2-F by at most 0.0012 g/s across conditions. Tau=0 replays T2-F at rtol=1e-12.

## Restart

Observed last-five-second slopes rise in order: 1.833, 3.203, 3.543, 3.900, 4.255, 4.306 g/s. Four of five post-restart segments decline slightly within the segment, but the successive levels ratchet upward instead of returning to the first level. Under the pre-declared reading, this points toward an irreversible change or mixed behavior, not a sufficient reversible lag. The five intervening pauses add 0.567 to 1.231 g (0.104 to 0.199 g/s).

The replay uses q = 0 in pauses. In the line-pressure scenario, S tracks off-state line pressure while q = 0, which is a bound, not a model of the pause. Both fitted replays give only about 1.014 to 1.022 times the first slope. No tau in [0.1,1000] s reaches either observed ratio, 1.747 or 2.349. The largest attainable minimum/maximum restart ratios are 1.149/1.254 (zero off-state) and 1.103/1.159 (line off-state). One time constant does not serve traces and this qualitative restart record.

Cumulative analysis/check time through output: 44.17 s; serial, one BLAS thread, two-hour cap. [Full brew/fold/condition/episode results and CI fixtures](RESULT_TABLE.csv). Waszkiewicz et al., Zenodo 18046315, CC-BY-4.0. Diagnostics are ready for owner review. C3 is not authorized.
