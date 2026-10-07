# Flow-consistent observer results

**VERIFIED_ON_DECLARED_CASES**; pannusch2024.flow_consistent_observer.volume_clock.v1.
G2 / NUMERICAL_METHOD_CHANGE / RESEARCH_ONLY. Runtime accuracy NOT_ASSESSED.
PHYSICAL_VALIDATION=NOT_ESTABLISHED. Historical 004 remains failed.

| Check | Disposition |
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
| S.recombination | PASS |
| L.prefix | PASS |
| L.resume | PASS |
| L.recombination | PASS |
| branch_reference | PASS |
| default_finer | PASS |
| Radau.default | PASS |
| Radau.fine | PASS |
| reference_resolution | PASS |
| resolved_temporal_decrease | PASS |
| mesh | PASS |
| deterministic_repeat | PASS |
| all_independent_accounting | PASS |
| full_coverage | PASS |

| Comparison | Liquid | Fine | Coarse | Outlet | Root mass | Fractions |
|---|---:|---:|---:|---:|---:|---:|
| equilibrium.caffeine | 1.02734179e-15 | 2.46716228e-15 | 5.0165633e-15 | 4.93432455e-16 | 4.83247604e-14 | 9.62810079e-14 |
| supplied_reference.caffeine | 2.57083066e-14 | 7.18476968e-14 | 1.4960201e-13 | 2.47884237e-14 | 2.45203773e-13 | 2.1593041e-14 |
| equilibrium.trigonelline | 2.61740377e-15 | 2.11975756e-15 | 3.76256968e-15 | 6.35927269e-16 | 3.66692932e-14 | 1.12506133e-13 |
| supplied_reference.trigonelline | 2.80783252e-14 | 7.15685312e-14 | 7.80577442e-14 | 2.80783252e-14 | 6.8497558e-14 | 2.6892796e-14 |
| equilibrium.5CQA | 1.85000045e-15 | 2.13847132e-15 | 3.70668361e-15 | 4.9897664e-16 | 1.99860049e-14 | 8.73921944e-14 |
| supplied_reference.5CQA | 2.94172913e-14 | 7.15918672e-14 | 1.541785e-13 | 2.39199087e-14 | 4.84338444e-14 | 2.08145171e-14 |
| equilibrium.tds | 2.0298171e-15 | 2.49861182e-15 | 3.59175449e-15 | 4.68489716e-16 | 3.33005897e-14 | 2.07072454e-13 |
| supplied_reference.tds | 5.58045983e-14 | 7.16174334e-14 | 1.25307525e-13 | 5.53449229e-14 | 2.53130193e-13 | 4.52320632e-14 |
| S.prefix | 0 | 0 | 0 | 0 | 0 | 0 |
| S.resume | 0 | 0 | 0 | 0 | 0 | 0 |
| L.prefix | 0 | 0 | 0 | 0 | 0 | 0 |
| L.resume | 0 | 0 | 0 | 0 | 0 | 0 |
| branch_reference | 1.0554446e-14 | 5.50961448e-14 | 9.47963547e-14 | 1.04576162e-14 | 6.52152977e-14 | 6.89912183e-15 |
| default_finer | 2.82171553e-07 | 2.58582779e-07 | 1.66823628e-08 | 5.41627063e-08 | 1.29633793e-08 | 3.21657023e-08 |
| Radau.coarse | 1.41159599e-06 | 1.3386847e-06 | 8.74382614e-08 | 2.71418025e-07 | 6.88929132e-08 | 1.59721694e-07 |
| Radau.default | 3.66696589e-07 | 3.35871527e-07 | 1.85419782e-08 | 7.04197533e-08 | 1.72844964e-08 | 4.26277041e-08 |
| Radau.fine | 8.45250361e-08 | 7.72887479e-08 | 3.82554979e-09 | 1.62570469e-08 | 4.32111711e-09 | 1.04620018e-08 |
| reference_resolution | 1.08802782e-12 | 7.85289516e-14 | 1.87849773e-14 | 1.08802782e-12 | 2.48148517e-14 | 9.682978e-16 |

Errors above use original fixed C*/M* scales and reducers. All 86 observation channels, original primary endpoint comparisons,
all 17 old/new/reference fractions at all three levels, signed accounting and all gates are in RESULTS.json.
Hash-bound full phase arrays and logs are external. New reference fractions use physical-time actual-Q quadrature;
cumulative-difference reference fractions are separately retained as a diagnostic.

| h (s) | Old controlling fraction | New | Reference | Old signed error / C* | New signed error / C* |
|---|---:|---:|---:|---:|---:|
| 0.04 | 3.4224163094 | 3.42314777231 | 3.42314923737 | -7.99042763e-05 | -1.59721694e-07 |
| 0.02 | 3.42128802772 | 3.42314884636 | 3.42314923737 | -0.000202910268 | -4.26277041e-08 |
| 0.01 | 3.42238278103 | 3.42314914141 | 3.42314923737 | -8.35595614e-05 | -1.04620018e-08 |

N400/N800 is bounded mesh sensitivity, not continuum or physical validation.
Software QA, hosted checks and one independent nonhuman exact-head review are separately reported.
No merge, adoption, EWP/default/lock change, envelope extension, fit, score or successor.

Pannusch et al., 10.17632/y2tz67f6ry.1; CC-BY-NC-3.0 source-derived output; first-party software licensing separate.
