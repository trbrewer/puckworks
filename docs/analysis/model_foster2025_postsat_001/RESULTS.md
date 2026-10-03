# MODEL-FOSTER2025-POSTSAT-001 results

BOUNDED_NUMERICAL_AND_SOURCE_RECONSTRUCTION_PASS

G2 / GOVERNING_PHYSICS_CHANGE. PHYSICAL_VALIDATION=NOT_ESTABLISHED.

The old constant headspace is replaced by source Eq. 29/38 after actual saturation.
Source-conditioned equation reconstruction only; no fitting, new physics or EWP adoption.

The initial finite-difference entry-derivative diagnostic remains NOT_QUALIFIED_AS_DENSE_OUTPUT_DERIVATIVE.
Its normalized error is retained in JSON. The solver RHS at entry is verified independently at algebraic roundoff;
no derivative observer is supplied. The initial diagnostic disposition and correction remain recorded.

| Outcome | Disposition |
|---|---|
| equation_completion | PASS |
| domain_boundedness | PASS |
| water_conservation | PASS |
| temporal_accuracy | PASS |
| independent_method | PASS |
| equilibrium_stability | PASS |
| finite_horizon_equilibrium | PASS |
| earlier_stage_compatibility | PASS |
| source_reference_dimensional_defaults | PASS |
| source_reference_rounded_fixture | PASS |
| software_QA | REPORTED_SEPARATELY_IN_HANDOFF |
| hosted_CI | REPORTED_SEPARATELY_IN_HANDOFF |
| independent_exact_head_review | REPORTED_SEPARATELY_IN_HANDOFF |

Pinned baseline defect: saturation 6.665255636 reported s; pump minus bed inflow 0.680752586 mL/s.

| Continuous channel | Fine/finer normalized max | Independent normalized max |
|---|---:|---:|
| s_m | 1.246e-10 | 2.717e-18 |
| H_m | 1.147e-09 | 1.234e-11 |
| headspace_pressure_absolute_Pa | 6.534e-09 | 6.922e-11 |
| Q_pump_m3_s | 6.047e-09 | 6.352e-11 |
| Q_bed_in_m3_s | 4.794e-09 | 5.079e-11 |
| Q_out_m3_s | 4.794e-09 | 5.079e-11 |
| V_pump_m3 | 5.023e-10 | 5.012e-12 |
| V_out_m3 | 3.74e-10 | 4.414e-12 |
| V_storage_m3 | 8.122e-10 | 8.74e-12 |

Independent global water residual: 9.195e-12; headspace subinterval residual: 8.672e-12 (budget 1e-6).
Outlet comparison excludes 1 samples in the disclosed event interval [5.869255635648925, 5.869255635661578] model s. All continuous channels retain these samples; event-time errors are separate.

| Case/window | n | reported seconds | Q RMSE/max | p_h RMSE/max |
|---|---:|---|---|---|
| dimensional_defaults/pre | 294 | [0.8, 6.66] | 0.0001268/0.00057351 | 0.00011603/0.00028894 |
| dimensional_defaults/post | 167 | [6.68, 10.0] | 0.00036541/0.00037605 | 0.0003517/0.00036368 |
| dimensional_defaults/overall | 461 | [0.8, 10.0] | 0.00024212/0.00057351 | 0.00023107/0.00036368 |
| rounded_fixture/pre | 294 | [0.8, 6.66] | 9.4178e-06/2.1799e-05 | 2.1013e-05/4.6416e-05 |
| rounded_fixture/post | 167 | [6.68, 10.0] | 7.3155e-06/2.7414e-05 | 9.9473e-06/3.7999e-05 |
| rounded_fixture/overall | 461 | [0.8, 10.0] | 8.715e-06/2.7414e-05 | 1.7817e-05/4.6416e-05 |

Both representations are frozen separately; neither rescues the other. All reference timestamps are covered.
The existing early-flow and fitted-trajectory checks retain their original thresholds; see JSON for each result.
Rounded source-event classification is fixed at reported 6.667 s; candidate differences are disclosed in JSON.

See RESULTS.json for source/configuration hashes, parameters, transforms/discrepancies, support, every norm and gate.
See HANDOFF.md for variable execution metadata, QA, hosted CI, exact-head review and unresolved limitations.
