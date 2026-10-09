# 007 configuration-specific qualification

**FINE_BASELINE_QUALIFICATION_INCOMPLETE**

Baseline: cells=512, modes=32 plus unchanged production tail, mesh power=2, rtol=2e-8, atol=2e-10, max_step=.05, horizon=8; canonical physical parameters and exact environment/source/support/mask bindings in PLAN.

G1 / NO_GOVERNING_PHYSICS_CHANGE. **PHYSICAL_VALIDATION=NOT_ESTABLISHED.** No continuum accuracy, physical accuracy, universal validity, production-versus-004 comparison, adoption or default change is established.

Original 006 baseline identity is retained: task MODEL-GRUDEVA2026-SPATIAL-RESOLUTION-006, attempt 006-spatial-512, original PLAN 4dff690bb93165a0e34e81b67d8d396b060324d9e1d1b439b93432dd7a7ee95b. New reuse validation: True.

## Readout, pilot, neutrality and repeat

| Mesh/modes | Family | Eligible included/requested | Eligible max | Younger max | Raw endpoint max | Reference checks | Reference valid | Eligible gate |
|---|---|---|---|---|---|---|---|---|
| 1024/32 | nonconstant | 84/84 | 5.086020203881603e-07 | 8.338090656256902e-05 | 8.338090656256902e-05 | 18/18 | True | True |
| 1024/32 | zero_boundary | 84/84 | 5.350468291753785e-07 | 8.780910951022847e-05 | 8.780910951022847e-05 | 18/18 | True | True |
| 1024/64 | nonconstant | 84/84 | 5.086020203881603e-07 | 0.0009857159759376621 | 0.0009857159759376621 | 24/24 | True | True |
| 1024/64 | zero_boundary | 84/84 | 5.350468291753785e-07 | 0.0010380674206222906 | 0.0010380674206222906 | 24/24 | True | True |
| 512/32 | nonconstant | 84/84 | 3.741585943850545e-06 | 0.002014782904536716 | 0.002014782904536716 | 18/18 | True | True |
| 512/32 | zero_boundary | 84/84 | 3.936094188805583e-06 | 0.002121783995594706 | 0.002121783995594706 | 18/18 | True | True |
| 512/64 | nonconstant | 84/84 | 3.741585943850545e-06 | 0.006507027922002084 | 0.006507027922002084 | 24/24 | True | True |
| 512/64 | zero_boundary | 84/84 | 3.936094188805583e-06 | 0.006852615197338707 | 0.006852615197338707 | 24/24 | True | True |

Each family retains 139 requested/84 eligible/55 younger points. READOUT.json preserves exact maxima/locations, independent reference identities, unavailable support and the advancing-front INITIAL distinction. Eligible readout allowance is 2e-5; independent reference validity is separate at 1e-11.

- 007-pilot: EXECUTED_UNQUALIFIED; passed=False.
- 007-control_512: NOT_RUN; passed=False.
- 007-repeat_512: NOT_RUN; passed=False.

The pilot reached its fixed 300-second allocation watchdog at 298.05785053400905 seconds before production returned. No complete public Result, returned segment archive or pilot scientific gate result became available. Partial input metadata, runtime/headroom receipts and termination log are retained. Full-panel admission was not issued. Control and repeat were NOT_RUN, so neutrality and repeatability remain unestablished. No retry, resource increase or extra invocation is authorized.

## Four mandatory refinements

| Baseline versus | Family | Requested | Included | Excluded | Unavailable | Maximum | Exact location | Allowance | Pass |
|---|---|---:|---:|---:|---:|---|---|---|---|
| bed_fine | activation | 220 | 0 | 0 | 220 | None | `null` | 0.001 | False |
| bed_fine | arrival | 1 | 0 | 0 | 1 | None | `null` | 0.001 | False |
| bed_fine | boulder_inventory | 395 | 0 | 0 | 395 | None | `null` | 5e-05 | False |
| bed_fine | cup | 395 | 0 | 0 | 395 | None | `null` | 5e-05 | False |
| bed_fine | fines_inventory | 395 | 0 | 0 | 395 | None | `null` | 5e-05 | False |
| bed_fine | front | 395 | 0 | 0 | 395 | None | `null` | 0.001 | False |
| bed_fine | grain_histories | 2765 | 0 | 0 | 2765 | None | `null` | 0.00023 | False |
| bed_fine | grain_profiles | 86900 | 0 | 0 | 86900 | None | `null` | 0.00023 | False |
| bed_fine | liquid_inventory | 395 | 0 | 0 | 395 | None | `null` | 5e-05 | False |
| bed_fine | liquid_profiles | 86900 | 0 | 0 | 86900 | None | `null` | 0.001 | False |
| bed_fine | outlet | 395 | 0 | 0 | 395 | None | `null` | 0.001 | False |
| combined | activation | 220 | 0 | 0 | 220 | None | `null` | 0.001 | False |
| combined | arrival | 1 | 0 | 0 | 1 | None | `null` | 0.001 | False |
| combined | boulder_inventory | 395 | 0 | 0 | 395 | None | `null` | 5e-05 | False |
| combined | cup | 395 | 0 | 0 | 395 | None | `null` | 5e-05 | False |
| combined | fines_inventory | 395 | 0 | 0 | 395 | None | `null` | 5e-05 | False |
| combined | front | 395 | 0 | 0 | 395 | None | `null` | 0.001 | False |
| combined | grain_histories | 2765 | 0 | 0 | 2765 | None | `null` | 0.00023 | False |
| combined | grain_profiles | 86900 | 0 | 0 | 86900 | None | `null` | 0.00023 | False |
| combined | liquid_inventory | 395 | 0 | 0 | 395 | None | `null` | 5e-05 | False |
| combined | liquid_profiles | 86900 | 0 | 0 | 86900 | None | `null` | 0.001 | False |
| combined | outlet | 395 | 0 | 0 | 395 | None | `null` | 0.001 | False |
| modes_fine | activation | 220 | 0 | 0 | 220 | None | `null` | 0.001 | False |
| modes_fine | arrival | 1 | 0 | 0 | 1 | None | `null` | 0.001 | False |
| modes_fine | boulder_inventory | 395 | 0 | 0 | 395 | None | `null` | 5e-05 | False |
| modes_fine | cup | 395 | 0 | 0 | 395 | None | `null` | 5e-05 | False |
| modes_fine | fines_inventory | 395 | 0 | 0 | 395 | None | `null` | 5e-05 | False |
| modes_fine | front | 395 | 0 | 0 | 395 | None | `null` | 0.001 | False |
| modes_fine | grain_histories | 2765 | 0 | 0 | 2765 | None | `null` | 0.00023 | False |
| modes_fine | grain_profiles | 86900 | 0 | 0 | 86900 | None | `null` | 0.00023 | False |
| modes_fine | liquid_inventory | 395 | 0 | 0 | 395 | None | `null` | 5e-05 | False |
| modes_fine | liquid_profiles | 86900 | 0 | 0 | 86900 | None | `null` | 0.001 | False |
| modes_fine | outlet | 395 | 0 | 0 | 395 | None | `null` | 0.001 | False |
| time_fine | activation | 220 | 0 | 0 | 220 | None | `null` | 0.001 | False |
| time_fine | arrival | 1 | 0 | 0 | 1 | None | `null` | 0.001 | False |
| time_fine | boulder_inventory | 395 | 0 | 0 | 395 | None | `null` | 5e-05 | False |
| time_fine | cup | 395 | 0 | 0 | 395 | None | `null` | 5e-05 | False |
| time_fine | fines_inventory | 395 | 0 | 0 | 395 | None | `null` | 5e-05 | False |
| time_fine | front | 395 | 0 | 0 | 395 | None | `null` | 0.001 | False |
| time_fine | grain_histories | 2765 | 0 | 0 | 2765 | None | `null` | 0.00023 | False |
| time_fine | grain_profiles | 86900 | 0 | 0 | 86900 | None | `null` | 0.00023 | False |
| time_fine | liquid_inventory | 395 | 0 | 0 | 395 | None | `null` | 5e-05 | False |
| time_fine | liquid_profiles | 86900 | 0 | 0 | 86900 | None | `null` | 0.001 | False |
| time_fine | outlet | 395 | 0 | 0 | 395 | None | `null` | 0.001 | False |

The frozen contract requires pair-specific unchanged masks and histories at all seven fixed positions. These comparisons were not executed because their refinement rows are missing. Included support is zero and the listed required support is unavailable; False means the qualification requirement is unsatisfied, not a measured numerical failure.

## Individual audits

All 22 gates for repeat_512, modes_fine, time_fine, bed_fine and combined are NOT_RUN; their trajectory support, maxima and locations are unavailable. The complete named 22-gate panel for original baseline reuse is retained below. Categorical gates have no physical maximum. Exact detailed fields, signed extrema and separate quadrature maxima are in RESULTS.json.

### baseline_512 (original 006 reuse)

| Gate | Requested/included/excluded/unavailable | Maximum | Location | Allowance | Pass |
|---|---|---|---|---|---|
| activation_support | 227/227/0/0 | 0 | `null` | 0 | True |
| aqueous_bounds | 3039/3039/0/0 | 0.0 | `{"cell": 0, "provenance": "accepted", "segment": 0, "t": 0.0, "trace": false}` | 1e-08 | True |
| complete_status | 1/1/0/0 | 0 | `null` | 0 | True |
| conservation | 3039/3039/0/0 | 3.037545239352549e-09 | `{"provenance": "accepted", "segment": 1, "t": 6.155460976930302}` | 1e-06 | True |
| cup_quadrature | 3686/3686/0/0 | 0.0 | `{"t": 0.0}` | 1e-10 | True |
| cup_state_integral | 3686/3686/0/0 | 3.1560185576040567e-09 | `{"t": 7.547969439045619}` | 5e-05 | True |
| diagnostic_grain_history_bounds | 4326/4326/0/0 | 1.3880000000000001 | `{"maximum": {"provenance": "required", "t": 0.0, "z": 0.025}, "minimum": {"provenance": "required", "t": 8.0, "z": 0.025}}` | 1e-08 | True |
| diagnostic_grain_profile_bounds | 135960/135960/0/0 | 1.3880000000000001 | `{"maximum": {"provenance": "required", "t": 0.0, "z": 0.0}, "minimum": {"provenance": "required", "t": 8.0, "z": 0.0}}` | 1e-08 | True |
| diagnostic_inlet | 395/395/0/0 | 1.5171920852152798e-06 | `{"t": 0.175, "z": 0.0}` | 2e-05 | True |
| diagnostic_liquid_profile_bounds | 135960/135960/0/0 | 1.0 | `{"maximum": {"provenance": "required", "t": 0.01, "z": 0.005}, "minimum": {"provenance": "required", "t": 0.0, "z": 0.0}}` | 1e-08 | True |
| events | 2/2/0/0 | 0 | `null` | 0 | True |
| front_support | 6074/6074/0/0 | 0.0 | `{"provenance": "accepted", "segment": 0, "t": 0.0}` | 1e-10 | True |
| grain_bounds | 3039/3039/0/0 | 0.0 | `{"cell": 0, "provenance": "accepted", "segment": 0, "t": 0.0}` | 1e-08 | True |
| horizon | 1/1/0/0 | 0 | `null` | 0 | True |
| independent_inventory_sums | 3039/3039/0/0 | 0.00018310546875 | `{"provenance": "accepted", "segment": 0, "t": 0.46325122333617424}` | 1.0 | True |
| phase_bounds | 3039/3039/0/0 | 0.0 | `{"phase": 0, "provenance": "accepted", "segment": 0, "t": 0.0}` | 1e-08 | True |
| public_cup_outlet_reconstruction | 150/150/0/0 | 0.0 | `{"field": "cup", "t": 0.0}` | 2.2737367544323206e-13 | True |
| public_inventory_algebra | 225/225/0/0 | 0.0009381003842459175 | `{"phase": 1, "t": 0.0}` | 1.0 | True |
| public_profile_reconstruction | 18000/18000/0/0 | 4.440892098500626e-16 | `{"field": "grain", "t": 6.451127819548873, "z": 0.99}` | 2.2737367544323206e-13 | True |
| required_times | 614/614/0/0 | 0 | `null` | 0 | True |
| solver_segments | 3/3/0/0 | 0 | `null` | 0 | True |
| tail_weights_rates | 33/33/0/0 | 0.0 | `{"rate_mode_index": 0, "tail_index": 32, "weight_mode_index": 0}` | 5.684341886080802e-14 | True |

## Closed resources and limitations

| Invocation | Kind | Actual seconds | Allocation | Exit | Peak virtual bytes | Peak RSS bytes |
|---|---|---:|---:|---:|---:|---:|
| 007-pilot | short | 298.05785053400905 | 300.0 | 124 | 1692385280 | 917729280 |
| 007-readout | short | 10.284434583998518 | 120.0 | 0 | 925233152 | 747847680 |
| 007-reduction | short | 0.4799090840097051 | 240.0 | 2 | 263565312 | 88821760 |

**0 new full / 3 short / 308.8221942020173 numerical seconds.** Closed accounting passed=True; unresolved starts=[]. RLIMIT_AS soft/hard is exactly 34359738368 bytes. ACCOUNTING retains live host/cgroup/virtual/storage checks and the separate preliminary reduction receipt.

005 remains OBSERVER_QUALIFICATION_INCOMPLETE / OBSERVER_DIAGNOSTIC_INLET_BLOCKED, closed 7 full / 21 short / 727.042119908976 seconds. 006 remains conclusion A, closed 1 full / 2 short / 166.21631713100942 seconds. Historical failures and unresolved corruption cause remain intact.

A successful 007 permits consideration in a separately authorized matched comparison; it performs no such comparison, establishes no backend agreement or publication validation, and authorizes no adoption or successor. Issue #67 remains open; PR remains draft; auto-merge disabled; EWP/lock unchanged.

Software QA, exact-head hosted CI and independent review are separate receipts in HANDOFF and the PR.
