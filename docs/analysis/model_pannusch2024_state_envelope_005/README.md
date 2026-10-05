# Initial-state delivery envelopes and shared-state contrasts

MODEL-PANNUSCH2024-STATE-ENVELOPE-005 — G0 / NO_GOVERNING_PHYSICS_CHANGE /
RESEARCH_ONLY. PHYSICAL_VALIDATION=NOT_ESTABLISHED.

This is a fixed-model query of the existing Pannusch finite-volume operator.
It bounds interval delivery over explicitly assumed initial states and compares
two plans starting from the **same unknown state**. It supplies no state
estimator, fitted kinetics, profile optimizer, probability distribution, or
physical-validation claim. The prior runtime files, source parameters,
application defaults, registry and historical scientific decisions are unchanged.

## Public operations

Import the following from `puckworks.models.pannusch2024.state_envelope`:

1. `FVChemicalStateSet(lower, upper, total_inventory_kg, assumption_label,
   phase_inventory_kg=None)`: lower/upper are explicit existing
   `FVChemicalState.from_cell_averages` objects. Every liquid, fine and coarse
   cell is bounded. Total inventory is an explicit finite interval in kg;
   optional phase intervals are in liquid/fine/coarse order, also kg. The
   assumption label is mandatory. There is no plausible-coffee default or
   implicit equilibrium initialization.
2. `build_delivery_response(plan, solute=..., window_s=(a,b), grind=...,
   settings=FVEnvelopeSettings(...))`: build a reusable `FVDeliveryResponse`
   with one coefficient per canonical initial phase mass. It includes the
   original immutable `FVPlan`, source/model/basis identity, numerical settings,
   algorithm/source identity, work counts and arithmetic allowances.
3. `bound_delivery(states, response, epsilon_kg=...)`: minimize and maximize
   delivery. `contrast_deliveries(states, response_a, response_b,
   epsilon_kg=..., delta_kg=..., comparison_basis=...)` directly optimizes the
   difference over the same state set. Both return structured extrema, checked
   optimization evidence, candidate states and an outer interval.
4. `replay_extrema(result)` explicitly performs two forward calls for an
   envelope or four for a contrast and returns the final qualification and
   decision. Alternatively, call `replay_witness(states, response, witness)`
   once per witness/plan, then `qualify_envelope(...)` with both groups of
   fresh receipts. No trajectory is launched inside an LP objective.
5. `result.to_json()` emits canonical strict JSON with array hashes and no
   wall timing by default. `include_arrays=True` and `include_timing=True`
   explicitly include bulky arrays and nondeterministic performance data.

The small public-operations example is:

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 \
python examples/pannusch_state_envelope.py
```

Input and result arrays have immutable bytes backing, including optimizer and
reconstructed witness arrays. A response can serve another compatible set
without repeating propagation. Different species, geometry/source/configuration,
phase bases, mesh or starting clock cannot reuse it. Bounds from different
windows can have different witnesses and need not describe one trajectory.

## The declared set

With `W=A*dz`, capacities are

```
liquid: W*alpha_l
fine:   W*psi*(1-alpha_l)
coarse: W*phi_v2*(1-psi)*(1-alpha_l).
```

Fine capacity excludes phi_v2. Concentrations are kg/m^3 on their respective
source phase bases. Canonical order is all liquid masses, all fine masses,
then all coarse masses. The implementation uses the unchanged forward
capacity map, including its floating-point operation order. Concentration to
mass and witness reconstruction must remain representable; a positive quantity
cannot silently become numerical zero.

Let cell mass bounds be l,u, phase inventory bounds Lp,Up and total bounds
L,U. The set is exactly the intersection of those constraints. Its laminar
structure makes feasibility decidable without trusting a solver flag:

```
ap = max(sum_phase(l), Lp)     bp = min(sum_phase(u), Up)
all ap <= bp
max(L, sum(ap)) <= min(U, sum(bp)).
```

Omitted phase bounds leave the corresponding cell sums. These sums/comparisons
use exact rational arithmetic on the canonical binary64 mass bounds. Invalid
types/shapes/bases/identities are rejected; contradictory intersections return
`EMPTY_FEASIBLE_SET`. Numerical scaling, reconstruction or optimizer failures
return `NUMERICALLY_UNRESOLVED`, including a solver's infeasibility report that
conflicts with the established nonempty set. No constraints are widened or
dropped and no nominal state substitutes for U. An exactly zero-inventory set
is handled analytically with zero scale, never a 1 kg normalization floor.

## Response and optimization mathematics

For each original primary step, the existing augmented mass generator has a
zero outlet-accumulator column. Backward transpose exponential actions therefore
give `lambda_j=P_j.T*lambda_(j+1)+r_j`, with terminal lambda zero. The returned
physical coordinates are g, so exact discrete-model delivery is `S(m)=g.m`.
The uncertain state has only 3N mass coordinates, never a cumulative outlet
offset. For a partial overlap, an inactive suffix, active interval reward, and
inactive prefix all use that original step's frozen midpoint T/Q. The active
reward is integrated directly; no difference of large cumulative responses is
formed. Observations do not rebuild the primary plan.

One full and one split-action pass check fixed-operator arithmetic. Both keep
the original frozen forcing; constructing h/2 or h/4 plans is a separate
discretization comparison. Solute retains frozen-step interval accounting;
volume is `FlowHistory.integral(a,b)`. Concentration is delivery/volume in
**kg/m^3**, without a density or percent-TDS conversion. Zero-duration delivery
is zero with undefined concentration. Unrepresentable positive volumes,
deliveries, products or allowances fail explicitly.

HiGHS dual simplex minimizes both signs after scaling mass by the finite
feasible inventory upper bound and scaling the dimensionless objective. Every
original-coordinate cell, phase and total residual and objective is recomputed.
For normalized constraints `A*x<=b`, box `[l,u]`, and sign-checked dual y<=0,

```
r = c - A.T*y
dual lower bound = y.b + sum_i min(r_i*l_i, r_i*u_i).
```

This is a global lower bound for any such dual, even with a nonzero stationarity
residual. Its checked arithmetic allowance and a reconstructed feasible witness
bound the extremum. Thus a success flag or a small reported optimizer gap is
insufficient. Each extremum reports its complete interval, gap, optimizer gap,
response allowance, summation/conversion allowance, dual evidence, termination,
tolerances and counts. `OPTIMIZATION_QUALIFIED` means the bracket evidence was
checked; the parent query separately requires **both** complete gaps <=epsilon
and fresh witness replay before `NUMERICALLY_QUALIFIED`.

An explicit roundoff repair may clamp to the original cell box and rebalance
violated phase/total bounds within the predeclared small repair limit. Original
vectors/residuals, repair updates and mass change remain visible. The repaired
state is reconstructed through `from_cell_averages`, strictly checked against
the original set, and its objective recomputed. A rejected/unresolved witness
does not remove its region from U. The interval becomes unqualified. Positivity
and inventory provide a labelled `[0,M]` (or `[-M,M]` contrast) fallback; they
never certify a failed response or optimizer.

The [verification specification](VERIFICATION.md) gives the exact arithmetic
allowances, tolerances, synthetic cases and resource limits chosen before the
full comparison. These are computed engineering enclosures, not rigorous
interval-arithmetic certificates, statistical confidence intervals, promises
that every possible forward call completes, or continuum/physical accuracy.
Replays retain the unchanged parent's `accuracy_status=NOT_ASSESSED`.

## Shared-state decisions

The primary contrast uses `d=g_A-g_B` directly, including both response errors
and subtraction/dot-product allowances. Independent envelope subtraction is
not the contrast algorithm. `epsilon_kg` is a requested numerical extremum-gap
resolution. `delta_kg` is a separate declared material decision margin. Both
must be explicit; neither is measurement accuracy or a taste threshold.

`MATCHED_COLLECTED_VOLUME` checks both prescribed flow integrals and reports
their signed difference and a 64-epsilon relative arithmetic allowance.
`EXPLICIT_UNEQUAL_VOLUME` is required to admit a volume mismatch and remains
visible on the result; it earns no unqualified profile-superiority claim.

After numerical qualification, classification precedence is:

1. L>delta: `A_UNIFORMLY_EXCEEDS_B_BY_MARGIN`.
2. U<-delta: `B_UNIFORMLY_EXCEEDS_A_BY_MARGIN`.
3. `[L,U]` inside `[-delta,delta]`: `NO_MATERIAL_DIFFERENCE_THROUGHOUT_SET`.
4. Two feasible, freshly replayed, uncertainty-adjusted witnesses respectively
   above +delta and below -delta: `DEMONSTRATED_MATERIAL_REVERSAL`.
5. Otherwise: numerically qualified `NO_UNIFORM_MATERIAL_CONCLUSION`.

Numerical failure gives `NUMERICALLY_UNRESOLVED`. The underlying interval and
witness facts remain. Opposite-sign reversal relative to zero is an additional
reported fact, separate from material reversal. An enclosure crossing zero
alone establishes neither. A well-resolved range `[.2*delta,2*delta]` is a valid
no-uniform-conclusion outcome, not a numerical failure.

## Verification scope and preservation

Ordinary tests use N<=12. The separately invoked runner uses exactly one
predeclared caffeine/grind1.7 comparison, matched synthetic volumes, nonuniform
cell bounds and phase/total constraints. Temporal differences for A, B and
A-minus-B optimize **both signs over the whole original U**. N400/N800 uses
equal mass in each of two child cells and compares g400 with P.T*g800 over that
same N400 U. No independently enlarged N800 state set is used. Every temporal
level is reported; the default is not replaced by a favorable row. Refinement
disagreement is sensitivity evidence, not a rigorous continuum-error bound.

The historical 004 `resolved_temporal_decrease=FAIL` and
`IMPLEMENTED_QUALIFICATION_INCOMPLETE` remain unchanged. Its 28-case programme
was not rerun, restamped or repaired by this layer. Source inputs and original
observation access are recorded in [INTAKE.json](INTAKE.json): no originals were
newly inspected, acquired or scored; normal isolated silent integrity QA is
separate. Pannusch experimental kinetics and Schmieder raw fractions share one
lineage and are not independent datasets.

Source-derived reports retain Pannusch et al., DOI 10.1016/j.jfoodeng.2023.111887
and Pannusch/Schmieder Mendeley 10.17632/y2tz67f6ry.1 attribution and CC-BY-NC-3.0
rights separately from first-party code licensing. No EWP writes/runs, lock
change, release, merge, laboratory action, author contact or successor.
