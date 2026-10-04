# MODEL-PANNUSCH2024-STATEFUL-FV-004 frozen contract

G2 / NUMERICAL_METHOD_CHANGE, including an explicit initial-condition extension.
RESEARCH_ONLY; PHYSICAL_VALIDATION=NOT_ESTABLISHED. Runtime accuracy NOT_ASSESSED.
No governing balance, source parameter, geometry or constitutive-law change.

## Authority and decision

Puckworks base: `58b6cd2f29af3fa4372119ba59f8a6a1446369cc`, containing merged
PR #317. Read-only EWP main: `73ec476ffe6ac626705ca949e28b32935ddf2992`.
The owner EWP checkout remains on its original research branch. Live main,
recent commits, open issues/PRs, relevant remote branches and accessible owner
worktrees showed no overlapping stateful implementation. #313 is an open
issue for the already implemented temperature-only task. Original 001/002/003
CONTRACT, RESULTS and HANDOFF artifacts remain historical and byte-identical.

INTAKE.json records the three-test task-selection gate, scope, source identities
and verified reuse of the existing data preflight. This supplies supported
numerical initial-state/continuation operations absent from 003; existing
arbitrary-vector generator tests do not supply that interface. Success exposes
only the declared research capability. Failure leaves failed/unsupported
operations explicitly unqualified, with no rescue campaign or successor.
This does not resolve measured post-wetting chemical state, inventory
identifiability, experimental flow mapping or whole-shot coupling.

Only equations, geometry, source tables and code provenance are needed.
Relevant IDs: `pannusch2024/table2_params`, `pannusch2024/experimental_kinetics`,
and literal `pannusch2024 (Mendeley repo)`. Eight original MATLAB text
inspections from 001 are reused through their verified receipt hashes;
INTAKE.json names every original and hash. No original file is freshly inspected
or executed. Repository code/card/catalog metadata and retained EWP flow/input
mapping results were inspected. Schmieder fractions share lineage; they are not
independent observations. Unavailable external evidence is not nonexistent or
exhausted. No new corpus audit, assay use, fitting, protected comparison, lab
operation, source contact or dependency-lock update is authorized.

Pannusch et al., DOI 10.1016/j.jfoodeng.2023.111887 and Mendeley
10.17632/y2tz67f6ry.1 retain attribution. Source-derived reports retain
CC-BY-NC-3.0 separately from first-party code licensing.

## State and numerical contract

The unchanged FV balances evolve liquid/fine/coarse masses with clean inlet
FACE flux zero and positive-Q upwind outlet flux Q*c_l,last. Let W=A*L/N,
alpha_s1=psi*(1-alpha_l), alpha_s2=(1-psi)*(1-alpha_l). Capacities are
W*[alpha_l, alpha_s1, phi_v2*alpha_s2]. In particular fine capacity excludes
phi_v2 and coarse capacity includes it. Paired exchange fluxes, source K(T),
Sherwood h(T,Q/A), source geometry and all source species/grinds are unchanged.
Physical-field inventories are independently reconstructed using these bases.

`FVChemicalState.from_cell_averages` requires all three separately named
one-dimensional real finite nonnegative arrays and exact source mesh edges.
It binds species, grind, finite absolute model time, schema, kg/m^3 source
phase bases, source/configuration identities and CALLER_SUPPLIED provenance.
No broadcast, remesh, interpolation, missing-phase inference, equilibration,
clipping, redistribution or c_s0 cap occurs. Positive concentrations whose
mass conversion underflows to zero, and nonfinite/overflowed inventory, are
rejected before propagation. Structural admissibility is not physical
qualification. A source identity does not turn a supplied value into a measurement.

`source_equilibrium` explicitly supplies c_l=K(T(t0))*c_s0 and c_f=c_c=c_s0
using the same multiplication order as 003. The first liquid cell may be positive.
Source fitted c_s0 remains a reference/parameter, not arbitrary-state inventory.
Fresh states begin their own origin at state.time_s with collected mass/volume
zero. Offsets enter only through a checked checkpoint. Simultaneous state and
checkpoint inputs are rejected. Old API meanings, defaults and failure behavior
remain unchanged; the new result uses explicit segment/origin names and does
not redefine legacy M0_cont_kg, M0_fv_kg or outlet_solute_kg.

`FVPlan` retains the complete horizon, both histories, immutable settings,
original union-segment partition, exact primary endpoints and midpoint-frozen
Q/T. Each union segment uses ceil(duration/h_max) and linspace exactly as 003.
A requested stop selects an existing endpoint of this plan; it never clips and
rebuilds the schedule. Plan identity excludes passive observation/fraction
requests. Model/source/numerical compatibility, forcing/schedule identity and
request/report identity remain separate. Checkpoint index 137 is zero-based in
the endpoint array (137 completed steps); CASES records exact decimal, float
hex and plan identity for S and L. Small-mesh tests use shorter synthetic clocks.

The production method is still the same exponential midpoint mass generator.
For the stateful path only, every primary/partial exponential uses an outlet
accumulator initialized to zero; its phase-mass input is the exact saved raw
vector. The outlet column is zero, so this leaves the governing balances
unchanged. Each evolved interval delivery is retained as a separate term;
math.fsum forms local and origin totals. Full and restarted paths use this
same method, including the same remaining endpoints/frozen forcing. No outlet
mass is obtained from inventory complement, repaired fluxes or cancellation
of two large historical totals. Checkpoints retain the raw vector (including
its last interval accumulator), physical-field views, root initial state and
inventory, time/index, prior mass/volume terms, parent identity and full plan.

Fractions use stored complete-step deliveries and interval-local partial
exponentials with zero accumulator. An interior lower boundary uses the owning
step's frozen-operator state; its new increment is directly integrated, never
formed by subtracting large cumulative totals. Each panel belongs to one step;
checkpoint-boundary panels cannot be counted twice. Hydraulic volume is the
analytic FlowHistory integral over each local interval, with earlier terms
accounted separately. Adjacent portions recombine by mass and volume.
Requests starting before the continuation are rejected; no general query
service across checkpoints is provided. Zero-duration/zero-volume concentration
is absent with a reason. A truly zero root state remains zero and receives
VALID_NUMERICAL_ZERO for positive-volume fractions. A positive root state with
unresolved zero delivery remains unqualified, never promoted to exact zero.
No solid-phase monotonicity requirement exists: reverse transfer is permitted.

Primary propagation finishes before observers. Only wholly evaluated diagnostic
intervals enter the supported prefix. Sampled phase positivity, outlet delivery
monotonicity and independent interval/local/origin inventory are checked.
Export rejects an interior observation, an uncomputed/unchecked endpoint or
an inadmissible prefix. Raw negative numerical values within the frozen scaled
tolerance are retained without clipping or conversion through the fresh-state
constructor. A completed initial instant alone is not a primary-step checkpoint.
Resource failure remains distinct from a preselected PLANNED_STOP.

Same-schedule resume rejects changed forcing or plan identity. Explicit
`branch_stateful_fv` requires a new plan starting at checkpoint time with the
same mesh/backend/numerical settings. It preserves chemistry, root origin,
previous accounting, source identity and parent identity. A Q/T jump changes
coefficients only. Checkpoints are immutable, reusable and cache-free. Optional
serialization is bounded 32 MB versioned data-only strict JSON; duplicate keys,
nonfinite values, malformed identities and reconstructed-schedule mismatch are
rejected. Hashes detect corruption; they authenticate neither a physical
measurement nor a maliciously fabricated execution history. No pickle or payload
execution is used. No historical checkpoint migration is supported.

## Frozen matrix, scales and gates

CASES.json is executable authority: exactly 28 integrations (A8, B8, C2, D7,
E2, F1), four correction slots, hard ceiling32. All N400/grind1.7/0..30 s
and default FV settings except declared .04/.01 levels and N800. S and L use
explicit Celsius constructors and the exact brief histories. U is the exact
cell-average polynomial family in CASES, synthetic and nonequilibrium. The
common 86 observations and 17 fraction windows include both forcing-knot
families, primary checkpoints, interiors and crossing-checkpoint recombination.
References additionally observe the union of .04/.02/.01 primary endpoints.
No extra prefix, hidden reference, species/mesh/profile campaign or automatic
repeat is authorized. C's genuinely stopped checkpoint is reused by E.

A independently loads the pinned 003 source for four baseline calls; explicit
source-equilibrium calls supply the other four. B has four uninterrupted U/S
calls and four independent ordered concentration-exponential references.
C genuinely stops and resumes caffeine/U/S against B's uninterrupted run.
D has U/L default, .04, .01, actual-time Radau, N800, genuine prefix and suffix.
E branches C's checkpoint to future93 C /2.2e-6 m^3/s; its independent reference
starts from B's independent parent-reference fields at the exact checkpoint.
F repeats D.default in the exact environment and compares numerical arrays,
excluding wall time, request/report hashes and other runtime metadata.

References share unchanged source tables/geometry/closures only. They assemble
concentration balances, phase capacities/initial inventory, history ownership,
volume and comparisons independently. Candidate U uses integrated polynomial
primitives; reference U uses analytic polynomial averages. No candidate
initialization/generator/checkpoint/inventory helper supplies expected answers.
Radau uses rtol2e-12, concentration atol2e-14*C*, outlet atol2e-14*M*, max_step.02.
The 003 default reference behavior and historical evidence are preserved.

For supplied U, C*=max initial phase cell average and M*=independent physical
initial inventory; each checkpoint also has remaining-inventory/local-field
scales. Compatibility additionally uses legacy source c_s0. No moving maximum
or late-concentration denominator. Explicit zero/representability branches
replace division by zero. Every gate reports absolute errors and fixed scales:

- Equilibrium compatibility: each phase/outlet/mass/volume/resolvable fraction
  <=1e-12; implicit API also exercised by small tests.
- Same-schedule restart: exact timestamps/frozen forcing; each phase, outlet,
  local/origin mass/volume and fractions <=1e-12 on root and relevant local
  scales. Raw bitwise equality is desirable, not a cross-platform promise.
- U/S and branch/reference: each field/outlet/mass/fraction <=1e-8.
- Sampled primary/observer/diagnostic/quadrature phases and chronological
  outlet increments >=-1e-10 on fixed scales; no clipping.
- Independent initial, interval/local and origin inventory residual <=1e-8
  on corresponding nonzero inventory scale. Report signed initial/final/min/max
  and worst absolute residual; large historical totals cannot hide local errors.
- Analytic volume <=1e-12 on local/full volume scales.
- Independent numerical frozen-Q outlet-flux closure and GL8-GL4 for numerical
  and actual-prescribed-Q flux <=1e-6*M*. Preserve their distinct discrepancy.
- U/L default/finer and default/Radau each phase/outlet/mass/fraction <=5e-4.
  Report .04/.02/.01 separately; resolved aggregate error must decrease above
  fixed normalized floor1e-10. Prescribed-flow flux/Mout <=5e-4*M*.
- N400/N800: fractions <=.005*C*, mass and capacity-weighted absolute field
  differences <=.005*M*, with conservative pair averaging. This is bounded
  mesh sensitivity, not asymptotic order or physical/continuum validation.
- Exact-environment repeated numerical arrays equal. All mandatory small tests
  pass, including zero/depletion, all-species restart, adversarial defects,
  raw-state immutability, future-forcing rejection, tiny local delivery under
  huge earlier totals, checked-prefix failures and strict JSON.

## Execution and delivery

Use the existing task-wide Git-common-directory reservation/receipt pattern.
One worker, one BLAS thread; <=120 s per invocation and <=remaining allowance;
1800 aggregate qualification numerical wall-seconds. Baseline, prefix, suffix,
reference, branch, failed launch, correction and reviewer replay each count.
Changing output location cannot reset the budget. Reserve before launch and
preserve failed attempts. Ordinary regression/small N<=12 analytical/API tests
are separately identified and may not hide full qualification trajectories.
No fallback method, widened gate or outcome-selected execution. Resource
exhaustion yields an incomplete handoff, not a successor.

Freeze this contract and cases before the first full integration. One independent
exact-head review (nonhuman reviewer disclosed), not a G1/G3 scoring ceremony.
Only affected evidence reruns; unchanged-hash proof/addendum covers bounded
nonsemantic deltas. Existing minimum-governance circuit breaker applies.

Run applicable unprotected regression and registry checks, lint/types, package
and installed-wheel checks, strict JSON, privacy/path checks and generated docs.
Protected-target lanes and empirical/refit registry gates are excluded from task
execution. Full qualification stays outside ordinary CI. Update current card,
ROADMAP/SPRINTS, ledger/status and generated STATE_OF_TRUTH proportionately;
reconcile #317's merge without rewriting 003 historical text. Keep one feature
worktree/branch and one draft PR, unmerged with auto-merge disabled. EWP and
owner worktrees stay unchanged. No release, adoption, fitting, scoring, source
contact, laboratory operation or successor.

VERIFIED_ON_DECLARED_CASES requires every mandatory numerical gate. Otherwise
report IMPLEMENTED_QUALIFICATION_INCOMPLETE or the specific failure category.
Implementation, input-state checks, continuation, branching, temporal/mesh,
software QA, hosted CI and independent review receive separate dispositions.
Unavailable review/pending CI remain pending. Runtime accuracy NOT_ASSESSED;
PHYSICAL_VALIDATION=NOT_ESTABLISHED in every disposition.
