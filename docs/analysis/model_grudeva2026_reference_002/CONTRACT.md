# MODEL-GRUDEVA2026-REFERENCE-002

G2 / NUMERICAL_METHOD_CHANGE. Issue #67; one new branch and draft PR.
PHYSICAL_VALIDATION=NOT_ESTABLISHED. This is a public numerical-reference
diagnostic, not a protected holdout. No fitting or source-setting alternative.
Frozen before comparative execution; finite matrix below follows two short pilots.

## Scope, source preflight and selection

Live Puckworks main is 8f5607799ff08ced4524b58aef653b8760a448d9, the merge
of #308 at d4c2290adac26012d09fa2868b7faef9aec30598. Live EWP main is
73ec476ffe6ac626705ca949e28b32935ddf2992. Neither has drift from the supplied
bases. #308's two independent nonhuman review receipts and final QA receipt
were inspected; no GitHub formal review submission is recorded. Open issues, PRs, remote branches and local worktrees disclose no duplicate REFERENCE-002.
Owner worktrees, EWP, its dependency lock/tag, production models/defaults and
every #308 artifact are preserved. No automatic successor or issue closure.

NEW_INFORMATION: a different coupled numerical route and independently weighted
phase accounting. POSITIVE: retain the baseline if independently corroborated;
demonstrated defect: repair only that defect; DISAGREEMENT: localize it or retain
an unresolved result; BLOCKED: no oracle or publication inference. GRINDER_TO_CUP:
qualify the native fixed-flow extraction reference. REPEATED_BLOCKER: this is
not another absolute-chemistry or laboratory-closure study. The owner's bounded
task adds numerical information; a second backend or full-PDE rescue is excluded.

MANIFEST, AVAILABLE_DATA_REGISTER, data guide, current cards and previous
contract/results/remediation were inspected. Relevant dataset IDs are
grudeva2026/analytic_reference, grudeva2026/publication_reference,
grudeva2025/params and grudeva2025/exp13_vial_stats. The latter two are catalog
context, not numerical Figures 3/4 arrays or chemistry inputs. The existing
data-source configuration resolves the publication collection. Actually read:
primary article Eqs.18–29,67–77, Tables 1/2, Figures 3/4 and legends; supplement
E.2, E26–E33 (pp.13–15), including fixed-z grains, interpolation, explicit grain
and front steps and implicit upwind liquid transport. Merely cataloged unrelated
corpora are not inspected observations or exhausted evidence.

Sources: Grudeva, Moroney & Foster, EJAM 37(2),496–519,
DOI [10.1017/S095679252500018X](https://doi.org/10.1017/S095679252500018X).
Article SHA256 592304014b7be482b5fe2814d730f7d128f9ec2e77d6f7d25f8e0292c5fce5e5;
supplement SHA256 5437e3310288c2a9506fbd1eb4c4d8854ec8f4293f6edcda5579bbdc9bae5179.
Article is CC-BY-4.0; source text/PDFs are not added. Figure fixtures keep their
original identities, raster extraction bounds (not Gaussian SD), coordinates,
samples and budgets. Gray is epsilon→0; colored curves are finite epsilon.
Figure 5 remains FIG5_REFERENCE_INCOMPLETE: no author full arrays, exact
diffusion coefficient or observation grid is supplied by these sources.

Selected route A: isolated adaptation of the already permissioned shipped
grudeva2025 reduced implementation, itself a port of Yoana Grudeva's
espresso-model. Permission record and THIRD_PARTY_NOTICES apply to this
derived analysis copy, not arbitrary upstream files or private correspondence.
This is a modified reference-lineage computation, never an untouched author
result. Reading it now does not rewrite #308's equation-derived provenance.
No grudeva2026 RHS, speed, modes, flux or moving-mesh helper enters this core.

## Equation → code → input mapping

All concentrations use the current phase-volume basis; time is t_dim/t_w,
t_w=phi_T*L/q_app. No dimensional geometry is assumed for the canonical solve.

| Mathematical quantity | Analysis implementation | Frozen value |
|---|---|---|
| phi_f,phi_b,phi_l,varphi_lb | canonical constants | .64,.16,.20,0 |
| phi_T,gamma,beta,delta,a | constants / normalization audit | .20,1,3.2,.8,4.2 |
| q,D_sb,c_f_init,c_b_init | coupled inputs | 1,1,1.388,1.388 |
| Q_f,Q_b | effective coefficient audit | .20/(3*.64),.20/(3*.16) |
| s_w | prescribed wetting | min(t,1) |
| a C_t+C_z=G_b, C(0,t)=0 | implicit upwind liquid step | moving eta=z/s |
| c_b,t=D/r² (r² c_b,r)_r | radial shell matrix | fixed physical z |
| c_b,r(0)=0,c_b(1)=C | zero central face / surface conductance | no clipping |
| B=3 integral c_b r²dr; B_t=-3Q_bG_b | shell-volume mean / flux | exact discrete balance |
| s'=(1-Cf)/(gamma(1-Cf)+beta(c_f_init-Cf)) | jump_speed | source Eq.74 grouping |
| outlet | segment convention | 0 before 1; 1 before arrival; C(1,t) after |

Rankine–Hugoniot: storage ahead minus behind is
gamma*(1-C_front)+beta*(c_f_init-C_front). Boulders have the same interior
inventory on either side at zero age, so their jump cancels. The advective
flux jump is 1-C_front. Dividing these jumps yields the front law above.

At each physical grain z, diffusion starts at t_desat=s^{-1}(z), not z.
Interior starts at 1.388; changing the surface has zero volume but integrable
short-age flux. Eqs.68–70 form an autonomous diffusion problem: shifting both
activation and observation time cannot change the result. Its Duhamel kernel
depends on t-u. Printed Eq.71's absolute/elapsed-time inconsistency is not used.
Ahead of desaturation, grains retain 1.388; liquid is one where wet and absent
where dry. The fixed whole-bed problem continues after localized arrival.

Legacy audit: b0=(3phi_f/af+3phi_b/ab)/2, bf=3phi_f/(af*b0),
bb=3phi_b/(ab*b0), Qf=phi_T/(af*b0), Qb=phi_T/(ab*b0). Thus
bf/(3Qf)=beta=3.2 and bb/Qb=3delta=2.4=1/Q_b_canonical, regardless of radii.
Bare canonical Q values must not be substituted while retaining bf/bb.
The shipped clock uses t_drip and a 32-second horizon, empirical post-drip flow,
Darcy pre-drip flow and a cafe D=.021. None is a canonical parameter.
Its explicit M=30 diffusion step has dt*D/dr²≈1.795 at Nt=3000 and
t_drip=5 if D is replaced by one; it is not stable qualification for this case.
Table 1's 310/224=1.3839285714285714 is kept distinct from Table 2's 1.388.

## Numerical adaptation and accounting

Departures from the shipped reference: dimensionless fixed flow/horizon and
canonical inventories; configurable bed/radial/time controls; conservative
shell-volume radial diffusion with implicit backward Euler (instead of nodal
explicit diffusion); fractional first grain step beginning at the linearly
localized activation; source at the receiving liquid node (remove the original
one-node source lag); explicit event split at s=1, without front clamping;
separate pre/post-drip outlet convention and discharge; actual grain/liquid
states and integrated source observations. No fitted chemistry or epsilon knob.
The liquid grid and fixed-z grain-grid linear interpolation retain the legacy
route and must qualify independently; they are not assumed conservative.

Derivation: at fixed eta, C_t|eta=C_t|z+eta*s'*C_z, so
C_t|eta+(1/a-eta*s') C_eta/s=G/a. First-order implicit upwind approximates
this equation on moving liquid nodes. The front uses the preceding front value
and forward Euler with a split crossing step. Fixed-z grain states never move
with eta. Partial activation steps integrate only positive desaturation ages.
Radial shells have weights r_outer³-r_inner³ and conductances
3D*r_face²/(r_center_right-r_center_left); the surface uses half-shell distance.
The mass-weighted internal fluxes telescope. The implicit matrix is an M-matrix;
no explicit radial stability restriction or mass/concentration projection.

Independent inventory observer integrates the piecewise-linear liquid on
[0,s], and fixed-z grain means with an explicit untouched front value 1.388
before arrival. It reports both full and alternate quadrature controls; these
observations require refinement, and cannot be passed off as exact cell masses.
M_l=I_C+w-s; M_f=3.2*(I_C+1.388*(1-s));
M_b=.8*(I_B+1.388*(1-s)); M0=5.552. Residual=(sum phases+cup-M0)/M0.
Outlet integration splits at 1 and arrival; right-step discharge is checked
against independently integrated piecewise-linear smooth segments. Integrated
grain transfer is checked against actual B changes. Terminal bed inventory is
reported, not assumed depleted. No nonzero-pore run is selected.

## Qualification and comparison gates

Original gates: constant-front relative error 1e-12; analytic grain flux/mean
absolute errors 2e-4/2e-5 at ages .002,.02,.1,.3,.7; normalized global residual
1e-6; accepted aqueous bounds [-1e-8,1+1e-8], nonnegative grain/inventory
within 1e-8, s<=s_w. Each bed/radial/time refinement: smooth outlet and event
changes <=1e-3. No qualification follows just from stable process exit.
Independent analytic expectations are evaluated without either backend.
Tests include shifted activation 4.3 and 15.3, linear boundary, equilibrium,
uptake, shell balance, and the coupled D=0 analytical limit through front
passage (C=0, s=t/5.4416, inactive boulders, post-arrival C=0).
A small positive-D coupled case tests transfer/transport as well.

Before any main inter-method comparison, the alternate must pass its analytical,
coupled and refinement/conservation qualification. Failure gives
COMPARATOR_QUALIFICATION_INCOMPLETE; canonical qualification diagnostics may
still be reported but not scored as independent truth. Do not run another backend.

Prospective inter-method norms: max absolute difference, dimensionless scale 1,
over identical physical z and t. Liquid/outlet/front/arrival/activation <=1e-3.
Grain means <=5e-4 at ages >=.02: analytic mean budget 2e-5 per method leaves
4.6e-4 for independently measured spatial/temporal/observer errors; require
their sum <=5e-4 before acceptance. Each phase inventory and cup <=1e-4 in
phi_T*L*A*c_sat units, with independently assessed quadrature/refinement error
<=5e-5 per method. These are acceptance targets, not fitted tolerances.
Unqualified errors/support mean UNAVAILABLE, not agreement. Integrated source
and radial profiles are diagnostics (no indistinguishability claim).

Samples: t=0,.01,.05,.1,.2,.4,.8,1,1.01,2,3.2,4.8,6.4,8 plus all original
Figure 4 times and uniform .025 time intervals, with denser .005 intervals
from 6.3 to 6.7. Physical z=0:.005:1 plus original Figure 3 coordinates;
grain histories z=.025,.1,.25,.5,.75,.9,1. One-sided values at each localized
event; no interpolation across jumps. Numerical smooth support excludes the
entire interval between displaced fronts/events plus .008/.025 respectively;
displacement is separately scored. Early differences are diagnostic until
numerical and observation uncertainties qualify.

Publication gates stay Figure 3 concentration/front .015/.008 and Figure 4
concentration/arrival .015/.025, with their original whole-displaced-interval
masks. Included/excluded/unavailable counts must be explicit and nonempty.
No fixture or extraction correction absent a distinguishing provenance test.
Sparse publication data locate a discrepancy only at supported samples.

## Resource ceiling

Two short feasibility pilots: (bed,shells,dt,horizon)=(64,32,.002,.4) and
(128,64,.001,.4). They count even if failed. After them, freeze the exact
remaining matrix here before executing it. Total ceiling: 14 coupled runs,
including pilot, failed, diagnostic, baseline observer/replay and reruns;
3600 seconds summed numerical wall time, 900 seconds per run, 2 GiB per
process. Analytical fixture solves are separately counted and capped at 24
grain histories, 120 seconds each. Software regression/CI time is reported
separately. No silent cap extension; ordinary corrections consume remaining
slots and repeat affected qualification. No production instrumentation until
the comparator qualifies; baseline history is reusable only by verified hashes.

### Frozen post-pilot matrix

Both pilots completed with conservation residuals 0.0016467341 and 0.0010761622,
so neither qualifies. Radial analytical checks passed at 3200 shells. The
remaining matrix is chosen to distinguish bed interpolation, radial and time
errors; closeness to the publication is not a selection criterion.

| Run | Bed nodes | Radial shells | dt | Horizon | D |
|---|---:|---:|---:|---:|---:|
| limit | 32 | 16 | .01 | 8 | 0 (analytical fixture only) |
| normal | 128 | 64 | .001 | 8 | 1 |
| bed_fine | 256 | 64 | .001 | 8 | 1 |
| bed_finer | 512 | 64 | .001 | 8 | 1 |
| radial_fine | 128 | 128 | .001 | 8 | 1 |
| time_fine | 128 | 64 | .0005 | 8 | 1 |
| combined | 512 | 128 | .0005 | 8 | 1 |

Nine coupled scientific runs including pilots. Up to five remaining slots are
reserved for material debugging or baseline observation if qualification is
achieved, with controls declared before execution; unused slots expire. Each
scientific invocation, including a failed one, is retained. Repeated small
software fixtures/hosted tests are counted separately from this finite scientific
matrix. The coupled D=0 fixture requires front/event relative error <=1e-12,
zero liquid and constant grains, conservation <=1e-6 and correct outlet jump.
A manufactured moving-domain liquid case C=k*z, G=k, k=.2 tests transport and
coordinate transformation to 1e-12 at nonzero s. Its expected result is
algebraic and obtained without either backend. The positive-D pilots already
exercise coupled transfer and expose a failed conservation gate.

### Numerical debugging record (same route, unchanged problem and gates)

The first .0005 time-refinement attempt failed at the terminal sample because
an absolute-tolerance sample check advanced the index a fraction of a timestep
early. This is an alternate-harness scheduler defect, not a physical/source
change. Regular observation grids now remove floating-point duplicate times;
a sample is advanced only when the chosen step actually reaches its target.
The first four canonical outputs and the failed invocation are retained under
their original code identities. All six canonical qualification rows are rerun
at identical declared controls after this correction. The analytical D=0 limit
is unchanged and its prior exact analytical check is retained. Count: two
pilots + one limit + four initial canonical runs + one failed time run + six
final canonical runs = 14. This consumes the ceiling; no further coupled run,
new backend, baseline instrumentation or source-setting alternative follows.
Analytical/radial tests and software QA remain separate recorded checks.

The first scheduler correction exposed a second endpoint-rounding case in its
first normal run: adding dt rounded exactly to the target even though dt was
slightly less than target-t. That invocation failed serialization after a zero
step and counts as run 9. A direct regression now distinguishes exact endpoint
arrival from an early tolerance hit; no coupled solve is needed for that test.
Remaining five slots execute normal, bed_fine, radial_fine, time_fine and
combined at the SAME controls above. The extra bed_finer repeat is canceled;
its old diagnostic stays retained and unqualified. The cap remains 14; missing
qualification is reported as such, never waived. No scientific threshold or
source input changes. This supersedes the six-repeat plan, not prior evidence.

Post-run observation audit found the outer `horizon-1e-13` termination guard
still omitted the final saved sample for time_fine and combined (last saved
sample 7.975, although internal stepping approached 8). This is not hidden:
those runs lack a t=8 ledger observation. The current harness terminates on
exhaustion of scheduled samples, with a direct synthetic scheduler regression.
No coupled rerun is allowed after the 14-run cap. Therefore the final executable
is NOT numerically requalified after this observation-only fix, and all stored
numerical results remain bound to their pre-fix source SHA; a private copy of
that source is retained. No old result is restamped. Source/baseline claims are
unaffected; the comparator remains unqualified for several independent reasons.
