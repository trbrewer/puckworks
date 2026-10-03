# MODEL-GRUDEVA2026-CONSERVATIVE-003

**LOCAL_REPAIR_COUPLED_QUALIFICATION_INCOMPLETE.** G2 / NUMERICAL_METHOD_CHANGE.
PHYSICAL_VALIDATION=NOT_ESTABLISHED.

The conservative successor closes the actual exchanged amounts and complete
phase/cup balance. The finite bed refinement still exceeds the inherited outlet,
profile, grain-history and phase/cup allowances. Baseline raw-state qualification
and inter-method agreement are therefore unavailable; no baseline defect or
publication correction is demonstrated. Production and historical 001/002
evidence remain unchanged.

The deterministic [RESULTS.json](RESULTS.json) contains executed source,
configuration, observer and artifact hashes; every numerical invocation; all
norm counts; and unchanged baseline/publication replay. [CONTRACT.md](CONTRACT.md)
derives the repair and defines the frozen budgets. [HANDOFF.md](HANDOFF.md)
contains reproduction commands. Raw arrays, full logs and source PDFs remain
external. All five final canonical rows reach t=8 on the same scientific core.

## Separate dispositions

| Item | Disposition |
|---|---|
| Paired transfer and actual coupled conservation | PASS within declared algebraic allowance |
| Coupled qualification | INCOMPLETE: bed and combined refinement fail |
| Baseline raw-state/observation qualification | UNAVAILABLE_NOT_EXECUTED; synthetic seam tests only |
| Inter-method agreement | UNAVAILABLE on the entire required support |
| Figure 3 | Original baseline FAIL retained; alternative not scored |
| Figure 4 | Original baseline FAIL retained; alternative not scored |
| Figure 5 | FIG5_REFERENCE_INCOMPLETE |
| Baseline preservation | Unchanged production, inputs, 001/002 source and historical evidence hashes |
| Software QA | PASS: focused, full quick regression, static, generated, packaging and boundary checks |
| Hosted CI | Pending at numerical report generation; exact-head receipt in draft PR |
| Independent review | Pending at numerical report generation; nonhuman exact-head receipt in draft PR |
| Physical validation | NOT_ESTABLISHED |

## What changed and what was verified

The old algebra-only mismatch is reproduced: mapped-source integral .00016
versus old nodal observed donation .00008. That is not a coupled trajectory or
a claimed factor-two canonical error. The successor transfers signed amounts
from actual shell-state changes into liquid **plus equilibrated fines** storage,
using compatible physical volumes. Fixed physical cells retain grain memory;
continuous admission integrates the different ages of newly activated material.
The moving-volume face amounts and the front equation share the same trace and
time quadrature. Tests cover nonmatching/nonuniform grids, mixed release/uptake,
equilibrium, partial cells, admission/cohort subdivision, geometric conservation,
manufactured transport, fixed-domain and initially empty limits. Full runs
localize every front cell crossing, first drip and desaturation exit.

The actual all-shell exponential integrator is analytically checked at ages
.002, .02, .1, .3, .7 with constant/varying boundaries, uptake, equilibrium and
shifted activation. At 3200 shells the worst flux/mean errors are
1.600166e-4 / 6.762189e-7; at 6400 they are 4.000455e-5 / 1.690514e-7.
Both meet 2e-4 / 2e-5. The 800/1600-shell flux failures remain recorded.
The zero-diffusion fixture gives exactly zero liquid concentration, unchanged
boulders to 7.64e-14, exit 5.441599999999974 (relative error 4.88e-15),
plateau from 1 to exit, then zero outlet. It is not a changed canonical case.

Across final canonical evolution, the largest normalized global residual is
6.143021e-14. The largest paired-transfer amount residual is 3.36e-17;
the largest fraction of the predeclared scale-aware allowance is .0332.
Measured linear residuals are themselves below .000413 of their roundoff
allowance. The largest discrete front amount residual is 1.31e-18.
Independent phase reconstruction differs by at most 8.89e-16, shell-integral
reconstruction by 4.86e-17, and event-split independent cup quadrature by
3.18e-13. Cell quadrature of the piecewise-constant cell-average reconstruction
is exact in this arithmetic; this does not establish continuum profile accuracy.

Aqueous cell/face values and observed grain means meet the bounds; the
desaturation front never overtakes wetting. Individual radial-shell positivity
follows from the positive diffusion semigroup for nonnegative initial and
boundary histories, rather than an exhaustive saved-shell minimum audit.
No concentration clipping, mass-complement inventory or compensating reservoir
is used. At t=8 the normal row still has phase inventories
(1.010196e-7, 3.232627e-7, 2.368936e-7); finite horizon does not mean exact depletion.

## Final-source refinement

Normal controls: 512 bed cells, 3200 radial shells, dt=.002. Separate rows double
bed cells, double shells or halve dt; the combined row does all three. These
are empirical changes, not rigorous continuum-error bounds. The allocation
and measured pilot costs were frozen before spending the final-source reserve.

| Max absolute change from normal | Budget | Bed | Radial | Time | Combined |
|---|---:|---:|---:|---:|---:|
| Smooth outlet | .001 | .00430093 | 1.20e-8 | 5.27e-5 | .00425668 |
| Front position | .001 | .00011945 | 8.18e-10 | 5.45e-7 | .00011873 |
| Exit time | .001 | .00078041 | 5.24e-9 | 2.83e-6 | .00077632 |
| Activation time | .001 | .00078200 | 5.61e-9 | 4.07e-6 | .00077806 |
| Liquid profile | .001 | .00513913 | 1.20e-8 | 5.27e-5 | .00511102 |
| Grain spatial mean | .00023 | .00351323 | 4.59e-8 | 1.30e-5 | .00350577 |
| Fixed-z grain history | .00023 | .00351323 | 6.21e-8 | 1.49e-5 | .00350577 |
| Cup | .00005 | .00042562 | 2.82e-9 | 2.00e-6 | .00042329 |
| Liquid inventory | .00005 | .00010046 | 4.23e-10 | 4.82e-7 | .00009987 |
| Fines inventory | .00005 | .00032148 | 1.35e-9 | 1.54e-6 | .00031959 |
| Boulder inventory | .00005 | .00002413 | 1.12e-9 | 1.95e-7 | .00002413 |

The grain allocation reserves 2e-5 analytical allowance per method from the
inherited 5e-4 total, leaving .00023 empirical allowance per method. The final
normal/combined exit times are 6.503098377078418 / 6.503874694060178.
Arrival alone passes; outlet, profiles and phase observations do not qualify.
No larger speculative matrix or baseline comparison was launched after this
declared matrix failed. Remaining resources are a ceiling, not a reason to
waive the observation gates or turn this into an unbounded refinement campaign.

All 395 requested times, 220 physical-z coordinates and seven grain histories
are present through t=8. Front crossing and one-sided outlet events are retained
in addition. Bed/combined norms include/exclude respectively: outlet 381/14,
liquid profiles 85664/1236, grain profiles 56544/30356, grain histories 1794/971;
each has zero unavailable samples. Front and inventories include 395; activation
includes 220; exit includes one. Radial/time spatial counts differ slightly with
the displaced-front masks and are listed separately in JSON. Grain masks also
require positive age >=.02. No empty support passes and no missing endpoint is
extended. After both fronts exit, z=1 is retained outside the outlet's temporal
event margin, rather than hidden by a nonexistent spatial front mask. The same
review identified that this endpoint trace must share the outlet event mask;
that reporter-only correction was replayed on unchanged coupled artifacts.
Interior profiles and continuous grain/inventory support were not excluded by
that correction. Inter-method included/excluded counts are zero,
with the entire support explicitly unavailable because qualification is absent.

## Baseline and publication preservation

All eleven current source/remediation bindings and all six archived 001 raw
result hashes were verified. Replayed archived inventory arithmetic is labelled
as reuse, not raw-state reconstruction. The task-local return observer returns
the original solver objects and restores the seam; synthetic tests do not prove
neutrality or reconstruction on the actual baseline. That conditional numerical
audit was not executed because the alternative did not qualify.

Original Figure 3 concentration/front discrepancies remain .0975273/.0134474
against .015/.008 budgets (9 included, 10 excluded, 0 unavailable). Original
Figure 4 concentration/arrival discrepancies remain .1413303/.1208506 against
.015/.025 (5 included, 3 excluded, 0 unavailable). Fixtures and masks are reused
by identity, without redigitization or using the alternative as an oracle.
REFERENCE-002 remains COMPARATOR_QUALIFICATION_INCOMPLETE: its 12 successful
arrays, two failed attempts, missing terminal observations and unrequalified
final scheduler change are historical facts, not overwritten by 003.

## Resources and acceptance evidence

The complete timestamped invocation ledger in JSON records **17 full-horizon
attempts, six short invocations, 2644.684 aggregate numerical seconds**.
One full attempt failed early on a D=0 front-root bracket and remains counted.
The largest invocation was 539.766 seconds. No unresolved starts, resource
terminations or baseline coupled executions occurred. Limits were 24 full,
3600 aggregate seconds, 900 per run and 2 GiB per process. The external
controller enforced timeout and address-space limits; peak RSS was not measured.
At final allocation 19 full slots and 3368.27 seconds remained, exceeding the
required reserve of eight slots/1800 seconds. Scientific core versions for old
attempts are retained externally under their verified execution hashes.

Hosted minimum-dependency QA subsequently exposed a SciPy 1.13 one-cell
banded-solve shortcut using the wrong diagonal row. The initial empty-domain
D=0 regression failed in that environment; the other hosted jobs passed.
The scalar equation is now solved directly as rhs/diagonal, preserving the
same equations and all larger banded solves without changing dependency locks.
The corrected core is `bfddfc3340867024b2f6e0522811205d3083b6c3014bac0baa6ebf7dd474028a`.
Local qualification and all six full final-source invocations were reexecuted;
no old PASS was transferred. All six reexecuted numerical payloads are identical
to their predecessors after excluding only timing and core-identity metadata.
The old artifacts remain retained. Before this requalification, 13 slots and
2163.001 seconds remained; the predeclared reserve and final matrix were feasible.

The baseline quick suite passed 5463 tests; the candidate quick suite before
the endpoint reporter correction passed 5475, with 65 skipped and 63 deselected
in each. The same existing development salt warning occurred. Affected evidence
was replayed after that bounded correction; final focused tests: 60 passed,
three deselected. The same 60 focused tests also pass on the corrected core
with NumPy 2.0 / SciPy 1.13 and with the current numerical environment.
Final-head hosted regression is recorded separately in the PR.
Registry gates: 66 PASS plus one existing ACKNOWLEDGED_EXCEPTION. Ruff, configured
mypy, generated-artifact checks, wheel/sdist build and packaging inventory pass.
Source/AST, JSON, rights/provenance, changed-file secret/path and unchanged
production/historical boundary checks pass. No shell sources changed.
Only the existing Insight Foundry generator regenerated affected card snapshots.
Required hosted contexts and the independent review remain separate exact-head
acceptance receipts in the draft PR, avoiding a circular self-hash claim.

The learned result beyond #309 is conservative actual evolution and qualified
radial/time controls, with bed-resolution error now measured on the required
observations. It does not yet corroborate or refute the production baseline,
resolve the publication discrepancy or establish physical validation. Issue #67
remains open. No production adoption, automatic successor or merge is authorized.
