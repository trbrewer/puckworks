# 006 spatial-resolution result

**A — Finer resolution is a promising measured route to a separately authorized finer-configuration qualification.**

All declared 512-cell age-eligible fixture gates, all 22 candidate individual gates, and all eleven native 256/512 comparison families pass. The single full attempt and both short invocations completed in 166.21631713100942 charged seconds, within the fixed 600-second total. No scientific input, allowance, support rule or implementation changed after the freeze.

G1 / NO_GOVERNING_PHYSICS_CHANGE; task-local accounting G0. **PHYSICAL_VALIDATION=NOT_ESTABLISHED.** This result does not establish complete 512-cell qualification, a new-config observed repeat or neutrality, continuum accuracy, readiness for production-versus-004 comparison, or production adoption. No successor is authorized.

## Frozen candidate and evidence

512 cells / 32 resolved modes plus the unchanged positive production tail; front_mesh_power=2, rtol=2e-8, atol=2e-10, max_step=0.05, horizon=8 in canonical time. Canonical parameters, original public request, full diagnostic request, units, masks, normalizations and event semantics are unchanged. The solver, mathematical observer, persistence and safe replay implementations are reused byte-for-byte.

[PLAN.json](PLAN.json) binds the numerical freeze; [EVIDENCE_BINDINGS.json](EVIDENCE_BINDINGS.json) identifies the inspected 128-cell normal-persistence and 256-cell **bed_fine** captures, complete new Result, saved observations, all segment files/receipts and actual weights/rates. Combined is not a control. The matched Python/NumPy/SciPy/BDF environment was reused. Full arrays and logs remain external.

## Exact-average readout prerequisite

Each mesh/family has 139 literal requested points: 84 age-eligible, 55 younger, zero unavailable. The gate allowance is 2e-5. Signed errors below are reconstructed minus independent expected values; all maximum locations have age=0.020999999999999908. The 128 result was reused through its original bindings; 256 and 512 used the same actual 32-mode-plus-tail spectrum.

| Cells | Family | Eligible absolute maximum | Signed error at maximum | t, z | Exceedances / 84 | Gate |
|---|---|---:|---:|---|---:|---|
| 128 | nonconstant | 0.000150325356467 | 0.000150325356467 | 5.0001, 0.99582 | 11 | FAIL |
| 128 | zero_boundary | 0.000158134628302 | 0.000158134628302 | 5.0001, 0.99582 | 11 | FAIL |
| 256 | nonconstant | 2.12991873279e-05 | -2.12991873279e-05 | 4.9, 0.9758 | 1 | FAIL |
| 256 | zero_boundary | 2.240770783e-05 | -2.240770783e-05 | 4.9, 0.9758 | 1 | FAIL |
| 512 | nonconstant | 3.74158594385e-06 | 3.74158594385e-06 | 5.0001, 0.99582 | 0 | PASS |
| 512 | zero_boundary | 3.93609418881e-06 | 3.93609418881e-06 | 5.0001, 0.99582 | 0 | PASS |

The 512-cell screen passes both families. Independent reference checks have 18/18 included per family/mesh; every discrepancy and quadrature uncertainty is finite. The largest discrepancy-plus-reported-uncertainty across the six cases is 3.402491772798744e-14, below the separate 1e-11 arithmetic validity limit. All eight inherited fixture gates pass; their original allowances are not added to any canonical budget.

Younger points remain diagnostics: 128 has 33/55 exceedances per family, 256 has 24/55, and 512 has 7/55. At 512, raw endpoint maxima are 0.002121783995594706 (zero boundary) and 0.002014782904536716 (nonconstant), at t=5, z=1, age=0; each has 4/13 raw-endpoint exceedances. The actual advancing-front assignment remains INITIAL=1.388 with zero assignment error at the eight advancing-front records. Raw polynomial endpoint values are not that assignment. [READOUT.json](READOUT.json) retains all-point, eligible, younger and endpoint extrema, signed minima/maxima, locations/ages, support/exceedance counts and independent-reference discrepancies/uncertainties.

## Complete native 256/512 acceptance panel

Inherited dimensionless budgets and coarse-minus-refined acceptance semantics are unchanged. Requested/included/excluded/unavailable counts are actual native pair support. Every family has zero unavailable points. Profile and history masks remain distinct; displaced-front intervals remain excluded by the original rules, and legitimate post-exit z=1 observations remain included.

| Family | Absolute maximum | Allowance | Maximum location | Requested / included / excluded | Gate |
|---|---:|---:|---|---:|---|
| activation | 4.51574493665e-06 | 0.001 | z=0.49 | 220 / 220 / 0 | PASS |
| arrival | 2.33852756537e-06 | 0.001 | normal_t=6.50430613152, refined_t=6.50430847005, z=1 | 1 / 1 / 0 | PASS |
| boulder_inventory | 5.22256657904e-07 | 5e-05 | t=6.665 | 395 / 395 / 0 | PASS |
| cup | 3.85529045488e-06 | 5e-05 | t=6.6 | 395 / 395 / 0 | PASS |
| fines_inventory | 2.58529258135e-06 | 5e-05 | t=6.585 | 395 / 395 / 0 | PASS |
| front | 6.89431384315e-07 | 0.001 | t=3.15 | 395 / 395 / 0 | PASS |
| grain_histories | 9.30287437322e-05 | 0.00023 | t=5.975, z=0.9 | 2765 / 1794 / 971 | PASS |
| grain_profiles | 0.000124852723816 | 0.00023 | t=6.51, z=0.995 | 86900 / 56541 / 30359 | PASS |
| liquid_inventory | 8.07903931754e-07 | 5e-05 | t=6.585 | 395 / 395 / 0 | PASS |
| liquid_profiles | 4.46687285735e-05 | 0.001 | t=6.535, z=0.985228951256 | 86900 / 85676 / 1224 | PASS |
| outlet | 2.32223033534e-05 | 0.001 | t=6.53 | 395 / 381 / 14 | PASS |

History acceptance covers all seven inherited physical positions. The new native support counts happen to equal historical 128/256 counts; no counts were forced and no masks were widened. The original 128/256 panel is copied unchanged in [RESULTS.json](RESULTS.json), with authority in [005 ATTRIBUTION.json](../model_grudeva2026_baseline_observation_005/ATTRIBUTION.json): grain profiles fail at 5.99964833227995e-4 and histories fail at 4.3232399697179513e-4. That historical failure remains unchanged.

## Candidate individual audits and persistence

All 22 inherited gates pass. The following table retains support and locations; all excluded/unavailable counts are zero. Bounds rows show field ranges, not residual magnitudes: liquid must remain within [-1e-8,1+1e-8], while grain profile/history values must be >=-1e-8. Algebra-fraction rows divide by their inherited floating-point allowance. Categorical rows have no physical maximum.

| Gate | Maximum residual or range | Allowance | Included / requested | Location |
|---|---:|---:|---:|---|
| activation_support | 0 | 0 | 227 / 227 | categorical / no physical maximum |
| aqueous_bounds | 0 | 1e-08 | 3039 / 3039 | cell=0, provenance=accepted, segment=0, t=0, trace=0 |
| complete_status | 0 | 0 | 1 / 1 | categorical / no physical maximum |
| conservation | 3.03754523935e-09 | 1e-06 | 3039 / 3039 | provenance=accepted, segment=1, t=6.15546097693 |
| cup_quadrature | 0 | 1e-10 | 3686 / 3686 | t=0 |
| cup_state_integral | 3.1560185576e-09 | 5e-05 | 3686 / 3686 | t=7.54796943905 |
| diagnostic_grain_history_bounds | 1.07004678165e-32 to 1.388 | 1e-08 | 4326 / 4326 | min: provenance=required, t=8, z=0.025; max: provenance=required, t=0, z=0.025 |
| diagnostic_grain_profile_bounds | 6.44249673437e-35 to 1.388 | 1e-08 | 135960 / 135960 | min: provenance=required, t=8, z=0; max: provenance=required, t=0, z=0 |
| diagnostic_inlet | 1.51719208522e-06 | 2e-05 | 395 / 395 | t=0.175, z=0 |
| diagnostic_liquid_profile_bounds | 0 to 1 | 1e-08 | 135960 / 135960 | min: provenance=required, t=0, z=0; max: provenance=required, t=0.01, z=0.005 |
| events | 0 | 0 | 2 / 2 | categorical / no physical maximum |
| front_support | 0 | 1e-10 | 6074 / 6074 | provenance=accepted, segment=0, t=0 |
| grain_bounds | 0 | 1e-08 | 3039 / 3039 | cell=0, provenance=accepted, segment=0, t=0 |
| horizon | 0 | 0 | 1 / 1 | categorical / no physical maximum |
| independent_inventory_sums | 0.00018310546875 | 1 | 3039 / 3039 | provenance=accepted, segment=0, t=0.463251223336 |
| phase_bounds | 0 | 1e-08 | 3039 / 3039 | phase=0, provenance=accepted, segment=0, t=0 |
| public_cup_outlet_reconstruction | 0 | 2.27373675443e-13 | 150 / 150 | field=cup, t=0 |
| public_inventory_algebra | 0.000938100384246 | 1 | 225 / 225 | phase=1, t=0 |
| public_profile_reconstruction | 4.4408920985e-16 | 2.27373675443e-13 | 18000 / 18000 | field=grain, t=6.45112781955, z=0.99 |
| required_times | 0 | 0 | 614 / 614 | categorical / no physical maximum |
| solver_segments | 0 | 0 | 3 / 3 | categorical / no physical maximum |
| tail_weights_rates | 0 | 5.68434188608e-14 | 33 / 33 | rate_mode_index=0, tail_index=32, weight_mode_index=0 |

The retained archive contains 3,038 accepted states plus one terminal event state across three segments covering [0,1], [1,6.504308470045491] and [6.504308470045491,8]. Returned-array fidelity, archive/array/receipt identity and live/offline dense replay pass for every segment. Live/offline differences are exactly zero at 4,395 / 835 / 849 replay points. The complete public Result checkpoint precedes diagnostic work; the Result is unchanged afterward and the solve seam is restored. Three internal solver segments constitute one full attempt.

Independent liquid, fines and boulder inventories remain separate phase sums. Their terminal values are retained in RESULTS.json; horizon 8 is not defined as complete depletion. The diagnostic/public grain endpoint difference is separately retained as 0.0007302567648314051. This inherited diagnostic is not a failed public-reconstruction gate: the public request/output remains unchanged, and reproduction under its original public semantics has maximum error 4.440892098500626e-16. No new endpoint allowance is introduced; the historical audit does not retain a location for that diagnostic maximum.

## Three-grid behavior and supported decomposition

New diagnostic signs are refined minus coarse; original acceptance signs are preserved. The following grain values use identical physical points, including the three original failures and all newly selected point locations. All seven listed grain diagnostics are monotone with a smaller second difference. This finite diagnostic panel does not assert global monotonic convergence.

| t, z | 128 value | 256 value | 512 value | Δ128→256 | Δ256→512 |
|---|---:|---:|---:|---:|---:|
| 0.2, 0 | 0.117271693237 | 0.117286629391 | 0.117290637257 | 1.4936153395e-05 | 4.00786566845e-06 |
| 5.875, 0.9 | 0.897804099803 | 0.897371775806 | 0.897312358082 | -0.000432323996971 | -5.94177236819e-05 |
| 5.975, 0.9 | 0.395335435956 | 0.394981177234 | 0.39488814849 | -0.00035425872209 | -9.3028743732e-05 |
| 6.51, 0.995 | 0.796319719634 | 0.795719754801 | 0.795594902077 | -0.000599964833228 | -0.000124852723816 |
| 6.525, 0.98 | 0.325464078915 | 0.325026987479 | 0.324925621106 | -0.000437091436021 | -0.000101366373043 |
| 6.53, 1 | 0.898948669941 | 0.899007625563 | 0.899043867599 | 5.89556219853e-05 | 3.62420356416e-05 |
| 6.535, 0.985228951256 | 0.390723832896 | 0.390297801373 | 0.390188386743 | -0.000426031523239 | -0.000109414629554 |

RESULTS.json also retains **all 22 same-observable rows** at the original and new pairwise maximum locations, with three signed values, native pair masks and common eligibility. The arrival time reverses direction: Δ128→256=-3.1561209574704208e-6, Δ256→512=+2.338527565370896e-6. Every recorded same-point absolute difference decreases, but this reversal prevents an unqualified monotonicity claim.

At the original history failure (t=5.875,z=.9), the native 256/512 decomposition has stored-field=-8.170339843915908e-5 and readout=+2.2285674757815954e-5: partial cancellation remains. Both history masks include this point while both profile masks exclude it. At the profile failure (t=6.51,z=.995), stored-field=-1.1245485295119373e-4 and readout=-1.2397870864266913e-5 reinforce each other. Thus improvement is not inferred solely from a change in reconstruction or maxima at different locations.

Common physical 128-cell stencils are supported for all seven diagnostic points. Exact full-cell amounts and split partial overlaps are retained in the external reduction. All recorded decomposition closure residuals are zero; point-versus-polynomial grouping residuals are separately retained at roundoff scale. Native 256/512 projection at t=6.53,z=1 is explicitly **unsupported**: the 256 domain ends at 1.0000000000000002 while the 512 domain ends at 1.0. No front is snapped and no field is extrapolated. The common 128 stencil is supported there, but does not replace that unavailable native projection or shrink acceptance support.

No convergence order is estimated, and no continuum truth is assigned to the finest field. Three-grid agreement does not establish physical validation.

## Measured cost and closed accounting

| Invocation | Kind | Charged wall seconds | Allocated seconds | Peak virtual bytes | Observed peak RSS bytes |
|---|---|---:|---:|---:|---:|
| 006-readout | short | 4.36702498401 | 90 | 551034880 | 376922112 |
| 006-spatial-512 | full | 139.326045854 | 290 | 3685965824 | 3334967296 |
| 006-reduction | short | 22.523246293 | 180 | 1791639552 | 1607794688 |

**1 full / 2 short / 166.21631713100942 seconds.** RLIMIT_AS soft and hard were both 8589934592 bytes for every worker. Maximum observed virtual usage was 3685965824 bytes; maximum sampled RSS high-water was 3334967296 bytes (wait4 resource receipt: 3328622592). These telemetry channels are retained separately rather than forced to agree. No failure, timeout, termination, unresolved start, retry or extra attempt occurred.

Production phases: solver/capture 98.29499366000528 s; public checkpoint 0.12633136301883496 s; segment persistence/fidelity/replay 22.839138340001227 s; observations/audits/persistence 16.354191923019243 s. Remaining invocation overhead is charged. Final reduction cost 22.523246292985277 s; its preliminary pending entry is retained and accounting-only closure finalized it without a second reduction.

The retained scientific artifact set occupies 2322150921 bytes, including 2240730162 bytes of segment archive files. Admission checked current host/cgroup usage, inherited address-space limits and storage headroom with a 2 GiB operating margin and 32 GiB storage minimum. All ancestor cgroup limits were unlimited and inherited RLIMIT_AS was unlimited; none was raised. Per-invocation headroom receipts are in [ACCOUNTING.json](ACCOUNTING.json). Measured cost fits the authorized envelope; historical cost comparisons remain context, not a BDF scaling law.

005 stays **OBSERVER_QUALIFICATION_INCOMPLETE / OBSERVER_DIAGNOSTIC_INLET_BLOCKED**, with its original failed attempts, unresolved historical capture cause and closed 7-full / 21-short / 727.042119908976-second ledger unchanged. The observed normal repeat is still unavailable. Earlier normal/control neutrality is not transferred into 512-cell qualification.

Software QA, hosted CI and independent review are separate from these numerical results; see [HANDOFF.md](HANDOFF.md). Draft PR #328 stays unmerged, issue #67 open, auto-merge disabled and EWP unchanged.
