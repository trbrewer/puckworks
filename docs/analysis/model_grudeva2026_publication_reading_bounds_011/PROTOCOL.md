# Grudeva publication discrepancy under figure-reading uncertainty

Task: MODEL-GRUDEVA2026-PUBLICATION-READING-BOUNDS-011. Frozen before the complete
new propagation, subject to one independent method audit. G1; TARGET_EXPOSED;
PUBLIC_NUMERICAL_REFERENCE_COMPARISON; NO_GOVERNING_PHYSICS_CHANGE;
PHYSICAL_VALIDATION=NOT_ESTABLISHED. This retrospective numerical comparison is
not an independent experiment or blind test.

The question is whether the selected 009 discrepancy witnesses exclude zero and
resolve their original acceptance limits after propagating the recorded figure
coordinates. Improving the reliability of that evidence informs later wetting
and extraction decisions. This completes only the earned reading-bound part of
R-06 / T07. It does not establish the cause of the discrepancy or close issue #67.

## Identities, population and reuse

[BINDINGS.json](BINDINGS.json) binds current PW main
`b755f250aaa300ccb7d379ef3a3ec2de672044a5`, read-only EWP main
`7c025527da7e07982428d4c78a3e79bfa29a76ac`, the source fixture, historical
contracts/results and exact four inputs. Both mains still equal the supplied
reviewed identities. Live branch/PR/issue and repository searches found no
equivalent 011; full-reference 010 / PR #333 remains separate. PR #343 is
integrated; its existing integration evidence is reused without another campaign.

Dataset `grudeva2026/publication_reference` comprises selected source-derived
numerical curve readings: Grudeva, Moroney & Foster, EJAM 37(2), 496–519,
DOI 10.1017/S095679252500018X, CC-BY-4.0. These are not measured espresso
observations or author arrays. Retain the fixture's attribution, image/container
identities and rights; 004's permission-attributed adapted reference retains
THIRD_PARTY_NOTICES. No new source extraction or broad source review.

Reuse 009's completed equation/parameter/observation crosswalk and SOURCE_REUSE.
Only the original figure-producing configuration/revision/arrays/readout remain
unresolved source questions relevant here. Agreement of implementations cannot
identify author error. FIG5_REFERENCE_INCOMPLETE remains unchanged.

P0 is original 006 spatial-512; P1 is original 007 combined, admitted only through
unchanged 008 helpers and accepted 007 certificate composition. C0/C1 are 004
normal-final/combined-final. All actual admission receipts must equal 009's
verified numerical bindings, themselves equal to 008. Keep P1's original failed
replay and DIAGNOSTIC_ONLY provenance. All lower-level array, support, manifest,
receipt, source and environment validation stays enabled. No certificate rerun,
historical wrapper invocation, replacement baseline or refinement selection.

Each input retains 31 targets: F3 concentration 19 requested/9 included; F3 front
3/3; F4 concentration 8/5; F4 arrival 1/1. Totals: 124 rows, 72 included,
52 excluded, zero historically unavailable. Included family denominators are
36/12/20/4 respectively. Every input retains 17 historical failures and F3F-001
as its sole historical pass. All original row fields are copied unchanged under
`original`; new availability cannot rewrite history. Four evaluations of a source
target do not create four independent source observations.

## Reading sets and support

For F3 concentration vary only z by its recorded half-width and the publication
concentration by its recorded half-width; labeled time stays fixed. For F4
concentration vary only t and the publication concentration; z=1 stays fixed.
For fronts and arrival vary only the corresponding publication scalar interval.
No added time/depth uncertainty, clock, parameter or normalization variation.

The fixture supplies nominal calibration and marginal widths, without a joint
calibration-error law. Use each target's Cartesian rectangle as a conservative
outer set. It is neither a probability distribution nor evidence of simultaneous
favorable extremes across targets. Same-target source perturbations are common
to every arm; equal marginal widths do not define correlations or shared offsets.

Freeze each input's exact 009 closed displacement mask. Test the entire interval,
not just its center, against that mask and captured support. Reproduce the public
56/56 concentration intervals outside masks; this is not raw-state qualification.
No clipping, extrapolation, mask movement, jump interpolation or new inclusion.
Excluded rows remain visible and unscored. If full coverage or admission fails,
retain vertical-only/scalar calculations and finish unaffected operations.

## Declared observation reduction

009 read exact saved coordinates. 011 introduces the following separately tested
reduction; old qualification does not automatically qualify arbitrary queries.

* Production F3: unchanged `Trajectory.evaluate` (P0) or admitted
  `DiagnosticTrajectory.evaluate` (P1) at the labeled time, then the mathematical
  piecewise quadratic cell-average reconstruction of `profiles(public=False)`.
  The returned binary64 state, geometry and front are fixed inputs to this
  spatial reduction. Reconstruct the three native cell averages, split at all
  intersecting physical stencil faces and active/saturated/dry boundaries, and
  retain both one-sided limits and native boundary values. This does not recover
  ideal unrounded time-state values or certify their instantaneous accuracy.
* Production F4: compose the native two-cell `production_trace` linear functional
  with each retained BDF difference polynomial. Split at captured valid dense
  breakpoints and physical events, honor `dense_side` at exact knots, preserve
  both sides at first drip/exit. Underlying step extents do not extend valid
  support. The diagnostic spatial endpoint is not the native outlet channel.
* Comparator F3: use saved faces/liquid_cells at exact labeled times and the
  native `point_liquid` basis, including inlet/one-cell linear special cases and
  the local constant/linear/square-root integral reconstruction. Split at native
  stencil changes and retain both limits. All present figure times precede exit;
  no general post-exit spatial extension is introduced.
* Comparator F4: identify t/cup/front_trace by `accepted_columns`; use the entire
  accepted-step trace with zero before first drip, one until desaturation exit,
  then native front_trace. Exact knots and both event sides are preserved. The
  event-split linear interpolant is the discrete convention used in audit_run's
  independent cup integration. Verify cup consistency against its existing
  5e-12 criterion; this is not an instantaneous concentration error allowance.
* Fronts/arrival: retain original observable/event definitions and saved values;
  no concentration-threshold arrival. Preserve available event sides/bracketing
  metadata separately from any certified event-location error (unestablished).

Nominal reproduction: verify every historical saved observation exactly through
009 `observe`. Before horizontal propagation, require new native concentration
adapters to match all 14 included nominal values per arm within 1e-10 absolute,
zero relative tolerance. This is a roundoff-level identity check, not a scientific
acceptance limit. Isolate a failing operation, diagnose implementation before
claiming an evidence limitation; do not change targets, identity or tolerance.
Check both the native implementation and the declared mathematical reduction.
Readout failures remain local to their family and cannot rewrite a successful
archive admission; comparator temporal preparation is independent of spatial use.

## Full-range arithmetic and pairing

Coefficient construction, the three-constraint solves, square roots, evaluation
and subdivision use 60-digit Decimal interval arithmetic with directed lower/upper
rounding. Decimal's nearest-rounded square root is expanded by one Decimal step
on each side. Binary64 input floats are converted exactly; output conversions
are rounded outward. Local polynomial translation avoids global-power dependency
inflation. Reading coordinate endpoints are also rounded outward; physical
perturbation witnesses are moved inward if necessary to remain in the original
exact rectangle.
Physical spatial cuts use exact retained-float products in a 2200-digit context,
so binary64 rounding cannot truncate a neighboring stencil's one-sided limit.

On each piece, include endpoints/one-sided limits. Prove monotonicity with an
enclosing derivative where possible; otherwise use the intersection of natural
and centered mean-value interval forms and bisect. Every interior derivative root,
including a boundary-adjacent or multiple root, remains inside a subdivided region
until its full range is enclosed. No approximate root can be lost by a floating
root finder. Stop a region only when its complete enclosure lies within 1e-11 of
the currently demonstrated inner min/max bounds, or monotonicity proves endpoint
sufficiency. Return the enclosing boxes themselves, not a padded sample range.
Report residual overestimation and stationary brackets. A 100000-box/160-depth
guard returns unavailable, never a sampled substitute. These are computational
guards on the reduction, not trajectory budgets or acceptance thresholds.

For P0/C0, P1/C0, P0/C1, P1/C1 and refinements P1−P0/C1−C0, form the algebraic
direct difference on the union of both native piece boundaries, then enclose it.
At every union boundary also evaluate the direct native point difference with
each reader's own endpoint ownership, including overrides present in only one
arm and opposite dense-side conventions. Same-side limits alone do not suffice.
The publication ordinate cancels. Never subtract independently optimized ranges,
average arms or assume independent numerical errors. Each required individual
result remains visible even if a pair lacks common support. Scalar differences
use retained values. Empirical differences are sensitivities, not continuum bounds.

Retain piecewise enclosures where jumps occur. Their hull is conservative; values
in a gap are not claimed attainable. Arithmetic encloses this new mathematical
reduction only; it does not turn replay fidelity, an empirical refinement limit,
solver tolerance or a synthetic fixture allowance into continuum accuracy.

## Decisions, components and valid partial outcomes

For each included concentration row, reading residual is
`[model_min-(d+u_d), model_max-(d-u_d)]`. Also report the vertical-only interval
using the unchanged retained nominal value. Scalars use their publication reading
interval and retained model scalar. Arithmetic enclosure is included once.

For signed [L,U], absolute lower bound is zero if it contains zero, otherwise
min(|L|,|U|); upper bound is max(|L|,|U|). These are bounds, not claims of attainable
extrema. L>0 / U<0 gives positive/negative separation; otherwise unresolved.
Original inclusive limits remain concentration .015, front .008, arrival .025.
Absolute lower bound > limit means exceeded throughout; upper bound <= limit
means within throughout; otherwise threshold unresolved.

Reserve demonstrated threshold sensitivity for native evaluations at compatible
coordinate/ordinate witnesses giving both acceptable and unacceptable results.
An additional 1e-10 arithmetic guard on concentration witness classification
prevents a near-roundoff declaration; the guard is not a physical perturbation
or allowance added to the range. No such guard is needed for exact retained
scalar arithmetic. Failure to find two witnesses is not proof of insensitivity.
Concentration witnesses must also pass classification using an outward point
enclosure of the declared reduction with native boundary ownership.
Zero inclusion does not establish equality, equivalence, adequacy or reconciliation.

Component record: figure-reading widths are established source bounds; new range
arithmetic is outward enclosed; comparator temporal interpolation is explicitly
conditional; mesh/timestep/refinement differences are empirical sensitivities;
instantaneous readout and continuum errors are unestablished. No existing evidence
provides a justified new trajectory-wide numerical allowance, so expanded
enclosures are null with that reason, not equal to reading-only by assuming zero.
P1's certificate and cup consistency retain only their specific accepted scope.
No component is counted twice; no root-sum-square or independence assumption.

Execution order: verify immutable identities/population/nominal arithmetic (A),
save vertical/scalar results (B), independently admit all available inputs and
check native nominal reproduction (C), enclose horizontal/combined reading sets
(D), compute direct pairs and explicit-denominator summaries (E). No trajectory,
full reference, dense recovery, acquisition, source re-extraction, fitting or
qualification campaign is authorized. Archive/readout unavailability yields a
completed partial result with the smallest missing requirement named.

Synthetic verification covers constant/linear/quadratic functions, interior
extrema near boundaries, native stencils/one-sided limits, square-root endpoint,
valid versus underlying BDF support, physical event sides, full coverage failure,
common-coordinate cancellation, hull overlap without crossing, sign versus limit,
and equality at the inclusive historical limit. Normal unchanged repository QA,
hosted checks and independent review remain distinct from scientific findings.
Protected-target automated regression is QA only, never analysis/fitting/selection.

Deliver one additive bundle with all 124 original rows, every included disposition,
JSON/CSV, component/readout scope, pairs, reproduction, QA and review references.
Leave one PW PR draft/unmerged with auto-merge disabled. Preserve EWP, source
fixtures, historical solvers/results/receipts, mass/H1 findings and 010/#333.
No automatic successor, adoption, author contact or physical-validation claim.
