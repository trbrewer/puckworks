# MODEL-GRUDEVA2026-CONSERVATIVE-003

G2 / NUMERICAL_METHOD_CHANGE; issue #67. Analysis only. One isolated branch,
one draft PR, no merge or automatic successor. PHYSICAL_VALIDATION=NOT_ESTABLISHED.
This contract is fixed before numerical development. Settings will be selected
by numerical error and measured cost, never publication agreement.

## Intake and available-data preflight

Live main heads checked 2026-10-03: Puckworks
`73b55cf807051b3ce2a0740bdb768f821f002668`, EWP
`73ec476ffe6ac626705ca949e28b32935ddf2992`. PR #309 is merged at the supplied
reviewed head; #67 is open. Open PR searches in both repositories, remote
model/grudeva2026 branch prefixes, and local worktree lists show no 003 duplicate.
The new branch starts at Puckworks main. EWP's clean owner checkout is older
than public main; both its local boundaries and public state/claim ceiling/use
map were inspected read-only. No unrelated development or dependency refresh.

NEW_INFORMATION: conservative actual coupled exchange and transport on the
fixed-position radial route that 002 could not qualify. POSITIVE: independently
corroborate the preserved baseline; NEGATIVE: retain a qualified distinguishing
discrepancy for owner disposition; INCOMPLETE: retain the local repair without
an oracle claim. GRINDER_TO_CUP_LINK: numerical reliability of native fixed-flow
extraction. REPEATED_BLOCKER: this does not revisit the missing absolute-chemistry
measurement; the new information is a direct conservative numerical calculation.
LOWER_COST_ALTERNATIVE: the algebraic counterexample alone cannot adjudicate a
trajectory. No new governance machinery, chemistry inputs or measurement agenda.

Read: repository rules/onboarding, minimum governance, scoped planning/card,
data guide, MANIFEST and capability register, 001 contract/results/handoff and
remediation bindings, 002 contract/results/handoff/core/reporter/tests, production
API/result/observation seam, permission record and notices. Relevant IDs:
grudeva2026/analytic_reference and publication_reference. grudeva2025/params and
exp13_vial_stats are lineage/catalog context, not canonical arrays or new inputs.
Other external corpora are catalog-only; no data-exhaustion conclusion.

Actually inspected through the existing configured collection: article reduced
equations 64–77, clocks and storage; supplement E.2/E26–E33, pp.13–15 (fixed-z
grains, source interpolation, explicit grain/front and implicit liquid methods).
Article SHA256 `592304014b7be482b5fe2814d730f7d128f9ec2e77d6f7d25f8e0292c5fce5e5`;
supplement `5437e3310288c2a9506fbd1eb4c4d8854ec8f4293f6edcda5579bbdc9bae5179`.
Private source text and correspondence are not distributed. Figure fixtures
are reused by verified identity; this task does not claim fresh visual extraction.

Mathematical authority: Grudeva, Moroney & Foster, EJAM 37(2), 496–519,
[DOI 10.1017/S095679252500018X](https://doi.org/10.1017/S095679252500018X),
CC-BY-4.0 article. The 002 radial finite-volume operator is reused under its
documented Grudeva reference-lineage permission; the surrounding conservative
adaptation is new. This is neither an untouched author run nor an independently
equation-derived historical port. No production RHS, front, mesh or modal
evolution helper is copied into the core. Diagonalizing the *radial shell matrix*
below is a time integrator for that matrix, not another spatial backend.

## Unchanged physical problem and storage

phi_f=.64, phi_b=.16, phi_l=.20, varphi_lb=0, phi_T=.20, q=D_sb=gamma=1,
c_f_init=c_b_init=1.388, beta=3.2, delta=.8, a=4.2,
Q_f=.20/(3*.64), Q_b=.20/(3*.16), s_w=min(t,1).
Behind s=s_d: a C_t+C_z=G, C(0,t)=0; c_t=D r^-2(r²c_r)_r,
c_r(0)=0, c(1)=C, B=3 integral c r²dr, delta B_t=-G.
s'=(1-Cf)/[1+beta*1.388-a*Cf]. Activation is s^-1(z), not z.
The corrected Eq.71 elapsed-time kernel and Eq.74 grouping are inherited;
the effective legacy audit remains bf/(3Qf)=3.2, bb/Qb=2.4. Bare canonical
Q values are never inserted into formulas retaining separate legacy areas.

a*C is **liquid plus locally equilibrated fines storage**. Only C is advected.
Exchange on fixed support satisfies ΔM_l+ΔM_f+ΔM_b=0, with
ΔM_l=ΔI_C, ΔM_f=beta*ΔI_C, ΔM_b=delta*ΔI_B.
For actual state integrals I_C, I_B on [0,s], w=min(t,1):
M_l=I_C+w-s; M_f=beta*(I_C+1.388*(1-s));
M_b=delta*(I_B+1.388*(1-s)); M0=5.552.
Cup is zero before 1, then integrates plateau 1 until exit, then actual outlet.
No arbitrary initial reservoir, hidden time offset, renormalization, clipping,
outlet rescaling or M_bed=M0-M_cup. Finite t=8 does not assert depletion.

## Conservative representation and transfer

Physical bed faces are fixed. The last active cell is cut at the advancing
front, so only its right face moves. Liquid state is a cell average; grain
state J is the **integral** of radial shell concentration over each active
physical cell. Existing grains never move or reset. An incomplete cell receives
initial material continuously at rate v', not a lump of grains with a common
age. This differs from the old nodal inventory and must use its own volumes.

For overlaps O_ij=length(receiver_i intersect donor_j), v_r=O*1,
v_d=O^T*1, P=diag(v_r)^-1 O. Thus v_r^T P=v_d^T. Transferred amounts use
T=O diag(v_d)^-1, whose columns sum to one. Signed donor losses are passed
through the same amount operator used by the coupled solve. Coincident cut
cells are its identity case; nonmatching/nonuniform supports exercise the
same exchange update on fixed support. Uncovered support is an error, never
constant-endpoint extension. [Taylor 2024](https://gmd.copernicus.org/articles/17/415/2024/)
is authority for compatible integral weights, not a coffee algorithm.

The old fixed-front counterexample is retained: nodal mapping receives .00016
while a triangular loss profile donates .00008. This is an algebraic mismatch
of mapped source versus observed loss, not a measured liquid-state change or
a claimed factor-two canonical trajectory error.
In the new cell-average representation that prescribed triangular loss has
mean .05 on [0,.002], hence amount .8*.002*.05=.00008. The paired map retains
that amount on a nonmatching receiver grid. The actual implicit exchange test
instead starts from grain/liquid states and derives its donation from the solved
shell-state change; it is not forced to reproduce .00008 for different states.

## Radial time integration and activation

Use the existing conservative shell operator A, weights W=diag(diff(r³)),
and A*1=-f. Symmetric W^.5 A W^-.5 is diagonalized once, retaining **every**
shell degree of freedom. No analytic-mode truncation or fitted tail is added.
If Q diagonalizes this matrix, p=Q^T sqrt(w), shell integrated state is
J=W^-.5 Q diag(p) j and its mean integral is (p²)^T j.
These weights are derived, never adjusted to close inventory. Independent
shell reconstruction checks the integral. Rates are minus the eigenvalues.

For rate lambda, x=lambda*h, E=exp(-x), f1=(1-E)/x,
f2=(x-1+E)/x², with analytic limits at zero. Linear boundary C0→C1 and
linear active volume v0→v0+dv give the exact shell-ODE update

    j1 = E*j0 + v0*((f1-E)*C0+(1-f1)*C1)
         + dv*(1.388*f1+(2*f2-f1)*C0+(1-2*f2)*C1).

This is the integral over continuously admitted activation cohorts, including
their different ages. No instantaneous continuum flux of zero is assigned at
activation. Finite radial resolution regularizes the pointwise singularity;
interval exchange is the actual initial-plus-admitted inventory minus J1.
Positive-age flux and mean are separately tested with the same shell matrix
and exact interval integrator, including linear boundary, signed uptake,
equilibrium and time translation.

## Transport and front balance

Reynolds transport applied to a*C_t+C_z=G gives
d/dt integral_[left,right] a*C dz = -[(1-a*v_mesh)*C]_left^right + integral G dz.
The cut-cell update uses actual old/new volumes and conservative face amounts,
with trapezoidal concentration traces at both ends of the step:

    a*(v1*C1-v0*C0) = F_left-F_right + transferred_grain_amount,
    F_face = (h-a*Δz_face)*(Cface0+Cface1)/2.

Interior traces use linear upwind reconstruction of cell averages; the inlet
is zero. The front displacement is solved with that SAME front trace:
h*(1-Cf_star)-ds*(1+beta*1.388-a*Cf_star)=0.
At cell crossings and exit, localize h to the face. The sum telescopes to the
complete phase/cup balance, including admitted initial boulders and changing
saturated/dry volumes. Zero moving speed recovers fixed-volume transport;
constant traces recover geometric conservation. First drip splits exactly at 1.
The initially empty active domain starts with zero integrated states at t=0.

## Verification, observations and budgets

Before testing, algebraic allowance is 256*machine_epsilon times the sum of
absolute participating inventory/flux terms, plus measured linear/nonlinear
solve residual in amount units. Report the dimensionless residual divided by
that scale as well as the raw amount error; never use the 1e-6 global budget
as a transfer tolerance. Eigenbasis reconstruction additionally reports its
orthogonality/integral error separately.

Inherited numerical gates: constant-front speed/arrival relative <=1e-12;
positive-age (.002,.02,.1,.3,.7) flux <=2e-4, mean <=2e-5; global normalized
residual <=1e-6; aqueous [-1e-8,1+1e-8], grains/inventories >=-1e-8;
s_d<=s_w. Each bed/radial/time refinement and combined refinement requires
smooth outlet/event changes <=1e-3, with local profiles/histories and individual
phase/cup refinement assessed too. The D=0 limit remains C=0, boulders unchanged,
exit 5.4416 and plateau from 1 until exit. No upper grain concentration cap.

Actual discrete integrals are authoritative. Independent shell reconstruction,
cell quadrature and event-split cup quadrature are separate checks, not plotting
sample integration. Balance is checked at every accepted step and event.
Fixed-z histories are separate observation trajectories driven by the numerical
liquid history; their reconstruction/refinement must qualify before comparison.

Observation support and all acceptance semantics are inherited without waiver
from 002: stated 14 times, original Figure 4 times, uniform .025 samples, .005
from 6.3–6.7, z=0:.005:1 plus Figure 3 coordinates, grain z=.025,.1,.25,.5,.75,.9,1.
Retain one-sided event states, no extrapolation or interpolation across jumps.
Exclude the full displaced-jump interval plus .008 spatial/.025 temporal;
score displacement separately; count included/excluded/unavailable; empty
support cannot pass. Liquid/outlet/front/arrival/activation <=1e-3; grain means
at age>=.02 <=5e-4 with the inherited error allocation; phase/cup <=1e-4 with
independently assessed allowance <=5e-5 per method. Empirical refinement changes
are not rigorous continuum-error bounds. Figures 3/4 budgets .015/.008 and
.015/.025, unchanged masks and historical FAIL/FAIL; Figure 5 remains incomplete.

Baseline runs are conditional on alternative coupled qualification. A task-local
observer may intercept solver returns, return the same objects unchanged and
restore instrumentation. Raw states/geometry must independently reconstruct
inventories; observations stay within valid segments. Identical-settings
unobserved or hash-qualified archived output is required to establish neutrality.
Unqualified alternative, baseline or observer makes agreement UNAVAILABLE.

## Resource contract

Every scientific numerical invocation is timestamped and retained, including
short fixtures, failed starts and terminations. Ceiling: 24 intended full-horizon
executions including failures/baselines; 3600 aggregate numerical seconds;
900 seconds and 2 GiB per process. Software QA is separate and contains no new
full-horizon runs. Before final-source use reserve >=8 full slots and >=1800
seconds; stop candidate debugging at either boundary. Pilot costs determine a
feasible final matrix. Source/observer/scheduler fixes precede the reserve;
changed scientific hashes invalidate affected evidence. No automatic increase.

Prospective first short qualification: shell integrator at 800/1600/3200 shells,
local signed exchange/geometry/activation fixtures, then two canonical short
pilots (bed 64/128, shells 1600, dt .002/.001, horizon .4). These are not
full-horizon slots and consume aggregate time. The finite full matrix is declared
after those costs, before execution. Baseline qualification is earmarked at least
four slots (identical-settings neutrality, bed, time and modes); fewer available
slots cannot silently reduce its uncertainty gates.

Pilot outcome before full execution: both .4 trajectories conserve to
3.20e-16 normalized; invocation costs 1.47/2.47 seconds. The exact shell
integrator requires 3200 shells (1600 fails positive-age flux, about 6.40e-4;
3200 gives 1.61e-4). Next candidate full rows, before the completion reserve:
(128,3200,.002,8,D=1) and the limit (32,16,.01,8,D=0). A 256-cell/.001
candidate may follow only if the first full row supports continuation. No
baseline trajectory or inter-method score occurs during candidate development.

Both first full candidates conserve (max normalized residual below 7e-14), but
128→256 cells with the time refinement changes arrival by .00555, so neither
is qualified by that pair. Before a final matrix, one 512/3200/.004 candidate
measures feasibility at finer bed resolution with the exact radial integrator.
The timestep is a numerical control, not a parameter fit. Algebraically identical
radial mean-first evaluation avoids constructing full trial states while locating
cell crossings; fixed-z observers now use cell-local linear liquid reconstruction.
Earlier candidates remain tied to their old source. Final evidence must use the
corrected observer and source, including the D=0 full limit.

The first D=0 full invocation failed its front-root bracket; it remains counted.
The strict bracket ds in [0,h/a] has residual h*(1-JUMP/a)<0 at its upper end,
independent of roundoff-sized C, without clipping C. The corrected limit exits
at 5.441599999999974. An audit also found that the amount allowance's scale must
include both actual grain inventories participating in their subtraction, as
already required by the norm definition, even when their difference is zero.
The final observer supplies the actual inlet grain limit and evolved outlet
history rather than extending endpoint cell averages. These corrections precede
the final matrix; old outputs are not restamped.

### Final-source allocation (2026-10-03)

Core `e2f39c4faaca47effac7ff55179e00d7a788a03a7d0d6f17b26f71354a67a57f`;
task-local baseline observer
`497eb0ee3e5a1ccce5814e0bc65ce302bcb0ef2e3f45199d0a650f1569e65022`.
The corrected-source local analytical invocation passes; the full final matrix
is [MATRIX.json](MATRIX.json). Immediately before it: five full attempts and
231.73 numerical seconds used, leaving 19 slots and 3368.27 seconds. The final
512/3200/.004 pilot cost 63.84 seconds. Conservative cost estimates for the
matrix below total approximately 1500 seconds, with the largest about 650,
leaving the required >=1800-second and >=8-slot reserve available at allocation.
Earmark five baseline runs (normal with archived neutrality, bed, time, modes,
combined), plus one unobserved control if archived neutrality is not exact;
these are conditional and are not silently spent on candidate debugging.

| Final row | Bed cells | Shells | dt | Horizon |
|---|---:|---:|---:|---:|
| normal | 512 | 3200 | .002 | 8 |
| bed_fine | 1024 | 3200 | .002 | 8 |
| radial_fine | 512 | 6400 | .002 | 8 |
| time_fine | 512 | 3200 | .001 | 8 |
| combined | 1024 | 6400 | .001 | 8 |

Also rerun the corrected-source full D=0 limit (32/16/.01), counting its full
slot. All rows preserve source parameters. This is a bounded qualification
matrix, not a guarantee of passing. Full local/phase observations and their
allowances remain load-bearing; outlet or conservation success cannot waive
them. If they fail, baseline execution and inter-method scoring stay unavailable.

The final local invocation also checks 6400 shells, the radial-fine setting;
neither its analytical qualification nor 3200-shell qualification is inferred
from the other setting. Reporter-only JSON serialization and support-mask
corrections are replayed against retained arrays; they do not restamp an earlier
scientific source or require a different coupled trajectory.
