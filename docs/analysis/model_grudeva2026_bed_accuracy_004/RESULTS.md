# MODEL-GRUDEVA2026-BED-ACCURACY-004

**COMPARATOR_NUMERICALLY_QUALIFIED_ON_DECLARED_CASES.**
G2 / NUMERICAL_METHOD_CHANGE. PHYSICAL_VALIDATION=NOT_ESTABLISHED.

The corrected analysis-only comparator passes all mandatory analytical,
conservation, bounds, support and bed/radial/time/combined refinement gates on
the unchanged canonical fixed-flow problem. This qualifies the comparator for
a separately authorized solver comparison. Production raw-state/observer
qualification remains a separate prerequisite. No such comparison, production
adoption, publication rescoring or successor is executed here.

[CONTRACT.md](CONTRACT.md) records source inspection, the prospective three-family
campaign, diagnosis, correction and compatibility. [MATRIX.json](MATRIX.json)
freezes scientific/observer/reporter/controller identities and controls.
[RESULTS.json](RESULTS.json) contains every metric/count, execution/artifact
binding and complete attempt ledger. [HANDOFF.md](HANDOFF.md) gives reproduction
and owner boundaries. Full arrays, PDFs, source snapshots and logs stay external.

## Demonstrated mechanism and correction

At positive diffusion, newly activated grain concentration has a leading
square-root dependence on age. The coupled liquid inherits this layer. Linear
upwind reconstruction from even **exact cell integrals** gives approximately
half-order front-trace error. On the independent finite-shell travelling oracle,
the 128-cell half-cut front error is .0717149; substituting exact grain transfers
still leaves evolved liquid/face-amount error. Canonical 003's largest liquid
and grain-history differences occur as this layer reaches the outlet. The
endpoint grain profile is an actual fixed-z history, excluding a readout-only
explanation. No admission reset or radial-backend defect was demonstrated.

004 uses one conservative integral reconstruction with basis
`{1,z,sqrt(anchor-z)}` for face evolution, point liquid forcing and compatible
grain-profile readout. The anchor follows the physical front before exit and
continues its local age-distance basis after exit. It never changes activation
or grain positions. Signed grain loss, continuous admission, actual phase
integrals and telescoping face amounts retain 003's conservation correction.
The one-cell scalar solve remains compatible with SciPy 1.13.

Exact square-root trace/point tests fall to roundoff. The independent positive-
diffusion oracle's half-cut trace error falls to .00626238 (higher-order terms
remain). Smooth curved transport passes the predeclared order/time criteria,
but its absolute cell-average error is not uniformly smaller. The old smooth
average ratio 2.949 fails the predeclared >=3 criterion and remains recorded.
Admission with varying boundaries converges against independent physical cohorts;
its quadrature uncertainty is <=3.23e-13. Family C additionally exercises inlet,
interior, partial/front and post-exit positions with prescribed activation and
quadratic time histories: profile-integral oracle change <=2.00e-15; the largest
history mean error at dt=.001 is 2.76e-9. Its reconstruction probes at the exact
front or post-exit endpoint are distinct from the actual readout: at admission
the grain readout is INITIAL, and after exit z=1 uses the separately evolved
fixed-z history. Finite-shell oracles isolate bed operations; the separate
analytical spherical fixtures control radial continuum error.

## Original acceptance gates

Every entry below passes its original allowance. These are dimensionless
empirical refinement differences, not rigorous continuum bounds or experimental
errors. No tolerance or exclusion was enlarged. The 2e-5 analytical grain
allocation per method remains separate from the 2.3e-4 empirical allowance.

| Observable | Allowance | Bed | Radial | Time | Combined |
|---|---:|---:|---:|---:|---:|
| Smooth outlet | 0.001 | 0.00012917712 | 1.2332983e-08 | 4.5443432e-05 | 0.00016044646 |
| Liquid profile | 0.001 | 0.00016060603 | 1.2332983e-08 | 4.5443432e-05 | 0.00018021578 |
| Front position | 0.001 | 1.1465584e-05 | 8.2279017e-10 | 3.8926404e-06 | 1.0173076e-05 |
| Exit time | 0.001 | 1.0575567e-05 | 5.2078821e-09 | 9.9895689e-06 | 2.3328293e-05 |
| Activation time | 0.001 | 5.2102496e-05 | 5.4161244e-09 | 2.290492e-05 | 3.7294134e-05 |
| Grain spatial mean | 0.00023 | 9.1878151e-05 | 4.4392341e-08 | 3.7546104e-05 | 7.1610839e-05 |
| Fixed-z grain history | 0.00023 | 7.3859073e-05 | 6.1288602e-08 | 9.8201685e-05 | 5.7505322e-05 |
| Cup solute | 5e-05 | 9.470187e-06 | 2.8419009e-09 | 4.8964934e-06 | 1.278897e-05 |
| Liquid inventory | 5e-05 | 3.5146296e-06 | 4.3543968e-10 | 1.2894934e-06 | 3.0897284e-06 |
| Fines inventory | 5e-05 | 6.9012123e-06 | 1.3934065e-09 | 3.9060279e-06 | 9.8871307e-06 |
| Boulder inventory | 5e-05 | 6.0046996e-07 | 1.1228474e-09 | 5.8277009e-07 | 5.9762198e-07 |

All seven mandatory full trajectories reach t=8. The normal/repeat payloads
are bit-identical excluding timing only. The D=0 exit is 5.441599999999974;
arrival relative and front absolute errors are both 4.885e-15, grain error
7.639e-14. The constant-front analytical speed/arrival control meets 1e-12.
At 3200/6400 shells the inherited positive-age radial flux maxima are
1.600166e-4/4.000455e-5; mean maxima 6.762189e-7/1.690514e-7. Both pass
2e-4/2e-5; failed coarser radial diagnostics remain in the local evidence.

Maximum normalized global residual: 6.287e-14 (allowance 1e-6). The largest
local amount residual uses .027218 of its declared allowance; measured linear
solve residuals use .000492 of their roundoff allowance. Independent actual
phase reconstruction differs by <=8.882e-16, shell integration <=6.662e-16,
and event-split cup quadrature <=3.278e-13. These check actual discrete states,
not a mass complement. Aqueous bounds, grain/phase nonnegativity and s_d<=s_w
pass. No clipping, compensating inventory or outlet rescaling is used.

Normal t=8 inventories are liquid 9.70288614e-8, fines 3.10492357e-7 and boulders
2.29207751e-7; delivered cup solute is 5.55199936327071. This is finite-time
residual inventory, not exact depletion. Shell positivity has the inherited
positive diffusion-semigroup basis for nonnegative initial/boundary histories;
full saved-shell extrema are not claimed as a separate exhaustive audit.

## Support and masks

The source generator identity is retained: 395 requested times, 220 physical-z
coordinates, seven fixed-z histories, first drip, every cell crossing and exit.
All four final comparisons happen to have the same counts below; JSON records
each independently. Spatial .008 and temporal .025 displaced-jump margins and
grain age >=.02 are unchanged. Continuous inventories retain every time. After
both fronts exit, z=1 remains included outside its legitimate event margin.
No missing endpoint, unavailable sample or empty norm is treated as passing.

| Observable | Requested | Included | Excluded | Unavailable |
|---|---:|---:|---:|---:|
| Smooth outlet | 395 | 381 | 14 | 0 |
| Liquid profile | 86900 | 85676 | 1224 | 0 |
| Front position | 395 | 395 | 0 | 0 |
| Exit time | 1 | 1 | 0 | 0 |
| Activation time | 220 | 220 | 0 | 0 |
| Grain spatial mean | 86900 | 56541 | 30359 | 0 |
| Fixed-z grain history | 2765 | 1794 | 971 | 0 |
| Cup solute | 395 | 395 | 0 | 0 |
| Liquid inventory | 395 | 395 | 0 | 0 |
| Fines inventory | 395 | 395 | 0 | 0 |
| Boulder inventory | 395 | 395 | 0 | 0 |

003's bed comparison had liquid-profile counts 85664/1236 and grain-profile
counts 56544/30356; 004 has 85676/1224 and 56541/30359. These changes follow the
same masks with genuinely displaced fronts/activation times. Historical counts
were not forced onto the corrected trajectories. Physical-coordinate norms
remain controlling; no aligned-profile norm substitutes for them.

## Verified comparison with unchanged 003

The original normal and bed-fine arrays are available and match their retained
artifact, source, radial, configuration and support identities. They were not
rerun or restamped. The following compares refinement errors, not merely output
changes. Complete matched-control changes in all eleven observables, with
included/excluded/unavailable counts, are also retained in RESULTS.json.

| Bed refinement observable | Unchanged 003 | Corrected 004 | Reduction factor |
|---|---:|---:|---:|
| Smooth outlet | 0.004300932 | 0.00012917712 | 33.295 |
| Liquid profile | 0.0051391299 | 0.00016060603 | 31.998 |
| Front position | 0.0001194476 | 1.1465584e-05 | 10.418 |
| Exit time | 0.0007804082 | 1.0575567e-05 | 73.794 |
| Activation time | 0.00078200259 | 5.2102496e-05 | 15.009 |
| Grain spatial mean | 0.0035132312 | 9.1878151e-05 | 38.238 |
| Fixed-z grain history | 0.0035132312 | 7.3859073e-05 | 47.567 |
| Cup solute | 0.00042562119 | 9.470187e-06 | 44.943 |
| Liquid inventory | 0.00010046283 | 3.5146296e-06 | 28.584 |
| Fines inventory | 0.00032148106 | 6.9012123e-06 | 46.583 |
| Boulder inventory | 2.4131893e-05 | 6.0046996e-07 | 40.188 |

The correction reduces the demonstrated bed-refinement errors materially, while
the time-refinement grain-history change increases to 9.82e-5 and still passes
its original allowance. Improvement is not claimed uniformly on every diagnostic.
Historical normal/bed solver times were 98.678/219.433 seconds; current times
are 119.942/260.260 seconds. These are recorded execution costs, not a controlled
equal-cost benchmark across environments. No equal-cost superiority is claimed.

No moments or cohorts were added. For N bed cells and R radial shells, evolved
state is N liquid scalars, N*R grain scalars and 7*R fixed-history scalars. The
inherited dense radial transform has R² entries and is not extra physical state.
The enriched basis adds reconstruction work and a wider liquid banded solve.

| Row | Evolved scalar degrees of freedom | Solver seconds | External invocation seconds |
|---|---:|---:|---:|
| normal | 1,661,312 | 119.942 | 121.021 |
| bed_fine | 3,300,224 | 260.260 | 262.421 |
| radial_fine | 3,322,112 | 184.294 | 185.372 |
| time_fine | 1,661,312 | 194.397 | 195.553 |
| combined | 6,599,424 | 576.321 | 578.509 |
| limit | 656 | 7.293 | 7.733 |
| repeat | 1,661,312 | 119.974 | 121.079 |

## Resources, preservation and separate QA

**7 full attempts, 13 short invocations, 1518.092603
aggregate numerical wall-seconds.** Largest invocation 578.509216 seconds;
maximum measured final-process RSS 780455936 bytes. Limits remain 24 full,
3600 aggregate seconds, 900 per invocation and 2 GiB/process. No unresolved
starts or resource terminations occurred. The initial zero-volume crossing
pilot failed and is retained, with its verified source snapshot. The correction
was completed before freezing the final matrix. No final defect correction or
reserve trajectory was needed; 17 full slots and 2081.907397 seconds remain
unused. All scientific invocations were serial with one numerical-library
thread. Ordinary QA and offline saved-JSON reduction are separate from this
scientific execution ledger.

The source PDFs were actually reopened; their hashes match 003. Historical
001/002/003 code, fixtures and evidence, permission records, production defaults,
dependency pins and EWP are preserved. Figures 3/4 retain FAIL/FAIL; Figure 5
remains incomplete. Synthetic production-observer seam tests establish no
production raw-state qualification. PR #325's post-merge run 37711116381 remains
completed/cancelled (min-deps cancellation, no demonstrated numerical failure);
its integration closeout is not retrospectively declared green.

Local baseline QA: 6132 passed, 33 skipped, 72 deselected. Candidate normal suite:
6168 passed, 33 skipped, 72 deselected, same selectors, 9 existing warnings.
After card/status regeneration, 234 affected checks pass (three existing slow
tests deselected). The complete saved-result replay is byte-identical.
Focused old/new checks on NumPy 2.0.2/SciPy 1.13.1: 96 passed, three existing
slow tests deselected, before final numerical execution. Five scientific-baseline
tests, configured ruff/mypy, registry/integrity, generated artifacts and strict
evidence scopes pass. Wheel/sdist inventory, clean-room installed-wheel service
checks, retained notices and sdist rebuild pass. The first minimum-dependency
shell-center assertion failure is retained; the replacement checks independently
computed non-cancelling physical shell amounts under the already-declared
256-epsilon rule. No scientific allowance was increased.

Hosted CI and the one independent **nonhuman** exact-head review are pending
at numerical report generation. Their receipts belong in the draft PR and final
owner handoff, outside circular commit/tree hashes in this evidence. Numerical
qualification does not imply either status. Issue #67 stays open; PR stays draft,
auto-merge disabled, no merge or successor. PHYSICAL_VALIDATION=NOT_ESTABLISHED.
