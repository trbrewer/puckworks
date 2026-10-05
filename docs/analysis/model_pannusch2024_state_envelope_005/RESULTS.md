# Declared 005 numerical verification results

G0 / NO_GOVERNING_PHYSICS_CHANGE / RESEARCH_ONLY. PHYSICAL_VALIDATION=NOT_ESTABLISHED.

**Declared numerical verification passed.** Overall engineering acceptance remains conditional on the separately recorded software QA and hosted CI; ordinary draft-PR review is separate. No declared full-mesh check failed. Subsequent author review found and corrected
an extreme-dynamic-range upper-bound scaling underflow. Four reserved response
executions verified the original responses, intervals, gaps and six states
exactly; see [CORRECTION.json](CORRECTION.json). The eight original fresh replay
receipts remain at their original producer, not relabelled as new executions.

Caffeine, grind1.7, N400, default h=.02 s, absolute clock/window [7,17] s. Both prescribed collection volumes are 2.16e-5 m^3. The synthetic U, epsilon=1e-9 kg, and delta=1e-6 kg were declared before this comparison.

| Query | Outer interval (kg) | Maximum extremum gap (kg) | Decision |
|---|---|---|---|
| A | [2.67072164263e-05, 7.3401986337e-05] | 4.54378e-14 | NOT_A_DECISION_QUERY |
| B | [2.63995614636e-05, 7.29711439721e-05] | 4.54371e-14 | NOT_A_DECISION_QUERY |
| A-minus-B | [-9.53471518632e-08, 8.57447041541e-07] | 9.07609e-14 | NO_MATERIAL_DIFFERENCE_THROUGHOUT_SET |

A-minus-B is **NO_MATERIAL_DIFFERENCE_THROUGHOUT_SET**. Fresh common-state witnesses also support an opposite-sign reversal relative to zero, below the declared material margin. No profile is required to win. A concentration interval is [1.23644520492,3.39824010820] kg/m^3; B is [1.22220191961,3.37829370241] kg/m^3. These are not percent TDS.

## Primary witnesses

All six states pass strict original-coordinate constraints after explicit bounded repairs (7–14 updates). Original vectors/residuals, repaired mass changes and recomputed objectives are retained in RESULTS.json. Each individual envelope witness has one fresh forward; each contrast witness has two from the identical state.

| Query/extremum | Liquid / fine / coarse inventory (kg) | Response prediction (kg) | Largest replay discrepancy (kg) |
|---|---|---|---|
| A minimum | 8e-06 / 1e-05 / 6.2e-05 | 2.67072164491e-05 | 3.3881e-21 |
| A maximum | 3e-05 / 4.91763638e-05 / 4.08236362e-05 | 7.34019863143e-05 | 1.3553e-20 |
| B minimum | 8e-06 / 1e-05 / 6.2e-05 | 2.63995614864e-05 | 1.5247e-19 |
| B maximum | 3e-05 / 4.91763638e-05 / 4.08236362e-05 | 7.29711439494e-05 | 3.1171e-19 |
| A-minus-B minimum | 1.05923028e-05 / 4.91763638e-05 / 2.02313334e-05 | -9.53471064825e-08 | 1.3553e-20 |
| A-minus-B maximum | 2.67586708e-05 / 1.14610859e-05 / 8e-05 | 8.57446996161e-07 | 2.7783e-19 |

The individual response allowance is at most 2.269033e-14 kg on this U; the contrast retains both histories and subtraction allowance, 4.538020e-14 kg. Primal/dual and summation/conversion allowances are separate in each extremum. Forward replay arithmetic is separately reported and is not treated as a uniform whole-set discretization bound. The source parent remains accuracy NOT_ASSESSED.

## Every temporal level

The .02 s result remains primary. Finer rows are sensitivity-only optimization candidates, without extra primary-witness trajectories.

| h (s) | A interval (kg) | B interval (kg) | Direct A-minus-B interval (kg) |
|---|---|---|---|
| 0.02 | [2.67072164263e-05, 7.3401986337e-05] | [2.63995614636e-05, 7.29711439721e-05] | [-9.53471518632e-08, 8.57447041541e-07] |
| 0.01 | [2.6707218161e-05, 7.34019858777e-05] | [2.63995618238e-05, 7.29711405927e-05] | [-9.53488549789e-08, 8.57453377839e-07] |
| 0.005 | [2.67072185857e-05, 7.34019857718e-05] | [2.63995619049e-05, 7.29711397568e-05] | [-9.53492986691e-08, 8.57454979823e-07] |

## Whole-set sensitivity

Each row optimizes both signs of the response difference over the original U. The mesh lift allocates each N400 phase mass equally to its two N800 children. These are fixed-operator differences and refinement sensitivity, not rigorous bounds on an unknown continuum solution.

| Comparison | Functional | max_U abs(difference) interval (kg) |
|---|---|---|
| h=0.02 vs 0.01 | A | [4.52754803234e-12, 4.62854015173e-12] |
| h=0.02 vs 0.01 | B | [5.81151550095e-12, 5.91250521516e-12] |
| h=0.02 vs 0.01 | A-minus-B | [6.29782386313e-12, 6.49980382958e-12] |
| h=0.01 vs 0.005 | A | [1.07866539939e-12, 1.21035374735e-12] |
| h=0.01 vs 0.005 | B | [1.39966033478e-12, 1.53135603534e-12] |
| h=0.01 vs 0.005 | A-minus-B | [1.46800866774e-12, 1.73139175522e-12] |
| N400 vs lifted N800; h=.02 | A | [3.32765000854e-08, 3.32766258358e-08] |
| N400 vs lifted N800; h=.02 | B | [3.24174876531e-08, 3.24176134028e-08] |
| N400 vs lifted N800; h=.02 | A-minus-B | [1.36014232057e-09, 1.36039381975e-09] |

## Work and timing

28/28 planned large executions plus 4/4 reserved correction response passes:
32/32 hard total, comprising 22 response passes and 10 forward trajectories
(eight primary witness replays plus baseline/final timing). Exactly 104728
exponential actions and 44 LP calls. Aggregate numerical wall time
104.016653/1800 s; peak RSS 172368 KiB. Threads: OpenBLAS/OMP/MKL/HiGHS all 1.
No failed full-mesh launch or hidden full-mesh CI trajectory. The separate
small two-cell author-review defect probe is recorded in QA.json.

Same-machine wrapper timings include correctness checks and serialization/validation overhead: unchanged forward 7.652437 s baseline / 7.701574 s final; representative A response 1.464614 / 1.467481 s; A envelope optimization 0.047087 / 0.045481 s. The final forward delivery, response vector and envelope interval repeat exactly. These are timings, not a speedup claim.

Full arrays, full trajectories/logs and evidence paths remain outside Git. Compact array identities and all extrema/optimization/replay facts are in [RESULTS.json](RESULTS.json); execution receipts are in [RESOURCES.json](RESOURCES.json). The [pre-execution identities](PRE_EXECUTION.json) bind the original numerical producer code and specification at commit
`ef413fc6cd7182ef86450ab711e110985be9cb24`. The guard-only correction has its own
source identities and equality receipt; RESULTS.json is not restamped.

004 retains resolved_temporal_decrease=FAIL and IMPLEMENTED_QUALIFICATION_INCOMPLETE. Its programme was not rerun or restamped. No physical validation, measured-state recovery, universal profile superiority, taste conclusion, data-exhaustion claim or successor.
