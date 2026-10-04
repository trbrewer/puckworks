# MODEL-PANNUSCH2024-FLOW-TEMP-FV-003 results

**VERIFIED_ON_DECLARED_CASES**. G2 / NUMERICAL_METHOD_CHANGE; RESEARCH_ONLY.
PHYSICAL_VALIDATION=NOT_ESTABLISHED. Software QA, hosted CI and independent exact-head review are separate receipts.

**The 5e-4 joint-linear temporal target is new**, including frozen-step interior observations.
It is one-tenth of the .005 spatial allowance and does not amend or inherit 002's tighter
1e-6 temperature-only qualification. 001 INCOMPLETE and 002 declared-case VERIFIED are preserved.

## Required gates

| Gate | Result |
|---|---|
| full_coverage | PASS |
| positivity | PASS |
| conservation | PASS |
| numerical_flux | PASS |
| prescribed_flux | PASS |
| volume | PASS |
| compatibility | PASS |
| joint_steps | PASS |
| temporal_accuracy | PASS |
| spatial_accuracy | PASS |
| observers | PASS |
| repeatability | PASS |

Unavailable or failed executions: none.

## Numerical resources

| Group | Executions | Charged wall seconds |
|---|---:|---:|
| A | 8 | 235.815767 |
| B | 8 | 177.645861 |
| C | 8 | 295.211915 |
| D | 4 | 167.142555 |
| E | 1 | 38.376922 |
| F | 3 | 10.060074 |

Total: 32 trajectories, 924.253093 execution seconds.
Ceilings: 36 executions including four corrections; 1800 aggregate numerical seconds; 120 seconds per launch.
One numerical worker/BLAS thread. Auxiliary reductions and final totals are in RESOURCES.json; software QA is separate.

## Sampled admissibility and independent accounting

Exact-arithmetic positivity/conservation follows from paired nonnegative donor transitions and zero generator column sums.
Floating-point checks sample primary endpoints, diagnostic/observer points and GL4/GL8 nodes; no all-time certificate is claimed.
Inventory is reconstructed from physical fields and independently reconstructed phase capacities. Mout is independently evolved;
neither Mout nor either flux is repaired by a balance complement. RESULTS.json retains initial offsets and signed residual ranges.

| Maximum fixed-scale error | Observed | Allowance |
|---|---:|---:|
| Inventory / M* | 8.31329903e-14 | 1e-08 |
| Prescribed volume / V* | 1.24335112e-16 | 1e-12 |
| Numerical GL8 minus Mout / M* | 1.02721798e-13 | 1e-06 |
| Numerical GL8 minus GL4 / M* | 1.11895028e-15 | 1e-06 |
| Prescribed GL8 minus Mout / M* | 6.83785033e-07 | 0.0005 |
| Prescribed GL8 minus GL4 / M* | 1.11895028e-15 | 1e-06 |

## Constant-Q compatibility

Each channel uses its fixed C*, M* or V* scale; allowance 1e-12. Primary endpoints and common interior observations are included.

| Comparison | Liquid | Fine | Coarse | Outlet | Mout | Volume | Fractions |
|---|---:|---:|---:|---:|---:|---:|---:|
| caffeine | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| trigonelline | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 5CQA | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| tds | 0 | 0 | 0 | 0 | 0 | 0 | 0 |

## Joint steps versus independent ordered exponentials

Each channel uses its fixed C*, M* or V* scale; allowance 1e-08. Primary endpoints and common interior observations are included.

| Comparison | Liquid | Fine | Coarse | Outlet | Mout | Volume | Fractions |
|---|---:|---:|---:|---:|---:|---:|---:|
| caffeine | 1.77635684e-14 | 1.89149108e-14 | 4.26819074e-14 | 1.75990909e-14 | 3.68907769e-14 | 0 | 6.42490176e-14 |
| trigonelline | 7.75831269e-14 | 2.54370908e-14 | 4.82244846e-14 | 7.75831269e-14 | 1.60652115e-14 | 0 | 7.73711511e-14 |
| 5CQA | 2.10995836e-14 | 1.82482886e-14 | 3.56411886e-14 | 1.31159574e-14 | 4.03321181e-14 | 0 | 8.19390926e-14 |
| tds | 2.46737917e-14 | 2.49861182e-14 | 5.77803983e-14 | 2.46737917e-14 | 3.25564425e-14 | 0 | 4.87229305e-14 |

## Joint-linear default comparisons

Each channel uses its fixed C*, M* or V* scale; allowance 0.0005. Primary endpoints and common interior observations are included.

| Comparison | Liquid | Fine | Coarse | Outlet | Mout | Volume | Fractions |
|---|---:|---:|---:|---:|---:|---:|---:|
| up.finer | 8.11192998e-05 | 4.3771166e-07 | 8.10143784e-08 | 4.68206844e-07 | 1.09378986e-07 | 0 | 1.10946626e-08 |
| up.Radau | 8.1970955e-05 | 4.90203847e-07 | 7.63580815e-08 | 4.58697863e-07 | 1.09013156e-07 | 1.1504692e-16 | 1.47928882e-08 |
| down.finer | 6.95772175e-05 | 4.35750154e-07 | 2.17639931e-07 | 1.00626359e-06 | 1.7083107e-07 | 0 | 1.72966361e-08 |
| down.Radau | 7.15990433e-05 | 4.80370717e-07 | 2.03789351e-07 | 9.94496673e-07 | 1.70819365e-07 | 1.24335112e-16 | 2.30622193e-08 |

## Smooth refinement against actual-time Radau

Radau independently assembles concentration balances and uses actual T/Q with segmented carryover: rtol=2e-12,
concentration atol=2e-14*C*, Mout atol=2e-14*M*, max_step=.02. Shared source parameters/geometry/closures are disclosed;
reference history clocks, union segmentation and volume arithmetic are independent. No candidate generator/RHS is used.

| Case | h | Liquid | Fine | Coarse | Outlet | Mout | Fractions | Prescribed flux discrepancy / M* |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| up.coarse | 0.04 | 0.000243288185 | 1.98344876e-06 | 3.08851634e-07 | 1.81455381e-06 | 4.35870109e-07 | 5.91711587e-08 | 4.43286231e-07 |
| up.default | 0.02 | 8.1970955e-05 | 4.90203847e-07 | 7.63580815e-08 | 4.58697863e-07 | 1.09013156e-07 | 1.47928882e-08 | 1.10836014e-07 |
| up.finer | 0.01 | 2.73223447e-05 | 1.22164624e-07 | 1.90315887e-08 | 1.14518513e-07 | 2.72573766e-08 | 3.69822559e-09 | 2.77102799e-08 |
| down.coarse | 0.04 | 0.000212814345 | 1.95148794e-06 | 8.64003477e-07 | 3.96233631e-06 | 6.81679772e-07 | 9.22472688e-08 | 6.83785033e-07 |
| down.default | 0.02 | 7.15990433e-05 | 4.80370717e-07 | 2.03789351e-07 | 9.94496673e-07 | 1.70819365e-07 | 2.30622193e-08 | 1.70944818e-07 |
| down.finer | 0.01 | 2.38610872e-05 | 1.1721572e-07 | 4.91287537e-08 | 2.52494455e-07 | 4.27106845e-08 | 5.76558324e-09 | 4.27365985e-08 |

The .04 level is diagnostic for field accuracy; default/finer and default/Radau are gated.
Resolved aggregate errors and prescribed-flux discrepancies must decrease; comparison floor 1e-10.
No measured temporal order is claimed. Each fraction error and both trend checks are retained in RESULTS.json.
Every fraction maximum/gate includes adjacent fraction bounds and derived [7,19], [20,30], [5,25] windows;
individual derived-window errors are retained separately, using the same declared comparison allowances.

## Spatial refinement

Fine fields are conservatively restricted by paired cell averages; weights are A*dz*[alpha_l,as1,phi_v2*as2].
All channels and both mesh pairs are reported. Only N400 to N800 is gated at .005 on each fixed scale.

| Comparison | Fractions / C* | Mout / M* | Weighted field / M* |
|---|---:|---:|---:|
| up.200_to_400 | 0.00137597352 | 0.000494887372 | 0.00145327345 |
| up.400_to_800 | 0.000712332557 | 0.00024797077 | 0.000963323751 |
| up.ratios (resolved difference ratios, not order proof) | 1.931644859546176 | 1.9957488241405381 | 1.5086033617708514 |
| trigonelline.200_to_400 | 0.000877391711 | 0.000719918546 | 0.00214682802 |
| trigonelline.400_to_800 | 0.000439181339 | 0.000451685902 | 0.00142245672 |
| trigonelline.ratios (resolved difference ratios, not order proof) | 1.9977891439925421 | 1.593847720326012 | 1.5092396085801536 |

## Variable-flow passive benchmark

Private zero-exchange seam; exact translated compact sine-squared cell averages and outlet mass.
Times come from the independently inverted prescribed volume at s/L=[0,.25,.5,.75,1.25].

| N | Liquid L1/C0 at the five samples | Final remaining + absolute outlet error / M0 |
|---|---|---:|
| 32 | 1.3986208e-17, 0.0340355034, 0.041121421, 0.0297237714, 0.000704092253 | 0.00281636901 |
| 64 | 7.80625564e-18, 0.0177028849, 0.0223897411, 0.0164391355, 5.7877776e-05 | 0.000231511104 |
| 128 | 6.07153217e-18, 0.00902680432, 0.0117155674, 0.00869012938, 1.63282129e-06 | 6.53128518e-06 |

Mesh-pair orders at the three nonzero pre-exit samples: [[0.9430559622029503, 0.8770522771194563, 0.8544827470292279], [0.9716972457849198, 0.9344110160856718, 0.919684871331454]].
Initial-time rounding error is reported, with no order inferred from zero error. N128 pre-exit L1 allowance .05;
both mesh-pair orders must be >=.8; postexit remaining plus outlet error allowance .05.

## Observers, repeatability and limits

Volume-weighted recombination, crossing-knot [7,19]/[5,25] and delayed [20,30] windows use retained observations, with no additional trajectories.
Exact-environment repeat arrays: BITWISE IDENTICAL.
Focused tests cover rejection, immutability, strict JSON, finite prefixes, tiny unresolved fractions and deliberate defects; see QA.json.
Detailed arrays/logs remain outside Git; report mode reproduces these summaries without simulations.
Source/configuration/producer identities and preservation proofs are in SOURCE_IDENTITIES.json and execution receipts.
HISTORY_REUSE.json binds original/current hashes and unchanged campaign arithmetic after the reviewed extreme-clock input correction.
The fixed matrix is numerical evidence only. Arbitrary runtime calls remain accuracy NOT_ASSESSED.
No empirical/profile-benefit/taste/native-MATLAB/coupling/physical-validation claim or automatic successor follows.

Pannusch et al., DOI 10.17632/y2tz67f6ry.1; CC-BY-NC-3.0 source-derived outputs; first-party software licensing separate.
