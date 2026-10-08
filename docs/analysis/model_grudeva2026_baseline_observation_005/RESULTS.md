# MODEL-GRUDEVA2026-BASELINE-OBSERVATION-005

**OBSERVER_QUALIFICATION_INCOMPLETE — RESOURCE_FEASIBILITY_BLOCKED.**
G1 / NO_GOVERNING_PHYSICS_CHANGE. PHYSICAL_VALIDATION=NOT_ESTABLISHED.

The mandatory combined configuration could not finish the short positive-D
production/capture pilot within the unchanged 2 GiB process limit. No full matrix
was allocated or executed. This is a resource block, not a demonstrated failure
of production's richer numerical contract, governing physics or historical
REDUCED-001 qualification. No production-versus-004 comparison was performed.

## Measured resource result

The pilot used 256 cells, 64 resolved modes plus the tail, mesh power 2,
rtol=2e-9, atol=2e-11, max_step=.025 and horizon=.4. Its public request was the
frozen native request truncated at .4; the full diagnostic request remained
separate. The original solve_ivp raised MemoryError in its accepted-state
`vstack`, requesting 263 MiB for shape (2039,16898), before returning any solver
object. Thus no live dense solution was available for capture, and no public
Result was returned. The original exception and restored symbol are retained.

Measured elapsed time **87.535275 s**; peak RSS **1,838,239,744 bytes**;
requested additional allocation **275,640,176 bytes** (exact value in MATRIX).
The address-space limit was enforced; RSS and address space are distinct.
The failure occurred before observer serialization/reconstruction. Retaining more
memory for the full horizon, capture and observations cannot be defensibly
budgeted from this failed pilot under the same cap. Other full-row costs remain
unestimated, not asserted to scale linearly. No ceiling or support was reduced.

The later development delta only strengthens offline split validation,
accepted/event replay checks and exception-time retention of already-returned
segments. The interception function AST, production solver/kernel and SciPy
identities are unchanged; [MATRIX.json](MATRIX.json) records old/new observer
hashes. The pilot is reused only as resource evidence, never restamped as
successful observation or neutrality evidence. No correction recapture occurred.

One independent nonhuman review found three observer/reporting defects: missing
bounds on reconstructed profiles/histories, incorrect production attribution when
the independent inlet reconstruction failed, and NOT_EXECUTED labeling of failed
full attempts without reconstructable output. One coherent observer-only correction
adds unmasked diagnostic extrema/counts/locations at required/activation times and
both event sides, makes endpoint/reconstruction gates observer prerequisites, and
uses attempts/raw evidence for execution status. No clipping or allowance change.
The old/new observation identities and prior MATRIX hash are retained; the pilot's
resource evidence remains unchanged. The review addendum covers only this delta.

## Delivered implementation and compact qualification

One observer retains original return objects, reads the actual production modal
spectrum/geometry, writes safe NPZ coefficients and preserves complete public
Results. One offline reporter reconstructs fixed-physical-position modal profiles,
seven histories, activation, phase sums and the production cup trace; it checks
source/configuration/support identities and recomputes acceptance. A small runner
adapts the existing serial controller, and refuses full execution on this blocked
matrix. A manufactured example runs without a production trajectory.

These are executable paths with independent synthetic checks. They have **not**
been qualified on a complete captured canonical production trajectory. In
particular, actual production dense replay, endpoint errors, independent phase/cup
agreement, full-run neutrality and observed repeat remain unresolved. Synthetic
endpoint tests do not justify replacing public endpoints in an actual result.

The numerical fixture artifact retains actual and independently expected values;
the reporter recomputes errors, not a saved PASS flag. Maximum errors:

| Fixture | Largest error | Unchanged allowance | Included |
|---|---:|---:|---:|
| Constant/linear/quadratic cell-integral reconstruction | 2.220446e-16 | 2.273737e-13 (scale-aware roundoff fixture) | 90 |
| Varying finite-mode fixed-z history, inlet/front/post-exit | 2.389492e-6 | 2e-5 within grain allocation | 61 |
| Positive-age spherical mean, 32 modes + tail | 3.607825e-10 | 2e-5 | 20 |
| Positive-age spherical flux, 32 modes + tail | 2.342550e-6 | 2e-4 | 20 |
| Positive-age spherical mean, 64 modes + tail | 9.325873e-15 | 2e-5 | 20 |
| Positive-age spherical flux, 64 modes + tail | 2.046363e-12 | 2e-4 | 20 |
| Saved BDF polynomial replay | 6.938894e-18 | 2.273737e-13 | 12 |
| Event-split outlet integrals, quadrature orders 4/8 | 4.440892e-16 | 1e-10 within cup allocation | 14 |

All fixture requested points are included; excluded/unavailable=0. The moving-cell
index negative control exceeds .01. Tests separately cover unmodified argument
references, one original call/interception, identical returned objects, restoration
and identical propagated exceptions; tail sums/rates and complement-tail audit;
clock translation, uptake/equilibrium; invalid/nonfinite payloads; terminal-domain
truncation; distinct event-side provenance; missing support; and returned
NUMERICAL_VERIFICATION_FAILED diagnostics. These checks do not replace full-run
neutrality. The mathematical initial empty-domain convention introduces no volume.

## Complete full-matrix gates: unavailable

For **each** normal-versus-bed_fine/modes_fine/time_fine/combined pair, all
requested values below are unavailable: included=0, excluded=0, maximum and
location unavailable. Missing data are never reported as permitted exclusions.
The exact arrays are frozen externally, with generation/source and SHA256 bindings
in MATRIX, not just their counts. Public support remains 75 times/120 positions;
diagnostic support is the unchanged 395 times/220 positions/seven histories.

| Observable | Allowance | Requested = unavailable per pair |
|---|---:|---:|
| Outlet concentration | 1e-3 | 395 |
| Liquid concentration profile | 1e-3 | 86,900 |
| Front position | 1e-3 | 395 |
| Desaturation exit | 1e-3 | 1 |
| Activation | 1e-3 | 220 |
| Grain mean concentration profile | 2.3e-4 | 86,900 |
| Seven fixed-z grain histories | 2.3e-4 | 2,765 |
| Cumulative cup | 5e-5 | 395 |
| Liquid inventory | 5e-5 | 395 |
| Fines inventory | 5e-5 | 395 |
| Boulder inventory | 5e-5 | 395 |

Canonical conservation <=1e-6, aqueous [-1e-8,1+1e-8], grain/phase >=-1e-8,
front-within-wet-support, complete horizon/events, actual accepted/event-state
phase/cup audits, repeat and same-environment Result neutrality are **unavailable**.
No t=8 residual inventory or depletion claim is made. The complete historical
001 normal artifact was inspected and its public request matched exactly; its
scientific hash is retained. It is not new raw evidence or an assumed neutrality
control. No new full Result exists to adjudicate a historical environmental
mismatch, and none is hidden using tolerances or omitted fields.

## Attempts and separate acceptance states

Eight short invocations, zero full attempts, **94.661088 numerical seconds**.
One failed pilot, no timeout, no unresolved start. Peak process RSS is the pilot's
1,838,239,744 bytes; maximum invocation 87.535275 s. Six fixture-generation/check
invocations and one manufactured example are charged alongside the pilot.
Remaining: 10 full slots, 12 short invocations, 1,105.338912 seconds. The single observer-only correction used 3.621731 seconds and no full slots;
more than three full slots/300 seconds remain available within the ceilings. Unused budget is not authority
to bypass the demonstrated memory block or execute a successor.

The original normal software baseline passed 6,080 tests (67 skipped, 63
deselected); registry 66 PASS plus one acknowledged exception. New focused tests:
41 passed. Supported minimum NumPy 2.0.2/SciPy 1.13.1 focused inherited/new checks:
130 passed, three existing slow tests deselected, on local Python 3.12. The candidate normal suite passed 6,113 tests (67 skipped, 63 deselected).
Its collection preceded the final retention test and bounded correction; current
affected inherited/new checks passed 137 tests (three existing slow deselections),
and the current 41 new tests passed at minimum dependencies. Unaffected normal
checks are reused by unchanged source identity. Scientific-baseline: 5 passed,
7 optional-dependency skips. Packaging, configured static/type and applicable
integrity/generated checks passed. Hosted Python matrix/minimum lane and the one
independent nonhuman review/addendum have exact-head final receipts on the draft
PR. Pending checks are not inferred from the baseline. Selectors, dependencies,
thresholds, CI protections and historical receipts are unchanged.

Full arrays, source snapshots, PDFs, logs and private locators remain outside
Git. [RESULTS.json](RESULTS.json) is the offline reduced report; [HANDOFF.md](HANDOFF.md)
gives exact reproduction and remaining boundaries. Production preservation binds
50 protected paths; EWP and its dependency lock remain read-only. #67 remains
open, the PR stays draft, and auto-merge is disabled. No matched comparison is ready
on this evidence, and no solver repair, adoption, merge or successor is authorized.
