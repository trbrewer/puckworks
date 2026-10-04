# MODEL-PANNUSCH2024-STATEFUL-FV-004 results

**IMPLEMENTED_QUALIFICATION_INCOMPLETE**. G2 / NUMERICAL_METHOD_CHANGE.
RESEARCH_ONLY; PHYSICAL_VALIDATION=NOT_ESTABLISHED; runtime accuracy NOT_ASSESSED.

Software QA, hosted CI and independent exact-head review are separate dispositions.

| Frozen gate | Result |
|---|---|
| equilibrium.caffeine | PASS |
| supplied_reference.caffeine | PASS |
| equilibrium.trigonelline | PASS |
| supplied_reference.trigonelline | PASS |
| equilibrium.5CQA | PASS |
| supplied_reference.5CQA | PASS |
| equilibrium.tds | PASS |
| supplied_reference.tds | PASS |
| S.prefix | PASS |
| S.resume | PASS |
| L.prefix | PASS |
| L.resume | PASS |
| branch_reference | PASS |
| default_finer | PASS |
| Radau.default | PASS |
| Radau.fine | PASS |
| resolved_temporal_decrease | FAIL / INCOMPLETE |
| mesh | PASS |
| S.recombination | PASS |
| L.recombination | PASS |
| deterministic_repeat | PASS |
| full_coverage | PASS |
| all_independent_accounting | PASS |
| all_input_states | PASS |

Integrations: 28; charged execution wall time: 577.091886 s.
Hard ceilings: 32 integrations, 1800 aggregate numerical seconds, 120 seconds per invocation.
Every launched attempt is retained; report-only work is separately charged.

| Comparison | Liquid / C* | Fine / C* | Coarse / C* | Outlet / C* | Origin mass / M* | Fractions / C* |
|---|---:|---:|---:|---:|---:|---:|
| equilibrium.caffeine | 1.02734179e-15 | 2.46716228e-15 | 5.0165633e-15 | 4.93432455e-16 | 4.83247604e-14 | 9.63221272e-14 |
| supplied_reference.caffeine | 2.25613388e-14 | 7.15572075e-14 | 4.32829117e-14 | 6.53601015e-15 | 4.26628709e-14 | 5.86788467e-14 |
| equilibrium.trigonelline | 2.61740377e-15 | 2.11975756e-15 | 3.76256968e-15 | 6.35927269e-16 | 3.66692932e-14 | 1.12506133e-13 |
| supplied_reference.trigonelline | 2.25250565e-14 | 7.15685312e-14 | 3.4754727e-14 | 9.60902686e-15 | 7.34960285e-14 | 5.6718217e-14 |
| equilibrium.5CQA | 1.85000045e-15 | 2.13847132e-15 | 3.70668361e-15 | 4.9897664e-16 | 1.99860049e-14 | 8.73921944e-14 |
| supplied_reference.5CQA | 2.24931072e-14 | 7.15918672e-14 | 4.38951308e-14 | 1.10786946e-14 | 1.7929238e-14 | 1.34287207e-13 |
| equilibrium.tds | 2.0298171e-15 | 2.49861182e-15 | 3.59175449e-15 | 4.68489716e-16 | 3.33005897e-14 | 2.07072454e-13 |
| supplied_reference.tds | 2.25240965e-14 | 7.15254984e-14 | 3.91183799e-14 | 1.72837965e-14 | 1.80027939e-14 | 4.83578562e-14 |
| S.prefix | 0 | 0 | 0 | 0 | 0 | 0 |
| S.resume | 0 | 0 | 0 | 0 | 0 | 0 |
| L.prefix | 0 | 0 | 0 | 0 | 0 | 0 |
| L.resume | 0 | 0 | 0 | 0 | 0 | 0 |
| branch_reference | 9.12620677e-15 | 4.68656135e-14 | 3.65048271e-14 | 9.12620677e-15 | 2.91601441e-14 | 1.50328234e-14 |
| default_finer | 1.33973434e-05 | 3.00213755e-07 | 5.14715166e-08 | 2.24381533e-07 | 1.48606335e-07 | 0.000119350706 |
| Radau.coarse | 6.72620567e-05 | 1.73607969e-06 | 2.49067602e-07 | 1.12138283e-06 | 7.77520483e-07 | 7.99042763e-05 |
| Radau.default | 1.74297442e-05 | 3.90519017e-07 | 5.31831444e-08 | 2.91679527e-07 | 1.93186076e-07 | 0.000202910268 |
| Radau.fine | 4.0324008e-06 | 9.03052626e-08 | 9.34534796e-09 | 6.72979938e-08 | 4.45797411e-08 | 8.35595614e-05 |

N400/N800 is a bounded mesh-sensitivity comparison, not asymptotic convergence or physical validation.
Step/reference and branch/reference comparisons independently assemble concentration balances and source capacities.
S and L prefixes actually stopped before suffix calls. Same-schedule comparisons include raw states and exact saved forcing.
Fraction checks include every frozen window and mass/volume recombination across the checkpoint.
Absolute and signed initial/final/worst inventory residuals, flux checks, scales, per-fraction errors and failures are in RESULTS.json.

Failed or unavailable executions: none.

Pannusch et al., 10.17632/y2tz67f6ry.1; CC-BY-NC-3.0 source-derived output; first-party software licensing separate.
