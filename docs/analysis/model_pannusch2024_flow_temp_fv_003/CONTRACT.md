# MODEL-PANNUSCH2024-FLOW-TEMP-FV-003 frozen contract

G2 / NUMERICAL_METHOD_CHANGE. RESEARCH_ONLY.
PHYSICAL_VALIDATION=NOT_ESTABLISHED. One additive research capability, one
feature branch and one draft PR. No merge or automatic successor.

## Intake, source authority and preservation

Reviewed and live Puckworks main: `1d780b7fb57df4693e22e564010c891602df119d`.
Read-only EWP main: `73ec476ffe6ac626705ca949e28b32935ddf2992`.
Open issues/PRs, remote branches and accessible registered worktrees were checked:
no active overlapping implementation or material dependency drift. Owner checkouts
are preserved. 001 merged as `1e9f85a5e42d206baf05a0a95aa81847d506c9d5`
(PR314); 002 merged as the Puckworks base (PR315). Historical result/receipt
wording stays unchanged; only current lifecycle metadata is reconciled.

NEW_INFORMATION: independent FV calculations under joint prescribed flow and
uniform temperature, including conservative transfer/outlet accounting and
volume-weighted observations; fixed-flow FV and the nodal adapter do not supply it.
DECISION_IF_POSITIVE: expose this explicit research API within reported numerical
qualification; replay/coupling requires a separate decision and qualified inputs.
DECISION_IF_NEGATIVE_OR_INCOMPLETE: retain fixed-flow FV and name failed properties;
no alternative model or successor is selected.
GRINDER_TO_CUP_LINK: missing prescribed-flow extraction component only; material,
hydraulic, thermal and chemical-state coupling remains unestablished.
REPEATED_BLOCKER: this tests numerical capability, not the previously ineligible
experimental flow mapping. No new measurement or general data-gap claim.
LOWER_COST_ALTERNATIVE: nodal reuse does not establish FV positivity/accounting;
a volume clock alone does not reproduce differing transport/transfer Q powers.

Reuse the scoped 001 DATA_PREFLIGHT and SOURCE_IDENTITIES by hash (INTAKE.json).
Canonical IDs: `pannusch2024/table2_params`,
`pannusch2024/experimental_kinetics`, literal `pannusch2024 (Mendeley repo)`.
Only equations, source geometry, grind entries and parameter authority are used.
This task inspected the card, parameter/closure/solver code, provenance and catalog
metadata. Original MATLAB text inspections are reused from 001 by hash; no fresh
original-file inspection, native execution or assay access is claimed. The
established external resolver remains the route if original access becomes needed.
EWP FLOW_AUTHORITY_INELIGIBLE and input-mapping restrictions remain unchanged:
programmed endpoints and beverage-mass derivatives are not inlet histories.
Pannusch et al., DOI 10.1016/j.jfoodeng.2023.111887 and Mendeley
10.17632/y2tz67f6ry.1 retain attribution. Source-derived output treatment is
CC-BY-NC-3.0, separately from first-party software licensing.

No legacy API/arithmetic, source coefficient, constitutive law, geometry, registry,
production default, dependency lock, 001 INCOMPLETE or 002 declared-case VERIFIED
result is changed. No EWP writes, OpenFOAM, empirical scoring, fitting, optimization,
protected-target access, laboratory operation or author contact.

## Mathematical contract

Independent explicit histories supply Q in [1e-6,3e-6] m^3/s and spatially uniform
T in [353.15,371.15] K. Species: caffeine, trigonelline, 5CQA, tds; only existing
grinds, fixed source geometry throughout. No pauses/reversal, pressure conversion,
density reinterpretation, inferred experimental clock, preinfusion, thermal field,
dispersion, new kinetics or feedback.

Let dz=L/N, W=A*dz, as1=psi*(1-alpha_l), as2=(1-psi)*(1-alpha_l).
Source K=K(T), h1/h2=h1/h2(T,Q/A); k1=6*h1/d1,
k2=6*h2/(phi_v2*d2). Superficial q=Q/A enters Reynolds; interstitial
v=Q/(A*alpha_l) enters advection. Evolve cell masses:
ml=W*alpha_l*cl, m1=W*as1*cs1, m2=W*phi_v2*as2*cs2.
F0=0 and F[j+1]=Q*cl[j]. Paired transfers:
R1=W*as1*k1*(K*cs1-cl), R2=W*phi_v2*as2*k2*(K*cs2-cl).
ml'=Fleft-Fright+R1+R2; m1'=-R1; m2'=-R2; Mout'=F[N].

The mass generator has donor transitions to next liquid/outlet at
Q/(W*alpha_l), liquid to fine/coarse at as1*k1/alpha_l and
phi_v2*as2*k2/alpha_l, and fine/coarse to liquid at K*k1 and K*k2.
Each nonnegative transition inserts +r in the receiver and -r on the donor
diagonal. Thus off-diagonals are nonnegative and every column sums to zero,
including the zero outlet column. exp(dt*B) is nonnegative and column stochastic
in exact arithmetic; paired exchanges cancel, face fluxes telescope and Mout
is nondecreasing. Floating-point sampling checks are separate from this proof.
Never calculate or repair Mout by inventory complement.

At explicit t0 initialize ONCE: cl=K(T(t0))*c_s0, cs1=cs2=c_s0,
Mout=0, V=0. M0=A*L*c_s0*(alpha_l*K(T(t0))+as1+phi_v2*as2).
The first liquid cell holds its equilibrium average; clean inlet is a face
condition. Carry every phase and Mout continuously through knots. Fitted c_s0
is not independently measured recoverable inventory.

V(t)=integral(t0,t,Q); C[a,b]=(Mout(b)-Mout(a))/integral(a,b,Q).
Volume is outside the mass vector and integrated analytically, interval-locally,
including tiny/delayed windows. Recombination uses mass and volume, not duration.

## API, propagation and diagnostics

New module `flow_temperature_history_fv.py`, immutable model-local FlowHistory,
unchanged TemperatureHistory and FVSettings. Flow supports explicit constant
intervals and linear knots, strictly increasing finite real clocks, correct
value counts, finite real in-domain SI values. Reject complex/nonfinite/malformed
arrays, other units, callables and implicit endpoint holds before integration.
Constant intervals are left-closed/right-open; the last endpoint belongs to the
last interval. Duplicate times cannot encode jumps. Both histories independently
cover the model interval, including t0 inside support. integral(a,a)=0;
reversed/out-of-support bounds fail. No extrapolation.

Primary partitions are the sorted union of both histories' knots and model
endpoints, each segment split using ceil(duration/h_max). Segment-local forcing
owns both one-sided endpoints; no coefficient leaks backwards over jumps.
First-order spatial upwind, exponential midpoint only: freeze both T and Q at
one midpoint and propagate the same B and its outlet accumulator. Local exact
(T,Q) cache only; no rounded flow keys or cross-run mutable cache. No mutation
of the old fixed-Q system. Finish primary propagation before observers.
Interior observers use partial exponentials of that SAME frozen operator from
the saved step start, never query-specific midpoints, interpolation or resets.
One carried physical state at a knot; prescribed T/Q metadata can jump.
Analytic partial volume generally differs from Qmid*(t-a), even though the
full linear-flow step volume is Qmid*(b-a).

Retain named numerical frozen-step flux Qmid*c_h,out and prescribed-flow
diagnostic flux Q(t)*c_h,out. Independently GL4/GL8 integrate both on each primary
interval and partial panels ending at requested interior observations/fractions.
Partial panels always start at their owning primary step start. Prefix sums
use only full panels; partial panels are added to their prefix, never double
counted. Both diagnostics use approximate c_h, not an independent exact solution.
Retain panel support, raw flux, weights, inventory and minima at quadrature nodes.
Reconstruct capacities and inventory independently from physical phase fields.

Results retain histories, sampled and frozen forcing, physical cell averages,
geometry/capacities, outlet trace/Mout, prescribed volume, fractions, prefix,
settings, failures and code/source/configuration identities (all runtime/history
modules). Immutable arrays and strict JSON; no NaN/Infinity. Failed admissibility
or unresolved mass differences suppress public concentrations, retaining finite
raw diagnostics. Unsupported observations/fractions carry reasons and nulls;
known forcing volume is not supported solute output. No clipping, redistribution,
monotonization, zero-filled failures or correction flux.

## Frozen cases and engineering budgets

CASES.json freezes exactly 32 executions: A eight fixed-Q new/old comparators;
B eight joint-step candidate/independent ordered exponentials; C eight caffeine
up/down .04/.02/.01 and actual-time Radau; D four spatial runs (reuse N400);
E one exact-environment repeat; F three passive meshes. All source runs span
0..30 s, grind1.7, N400 unless stated, nominal h=.02, diagnostics .0125.
Histories, observers, fraction bounds, derived windows and resource exceptions
are in CASES. They are synthetic, not experimental reconstructions. No new
profile, mesh, species, method or outcome-selected sweep. Freeze precedes full
qualification; N<=12 synthetic/algebraic tests may precede freeze.

Independent reference operators assemble concentration balances directly,
sharing unchanged source parameters, geometry and closures only. History
segmentation/evaluation and volume integration are independently implemented.
Ordered step exponentials carry state across the independent union; small dense
expm and noncommuting order checks are separate. Actual-time Radau uses segmented
carryover, rtol=2e-12, concentration atol=2e-14*C*, outlet atol=2e-14*M*,
max_step=.02. Failures stay failures; no candidate fallback. References also
sample the union of .04/.02/.01 primary endpoints for endpoint comparisons.
Candidate common observations provide interior extension comparisons.

Fixed scales: C*=source c_s0, M*=initial continuum inventory,
V*=independent full volume. Passive C*=C0=1 and M*=exact initial inventory.
No moving maxima or late-concentration denominators. Gates:

- Generator column/exchange residual <=1e-12 on max(1, largest rate/derivative
  norm) scales; off-diagonals nonnegative.
- Phase minima >=-1e-10*C*, Mout and chronological increments >=-1e-10*M*,
  at primary/diagnostic/observer and GL4/8 samples. Sampling, not all-time proof.
- Independent inventory residual <=1e-8*M*, retain initial offsets and signed
  min/max/final residuals. Volume <=1e-12*V*, including local/cross-knot panels.
- GL8 numerical flux minus Mout <=1e-6*M* and GL8-GL4 <=1e-6*M* for BOTH fluxes.
- A compatibility <=1e-12 individually on phase fields, outlet, Mout, V and
  fractions; minimal constant-Q representations preserve primary partition.
- B full candidate/ordered-reference <=1e-8 on each corresponding fixed scale.
- C default/finer and default/Radau <=5e-4 independently on each phase,
  outlet, Mout and every fraction, at common interior observations and primary
  endpoints. Prescribed-flow flux/Mout <=5e-4*M*. Report .04/.02/.01 reference
  maxima and flux discrepancies for both directions. Resolved aggregate error
  is the max of phase/outlet/Mout/fraction errors; require decrease at each
  refinement when above floor1e-10. Unresolved differences earn no order claim.
- Spatial N400->800 fractions <=.005*C*, Mout <=.005*M*, weighted field
  <=.005*M*. Pair-average fine cells, weight absolute phase differences by
  A*dz*[alpha_l,as1,phi_v2*as2]. Report both mesh pairs, all channels and resolved
  ratios (floor1e-10); ratios are not asymptotic order proof.
- Passive: zero exchange via private manufactured seam only, zero grains,
  initial liquid exact cell averages of sin(pi*z/L)^2. Translate by
  s=integral(Q)/(A*alpha_l), primitive P(z)=z/2-L*sin(2*pi*z/L)/(4*pi), clipped
  to compact support. Times solve independent analytic volume for
  s/L=[0,.25,.5,.75,1.25], stop at last time. N128 L1 mean absolute liquid
  error/C0 <=.05 at pre-exit nonzero samples; both mesh-pair orders >=.8.
  Final (remaining liquid+absolute outlet error)/M* <=.05. Initial error reported
  but roundoff at t0 cannot establish order.
- Exact-environment repeated numerical arrays bitwise identical. API,
  observer-independence, preservation and failure tests pass.

**The joint-linear 5e-4 temporal budget is NEW**, one-tenth of the retained
.005 spatial fraction/Mout allowance. It covers variable-flow frozen-step
interior extension and does not change or inherit 002's tighter1e-6
 temperature-only qualification. Report actual errors prominently.

Small tests cover signs/exchange/capacities/initial inventory, closed-cell
relaxation/equilibrium, arbitrary nonnegative states, dense/noncommuting
references, all species with both constant-Q representations and constant,
stepped/linear T; mixed/noncoincident histories; volume and windows; explicit
origin/translation/observer independence; rejection, immutability, JSON,
resources/prefixes/tiny fractions and no global/parameter mutation. Test-only
defects must be rejected: frozen Q, T-only cache, frozen transfer h, interstitial
Reynolds, duration weights, partial midpoint volume, knot reset, and an injected
inventory error holding independent outlet-flux samples fixed. No production
alternate implementation or extra full-bed campaign.

## Resources, QA and delivery

32 planned executions, ceiling36 (four affected-correction slots), aggregate
1800 numerical wall-seconds including auxiliary reductions/reviewer work.
One numerical worker and BLAS thread. Reserve before launch; timeout <=120 s
or remaining allowance. Reuse the existing Git-common-directory budget/receipt
pattern; changing evidence directory cannot reset counts. Preserve failed
launches. Resume only unfinished authorized work; rerun only affected evidence
with changed hashes. No hidden replay, fallback or threshold relaxation.
Resource exhaustion is an incomplete handoff. CASES predeclares a supported
100000 diagnostic-sample and 150000 exponential allowance for C finer runs,
needed for interior partial-panel quadrature; all other defaults are retained.
Detailed arrays/logs stay outside Git. Report-only validates identities and
reproduces summaries without trajectories; reductions are charged separately.

Applicable unprotected baseline and affected/regression tests exclude
protected_target_integrity. Separate software, numerical and infrastructure
failures; no development over a demonstrated red baseline. Run applicable
lint/type, packaging/wheel, strict JSON, preservation, generated-document and
private-path checks; full qualification stays outside ordinary CI. Existing
workflow thresholds stay unchanged. Repeated non-scientific stops use the
minimum-governance circuit breaker, not a child-stage ladder.

One independent exact-head review, nonhuman reviewer explicitly labeled;
unavailable review and pending CI remain pending. Unchanged scientific evidence
is reusable by hash for nonsemantic deltas. Update card/ROADMAP/SPRINTS and
current.json with generated surfaces, respecting the active-queue cap.
Distinguish integration, sampled admissibility, temporal/spatial accuracy,
campaign qualification, QA, CI and physical validation. Runtime accuracy stays
NOT_ASSESSED. VERIFIED_ON_DECLARED_CASES requires every new gate; full-matrix
positivity requires all candidate coverage. Otherwise use the justified bounded
incomplete disposition and list failures. No profile benefit, taste, MATLAB
 equivalence or empirical accuracy. Leave PR draft, unmerged, auto-merge off;
EWP unchanged and no successor started.
