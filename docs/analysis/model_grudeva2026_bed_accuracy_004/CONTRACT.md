# MODEL-GRUDEVA2026-BED-ACCURACY-004

G2 / NUMERICAL_METHOD_CHANGE; analysis only, issue #67. One isolated branch and
one draft PR. PHYSICAL_VALIDATION=NOT_ESTABLISHED. No production changes, EWP
writes, source acquisition, parameter fitting, publication rescoring or successor.

## Starting state and source

Remote Puckworks main/tree are `4536775551c4ebd20a339e5143940532894d0d40` /
`ff7688e47d07743c901fecde6752cad2ac14bf62`; remote EWP main/tree are
`16eec1dda24ebf658965eddcf1a6fffa81903b32` /
`c044c7a6920af36842890758c0bfa423f36bd8d8`. No selecting-review drift. Issue #67
is open; live open-PR, branch and worktree searches found no equivalent 004.
Owner checkouts are preserved. PR #325 is merged; run 37711116381 remains
completed/cancelled: quality, mypy and four quick lanes passed; min-deps was
cancelled. Integration closeout is not declared complete.

Actually reopened the configured local article, typeset PDF pp.16–18 (printed
511–513), reduced equations 64–77 and surrounding definitions, and supplement
E.2, typeset pp.13–15, E26–E33. Article SHA256
`592304014b7be482b5fe2814d730f7d128f9ec2e77d6f7d25f8e0292c5fce5e5`;
supplement SHA256
`5437e3310288c2a9506fbd1eb4c4d8854ec8f4293f6edcda5579bbdc9bae5179`.
Both match 003. Source: Grudeva, Moroney & Foster,
[DOI 10.1017/S095679252500018X](https://doi.org/10.1017/S095679252500018X).
Article CC-BY-4.0; PDFs and correspondence stay external. The unchanged radial
shell operator retains the Grudeva reference-port permission and attribution
in [THIRD_PARTY_NOTICES](../../../THIRD_PARTY_NOTICES.md); this is neither an
untouched author execution nor an independently derived reused operator.

Equation mapping: 64–67 give liquid-plus-equilibrated-fines storage `a*C` and
advective flux `C`; 68–70 give fixed-z radial diffusion and paired grain loss;
74 gives the storage-jump front law; 75 gives the plateau/outlet convention;
76–77 give the canonical phase fractions, prescribed flow and diffusivity.
E26–E30 distinguish transformed liquid coordinates from physical coordinates;
E28 states the inlet/initial conditions and E31 gives the discrete zero initial
inlet value. E32–E33 retain fixed-position grains and their surface flux.
Their first-order published discretization is source context, not a requirement
to copy that scheme. Printed Eq.71's elapsed-time correction
and Eq.74 grouping remain as derived in 001–003.

| Source operation | 004 code mapping and deliberate adaptation |
|---|---|
| E26, eta=z/s_d; E27 transformed storage/advection | `run` retains physical bed faces; `transport_solve` integrates the equivalent Reynolds amounts, with only C advected. No grain coordinate transport. |
| E28, E31 zero inlet and initial liquid | `run` starts with zero liquid on empty support; `face_values` uses inlet=0. |
| E29 explicit published front step; article 74 | `step` solves the same physical front law with the shared trapezoidal face amount; `run` localizes crossings/exit. |
| E30 first-order published liquid solve | `reconstruction`/`transport_solve` use the derived integral constraints and banded conservative update below. |
| E32 fixed-z radial diffusion | Imported `003.Radial`, using permission-attributed `002.radial_operator`; unchanged exact modal interval integration and continuous birth amounts in `step`. |
| E33 surface exchange and subsequent paragraph's staggered interpolation | `step` pairs actual signed grain loss with `cut_transfer`/`transfer_amounts` on physical volumes; this retains 003's amount correction rather than the published lagged interpolation. |

## Unchanged physical and observation contract

`phi_f=.64, phi_b=.16, phi_l=phi_T=.20, varphi_lb=0, q=D_sb=gamma=1`,
`INITIAL=c_f_init=c_b_init=1.388, beta=3.2, delta=.8, a=4.2`.
`s_w=min(t,1); a*C_t+C_z=G_b; delta*B_t=-G_b` and
`s_d'=(1-C_front)/(1+beta*INITIAL-a*C_front)`.
Activation is `s_d^-1(z)`, with continuous admission and retained fixed-z
memory. Only C advects. Signed exchange uses identical transferred amounts
with compatible physical volumes. No clipping, complement inventory,
compensating reservoir, calibration, arbitrary time shift or rescaling.

For actual state integrals on [0,s_d], independently reconstruct
`M_l=I_C+min(t,1)-s_d`, `M_f=beta*(I_C+INITIAL*(1-s_d))`,
`M_b=delta*(I_B+INITIAL*(1-s_d))`; `M_initial=5.552`.
Cup is zero before t=1, then integrates the unit plateau until exit, then the
actual outlet flux. Continue region (i) through t=8; report residual inventory.

Reuse unchanged 003 observation_support: 395 times, 220 physical-z coordinates,
seven fixed-z histories plus event states. No interpolation across jumps or
unsupported endpoints. Preserve whole displaced-jump exclusions: spatial .008,
temporal .025 and grain age >=.02. After both exits z=1 remains included outside
its outlet event margin; continuous inventories retain all times.

Each bed/radial/time/combined refinement must pass max absolute changes:
outlet/liquid/front/arrival/activation .001; grain profiles/histories .00023;
cup and each phase .00005. Keep the .00002 analytical grain allocation per
method. These are empirical refinement allowances, not continuum error bounds
or experimental uncertainty. Report requested/included/excluded/unavailable
counts; missing or empty required support cannot pass.

Other gates: positive-age radial flux <=.0002 and mean <=.00002 on inherited
fixtures; constant-front/D=0 speed and arrival relative <=1e-12 (exit 5.4416);
global normalized conservation <=1e-6; local amount closure <=256*epsilon times
participating absolute amounts plus measured solve residual in amount units;
aqueous [-1e-8,1+1e-8], grain/phase >=-1e-8 and s_d<=s_w. Grain has no unit cap.
Check shell integrals and event-split cup quadrature independently.

## Prospective diagnostic families (frozen before diagnostic results)

Only these three families; all short numerical invocations use the external
controller and consume the common ledger. Bed refinements 32,64,128; optional
confirming pair 256,512 only for archived-state reconstruction, not new full
trajectories. No scheme is selected by these declarations.

**A — transport and reconstruction.** Hypothesis: the evolved transport or
boundary closure loses spatial accuracy even for smooth curved fields.
Use `C(z,t)=(.2+.1*t)*(z+z*z)` on fixed [0,1], exact primitive cell integrals,
face values and `G=a*.1*(z+z*z)+(.2+.1*t)*(1+2*z)`; horizon .1,
dt=1e-4 and a 128-cell dt/2 confirmation. Report cell-average, face and point
errors separately, including inlet/outlet. Expected second-order spatial
convergence; error ratio >=3 on 64/128 and time contamination <10% of spatial
error are the discriminators. Existing constant/linear tests are controls only.

**B — front and admission.** Hypothesis: curved/short-age fronts defeat a
linear trace, or admission integration incorrectly projects the liquid source.
Prescribe s(t)=.16*t+.01*t*t and analytic boundary histories (constant control
and time-varying quadratic plus spatial linear). Distinct cut fractions .2,.5,.8
and a cell crossing are required. Independently integrate physical cohorts
with matrix exponentials/Gaussian quadrature; double quadrature until changes
are <1e-9. Distinguish geometry (D=0, exact to roundoff) from positive diffusion.
For source-integration time refinement expect ratio >=3 when asymptotic.
Also measure reconstruction of the exact age-dependent spherical response:
finite-shell spectral sums are checked against independently assembled shell
matrix exponentials. No expectation of polynomial order at zero age is imposed;
measure its loss separately and compare its size with smooth errors.

**C — grain forcing and readout.** Supply analytic activation and liquid
histories, and independently integrated cell means. At inlet, interior, partial
front cell and post-exit endpoint compare: evolved integral, cell-center profile
interpolation and separate point_liquid forcing of fixed-z histories. Refine
32/64/128, keeping radial and temporal oracle differences <1e-9 for the finite
shell fixture. Vary activation/boundary history beyond the old constant fixture.
Errors >10 times the measured oracle uncertainty demonstrate an operation's
defect; materiality requires location/scaling agreement with verified archived
003 differences, not merely the existence of different observation paths.

Diagnosis and exclusions must be recorded here before implementation. Failed
diagnostics are retained. Front-aligned diagnostics never replace physical-z
acceptance or separately measured front displacement.

### Diagnosis before correction

The implicated operation is polynomial reconstruction of the short-age
diffusion layer from cell averages, both in face transport and in point-history
forcing. Spherical diffusion at admission has `B=INITIAL-O(sqrt(age))`.
With locally constant front speed v, conservation implies the leading relation
`C-C_front=delta*v/(1-a*v)*(B-INITIAL)`: C also has a square-root layer.
Linear upwind reconstruction does not reproduce it. Exact cell integrals of
`C=.3*(1-sqrt((s-z)/s))` give front errors .0284148/.0203945/.0145316 at
32/64/128 cells (full final cell), approximately half-order. Partial-cell errors
show the same mechanism at fractions .2/.5/.8. This is a trace error even when
the evolved cell averages are supplied exactly.

The stronger positive-diffusion oracle prescribes v=.15 and
`k=delta*v/(1-a*v)`, solves the finite-shell diffusion problem with `C=k*B`,
and integrates every exponential over physical cells analytically. Its
independent original-shell matrix exponential check differs by <=7.36e-14.
At fraction .5 the 32/64/128-cell front trace errors are approximately
.154/.104/.0717. Supplying exact grain transfer to the old transport update
still introduces nonzero cell-average and face-amount errors. Thus readout
alone cannot cure the mechanism.

Competing explanations are bounded, not declared absent. Smooth A at 128 cells
has average/face/point errors 6.88356e-6/9.29273e-6/1.06666e-5; time halving
changes them by <4e-12. The average ratio 2.949 narrowly FAILS the prospective
>=3 criterion (face/point pass); retain that failed diagnostic. This small smooth
closure error does not explain the much larger short-age error. Varying-boundary
quadratic-time admission gives shell-integral errors 1.62616e-8/5.99419e-9/
1.46666e-9 at dt .004/.002/.001, with independent cohort changes <=3.23e-13.
It retains continuous age integration and fixed-position memory. No activation
reset or radial backend defect is demonstrated.

The verified canonical 003 maximum liquid difference is .00513913 at
(t,z)=(6.505,.995), just after exit; maximum grain profile/history difference
.00351323 is at (6.525,1). The latter profile endpoint is the separately evolved
fixed-z history, not center interpolation. Both occur where the short-age
layer reaches the outlet. Cup and actual phase changes independently exclude
a reporting-only explanation. Canonical correction/refinement must still
establish whether fixing this mechanism suffices; no qualification is inferred.

### One coherent correction selected for development

Reconstruct cell averages with the local basis `{1,z,sqrt(d)}` where d is
distance to the moving front before exit and distance plus the elapsed-time
age distance after exit. The latter uses the measured exit speed solely as a
smooth reconstruction basis, never as a physical front or activation clock.
This resolves the demonstrated square-root term while retaining constant and
linear reproduction. Use the same conservative cell-average reconstruction
for transport faces and point liquid forcing, and a compatible reconstruction
for grain profile readout. Keep actual integrated grain states and the unchanged
exact radial/admission update; no additional radial modes or cohorts.

For weights w at a face, solve `sum(w)=1`, `sum(w*mean(z))=z_face`,
`sum(w*mean(sqrt(d)))=sqrt(d_face)` using nearby physical cell integrals
(and the exact inlet for the boundary closure). A single active cell retains
the linear inlet closure. The enriched reconstruction's integral is its stored
cell mean. Face amounts remain `(h-a*ds_face)*(trace0+trace1)/2`; front law and
paired exchange use those same amounts. Localize crossings/exit as before.
No existing grain moves or resets and no phase inventory is computed by mass
complement. This is one reconstruction correction spanning evolution/observation,
not a second radial solver or a mesh-refinement competition. Verify stability,
transition behavior and cost in bounded pilots before final allocation.

The inlet closure uses the inlet point plus the first two cell integrals in
the same basis (one-cell limit stays linear). Thus the first face enters both
neighboring equations, with opposite signs, and the banded solve has one upper
diagonal. An initial pilot exposed a singular zero-width second-cell root
bracket: coincident faces enclose no equation. Its exact limit now solves the
positive support and attaches the identical front trace; no zero-volume state
or amount is invented. The failed pilot and its source remain in the ledger.
The corrected .4 pilot (512/3200/.002) completes in 3.57 external seconds and
conserves to 3.20e-16. Minimum-dependency focused checks: 96 passed, three
existing slow tests deselected. The earlier shell-center roundoff test failure
is retained; its replacement checks non-cancelling shell amounts under the
already declared 256-epsilon allowance, not a larger scientific error budget.

Final diagnostics meet A's order/time criteria. Exact square-root face and
point errors are <=2.06e-14 and <=3.84e-15. On the independent finite-shell
travelling oracle, the 128-cell, half-cut front error falls from .0717149 to
.00626238; this oracle includes higher terms beyond the leading square root.
Smooth A's absolute cell error is not uniformly improved (1.43057e-5 at 128),
and this is reported rather than suppressed. The correction targets the
demonstrated short-age layer; full canonical refinement remains controlling.

## Resource and final execution contract

24 full-horizon attempts, including failures/repeats; 3600 aggregate numerical
seconds; 900 seconds/invocation; 2 GiB/process. Serial numerical execution,
single-thread BLAS/OpenMP; external fsynced append-only starts/ends ledger,
timeout and address-space enforcement. Unresolved starts block continuation.
Protect >=8 slots and >=1800 seconds before final allocation. No hidden full
scientific trajectory in software QA. Archived 003 normal/bed_fine arrays are
available and hash verified, so no 003 reruns are allocated.

Final rows remain (bed,shells,dt,horizon): normal (512,3200,.002,8), bed_fine
(1024,3200,.002,8), radial_fine (512,6400,.002,8), time_fine (512,3200,.001,8),
combined (1024,6400,.001,8), corrected D=0 limit, deterministic normal repeat.
After diagnosis/pilots freeze exact scientific hashes, schedule and matrix and
show remaining resources cover all seven rows plus one named bounded correction
reserve. No larger bed rescue, new masks or relaxed tolerances after failure.

### Final allocation

The exact [MATRIX.json](MATRIX.json) freezes core, observer, reporter, local
verification, controller and schedule identities before final trajectories.
At freeze: 12 short invocations, zero full attempts, 41.277029 seconds used;
24 full slots and 3558.722971 seconds remain. Local radial/diagnostic checks
pass, and the normal repository baseline passed 6132 tests (33 skipped,
72 deselected; normal selector unchanged). The new untracked implementation
was developed while the baseline suite ran; its collected baseline tests and
all pre-existing tracked files were unchanged. Final QA separately covers 004.

Estimated primary cost: 1970 seconds, largest row 720 seconds, based on the
short 512 pilot and verified 003 costs with additional reconstruction overhead.
The seven mandatory rows reserve seven slots; a further seven slots/1500 seconds
are named for **one demonstrable implementation-defect correction**, with all
affected evidence reexecuted if it fits. The external controller caps primary
spending, including development, at 2100 seconds and reserves the remaining
1500 seconds. A correction requiring more than that is incomplete, not an
automatic budget increase. Remaining resources cover the 1970+1500 estimate.
No speculative method development may consume this reserve.

Single integrations remain EXECUTED_UNQUALIFIED. Saved-result reduction must
launch no solver and fail closed on malformed/nonfinite/missing artifacts,
identity/support/event/history/resource failure. Numerical, QA, CI and one
independent exact-head review dispositions remain separate. Historical 001/002/
003 and Figures 3/4 FAIL, Figure 5 incomplete stay unchanged. Production raw-state
qualification and matched solver comparison are not executed here.

## Execution and saved-result reproduction

From an installed development checkout, set `EVIDENCE` to an external writable
directory and `ARCHIVE003` to the authorized archive containing the verified
`normal-compat-final.json` and `bed_fine-compat-final.json`. Do not put either
archive in Git. The controller refuses reused attempt names and unresolved
starts; keep the same ledger throughout a task. Commands below use the current
Python environment; run the focused tests separately with NumPy 2.0/SciPy 1.13
and retain a source-bound minimum-dependency receipt before final execution.

```sh
cp tools/grudeva2026_bed_accuracy_004_invoke.py "$EVIDENCE/invoke.py"
python "$EVIDENCE/invoke.py" example short development python -m puckworks.analysis.grudeva2026_bed_accuracy_004 --bed 32 --shells 48 --dt 0.004 --horizon 0.1 --output "$EVIDENCE/example.json"
python "$EVIDENCE/invoke.py" diagnostics-bound short development python tools/grudeva2026_bed_accuracy_004_diagnostics.py --implementation 004 --output "$EVIDENCE/diagnostics-bound.json"
python "$EVIDENCE/invoke.py" local-bound short development python tools/grudeva2026_bed_accuracy_004_verify.py --diagnostics "$EVIDENCE/diagnostics-bound.json" --minimum-receipt "$EVIDENCE/minimum-receipt.json" --output "$EVIDENCE/local-bound.json"
python tools/grudeva2026_bed_accuracy_004_campaign.py --runs-directory "$EVIDENCE" --matrix docs/analysis/model_grudeva2026_bed_accuracy_004/MATRIX.json
python -m puckworks.analysis.grudeva2026_bed_accuracy_004_report --runs-directory "$EVIDENCE" --matrix docs/analysis/model_grudeva2026_bed_accuracy_004/MATRIX.json --output "$EVIDENCE/reduced.json"
```

The small example returns an executed, unqualified trajectory; its producer
exit code is intentionally 2 and the controller records that code. Use a fresh
ledger for a separately authorized reproduction, not to reset this task's
budget. The final campaign driver is a convenience wrapper for the frozen seven
controller invocations. The executed external driver has the same row loop;
the numerical/controller hashes in MATRIX, not the wrapper's location, bind it.

The diagnostic tool also accepts `--implementation 003`; the separate
`grudeva2026_bed_accuracy_004_front_oracle.py` accepts the same switch.
`grudeva2026_bed_accuracy_004_history_oracle.py` completes family C with
independently prescribed activation, quadratic time histories and pre/post-exit
profile integrals. This supplementary verification follows implementation;
it is not retroactively presented as the evidence that selected the correction.

For the complete original evidence archive, the following **offline** writer
adds all attempt receipts and the matched 003 comparison to the frozen reducer's
output. It never runs a solver or relaxes a gate. Both reduction commands return
2 for incomplete qualification and 0 only for qualified results.

```sh
python tools/grudeva2026_bed_accuracy_004_evidence.py --runs-directory "$EVIDENCE" --baseline-directory "$ARCHIVE003" --matrix docs/analysis/model_grudeva2026_bed_accuracy_004/MATRIX.json --output docs/analysis/model_grudeva2026_bed_accuracy_004/RESULTS.json
```

The full arrays, invocation logs, source snapshots and PDFs stay external.
Public evidence binds their hashes. Historical code/fixtures/evidence are
checked against the intake preservation hashes. All reused 003 arrays retain
their original source and configuration identities. The 001 reuse register's
global `validation/gates.py` hash has unrelated Foster drift; inspection confirms
the Grudeva function is unchanged, and no historical 001 scores are recomputed.
