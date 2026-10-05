# MODEL-PANNUSCH2024-PREFIX-CONDITIONED-006

Pre-execution specification. G0 / NO_GOVERNING_PHYSICS_CHANGE / RESEARCH_ONLY.
PHYSICAL_VALIDATION=NOT_ESTABLISHED. No real-data scoring or successor.

## Scope and preflight

New information: a checked joint inverse query for depth-resolved starting phase
states, preserving correlations when bounding one finite later fraction.
Positive outcome permits this research query; negative or unresolved evidence
limits its qualification, without selecting another task. This supports a
conditional chemical-delivery query, not integrated grinder-to-cup prediction.
It does not resolve the repeated experimental inventory, flow-clock or
independent-validation blockers. Earlier empirical two-assay predictors exist;
this is not the programme's first early-to-late predictor and reverses no
MASS-DELIVERY result. Sparse transpose responses plus small LPs avoid one forward
trajectory per coordinate. The owner explicitly selected this bounded G0 work.

Original-observation access: NOT_NEEDED_FOR_SYNTHETIC_G0. Metadata only:
pannusch2024/experimental_kinetics and schmieder2023/raw_fractions share lineage
and prior source-internal/target exposure. No original observations inspected,
no source acquisition, no historical flow mapping, no corpus-exhaustion claim.
EWP's retained input-mapping and flow-history results remain controlling at their
scope: NO_QUALIFIED_MAPPING and FLOW_AUTHORITY_INELIGIBLE.

Live main is Puckworks 4f652dee3a43e9e97dc555173cb469d424cdc69a, tree
c17082884871e0a37dced8598560b191c8425da1; EWP read-only main is
73ec476ffe6ac626705ca949e28b32935ddf2992, tree
8ced37ad5b294616b8935d92a57e3845321d5eed. Both match the supplied review.
Puckworks #318 and #319 are merged. No prefix-conditioned branch/PR/capability
was found at intake. A new isolated branch starts at that main. EWP refs were
fetched into the Puckworks object store; no EWP worktree, refs or code were
written or executed. Other owner worktrees remain untouched.

The exact-base post-merge quick-pr run 37251064663 had a cancelled coverage
job, while Python 3.10–3.13, min-deps and mypy passed. One rerun of its failed
job was requested; actual outcome and clean local baseline are separate QA
receipts. Cancelled infrastructure is not a scientific failure.

## Numerical contract

Canonical variables m are nonnegative liquid, fine, coarse cell masses in kg.
U retains all original cell boxes and phase/total intervals and their provenance.
The supplied immutable original plan, model/source/configuration, phase bases,
mesh and absolute clock bind every response. Native 005 responses are reused
without editing state_envelope.py or any forward/parameter/default source.
Observations bind unique labels, positive finite windows [a,b), finite kg bands,
response/model/plan identities and an explicit provenance/assumption label.
They contain already specified masses: no assay conversion or inferred precision.
At most 32 observations; list/tuple inputs only, validated before allocation.
Duplicates with distinct labels, overlaps and reorderings retain all constraints;
canonical sorting makes order immaterial. Shared boundaries do not overlap.
Every early window ends by the target start. No target value is an input.

For each computed response g and nonnegative engineering allowance a:
|S(m)-g'm| <= a'm. Exact rational accumulation of binary64 inputs checks rows,
objectives and dual evidence. Coefficient sums/subtractions and conversion back
to binary64 round outwards for outer constraints and inwards for sufficient
checks. Positive underflow, nonfinite values and failed reconstructions are
visible numerical failures, never deleted constraints. Additional representable
scaling, summation/conversion and replay allowances are exposed separately.
The inherited response allowances are engineering estimates, not rigorous
interval-arithmetic, continuum or unconditional physical certificates, and
not statistical confidence intervals.

Outer rows: (g-a)'m <= u, -(g+a)'m <= -l.
Inner rows: (g+a)'m <= u, -(g-a)'m <= -l.
Both intersect ALL U constraints. Thus, under the declared allowance contract,
U_inner subset U_compatible subset U_outer. Ignoring unknown joint error
dependence is a conservative relaxation, not statistical independence. Inner
emptiness never establishes incompatibility; outer nonemptiness never establishes
an exact-model compatible state. Coordinate boxes do not replace this joint set.

HiGHS uses the finite inventory upper bound as mass scale (no 1 kg floor).
Genuine zero is analytic. A phase-I LP minimizes nonnegative common violation t
in A*m-t <= b with finite box bounds. Incompatibility requires its independently
checked lower bound to be strictly positive, including arithmetic; solver status
2 is insufficient. Otherwise feasibility remains unresolved until a candidate
is checked. Every LP retains status, work, scale, raw residuals and dual evidence.
For A*m<=b, finite box [L,H], y<=0, the exact binary-rational check evaluates
D=y'b+sum min((c-A'y)_i L_i,(c-A'y)_i H_i), then rounds down. This includes ALL
observation rows and does not depend on the solver-reported gap. Dual signs and
objective reconstruction are checked independently in original kg coordinates.

For the target, minimize g_f-a_f and minimize -(g_f+a_f) on U_outer. Separate
inner searches find candidates. Each candidate is reconstructed by
FVChemicalState.from_cell_averages and checked again in representable kg
coordinates. Raw vectors/residuals are retained. The optional bounded repair
re-solves with explicitly inward margins on ALL noncollapsed rows/boxes and
rechecks ALL constraints; no old phase-rebalancing repair is used. Repair can
fail honestly. A compatible witness supplies the attainable side only:
minimum [global lower, witness upper], maximum [witness lower, global upper].
QUALIFIED requires BOTH complete widths <= positive caller epsilon, all original
constraints, every observation and both fresh forward witness checks/replays.
Compatibility and tight-extremum qualification are separate statuses.

All early and target windows are batched through unchanged simulate_stateful_fv
on the original plan from each accepted state. Direct local mass accounting,
no cumulative subtraction or assay-time regridding. Replay discrepancy, actions,
allowances, identities and inherited accuracy NOT_ASSESSED remain visible.
A replay uncertainty interval must be contained in every observation band;
overlap alone is insufficient. Brackets include the hull of prediction/replay
uncertainties. Unresolved witnesses never become compatible extremizers.
Empty observations delegate directly to 005 bound_delivery/replay_extrema,
including failures, without new propagation. A valid fallback retains its own
qualification and cannot certify failed conditioning.

Conservation-only comparator: [0,Mmax-sum(l_j)] using a deterministic disjoint
subset of windows (weighted interval scheduling, maximizing summed lower
bounds), exact accumulation and outward conversion. No kinetic responses enter
this comparator. Overlaps/duplicates are not double-counted. It is a conservative
bound, not necessarily the tightest union bound. A negative upper bound is a
conservation contradiction, never clipped to zero.

## Tests and representative campaign

Ordinary tests use N<=12. Exact analytical core fixture: M=2^-10 kg,
simplex sum(m)=M, early=(1/2,1/4,0), band=[M/4,M/4],
future=(1/2,1/4,1/8), zero response error ONLY for this exact fixture.
Compatible states (t,M-2t,t), 0<=t<=M/2. Unconditioned [M/8,M/2],
conditioned [M/4,5M/16], endpoint witnesses (0,M,0),(M/2,0,M/2),
conservation [0,3M/4]. No unique-state or experimental-validation inference.
Independent rational/vertex and dense-equation references; analytical errors
<=1e-10*M and response/replay errors <=1e-11*M as well as declared allowances.
Adversarial, joint-infeasible, nonzero-error, underflow, solver/replay-failure,
identity, immutability and honest-resolution tests precede full-mesh execution.
No tolerance is loosened after full-mesh results.

Only history A and U from 005 VERIFICATION.md are copied: caffeine, grind 1.7,
source geometry; Q linear (7,10,17)/(1.2,2.7,1.8)e-6 m^3/s;
T linear Celsius (7,11,17)/(80,96,87). Coarse N400 cell-center x=z/L:
lower (.2+.5x,.2+.4x,.5+.3x), upper (3+3x,8-3x,8+2x) kg/m^3;
total [8e-5,1.2e-4], liquid [8e-6,3e-5], fine [1e-5,5e-5],
coarse [2e-5,8e-5] kg. Explicit synthetic assumptions, no coffee prior.
Generator: each phase interpolates its original lower/upper fields to the
midpoint of its feasible phase inventory interval; a common interpolation of
phase targets toward feasible lower/upper endpoints reaches total midpoint
1e-4 kg. The field interpolation is then recomputed for those phase targets. Construction
uses only U, is checked before simulation, and actual arrays are retained.
Early [7,10),[10,12); target [12,17). One N400/h=.02 unchanged forward requests
ONLY early fractions; freeze actual s_j and bands [max(0,s_j-d),s_j+d],
d=.01*U.inventory_scale_kg, before any future optimization. Synthetic width is
not assay precision. Epsilon=1e-9 kg.

Evaluate N400 h=.02,.01,.005 and N800 h=.02. Same physical history, U, bands,
windows at all levels. Fine states P*m split each coarse phase mass equally into
two children. Explicit separate pulled-back response P^T*g800 with |P|^T*a800
and conversion allowance; native fine response identity remains intact. Fine
replay uses P*m, and no independent fine-cell freedom is introduced. Report all
bounds/gaps/replays and endpoint/width sensitivities, including unresolved or
compatibility changes. No continuum certificate or monotonicity requirement;
004 IMPLEMENTED_QUALIFICATION_INCOMPLETE/resolved_temporal_decrease=FAIL remains.

Planned: 24 backward passes (3 windows x 2 passes x 4 levels), one generating
trajectory, eight conditioned witness trajectories = 33 propagations; zero
reference/repeat trajectories. At each level: baseline 2 LPs, phase I 1, outer
2, inner 2, at most 2 bounded all-row repair LPs = at most 36 planned LPs.
Reserve only for named bounded corrections; hard campaign caps 64 propagation
executions, 160 LP calls, 1800 s aggregate numerical wall, 120 s per propagation,
30 s per LP. External parent deadlines kill overruns. Every failed call is
charged before launch. Exponential actions count individually (including split
and fraction accounting). One persistent Git-common-directory receipt prevents
reset by output/worktree changes. All three BLAS/OpenMP thread settings are 1.
Normal tests/CI are separately accounted. No full-mesh densification or sweep.

## Handoff limits

One draft Puckworks PR, unmerged, auto-merge disabled. Software QA, numerical
qualification, ordinary review, hosted CI and scientific ceilings are separate.
ENGINEERING_CAPABILITY_VERIFIED requires mandatory capability tests AND the
representative fixed-operator query to qualify; otherwise report
IMPLEMENTED_QUALIFICATION_INCOMPLETE. No empirical advantage is established.
Existing first-party licensing remains distinct from Pannusch/Schmieder
source-derived CC-BY-NC-3.0 (DOI 10.1016/j.jfoodeng.2023.111887;
Mendeley 10.17632/y2tz67f6ry.1). No EWP writes/runs, release, lab or successor.

## Final small-test implementation details (before full-mesh execution)

Independent LP checking uses exact binary-rational sums and products; underflow
of any nonzero intermediate product or directed conversion returns unresolved.
The certificate has no hidden absolute tolerance. HiGHS uses 1e-9 primal/dual
tolerances, at most 10000 iterations and 30 s; these tolerances NEVER certify
primal feasibility or a contradiction. Scaling errors are recorded; the weak
dual certificate uses original coordinates regardless of normalized LP rounding.

For witness search only, each observation allowance is augmented by the
coefficient `512*eps*(1+max_forward_actions+response_conditioning_sum)`. This
reserves both response/forward discrepancy and the complete forward interval
using the plan's finite action limit. It is an explicitly conservative loss of
tightness; all outer rows and original bands stay unchanged. The full bracket
includes the resulting feasible-side distance. No sampling or best-fit claim.

If representable reconstruction fails, one all-row inward LP may search within
`64*primal_tolerance*M/(2*dimension)` of each raw coordinate, with total mass
change capped at `64*primal_tolerance*M`. Original noncollapsed boxes move
inwards by at most `1024*eps*M/dimension`; each non-equality row by
`1024*eps*M`. Exact opposing equality rows remain equalities. Every result is
reconstructed and rechecked against ALL original/sufficient observation rows.
Failure remains unresolved. This repairs floating-point representation only;
it is not calibration, regularization, or a replacement for U.

Small-test development exposed and corrected a repair search that could move
degenerate optima beyond its declared mass-change limit. The attempted witnesses
were rejected, not accepted. An overly tight repair variant returned unresolved
and was corrected before full-mesh execution. No full-mesh results or tolerance
relaxations informed these corrections.

## Retained post-execution bounded correction

The original specification and producer identities remain in PRE_EXECUTION.json.
JOINT_REPAIR_CORRECTION.json records a correction after the first four queries
left all witnesses unresolved. Actual sufficient inner rows are now stored
separately from the stricter replay-reserve search rows. Before the one all-row
repair LP, a bounded concentration-box projection may propose a candidate; it
performs no phase/total rebalancing and is accepted only after exact checks of
ALL original U and actual sufficient observation rows, representable reconstruction
and the same mass-change cap. The unchanged observations, response allowances,
LP tolerances and complete-gap epsilon remain controlling. Small regression
tests precede the corrected full queries; cached native responses and frozen
bands are reused. Initial failures remain in INITIAL_RESULTS.json.
