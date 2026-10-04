# MODEL-PANNUSCH2024-POSITIVE-FV-002 results

**Declared-case numerical qualification: VERIFIED.** G2 / NUMERICAL_METHOD_CHANGE.
PHYSICAL_VALIDATION=NOT_ESTABLISHED. Software QA, hosted CI and independent review
are separate handoff/PR receipts. No production adoption, empirical claim or successor.
Parent 001 remains INCOMPLETE with every original threshold, receipt and outcome preserved.

The fixed 28 executions completed without a failed/partial trajectory or full-bed replay.
The report was reproduced byte-identically from saved arrays; report mode launched no
simulation. CONTRACT and CASES were frozen at `a7b06cb` before numerical producer
`6311be0220d9cf1f62c10be9ad5d2813aabba654`. SOURCE_IDENTITIES binds unchanged
numerical blocks; REPORTING_CORRECTION discloses a reducer-only failure-path change.

## Mathematical structure, positivity and accounting

The paired donor/receiver construction proves nonnegative off-diagonals and zero
column sums for admitted positive coefficients. Independent small-mesh balance,
dense-exponential, exchange, capacity and sign tests pass. Exact exponential updates
preserve positivity and inventory in exact arithmetic; the following are sampled
floating-point checks, not an all-time or rigorous floating-point certificate.

| Check | Observed normalized extremum | Allowance |
|---|---:|---:|
| Candidate phase minimum (including passive inert zeros) | 0 | >= -1e-10 |
| Source-case phase minimum | 2.21814647e-05 | >= -1e-10 |
| Independent cell-average inventory + evolved Mout | 1.06091131e-13 | 1e-08 |
| Inventory at GL4/GL8 samples | 1.06091131e-13 | 1e-08 |
| Independent cumulative GL8 outlet flux versus Mout | 7.76394185e-14 | 1e-06 |
| Cumulative GL8 versus GL4 | 3.62386524e-16 | 1e-06 |
| Hydraulic volume versus Q*(t-t0) | 0 | 1e-06 |

All candidate trajectories also pass the scaled nonnegative and nondecreasing Mout checks.
RESULTS.json retains each case's signed inventory ranges/final residual, initial FV sum
and rounding offset. No balance complement, clipping, correction flux or normalization
was used. Checks include primary endpoints, midpoints, the <=0.0125 s grid, requested
early/knot observers and every GL4/GL8 sample. Quadrature splits every numerical step.

## Temporal accuracy

All gated channels pass 1e-6 using fixed C*, M* and V*. The default is N=400,
h_max=.02 s. Coarse/default is diagnostic; default/finer and default/reference are gated.
Reference Radau independently assembles concentration balances with actual T(t),
rtol=2e-12 and scaled atol=2e-14; candidate propagation uses frozen midpoint masses.

| Comparison | Liquid/C* | Fine/C* | Coarse/C* | Mout/M* | Volume/V* | Fractions/C* | Gated |
|---|---:|---:|---:|---:|---:|---:|---|
| fall.Radau | 2.1711675e-08 | 1.6654719e-08 | 6.5416918e-09 | 6.7897189e-10 | 0 | 4.579621e-09 | yes |
| fall.coarse | 7.1338987e-08 | 5.3042047e-08 | 2.1314859e-08 | 2.0405933e-09 | 0 | 1.373864e-08 | no |
| fall.finer | 1.6501018e-08 | 1.2657554e-08 | 4.9716091e-09 | 5.0939602e-10 | 0 | 3.4347139e-09 | yes |
| rise.Radau | 2.1632447e-08 | 1.6761164e-08 | 6.3361352e-09 | 6.9360046e-10 | 0 | 4.5813733e-09 | yes |
| rise.coarse | 7.1088459e-08 | 5.3447002e-08 | 2.0660455e-08 | 2.0840773e-09 | 0 | 1.3743896e-08 | no |
| rise.finer | 1.6440709e-08 | 1.2738387e-08 | 4.8153634e-09 | 5.2034552e-10 | 0 | 3.4360325e-09 | yes |
| steps.5CQA | 5.2076053e-12 | 2.0967711e-13 | 3.179194e-14 | 3.7507005e-14 | 0 | 2.7425895e-14 | yes |
| steps.caffeine | 4.49665e-12 | 2.1053118e-13 | 3.6102808e-14 | 4.4362199e-14 | 0 | 4.6012576e-14 | yes |
| steps.tds | 6.5432397e-12 | 2.1261625e-13 | 7.8393946e-14 | 2.5081677e-14 | 0 | 2.4361465e-14 | yes |
| steps.trigonelline | 7.5035178e-12 | 2.1176378e-13 | 4.1229285e-14 | 2.3569109e-14 | 0 | 4.3335794e-14 | yes |

## Spatial accuracy

Fine fields were conservatively restricted by averaging paired cell averages.
Each 400-to-800 gate passes .005 on its own fixed scale; integrated outputs do not
substitute for the volume-weighted phase-field test. Upwind diffusion is numerical error.

| Comparison | Fractions/C* | Mout/M* | Weighted field/M* | Gated |
|---|---:|---:|---:|---|
| rise.200_to_400 | 0.0010158233 | 0.00049112549 | 0.0015635264 | no |
| rise.400_to_800 | 0.00050960524 | 0.00031507635 | 0.0010445837 | yes |
| trigonelline.200_to_400 | 0.001708958 | 0.00096521498 | 0.0025154809 | no |
| trigonelline.400_to_800 | 0.00085703442 | 0.00063275091 | 0.0016881559 | yes |

The resolved difference ratios are recorded per channel in RESULTS.json. They are
refinement diagnostics, not a measured-order proof for the source problem.

## Passive continuum benchmark

Exact cell averages of the translated sine-squared initial profile and exact outlet
integrals are analytical, using a test-only zero-exchange path. Source parameters were
not overwritten. Each pre-exit N128 L1 error is <=.05; both mesh-pair orders are >=.8.

| N | t/tau | L1 liquid/C0 | Signed outlet error/M0 |
|---|---:|---:|---:|
| 32 | 0 | 1.3986208e-17 | 0 |
| 32 | 0.25 | 0.0340356586 | 0.0226842738 |
| 32 | 0.5 | 0.0411214394 | -0.00235815214 |
| 32 | 0.75 | 0.029723878 | -0.059447756 |
| 32 | 1.25 | 0.000704092253 | -0.00140818451 |
| 64 | 0 | 7.80625564e-18 | 0 |
| 64 | 0.25 | 0.0177030597 | 0.0118020035 |
| 64 | 0.5 | 0.0223897497 | -0.000688157072 |
| 64 | 0.75 | 0.0164392444 | -0.0328784889 |
| 64 | 1.25 | 5.7877776e-05 | -0.000115755552 |
| 128 | 0 | 6.07153217e-18 | 0 |
| 128 | 0.25 | 0.00902699122 | 0.00601799414 |
| 128 | 0.5 | 0.0117155714 | -0.000185877149 |
| 128 | 0.75 | 0.00869023988 | -0.0173804798 |
| 128 | 1.25 | 1.63282129e-06 | -3.26564258e-06 |

Pre-exit orders (32→64): [0.943048295051104, 0.8770523660741273, 0.8544783592191711];
(64→128): [0.9716816204623517, 0.9344110818750134, 0.9196760884912103].
At 1.25 tau, N128 remaining liquid plus absolute outlet-mass error/M0 = 6.53128517e-06 (allowance .05).
This manufactured first-order check is not a source-espresso accuracy claim.

## Observers, determinism and limits

Repeated rising-ramp numerical arrays are bitwise identical. All 25 source candidate/
reference delayed-window, cross-knot and fraction-additivity checks pass. Focused API
tests verify observation independence, exact carried knot state, explicit model origin,
clock translation, malformed-input rejection, immutable parameters, strict JSON and
finite-prefix failure handling. Constant-case nodal fraction differences are optional
cross-discretization diagnostics only; retained 001 arrays are not FV reference truth.

Qualification applies only to the declared cases, histories, grids and settings.
It does not cover every admitted input, measured ramp/flow authority, native MATLAB,
experimental accuracy, recoverable inventory or physical coffee prediction. Source
attribution and CC-BY-NC-3.0 treatment remain separate from software licensing.
