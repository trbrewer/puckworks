# 007 saved-result replay reassessment

**FINE_BASELINE_RAW_OBSERVATION_NUMERICALLY_QUALIFIED_ON_DECLARED_CASES**.
The declared 512-cell/32-resolved-mode baseline plus its unchanged production
tail passes the complete fixed qualification under the separately justified and
independently reviewed [replay admission correction](REPLAY_ADMISSION_CORRECTION.md).
Canonical parameters, mesh power 2, rtol=2e-8, atol=2e-10, max_step=.05 and horizon
8 remain fixed. **PHYSICAL_VALIDATION=NOT_ESTABLISHED**.

The inherited accepted-state admission test omitted the conditioning introduced
by rounded BDF time coordinates. Archived replay faithfully reproduces the
native reconstruction. The native stored-coordinate polynomial has the reported
accepted-state discrepancy; this assessment accounts for its independently
bounded coordinate/evaluation rounding while retaining the original bound on
coefficient consistency. No solver, observer, output, interval selection,
scientific tolerance, support or mask changed.

## Exact discrepancy and cause

There is exactly **one** original-threshold exceedance among all 818 accepted
vectors (67,586 components each) in combined segment 2. Indices are zero-based.

| Field | Value |
|---|---|
| Time | 6.504314428732874 (`0x1.a046b00693c06p+2`) |
| Accepted-step index / state index | 22 / 67584 |
| Component | grain modal state, cell 1023, mode index 64 (production tail) |
| Saved accepted value | 0.8333753264039222 |
| Native/archived reconstruction | 0.8333753264033821 |
| Signed difference | -5.401235014801387e-13 |
| Original threshold | 4.547473508864641e-13 |
| Selected interval index / side | 22 / right |
| Selected interval | [6.504314428732874, 6.504315144666799] |
| Interpolation order | 5 (preceding interval: 4) |
| Actual interval step | 7.159339245887963e-7 |
| Dense interpolator h after rescaling | 7.179252158816856e-7 |

The next interval is selected at this interior accepted time by the recorded
BDF semantics. Switching to the preceding interval would hide the discrepancy;
selection remains unchanged. The preceding interval's residual is
-1.1102230246251565e-16. Neighboring intervals, accepted points 21/23, segment
endpoints, and front/cup controls are retained in [REPLAY_DIAGNOSIS.json](REPLAY_DIAGNOSIS.json).
The diagnostic neighboring extrapolations are explicitly distinguished from
inside-interval evaluations. Original event-state error is zero.

Independent 100/160-digit evaluation gives a stored-polynomial residual of
-5.401556678447613e-13; ordinary binary64 evaluation contributes only
+3.216636462268894e-17. The discrepancy therefore predates the final evaluation.
Exact rational evaluation with the **same coefficients** and exact endpoint/h
coordinates gives -9.648951643238711e-17, below the unchanged original threshold.
At basis index 1, rounding the shift by -2.831863017940437e-16 contributes
-5.564172126017898e-13 to the polynomial difference. Other coordinate terms
partially offset it. All signed coordinate contributions and exact rational
certificates are retained in [REPLAY_CERTIFICATE.json](REPLAY_CERTIFICATE.json).

This identifies rounded coordinate construction in the native interpolator and
an insufficiently specified admission test. It establishes neither a persistence
corruption nor a production-equation defect. The certificate independently tests
coefficient consistency; high precision alone is not used as proof of accurate
coefficient construction or continuum accuracy.

| Separate question | Assessment |
|---|---|
| A: were returned arrays saved faithfully? | Original direct array/file fidelity PASS, preserved; all three combined archives and manifests revalidated. |
| B: does archived replay reproduce native dense reconstruction? | Original live/offline evidence PASS; segment 2 maximum difference 0 over 1637 points. This offline work is not a new live-run comparison. |
| C: does the reconstruction reproduce accepted/event states? | Original fixed accepted-state test FAIL, preserved. Events PASS unchanged. Separately certified coordinate-aware admission PASS. |

The independently derived coordinate bound is 5.74342729148363e-13 and the
evaluation bound is 1.1104610231300187e-15. At this state/time, the triangle bound
T+C+E is 1.0302005410579572e-12. It was derived from exact stored coefficients,
time coordinates and operation counts, not selected from the observed maximum.
The coefficient-residual allowance T remains 4.547473508864641e-13. Exact rational
comparisons, overflow guards, round-to-nearest and gradual-underflow checks pass.
The same rule was applied to all seven retained observed captures: the 006
baseline, continuation pilot, repeat and four refinements. Only combined segment
2 needs the certified branch; earlier passing receipt evidence is reused.

## Combined comparison results

All values below use unchanged dimensionless definitions, normalization,
pair-specific masks and original support. Requested/included/excluded/unavailable
counts are actual measured support; zero unavailable required points is mandatory.
The grain-history family includes all seven fixed positions.

| Family | Requested | Included | Excluded | Unavailable | Maximum | Allowance | Exact location | Result |
|---|---:|---:|---:|---:|---:|---:|---|---|
| activation | 220 | 220 | 0 | 0 | 1.3127063209772416e-06 | 0.001 | `{"index":[124],"z":0.58}` | PASS |
| arrival | 1 | 1 | 0 | 0 | 1.0694237566610809e-06 | 0.001 | `{"normal_t":6.504308470045491,"refined_t":6.504309539469248,"z":1.0}` | PASS |
| boulder_inventory | 395 | 395 | 0 | 0 | 1.5884969747741173e-07 | 5.0000000000000002e-05 | `{"index":[335],"t":6.675}` | PASS |
| cup | 395 | 395 | 0 | 0 | 1.1354529600993146e-06 | 5.0000000000000002e-05 | `{"index":[318],"t":6.6}` | PASS |
| fines_inventory | 395 | 395 | 0 | 0 | 7.7203461358241188e-07 | 5.0000000000000002e-05 | `{"index":[315],"t":6.585}` | PASS |
| front | 395 | 395 | 0 | 0 | 2.0038106995912131e-07 | 0.001 | `{"index":[152],"t":3.75}` | PASS |
| grain_histories | 2765 | 1794 | 971 | 0 | 2.2239502444454384e-05 | 0.00023000000000000001 | `{"index":[241,5],"t":5.975,"z":0.9}` | PASS |
| grain_profiles | 86900 | 56541 | 30359 | 0 | 2.8391326331256295e-05 | 0.00023000000000000001 | `{"index":[300,218],"t":6.515,"z":0.995}` | PASS |
| liquid_inventory | 395 | 395 | 0 | 0 | 2.4126081665798438e-07 | 5.0000000000000002e-05 | `{"index":[315],"t":6.585}` | PASS |
| liquid_profiles | 86900 | 85676 | 1224 | 0 | 1.0955168643633773e-05 | 0.001 | `{"index":[304,215],"t":6.535,"z":0.9852289512555391}` | PASS |
| outlet | 395 | 381 | 14 | 0 | 5.1502851991513943e-06 | 0.001 | `{"index":[303],"t":6.53}` | PASS |

The previously passing modes_fine, time_fine and bed_fine pairs remain bound to
[CONTINUATION_RESULTS.json](CONTINUATION_RESULTS.json); combined completes the
four mandatory comparisons. No 1024-cell adoption, alternate candidate, fitting,
additional grid or production-versus-004 comparison was performed.

## Combined individual audits

All 22 required audit identities pass. Maxima below are residuals unless shown
as an actual min/max range. Categorical rows have no physical maximum. For grain
point bounds only the inherited lower bound applies; the liquid range has both
lower and upper bounds. Exact support and locations are also machine-readable in
[REPLAY_COMBINED_DIAGNOSTIC.json](REPLAY_COMBINED_DIAGNOSTIC.json).

| Audit | Requested / included / excluded / unavailable | Measurement | Allowance | Location | Result |
|---|---|---|---|---|---|
| activation_support | 227/227/0/0 | categorical completeness | complete | `null` | PASS |
| aqueous_bounds | 8547/8547/0/0 | 0 | 1e-08 | `{"cell":0,"provenance":"accepted","segment":0,"t":0.0,"trace":false}` | PASS |
| complete_status | 1/1/0/0 | categorical completeness | complete | `null` | PASS |
| conservation | 8547/8547/0/0 | 2.6718684901448742e-10 | 9.9999999999999995e-07 | `{"provenance":"accepted","segment":2,"t":6.953744038737861}` | PASS |
| cup_quadrature | 9194/9194/0/0 | 0 | 1e-10 | `{"t":0.0}` | PASS |
| cup_state_integral | 9194/9194/0/0 | 1.0687228879646682e-09 | 5.0000000000000002e-05 | `{"t":7.840010481953066}` | PASS |
| diagnostic_grain_history_bounds | 4326/4326/0/0 | min=1.0576692093362185e-32; max=1.3880000000000006 | min >= -1e-8 | `{"maximum":{"provenance":"required","t":0.0,"z":0.025},"minimum":{"provenance":"required","t":8.0,"z":0.025}}` | PASS |
| diagnostic_grain_profile_bounds | 135960/135960/0/0 | min=4.4105246951774673e-35; max=1.3880000000000006 | min >= -1e-8 | `{"maximum":{"provenance":"required","t":0.0,"z":0.0},"minimum":{"provenance":"required","t":8.0,"z":0.0}}` | PASS |
| diagnostic_inlet | 395/395/0/0 | 4.1378192047747397e-07 | 2.0000000000000002e-05 | `{"t":0.175,"z":0.0}` | PASS |
| diagnostic_liquid_profile_bounds | 135960/135960/0/0 | min=0; max=1 | min >= -1e-8; max <= 1+1e-8 | `{"maximum":{"provenance":"required","t":0.01,"z":0.005},"minimum":{"provenance":"required","t":0.0,"z":0.0}}` | PASS |
| events | 2/2/0/0 | categorical completeness | complete | `null` | PASS |
| front_support | 17090/17090/0/0 | 2.2204460492503131e-16 | 1e-10 | `{"provenance":"accepted","segment":1,"t":6.504309539469248}` | PASS |
| grain_bounds | 8547/8547/0/0 | 0 | 1e-08 | `{"cell":0,"provenance":"accepted","segment":0,"t":0.0}` | PASS |
| horizon | 1/1/0/0 | categorical completeness | complete | `null` | PASS |
| independent_inventory_sums | 8547/8547/0/0 | 0.000244140625 | 1 | `{"provenance":"accepted","segment":0,"t":0.28850660029188163}` | PASS |
| phase_bounds | 8547/8547/0/0 | 0 | 1e-08 | `{"phase":0,"provenance":"accepted","segment":0,"t":0.0}` | PASS |
| public_cup_outlet_reconstruction | 150/150/0/0 | 0 | 2.2737367544323206e-13 | `{"field":"cup","t":0.0}` | PASS |
| public_inventory_algebra | 225/225/0/0 | 0.00093810038424591751 | 1 | `{"phase":1,"t":0.0}` | PASS |
| public_profile_reconstruction | 18000/18000/0/0 | 6.6613381477509392e-16 | 2.2737367544323206e-13 | `{"field":"grain","t":0.0,"z":0.0}` | PASS |
| required_times | 614/614/0/0 | categorical completeness | complete | `null` | PASS |
| solver_segments | 3/3/0/0 | categorical completeness | complete | `null` | PASS |
| tail_weights_rates | 65/65/0/0 | 2.2204460492503131e-16 | 5.6843418860808015e-14 | `{"rate_mode_index":64,"tail_index":64,"weight_mode_index":0}` | PASS |

Cup state/integral admission includes the separate quadrature refinement maximum
(0 here). Inventories are independent phase sums; no mass-complement inventory
or depletion assumption was introduced. The original 395-time/220-position
request, activation support, event-side semantics, front exclusions, age criteria
and profile/history mask distinction remain unchanged. Exact matching readout,
512 neutrality, deterministic raw-state repeatability and other individual audits
are reused, not rerun.

## History, accounting and claim boundary

The original timeout, failed replay receipt, original and continuation results,
preliminary/closed accounting and 005/006 evidence remain byte-identical. The
normal qualified reader still rejects the historical failed capture. A separate
integrity-validated diagnostic reader produced the combined results using the
original observer code; the new certificate admits that unchanged evidence under
the reviewed 007-only rule. Diagnostic artifacts retain their original label.

New work: **0 production simulations; 3 offline invocations**. Diagnosis used
30.022281889017904 seconds, combined analysis 165.21344985999167 seconds, and
certificate/final assembly 60.042163345002336 seconds: **255.2778950940119 seconds**
with every start closed. No operational retry or machine-safety termination.
The observed analysis high-water resident memory was 8,098,893,824 bytes.
Original 007 remains 0 full/3 short/308.8221942020173 seconds; continuation remains
6 full/2 short/7358.471498611994 seconds. Overall 007 is **6 full/8 short-or-offline,
7922.5715879080235 seconds**. No task-imposed deadline, budget, quota or memory
ceiling was restored. [Closed accounting](REPLAY_ACCOUNTING.json).

005 retains OBSERVER_QUALIFICATION_INCOMPLETE / OBSERVER_DIAGNOSTIC_INLET_BLOCKED
and its unresolved historical capture-corruption cause. 006 retains Conclusion A.
Their original attempt/source/plan/artifact identities and accounting are unchanged.
The 256/512 comparison remains supporting evidence; the completed 512/1024 pair
supplies the required forward refinement.

This qualifies only the declared canonical 512/32 configuration, environment,
scientific sources, unchanged observer/support/masks and four refinements. It
establishes no continuum accuracy, physical validation, publication-figure
validation, inter-backend agreement, universal validity or adoption authority.
A future matched comparison requires separate authorization. EWP and its lock
are unchanged; PR #329 remains draft/unmerged, auto-merge disabled, #67 open.
See [handoff](REPLAY_HANDOFF.md) for software QA and final review/CI disposition.
