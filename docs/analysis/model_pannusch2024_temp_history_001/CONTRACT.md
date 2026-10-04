# MODEL-PANNUSCH2024-TEMP-HISTORY-001 — frozen numerical contract

2026-10-03; issue #313. G2 / **NUMERICAL_METHOD_CHANGE**. This adds a
segmented integration path for prescribed spatially uniform T(t); the governing
saturated homogeneous two-grain equations, closures, fitted parameters, geometry
and nodal spatial discretization are unchanged. PHYSICAL_VALIDATION=NOT_ESTABLISHED.
No empirical scoring, thermal-field model, optimization, coupling or adoption.

## Intake and scoped preflight

Base: Puckworks 95f6b54f1f00fda100fad9c994ac99037e50f801 (merged #312).
EWP remote main: 73ec476ffe6ac626705ca949e28b32935ddf2992, read-only. No
intervening main changes; targeted public issues/PRs/branches and accessible
local worktrees found no duplicate. Unpublished local work cannot be excluded.
One isolated branch/worktree; owner work and locked dependencies are preserved.

Read AGENTS/CLAUDE/onboarding, minimum governance, affected roadmap/sprints/live
state/task ledger, espresso data guide, MANIFEST and available-data register;
EWP data-first/available-data authorities and #132/#134 retained decisions.
Canonical IDs: `pannusch2024/table2_params`,
`pannusch2024/experimental_kinetics`, and the literal legacy manifest ID
`pannusch2024 (Mendeley repo)`. Only the parameter/source authority is consumed.
The latter legacy manifest row is not a new invented dataset ID. Source input,
prediction-condition and telemetry metadata were read; no observation rows are
numerical qualification inputs. March targets remain SOURCE_INTERNAL and
TARGET_EXPOSED, not an independent holdout. The flow convention remains
H_UNRESOLVED / FLOW_AUTHORITY_INELIGIBLE, with no operational EWP mapping.

The established resolver locates the mounted Mendeley repository. Eight original
MATLAB files were actually read (hash receipt in SOURCE_IDENTITIES.json): PDE,
initialization, physical/numerical parameters, spatial stencil and three closure
files. Their equations agree with the requested contract and implemented port.
The physical-parameter file's radius comment does not replace the d1/d2 lengths
used with 6h/d in the source equations. Fixed fitted psi/d2 are used directly;
no inverse PSD inference is made from the card's descriptive grind formula.
Public Mendeley metadata/license was checked; article DOI fetch was unavailable.
No original paper PDF or native MATLAB execution was performed, and no native
MATLAB equivalence is claimed. Source: Pannusch et al., J. Food Eng. 367,
111887, DOI 10.1016/j.jfoodeng.2023.111887; author repository
https://data.mendeley.com/datasets/y2tz67f6ry/1, DOI 10.17632/y2tz67f6ry.1.
Source-derived numerical reports retain attribution and CC-BY-NC-3.0 treatment,
separate from first-party software licensing. No originals or observation rows
are redistributed.

Data-first gate (owner selected; no task reselection): new information is a
previously absent prescribed-temperature integration capability and independent
numerical checks. PASS permits a bounded verified capability; FAIL or unresolved
checks leave qualification INCOMPLETE. The grinder-to-cup link is source-grind,
phase-resolved extraction under caller forcing, without hydraulic/thermal
coupling. This is not another attempt at the inventory/independence blocker.
Existing parameter/source evidence is sufficient for this numerical decision;
no corpus-exhaustion conclusion, laboratory recommendation or successor follows.

## Equations, bases and clocks

A=pi*0.058^2/4 m², L=0.015 m, alpha_l=0.17, d1=24e-6 m,
phi_v2=0.4; psi,d2 use declared source grinds 1.4/1.7/2.0. q=Q/A,
v=q/alpha_l, as1=psi*(1-alpha_l), as2=(1-psi)*(1-alpha_l),
d32=6/(psi*6/d1+(1-psi)*6/d2). Reynolds uses q. At actual RHS time:

```
f1=6*h1(T,q)/d1; f2=6*h2(T,q)/(phi_v2*d2)
m1=as1*f1/alpha_l; m2=phi_v2*as2*f2/alpha_l
cl_t = -v*D*cl + m1*(K*cs1-cl) + m2*(K*cs2-cl)
cs1_t = -f1*(K*cs1-cl); cs2_t = -f2*(K*cs2-cl)
Mout_t = Q*cl[-1]; Vout = Q*(t-t0)
```

SI physical concentrations (kg/m³): liquid per liquid volume, fine grain per
fine-grain volume, coarse grain on the source intragranular capacity basis
(phi_v2 multiplies its bulk coarse-phase inventory). Source c_s0 mg/mL is
numerically kg/m³, a fitted parameter, not measured recoverable content.
Caffeine, trigonelline, 5CQA and tds retain exact source identities; tds is a
pseudo-solute, never TDS percent or yield. All fitted A/B/K_ref/gamma/c_s0 stay
fixed. Water density appears only in unchanged closures, not Q conversion.

Initialize once at explicit t_span_s[0]: both grains=c_s0, interior liquid=
K(T(t0))*c_s0, inlet=0, mass=volume=0. Observations/fraction boundaries do not
set the model origin. Physical state and accumulators carry exactly across
knots; no temperature normalization, resetting or re-equilibration.

Reduced state has 3*nz entries: cl[1:nz], cs1[0:nz], cs2[0:nz], Mout.
The omitted liquid coordinate is identically zero, not the legacy stored drift.
All grain equations, interior/outlet equations and source five-point biased
upwind rows remain. Analytic time-dependent Jacobian follows this reduced
operator, including first/interior/outlet boundary dependencies and mass row.
The legacy sparsity helper and both legacy APIs remain byte-identical.

Piecewise-linear knots increase strictly, with one Kelvin value per knot.
Piecewise-constant edges increase strictly, with one value per interval;
[edge_i,edge_i+1), final endpoint uses final interval. A segment closes with
its own one-sided temperature; the next starts with its own coefficient and
exact carried state. Dense output stays within accepted step/segment support.

Input domain: finite 353.15–371.15 K, explicit Celsius constructors, fixed
1e-6 <= Q <= 3e-6 m³/s. This is a caller-prescribed numerical envelope,
not resolution of experimental flow units, and not qualification of all histories.
Reject malformed/nonfinite/duplicate/nonincreasing clocks, unsupported queries,
unknown species/grinds, invalid settings and unresolvable fraction widths before
integration. Never sort/fill/clamp/extrapolate user inputs. Validate settings with
5<=nz<=2000, finite positive tolerances/steps and bounded step/time ceilings.
Failures retain finite diagnostic prefixes with actual support and explicit
reasons; missing observations/fractions are null. Invalid inputs raise ValueError
(with INVALID_INPUT code); results serialize with strict JSON, no NaN/Infinity.
No numerical cache or LAST_SOLVE result contract.

## Independent accounting

Use composite trapezoidal spatial weights w (including both endpoints):
Mbed,h=A*w@(alpha_l*cl+as1*cs1+phi_v2*as2*cs2).
M0cont=A*L*c_s0*(alpha_l*K(T(t0))+as1+phi_v2*as2).
Compute M0h independently; retain M0h-M0cont (zero liquid inlet creates an
endpoint quadrature offset). Report signed trajectories/final values and maxima
of (Mbed,h+Mout-M0h) and (Mbed,h+Mout-M0cont). Gate the latter physical
continuum residual, as well as displaying the incremental discrete residual.

Weighted exchange cancels exactly at each interior node for every T. At the
pinned inlet, the grain exchange has no evolving liquid partner. Thus:

```
d(Mbed,h+Mout)/dt =
  Q*(cl[-1] - sum(w[1:]*Dcl[1:]))
  - A*w[0]*(as1*f1*K*cs1[0] + phi_v2*as2*f2*K*cs2[0])
```

Report transport/stencil and pinned-inlet exchange contributions separately;
integrate them with independent temporal Simpson quadrature and compare their
sum to the incremental residual. They are diagnostics, never correction fluxes.
Independently Simpson-integrate Q*cl[-1] at dt=0.025 and 0.0125 s; report both
versus the accumulator and their difference. Volume is checked independently
against exact Q*(t-t0). Do not use a complement to manufacture closure.

## Frozen cases, settings and budgets

Machine contract: CASES.json. All cases centre grind, Q=2e-6 m³/s, [0,30] s.
The exact legacy argument is 1.96; reproduce `1.96/1000.0/980.0`, not `2*1e-6`
from a nominal legacy argument of 2.0. Legacy cl1=c_s0 (no assay input).

A: constant 88 C, four species, legacy+new each (8).
B: steps edges [0,7,19,30], [88,93,86] C, four species, new+independently
assembled ordered matrix exponential each (8).
C: caffeine rising 88→93 C and falling 93→88 C, three BDF levels and one
independently assembled Radau integration each (8).
D: rising caffeine, nz=100 and 400; reuse matching C fine nz=200 (2).
E: exact repeat of C rising fine (1). Planned total 27.

Nominal nz=200. Coarse BDF rtol=1e-7, normalized atol=1e-9,
max_step=0.1 s; fine/public default 1e-9/1e-11/0.05 s;
finer 1e-11/1e-13/0.025 s. Radau 2e-12/2e-14/0.05 s.
Atol scales each concentration by C*=c_s0 and mass by M*=M0cont;
V*=Q*(tf-t0). These scales never move. New A/B/D/E use fine settings.

Requested retained observation grid is sorted union of k*0.0125 s,
k=0..2400, and [7-1e-8,7+1e-8,19-1e-8,19+1e-8]. Fraction bounds
[0,1,5,10,17,20,25,30] s include crossing windows. Delayed [20,30],
[7,19], and partition/additivity checks use retained mass/volume samples.
Comparison norms are maximum absolute channel errors over common physical
nodes/times / C*, M*, V* respectively. Fractions use /C*. Compare all temporal
levels, gate fine/finer and fine/independent separately; report coarse differences.
Spatial compare fraction vectors 100→200 and 200→400; gate finest change.
No history-ordering effect claim is required.

Allowances (not assay uncertainty or rigorous certificates): temporal fine/finer
and independent methods <=1e-6 separately for physical state, mass, volume,
fraction; legacy fraction <=1e-4; continuum inventory <=5e-3 at every checked
time for all new cases/grids; finest-grid fraction change <=5e-3. Independent
flux/budget quadrature discrepancy <=1e-6 of M*. Sampled undershoot allowance
is 1e-6*C*, no clipping. Check accepted internal steps, their quarter-step dense
samples, dt<=0.0125 s diagnostic samples and knot neighborhoods. Compare fixed
0.025/0.0125 sampling minima; report checked support/counts. Sampled positivity
is not an all-time proof. No threshold may be loosened after results.

References transcribe physical equations independently (no new RHS/builder
calls); share only unchanged closures/parameter tables/geometry and the separately
polynomial-verified source stencil. Step propagation is time-ordered expm;
ramp reference is Radau versus BDF. The saturation helper's production-column
assembly is not an independent equation reference. Temporal-discrepancy block
ideas are suitable, its assay/mass clock/rate/slow-population wrappers are not.
Small random-state tests independently check RHS/Jacobian and local cancellation.

Ceilings: 32 full-bed species/history/grid/settings/method executions and 1800
aggregate numerical wall-seconds, failures/cancellations/replays included;
segments counted separately. Per-execution hard timeout <=60 s and remaining
aggregate budget. Reserve four slots for source corrections; slot 28 may be
explicitly assigned a review replay, never silently consumed. Persist launch/end
receipts before/after each run; failed evidence remains. Small meshes <=12 nodes
and existing regression tests are separate QA, not exploration. Reporting saved
evidence never reruns solves. Exhaustion/failure gives INCOMPLETE, not a new sweep.

Focused tests cover no-op splits, knots, clocks/delayed observation, finite strict
serialization, input rejection before execution, source immutability, exact
repeatability, failures/partial prefixes, independent boundary derivatives and
frozen-temperature/reinitialized-state mutants. One independent nonhuman
exact-head review; QA and hosted CI are separate. No merge/auto-merge, release,
EWP write/run, lock/default change, fitting/scoring, protected data, laboratory
operation, author contact, corpus acquisition or automatic successor.

## Clean baseline receipt

Before implementation: quick selector `not slow and not live and not gpu and
not external_data and not protected_target_integrity`: 4,831 passed, 64 skipped,
760 deselected (1,186.91 s). Existing registry: 66 PASS, one acknowledged
exception. Affected solver/model-contract tests: 39 passed. Scientific-baseline
selector: five passed, seven optional plotting-module collection skips, 5,643
deselected. Ruff, core mypy, generated status and scoped preflight pass. Skips
are unrun, not PASS. Full logs/XML stay outside Git. No unrelated red-tree debt
was found in these baseline checks; optional/live/protected lanes were not run.

Pre-execution implementation clarification (no numerical outcomes inspected):
malformed scalar settings/flow/grind arrays are rejected. Diagnostic allocation
is bounded to 100,000 subdivisions per maximum step and one million uniform
subdivisions per model span. Requested knot-neighborhood samples are included
in the checked physical trajectory, alongside accepted steps and quarter points.
Worker entry points require a reserved launch and a single-use claim, preventing
unaccounted direct worker invocation. These are input/execution safeguards,
not changed scientific allowances or additional approval gates.
