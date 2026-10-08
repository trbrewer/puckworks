# MODEL-GRUDEVA2026-BASELINE-OBSERVATION-005

G1 / NO_GOVERNING_PHYSICS_CHANGE. Observation-operator and numerical-application
qualification under issue #67; no calibration or protected-target score.
PHYSICAL_VALIDATION=NOT_ESTABLISHED throughout. One isolated branch, one draft
PR, one independent exact-head review. No matched comparison, production repair,
adoption, merge, automatic successor, EWP write or dependency/default change.

## Authority and evidence

Live selecting main is `45f594b92e6bed01f254158fa002ef82519fd5a6`, tree
`ef85e16573dee279aa84b90dfc5440c8c948a2d3`; #326 merged reviewed head
`918e5e7481ce2072843bb218830f54fcf38723ca`. Seven exact-merge workflow runs
succeeded, including quick-pr 37768636318. No equivalent 005 work was found.
EWP live main is `16eec1dda24ebf658965eddcf1a6fffa81903b32`; its production
lock still selects Puckworks `fc61c4670ec7bf801e40bb391aab16048b8da26b`.
The older local main checkouts are left intact. Current card/results establish
004 qualification; historical draft/pending and older guide descriptions do
not override that evidence. REDUCED-001's original analytical, conservation,
bounds, outlet and event qualification is preserved, not rediscovered here.

Relevant datasets: `grudeva2026/analytic_reference` (synthetic verification)
and `grudeva2026/publication_reference` (published numerical reference).
Only its inherited coordinates enter observation support; no publication
rescore. Existing owner data-source configuration resolves the source collection.
Actually reopened article PDF pp.16–18, Eqs.64–77, and supplementary E.2,
pp.13–15, E26–E33. Authorized article SHA256
`592304014b7be482b5fe2814d730f7d128f9ec2e77d6f7d25f8e0292c5fce5e5`;
supplement `5437e3310288c2a9506fbd1eb4c4d8854ec8f4293f6edcda5579bbdc9bae5179`.
The older 001 archive article has different bytes
(`5b9e41e85591dce8a32b923663ee3ccf9e00c0ac34dc17659864ff7417326a29`);
it is not substituted for the authorized binding. No new acquisition, source
PDF, private path or correspondence is published. Article CC-BY attribution
and existing upstream permission/notices retain their separate scopes.

## Frozen production and observation definitions

Protect all production Grudeva2026 modules, data, 001–004 analysis modules,
tools, tests and evidence files by pre/post SHA256. Historical 003 stays intact.
Reuse its return-capture pattern and unchanged `observation_support` and
physical-coordinate refinement masks; no new runtime component or registry.

Canonical parameters are phi_f=.64, phi_b=.16, phi_l=.20, varphi_lb=0,
D_sb=q=gamma=1, c_f_init=c_b_init=1.388, beta=3.2, delta=.8, a=4.2,
s_w=min(t,1), horizon=8. Eq.71 uses elapsed-time convolution; Eq.74 retains
the corrected grouping. Production equations, RHS, mesh, stepping, tolerances,
events, public request, Result serialization and behavior are unchanged.

Each intercepted solve_ivp calls the original exactly once with unchanged
arguments and returns its identical object. Retain every segment, including
returned failure diagnostics. Restore the seam on every exit and preserve
original exceptions. No RHS evaluations or callbacks are added. Serial isolated
processes only. The public request is the original 001 native request (75 times,
120 positions); richer diagnostics are evaluated afterward. Freeze both exact
requests and their hashes, independently of any historical output agreement.

State layout is `[s, N liquid averages, (M+1)*N modal averages, cup]`, mode-major.
The last mode is a positive relaxation tail, not a radial shell. Read actual
weights/rates from the production RHS closure without evaluating it; retain
their numerical values. Audit resolved weights 6/(pi*n)^2 and rates (pi*n)^2*D,
and the tail sums of weights and integrated relaxation independently. Quantify
003's `1-sum(resolved)` difference without renormalization.

For xi_face[j]=1-(1-j/N)^2, physical faces are s*xi_face and widths are their
differences. At s=0 there is no active volume: retain the returned initial state
but do not divide by s or create a finite domain. Preserve the localized s after
exit, including floating-point deviation from one. Modal observations first
reconstruct each mode at a fixed physical z, then weight modes to form a
grain-volume mean concentration. Spatial integration is a separate operation.
No auxiliary grain ODE replaces those evolved modal fields.

The public center-linear interpolation, zero liquid inlet, two-cell liquid
outlet extrapolation and constant grain endpoint extensions are reproduced and
audited explicitly. The diagnostic reconstruction is a local quadratic fitted
to three exact physical cell averages, with normalized local coordinates;
its integral constraints determine the coefficients. It imports no 004
square-root basis. The diagnostic does not overwrite public profiles or the
outlet driving cup evolution. Its constant/linear/quadratic exactness and
nonpolynomial errors are separately tested. At the advancing front, the new
grain boundary is INITIAL in every mode. The inlet analytical limit is
INITIAL*exp(-rate*t) under C(0,t)=0; it is an independent diagnostic, not a
substitution for the reconstructed production state. Post-exit z=1 uses actual
cell-average extrapolation, with error tested independently of constant endpoint
extension. Dry grains and saturated grains retain INITIAL; absent liquid is
reported as zero, saturated liquid as one. Fixed-z activation is localized on
valid advancing segments; t_wet=z remains separate. No fixed-cell crossing events.

Retain BDF difference coefficients, order, shifts, divisors, actual accepted
times/states, valid dense breakpoints, event times/states, segment provenance
and SciPy's interval-selection convention. An event may truncate a polynomial
before its underlying step end. Evaluation cannot cross the captured domain.
Keep left/right production segments distinct at coincident boundaries. Safe
JSON and numerical arrays only; never pickles. Replay is checked against live
dense output at accepted nodes, interior nodes and event-side limits.

## Independent amounts, cup and error allocation

Compute I_C=sum(width*C), I_B=sum(width*sum(weight*mode)), then
M_l=I_C+min(t,1)-s, M_f=3.2*(I_C+1.388*(1-s)),
M_b=.8*(I_B+1.388*(1-s)), M_initial=5.552. No complement inventory.
Reorder modal/spatial summation as an independent algebra check. Compare public
amounts at public times and diagnostic amounts at all support times. Audit every
accepted and event state, with duplicate event provenance retained.

Algebraic allowance: 256*float64 epsilon times the sum of absolute participating
terms (including initial mass when subtracting balance). This is distinct from
the global normalized conservation allowance 1e-6. Dense replay uses the same
scale-aware allowance. No paired-step conservation identity is imposed on BDF.

Cup quadrature integrates the production two-cell liquid outlet trace over every
valid dense subinterval, split at first drip, exit and requested cumulative
times: zero before 1, unit plateau until exit, actual C(1,t) afterward.
Gauss orders 4 and 8 measure refinement (BDF degree <=5); one-sided conventions
are explicit. Quadrature allowance 1e-10 is contained within the inherited 5e-5
cup allowance; report state-versus-integral discrepancy and quadrature separately.
Do not use sparse plot-sample integration. Report finite-horizon residual phases.

Analytical grain mean allowance remains 2e-5 per method and positive-age flux
2e-4. Diagnostic reconstruction fixture errors must fit 2e-5 for grain and
1e-4 for liquid; these are subdivisions of, not additions to, the respective
empirical allowances below. Polynomial fixtures use scale-aware roundoff.
Report actual point/boundary/cell-integral errors separately. Fixture correctness
does not assert a rigorous continuum error bound for the canonical trajectory.

## Support and bounded campaign

Unchanged 003 support: 395 times, 220 physical positions and histories at
.025,.1,.25,.5,.75,.9,1, plus first-drip/exit and activation observations.
Record requested/included/excluded/unavailable counts, maximum and location for
every observable/pair. Unavailable required support and empty support cannot pass.
Masks retain full displaced-front intervals, .008 spatial/.025 temporal margins
where inherited, and grain age >=.02 using both activations. Include z=1 after
both exits outside its legitimate exclusions. Continuous phases/cup keep all times.

| Row | Cells | Modes | rtol | atol | max_step |
|---|---:|---:|---:|---:|---:|
| normal | 128 | 32 | 2e-8 | 2e-10 | .05 |
| bed_fine | 256 | 32 | 2e-8 | 2e-10 | .05 |
| modes_fine | 128 | 64 | 2e-8 | 2e-10 | .05 |
| time_fine | 128 | 32 | 2e-9 | 2e-11 | .025 |
| combined | 256 | 64 | 2e-9 | 2e-11 | .025 |

All full rows use mesh power 2, horizon 8. Add observed normal repeat and an
unobserved same-environment normal control unless an exact qualified archive
supplies neutrality. Literal 2e-11 is frozen as requested; historical 001's
time-fine serialized 2.0000000000000002e-11 is disclosed, not silently reused.
Require exact complete scientific Result equality for neutrality, independently
of seam identity/restoration; preserve historical cross-environment mismatch.

For normal against each refinement: outlet, liquid profile, front, exit and
activation <=1e-3; grain profile/seven histories <=2.3e-4; cup and each phase
<=5e-5. Aqueous in [-1e-8,1+1e-8], grain means/phase inventories >=-1e-8,
front within wet support under inherited 1e-10 numerical convention, complete
horizon/events/support and deterministic repeat are mandatory. No grain unit cap.

Ceilings: 10 full attempts, 20 short scientific invocations, 1200 aggregate
numerical seconds, 300 seconds/invocation, 2 GiB/process. Reuse the external
serial fsynced ledger/controller, adapted only to these task ceilings. Log every
start/end/failure/termination, reject unresolved starts. Include capture, memory,
replay and diagnostic work in measured costs. Ordinary software QA is separate;
no new full trajectories are hidden in tests. One short positive-D feasibility
pilot precedes any full matrix. Preserve three correction slots and 300 seconds;
primary work including pilots must fit 900 seconds. Full allocation requires
defensible time/memory estimates for every row, not linear cell-count scaling.
If infeasible retain RESOURCE_FEASIBILITY_BLOCKED and delivered code/tests;
do not spend full slots speculatively, reduce support or raise ceilings.

One demonstrated observer-only correction may reuse unchanged safe captures
with old/new observer identities and affected offline requalification. A failed
unchanged production gate is retained; no solver repair or resolution rescue.

## Failure-first reporting and handoff

A single execution is EXECUTED_UNQUALIFIED. The offline reporter launches no
solver and recomputes from identity-bound arrays. Wrong source/config/support,
malformed/nonfinite data, missing rows/events/histories, incomplete horizon,
unresolved attempts, resource violations and numerical failures retain individual
reasons. CLI disposition, JSON and exit code must agree.

Outcomes: BASELINE_RAW_OBSERVATION_NUMERICALLY_QUALIFIED_ON_DECLARED_CASES only
when every gate passes; BASELINE_QUALIFICATION_INCOMPLETE when observer/neutrality
qualify but unchanged production fails; OBSERVER_QUALIFICATION_INCOMPLETE when
observation or neutrality fails/is unresolved. Source/environment/resource blocks
remain separate; an unexecuted matrix is not a demonstrated production failure.
Software QA, hosted CI, independent review and physical validation stay separate.
