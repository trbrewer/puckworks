# Independent read-only review

Fresh reviewer session `/root/independent_review`, started with no implementing
conversation history after the scientific bundle was complete. Review completed
2026-11-05 UTC. Reviewed head **07154ed258e84448cf1a639a8c44a1cf8226010e** against
base **4c5ebab5df79929813949df7113c21290dde40cc**.

**No actionable findings; no repairs requested.** The review remained read-only.
It ran three compact artifact checks directly without caches and independent
record arithmetic; it did not rerun fitting, simulations or the full suite.
PW and EWP worktrees remained clean. Required PR CI is a separate closeout check.

The reviewer independently checked:

- Capacity adapter, coordinates, exact boundary paths, and inherited J1 front,
  liquid recovery, chemistry and observation behavior.
- All 48 selected fits and 912 start records against matching A-J1, ordinary
  C3E, C2 Mc and regenerated deterministic Latin-hypercube starts; whole-condition
  exclusion and all 56 brews.
- All 48 frozen-zero parameter vectors, retained-start minima, 48/48 start
  disagreements, 11 better feasible A solutions, and the primary 3.5-bar training
  gain's sign change between numerical steps.
- Score arithmetic, censoring/detection counts, all 1,000 shared draws,
  16 aggregate intervals and 176 pressure intervals.
- Eight frozen external shapes, 108 markers/twelve series, amplitude/unit
  arithmetic, fixed S²/equal-series contrasts, and all 156 intervals from
  4,096 retained graphical readings.
- Summary claims, both figures, source/code/result/external hashes,
  **204.744269 measured core-hours**, and the diff's restricted scope.

The reviewer judged the negative scientific conclusion supported. Start
dependence, target exposure, opposing pressure-specific errors, graphical-reading
intervals and the unmeasured failed-preflight CPU are disclosed limitations,
not hidden defects. No scientific result or implementation changed after review;
the following commit adds this review record and closeout metadata only.
