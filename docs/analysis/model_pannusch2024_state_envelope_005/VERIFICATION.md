# MODEL-PANNUSCH2024-STATE-ENVELOPE-005 verification specification

Prepared before implementation and before any full-mesh task execution.
G0 / NO_GOVERNING_PHYSICS_CHANGE / RESEARCH_ONLY.
PHYSICAL_VALIDATION=NOT_ESTABLISHED.

Base: Puckworks 28c32df8ed996043f943b777e9312016e8b5ce05,
tree 746e4c8970c57720d9c4b1dc51fcf40eee50a55c.
Read-only EWP remote main 73ec476ffe6ac626705ca949e28b32935ddf2992;
owner checkout 78cbd59c751393cddfe539e4c69e43a224329bca.
Normal clean baseline must pass before implementation.

## Scope and preflight

New information: fixed-model initial-state delivery bounds and direct contrasts
that cannot be inferred from existing scalar initial-inventory runs.
Decision consequence: qualified bounds support only conditional decisions over
the supplied set; a reversal, immaterial difference, threshold-straddling range
or unresolved computation is retained. No new profile search follows.
Grinder-to-cup link: a bounded query of the existing saturated chemical model;
no measured state recovery or integrated coupling claim.
Repeated blocker: no attempt to resolve experimental inventory identifiability,
source clock mapping, or independent physical validation by more simulation.
Lower-cost alternative: sparse response actions and linear programming, rather
than complete coordinate-wise forward trajectories.
Data preflight: G0, NOT_APPLICABLE to original observations. Existing parameter
tables and synthetic inputs suffice. Catalog entries inspected:
pannusch2024/table2_params, pannusch2024/experimental_kinetics,
schmieder2023/raw_fractions. The last two share lineage. No new originals,
observations, external corpus census, acquisition, fitting or target scoring.

## Algorithms and units

Mass order is all liquid, all fine, all coarse cells, in kg. Concentrations are
kg/m^3 on separate source phase bases. Capacities use A*dz times alpha_l,
psi*(1-alpha_l), phi_v2*(1-psi)*(1-alpha_l); fine excludes phi_v2.
State sets intersect explicit cell boxes with total and optional phase mass
intervals. Malformed inputs, proven empty intersections and numerical
unrepresentability remain distinct. No nominal substitution or constraint
widening. Genuine zero inventory has no artificial normalization floor.

Responses use the existing augmented sparse generator transposed backward
through FVPlan.primary_steps. The last coordinate is an interval-local outlet
reward, reset at original step boundaries. A partial reward is integrated over
its overlap directly, with the original step's frozen midpoint forcing. No
cumulative-response subtraction. A second action pass bisects actions while
retaining that exact generator. No finer FVPlan is used for arithmetic checks.
FlowHistory.integral supplies volume. Concentration is kg/m^3, never percent TDS.

HiGHS minimizes both signs, scaling masses by the finite feasible inventory
upper bound; all-zero sets are explicit. Independent residual and objective
recomputations use original units and compensated sums. Global lower objective
evidence uses sign-checked inequality duals and a finite-box support bound on
the stationarity residual, so optimizer success alone cannot qualify a bound.
Both extrema retain intervals and gaps, solver status and work counts. Failure
retains an explicit unresolved result and, if applicable, a labelled inventory
fallback. Primary witnesses are reconstructed through from_cell_averages and
explicitly replayed through simulate_stateful_fv. Contrast witnesses replay both
plans from the identical state. Internal sensitivity LPs require no trajectory.

Engineering arithmetic allowances are computed independently of the old 004
allowances. Response split discrepancy and a binary64 action/conditioning
allowance, LP dual residual allowance, summation/conversion allowance, replay
discrepancy and discretization sensitivity are separate fields. The requested
gap includes allowances, not merely solver primal/dual distance. These are not
rigorous interval arithmetic or continuum/physical accuracy certificates.

The implemented response coefficient allowance is the absolute difference
between the one-action and two-half-action passes plus
`128*eps*(1 + action_count + sum(dt*||B||_1))`, rounded upward. Its dimensionless
scale 1 is the exact positivity/inventory response bound. Both passes count.
The LP primal/dual tolerances are 1e-9, with 10000 iterations and 30 seconds per
solve. The mass scale is the outward-rounded finite feasible inventory upper
bound; zero is separate. Inequality duals are explicitly projected to y<=0;
the finite-box support of c-A^T*y supplies the checked global lower bound.
The dual allowance is `128*eps*(row_count+2)` times the sum of absolute dual
objective terms and coordinate-wise objective/dual magnitudes weighted by the
scaled box upper bounds; it also covers scaling/conversion arithmetic. Dot
products use compensated sums and `64*eps*sum(abs(g_i*m_i))`. Underflow of a
positive product or allowance is unresolved. Reconstruction checks all original
constraints; a bounded, explicit box clamp and phase/total rebalance is allowed
only within 8 times the declared primal tolerance on the inventory scale, with
the original vector/residuals retained and the final state strictly rechecked.
It never widens U. Every repaired objective is recomputed.
Replay arithmetic allowance is `256*eps*(1 + forward_actions + response_conditioning_sum)*M`;
it checks the forward comparison and is not a whole-set discretization bound.
Direct contrasts retain both response allowances and subtraction allowances.

## Small offline cases (N <= 12)

1. All four source species, grinds 1.4/1.7/2.0, singleton non-equilibrium depth
   profiles, nonzero model origins, genuinely zero and very small inventory.
2. Independent dense concentration-balance assembly converted to mass bases:
   capacities, packing, backward order, full/partial rewards. No densification
   of the candidate generator as the reference. Existing rate seams give
   no-exchange, advection-only and zero-advection checks.
3. Inventory-only analytical optima, mixed and redundant phase constraints,
   collapsed bounds, incompatible/empty intersections, independently checked
   original-coordinate primal and dual evidence.
4. Two-active-coordinate fixtures: (0.8,0.6)-(0.6,0.4) with shared sum M yields
   exactly 0.2*M; (0.8,0.2)-(0.2,0.8) yields opposite-sign feasible witnesses.
   Also identical plans, below-margin differences and [0.2*delta,2*delta].
5. Window additivity on one unchanged plan, zero/short/off-grid windows,
   unequal temperature/flow knots, jumps/ramps, immutable arrays and inputs,
   identity mismatch, booleans/nonfinite/underflow/overflow, solver and response
   limits/failures, and requested gaps below arithmetic resolution.
6. Every individual g lies in [0,1] within its computed arithmetic allowance;
   failed checks are unresolved, never hidden by an inventory fallback.

Dense/sparse and singleton replay differences must fit their reported computed
allowances and be <=1e-11 on the nonzero inventory scale. Analytical optimization
differences <=1e-10 on M. Exact-zero tests require exact zero. Each reported
extremum interval must contain its independent reference. Hostile-input tests
must fail closed. No tolerance will be enlarged after full-mesh results.

## One representative full-mesh case

Caffeine, grind 1.7, source geometry, t=7..17 seconds; window [7,17].
A: linear flow knots (7,10,17), values (1.2,2.7,1.8)e-6 m^3/s;
   linear Celsius knots (7,11,17), values (80,96,87).
B: constant flow 2.16e-6 m^3/s on [7,17];
   linear Celsius knots (7,9.5,17), values (96,84,92).
Both prescribed volumes are 21.6e-6 m^3. Match tolerance 64*machine-epsilon
times the larger volume, with actual signed volume mismatch reported.

At each cell center x=z/L, lower concentrations are
(.2+.5*x, .2+.4*x, .5+.3*x); upper concentrations are
(3+3*x, 8-3*x, 8+2*x), all kg/m^3.
Total inventory interval [8e-5,1.2e-4] kg; phase intervals
liquid [8e-6,3e-5], fine [1e-5,5e-5], coarse [2e-5,8e-5] kg.
This is an explicit synthetic assumption, not a plausible coffee-state prior.
Numerical gap epsilon=1e-9 kg; material margin delta=1e-6 kg. Neither is
measurement accuracy or a taste threshold. No parameter/profile search.

Default h=.02 s, then h/2=.01 and h/4=.005, all N400; retain every row and the
default result. For each adjacent temporal pair optimize both signs of
g_h-g_hfine over the same U, for A, B and the direct A-B contrast.
N800 at h=.02: lift each N400 phase mass equally into its two child cells;
P preserves inventory and phase allocation. Compare g400 with P^T*g800 over
the original N400 U; no enlarged N800 uncertainty set. Sensitivity is reported
without turning refinement disagreement into a continuum-error certificate or
requiring one profile to win.

Primary reported default witnesses: A minimum/maximum, B minimum/maximum,
and contrast minimum/maximum (both plans replay each contrast witness).
Each must satisfy original-coordinate feasibility checks and response/replay
allowances with fresh unchanged forward calls. Replayed uncertainty-adjusted
signs are required for a reversal claim. Numerical quality and material
classification remain separate. Uniform material A, uniform material B,
uniformly immaterial, demonstrated material reversal, then qualified
NO_UNIFORM_MATERIAL_CONCLUSION is the precedence after numerical qualification.
Opposite-sign reversal relative to zero is an additional fact.

## Resource limits and timing

Planned full-mesh executions: 16 response passes (two fixed-operator passes
for each A/B at the three N400 timesteps and N800 default), eight primary
witness trajectories, one unchanged representative forward baseline and its
final same-machine repeat, and two passes for a final repeat of the default A
response with its envelope query: 28. At most 28 planned plus four named correction
executions, hard total 32 including failures/repeats/references.
Aggregate numerical wall limit 1800 seconds; forward per-call limit <=120 s.
The runner reserves executions before launch and charges failures. An outer
deadline stops overruns. It cannot reset by changing evidence directories.
OPENBLAS_NUM_THREADS=OMP_NUM_THREADS=MKL_NUM_THREADS=1. Record exponential
actions, forward and LP calls, wall time, peak resident memory and environment.
Sparse full-mesh actions only. No dense transition matrix or coordinate-wise
trajectories. Ordinary QA is separately logged; no hidden campaign in tests.

Response/envelope same-machine timing is reported for the first default-A
build/query and its final repeat, with correctness checks included. There is
no pre-existing envelope implementation to benchmark; the preimplementation
baseline is the unchanged representative forward case. No speedup claim.

## Handoff and acceptance

All mandatory implementation and verification properties, ordinary regression,
Ruff/mypy, packaging/wheel smoke and required hosted CI must be reported
separately. ENGINEERING_CAPABILITY_VERIFIED requires all mandatory checks;
otherwise report an explicit incomplete disposition. Preserve 004's
resolved_temporal_decrease=FAIL and IMPLEMENTED_QUALIFICATION_INCOMPLETE.
No rerun/restamp of its 28-case programme. Preserve all existing runtime and
parameter bytes, historical decisions, application defaults and EWP lock.
One feature branch, one draft PR, auto-merge disabled; no merge or successor.
