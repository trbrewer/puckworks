# MODEL-PANNUSCH2024-POSITIVE-FV-002 frozen numerical contract

G2 / NUMERICAL_METHOD_CHANGE. PHYSICAL_VALIDATION=NOT_ESTABLISHED.
This is one new research spatial/temporal candidate, explicitly authorized by
its owner. It does not amend 001 or assert that the authors used this method.
Freeze this CONTRACT and CASES before any of the 28 full qualification runs.
Small N<=12 synthetic/algebraic implementation tests may precede the freeze.

## Dependency, source and scope

Base/parent is unmerged draft #314, head
`c7310ea1ac6c41ec2cb8f918584ab41cb485fa60`; its numerical producer remains
`a8c94caf35bff300519af9bcffb7d4771c5e9553`. The new draft targets the parent
branch and contains only the 002 delta. Main is
`95f6b54f1f00fda100fad9c994ac99037e50f801`. EWP main is read-only
`73ec476ffe6ac626705ca949e28b32935ddf2992`. Short live/overlap checks found no
drift or duplicate. Parent INCOMPLETE results, code, tests, receipts, arrays,
thresholds, budgets, input correction and process disclosure are preserved.

Reuse parent SOURCE_IDENTITIES and scoped INTAKE.json. Canonical identities:
`pannusch2024/table2_params`, `pannusch2024/experimental_kinetics`, literal
`pannusch2024 (Mendeley repo)`. Only equation/parameter authority is needed;
experimental outcomes are not inputs. Source parameter/provenance records were
read; original MATLAB text inspections are reused by hash from 001, not claimed
as new execution. No native-MATLAB equivalence, PDF inspection or corpus-absence
claim follows. Original source: DOI 10.1016/j.jfoodeng.2023.111887; author
code/data: DOI 10.17632/y2tz67f6ry.1. Source-derived reports retain CC-BY-NC-3.0
attribution separately from first-party software licensing. No originals,
observation rows, raw arrays/logs or private locators are committed.

Uniform prescribed T(t), fixed SI Q and homogeneous saturated geometry are
inputs; no thermal field, lag, hydraulic feedback, fitting or coupling is added.
EWP #132 FLOW_AUTHORITY_INELIGIBLE / #134 H_UNRESOLVED remain unchanged.
T is 353.15–371.15 K; Celsius conversion is explicit. Q is 1e-6–3e-6 m³/s,
temperature-independent, not an experimental mapping. Legacy arithmetic remains
flow_mL_s/1000.0/980.0; Q=2e-6 corresponds arithmetically to 1.96.

## Continuum and finite volumes

Let W=A*L/N, as1=psi*(1-alpha_l), as2=(1-psi)*(1-alpha_l),
k1=6*h1/d1, k2=6*h2/(phi_v2*d2). Retain source A,L,alpha_l,phi_v2,d1,
grind-specific psi/d2/d32 and every fitted coefficient for all four solutes.
Unchanged closures use actual prescribed temperature and superficial Q/A for
Reynolds. The continuum liquid velocity is Q/(A*alpha_l).

The liquid continuum equation is
cl_t+v*cl_z=as1*k1/alpha_l*(K*cs1-cl)+phi_v2*as2*k2/alpha_l*(K*cs2-cl);
grains obey cs1_t=-k1*(K*cs1-cl), cs2_t=-k2*(K*cs2-cl).

Uniform cells have edges j*L/N and centers (j+1/2)*L/N. Evolution variables
are ml=W*alpha_l*cl, m1=W*as1*cs1, m2=W*phi_v2*as2*cs2, plus Mout.
Returned phase fields are CELL AVERAGES. Incoming face flux is F0=0;
F[j+1]=Q*cl[j]. Transfers are R1=W*as1*k1*(K*cs1-cl) and
R2=W*phi_v2*as2*k2*(K*cs2-cl). Evolve ml'=Fleft-Fright+R1+R2,
m1'=-R1,m2'=-R2,Mout'=F[N], using identical paired transfers/fluxes.

In mass coordinates, transitions ml→next-liquid/outlet have rate
Q/(W*alpha_l); ml→m1 has as1*k1/alpha_l, m1→ml has K*k1;
ml→m2 has phi_v2*as2*k2/alpha_l, m2→ml has K*k2. Each nonnegative
transition adds +r to its receiver/donor entry and -r to its donor diagonal.
Therefore B is Metzler (off-diagonals nonnegative), 1ᵀB=0, and the Mout
column is zero. For finite admitted positive source coefficients, exp(dt*B)
is nonnegative, column stochastic and preserves total mass in exact arithmetic.
Mout is nondecreasing for nonnegative states. Local exchange cancels and
internal face fluxes telescope algebraically; no correction flux is present.
Floating-point checks are engineering checks, not rigorous certificates.

At explicit model t0 apply equilibrium ONCE: all grain averages=c_s0, every
liquid cell average=K(T0)*c_s0, Mout=Vout=0. The first cell retains liquid.
Zero inlet is a face condition; there is no pinned grain cell or endpoint
quadrature offset. Initial FV sum equals
M0=A*L*c_s0*(alpha_l*K(T0)+as1+phi_v2*as2), up to rounding.
c_s0 mg/mL is numerically kg/m³ on source bases, not measured inventory.

## Time, observations, support and finite precision

Use scipy.sparse.linalg.expm_multiply. Constant segments use their fixed B;
linear segments use exponential midpoint on ceil(duration/h_max) equal steps
with exact segment endpoints. Split jumps and slope-change knots; carry the
exact state and Mout. No history reset or temperature-dependent normalization.
Public defaults: N=400, h_max=.02 s, diagnostic spacing <=.0125 s.
There is one spatial candidate and one time method; no limiter or fallback.

For each primary step, observations inside it use a partial exponential of the
SAME midpoint-frozen B from that step's initial state. They do not choose a new
midpoint or interpolate masses. Primary propagation precedes observer work,
so observers cannot influence its arithmetic or partition. Extra observation
work still consumes application/time/allocation budgets. This continuous
numerical extension has frozen coefficients within a step; it is not exact
nonautonomous evolution. At a knot return one carried physical state, allowing
temperature metadata to jump. Dense evaluation never exceeds completed support.

Validate real finite inputs, clocks, history/model support, species/grind,
settings, observer support, volume resolution and allocation bounds before
propagation. Reuse the parent's immutable history/rejection utilities without
changing them. FV-specific result metadata identifies capacities/cell averages,
backend, numerical method, source/code/configuration hashes and support.

Integration COMPLETE, per-call sampled admissibility, unknown accuracy,
campaign qualification and physical validation are distinct. Never clip,
monotonize or redistribute. Failed/partial work retains checked finite prefixes;
unsupported values are null with reasons. A completed but inadmissible call
reports FAILED admissibility and null public fraction concentrations, retaining
raw diagnostics. Supported numerical fractions have accuracy NOT_ASSESSED and
physical-prediction status NOT_VALIDATED. Strict JSON excludes NaN/Infinity.
No runtime solution cache, global parameter mutation, registry promotion or
legacy-call redirection is introduced.

## Frozen cases, observers and independent references

CASES.json defines exactly 28 executions: four constants; four step species
candidate+Radau (8); two caffeine ramps at .04/.02/.01 plus Radau (8);
N=200/800 for rising caffeine and trigonelline steps (4); exact rising repeat
(1); passive N=32/64/128 (3). Source runs use Q=2e-6, grind1.7, 0–30 s.
Nominal N=400 trajectories are reused in refinement. No outcome-driven grids,
settings, scales, thresholds or additional sweeps are permitted.

Source observations are the sorted union of arange(2401)*.0125, 7±1e-8,
19±1e-8 and the explicit early_times_s in CASES. Fraction bounds are
0,1,5,10,17,20,25,30; retain 20–30 and 7–19 derived observers and partition
additivity without extra solves. Source fields are checked at primary endpoints,
midpoints, the uniform diagnostic grid and requested observers. GL4/GL8 nodes
are additionally checked for phase minima, inventory and Mout monotonicity.
Record actual sample support/counts, propagations, exponentials and segments.
Sampling is not an all-time floating-point positivity proof.

Independent references assemble CONCENTRATION balances directly, with no
candidate generator/RHS/basis-vector calls. Shared source parameters, geometry
and unchanged closures are disclosed. Segment-local Radau evaluates actual
T(t), rtol=2e-12, concentration atol=2e-14*C*, Mout atol=2e-14*M*,
max_step=.02 s. Small-mesh independent dense expm, arbitrary nonnegative
states, closed-cell equilibrium/relaxation, zero-exchange transport, old-stencil
negative-coupling rejection and generator identities support the algebra.

Passive test-only transport has zero exchange, inert/zero grains, and
cl0=C0*sin(pi*z/L)^2, C0=1 kg/m³. Exact initial/translated cell averages
integrate P(z)=z/2-L*sin(2*pi*z/L)/(4*pi), on compact initial support [0,L].
Exact outlet integral is A*alpha_l*C0*[P(L)-P(max(0,L-v*t))], reaching
M0=A*alpha_l*C0*L/2 at residence time tau=L/v. Benchmark observations:
0,.25,.5,.75,1.25 tau; constant exponential steps h_max=.02 s. Source
parameters are never overwritten by this private test-only initial/rate path.

## Accounting, comparison norms and fixed budgets

Fixed source scales: C*=c_s0, M*=continuum M0, V*=Q*(tf-t0).
Passive scales: C0 and exact initial inventory. Never use moving maxima or
near-zero relative denominators. Recompute inventory independently from returned
cell averages and W*[alpha_l,as1,phi_v2*as2], plus independently evolved Mout.
Record initial sum/offset and signed residual ranges/final values.

Independent outlet-flux quadrature uses Gauss–Legendre orders4 and8 on EVERY
numerical step, including every coefficient discontinuity. Evaluate partial
exponentials from the saved step start, retain raw Q*cl_out, times and weights;
never infer outlet mass by complement. Compare cumulative GL8 with Mout at all
step ends and cumulative GL8–GL4, each <=1e-6*M*. Evaluation cap60000,
application cap100000, steps10000, field values30000000 per execution.
No replacement by the underresolved parent global Simpson grid.

Frozen allowances:
- Generator sign construction/proof plus relative column/exchange residual<=1e-12.
- Candidate concentration minima>=-1e-10*C*, phase masses scaled by their
  capacities, Mout and its increments>=-1e-10*M*, on all retained samples.
- Independent total inventory residual<=1e-8*M*, independently checked volume.
- Default/finer and default/reference errors<=1e-6 separately for each phase
  (maximum absolute/C*), Mout/M*, volume/V*, and each fraction/C*.
  Coarse/default is diagnostic. Constant source cases have no new legacy-parity gate.
- N400→800 fraction<=.005*C*, Mout<=.005*M*. Conservatively average pairs
  of fine cell averages before comparison. Independently gate weighted field
  A*sum(dz*(alpha_l*|dcl|+as1*|dcs1|+phi_v2*as2*|dcs2|))<=.005*M*.
  Report both200→400 and400→800 maxima and their ratio only when both exceed
  1e-12 of their fixed scale; no measured-order claim near roundoff.
- Passive N128 L1 liquid error sum(dz*|cl-exact|)/(L*C0)<=.05; orders
  log2(error_N/error_2N)>=.8 for both refinement pairs at each pre-exit time.
  At1.25tau, (remaining liquid+|Mout-M0|)/M0<=.05 at the finest grid;
  report all grids/times. This is a manufactured consistency check.
- Identical-environment repeat arrays must be exactly equal. API/clock/support,
  observer independence, parameter immutability, strict JSON and failures pass
  focused tests. No chemistry scoring or physical prediction is inferred.

Parent fractions, if available and identity-verified, are cross-discretization
DIAGNOSTICS only, never truth or a fitting target. No FV center/nodal index
comparison. Missing private parent arrays limit only that optional diagnostic.

## Resources, QA and handoff

Own ceiling32 trajectories/1800 aggregate numerical seconds; final four slots
reserved for affected corrections. Three passive trajectories count. One worker,
one BLAS thread; each execution<=120 s or remaining allowance. Persist reserved
launch/failure/completion receipts before work. A task ledger in local Git
metadata binds the evidence directory, preventing reset by choosing a new one.
Resume only unattempted cases; explicit affected corrections consume new IDs.
Charge reduction/auxiliary/reviewer numerical work; report-only never simulates.
No new case/method/threshold/default selection after outcomes. Failed accuracy
may yield POSITIVITY_AND_CONSERVATION_VERIFIED_ACCURACY_INCOMPLETE if those
properties actually pass across all candidate cases; otherwise retain INCOMPLETE.

Before implementation baseline: parent new/legacy unprotected constituent
suite78 passed (4.47s); parent full-suite/QA receipts may be reused by exact
identity. Local commands exclude protected_target_integrity, including targeted
commands. Existing hosted QA retains its selectors. Known unchanged-base
coverage timeout is infrastructure debt, not a FV numerical failure; no workflow
or threshold edits. Parent accidental-integrity disclosure remains untouched.
Run affected tests, lint/type, packaging/wheel, JSON, preservation/private-path,
and affected generated checks. Obtain one independent exact-head review; no
self-approval. Current planning/card changes are additive; generated notes use
existing generators. Leave the stacked PR and parent unmerged, auto-merge off;
no release, adoption, EWP change/execution, empirical scoring, coupling or successor.
