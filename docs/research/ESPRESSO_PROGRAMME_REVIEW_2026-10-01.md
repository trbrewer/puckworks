# Espresso programme review, source execution and mass-budget findings

## A. Current findings and scope

**Evidence cutoff: 2026-10-01.** This is the enduring synthesis of the September
review/correction cycle and its completed October source studies. It is a G0
**NO_GOVERNING_PHYSICS_CHANGE** documentation snapshot. Publication runs zero new
released-source Cameron or native OpenFOAM integrations, fits or experimental scores.
Existing README qualification invokes PW registered gates as software checks; those
checks are disclosed separately and do not rerun the archived source studies. Numerical qualification,
source-code reproduction, conditional prediction and physical validation are different
achievements; **physical validation remains NOT_ESTABLISHED**.

The completed work establishes four useful results:

- PW's off-knot Cameron inventory inconsistency, misleading P2 comparator and
  viscosity conversion were repaired and integrated in [PW #304][pw304]. EWP's
  live descriptions were reconciled in [EWP #201][ewp201], without changing its
  native equations, frozen R0 or production PW lock. Do not recommend these same
  repairs again.
- The local audit executed 30 native EWP cases and two compiled fixtures. It
  separated R0's 30-second endpoint from its 40 g beverage event, qualified
  numerical reductions and exposed a converged WP03 pressure-response mismatch.
  These are not 30 independent experiments.
- C01 reconstruction recovered 36 absolute analyte/fraction results from existing
  source bytes, not a new dataset acquisition. It supplies partial observed cup
  delivery; operational closure and a justified model-input bridge remain missing.
- An equation-preserving sparse variant executed the released Cameron model on
  Octave 8.4.0. Its N=40 diagnostic mass deficit is explained by the original axial
  stencil/endpoint inventory construction, with numerical integration qualifications.
  The particle averaging conserves its shell-volume integral. Neither successful
  execution nor an explained deficit repairs the original scheme or validates it.

The [evidence map](espresso_programme_review_20261001/EVIDENCE_MAP.csv) identifies
producer artifacts by logical directory, original relative name and SHA-256; omitted
files are explicitly marked. The [supporting README](espresso_programme_review_20261001/README.md)
explains the immediately runnable aggregate check and optional external-source replay.
Hashes establish identity, not correctness. [Source/version notes](espresso_programme_review_20261001/SOURCE_NOTES.md) distinguish the omitted primary documents. No owner-local paths are public links.

## B. Evidence lineage and integration

The historical review pins were PW `713c3c229568bb189c548f4c8a490b69a6319bef`
and EWP `f15a417cbf3c7528ac734537bb844cab6dc98287`. Reviewer 1 and Reviewer 2
are the labels in the supplied review documents, not claims of independent human
review. The revised Reviewer 2 document added F13/F14 and its section 10 change log.
That section was preserved in the subsequent local audit and integration closeout;
this new synthesis does not rewrite either original review.

| Evidence stage | Actual work and authority | Later status / boundary |
|---|---|---|
| Reviewer 2 revised review, 2026-09-30 | Partial-package Cameron calculations, figure reading, static source/predicate review; no complete registry/native/private-source replay | Retained as a historical position, with its exact original hash in the evidence map |
| Local computational audit | Complete pinned PW; 38 supported-environment before/after Cameron cases, registry, 30 native cases plus two C++ fixtures, 16 source-score reconstructions and 10 read-only delivery records | An additional 19 initial Cameron cases used unsupported dependency versions and were retained separately, not qualification; producer was Codex local audit, with isolated task-agent contributions, not independent human reviewers |
| Integration closeout | Historical-source identity separated from current reducer/non-mutation checks; adversarial tests, generated descriptions and PV-04 binding reconciled | PW `6ea31974524eca4bec6c37b0b5d13a01389a795b`, tree `b42429c369a6e497ba016bbb82a5d92fbe5c5cd0`; EWP `5ff6a2e8b3b9c130aa8c18eb5de6c7e180c628c4`, tree `8ced37ad5b294616b8935d92a57e3845321d5eed` |
| PW hosted CI closeout | Six failed jobs each exposed the same authorship guard choosing local main rather than candidate HEAD; a detached reproduction demonstrated the false local pass | Follow-on `2f3c784ea9c17567205a1ca01a4089c2745fa048`, tree `9ce7152880b27553fef8626da5f7a36e845757cd`; exact automation identities retained, unknown human identities still rejected |
| Owner integration, confirmed by GitHub receipts | [PW #304][pw304] squash merge `15479363ab3bcd879364628a1938879f2db8c05c`; [EWP #201][ewp201] squash merge `73ec476ffe6ac626705ca949e28b32935ddf2992` | Trees respectively `9ce7152880b27553fef8626da5f7a36e845757cd` and `8ced37ad5b294616b8935d92a57e3845321d5eed`. PW main still equalled this merge at publication intake; this is not a claim about future main |
| C01 preparation | `absolute-benchmark-20261001T004537Z`: 36 reconstructed observations and 18 preparation tests; no new source version | Real local heads were the pre-squash corrected commits with the same integrated trees; no claim that absent merge objects were checked out |
| Octave dense-option attempt | `execution-20261001T124658.426064Z`: fixture completed, N=40 source attempt timed out | Supersedes runtime-unavailable reports, but returned no extraction trajectory |
| Sparse source execution | `sparse-execution-20261001T133411Z`: one sparse DAE, two N=6 comparisons, two N=40 solves | Successful numerical-method variant; not MATLAB equivalence |
| Balance attribution | `balance-attribution-20261001T144045Z`: three N=40 integrations, operator tests and independent reductions | Explained diagnostic budget; no spatial refinement or repair |

**Historical test qualification.** Closeout PW normal selector
`not slow and not live and not gpu and not external_data and not protected_target_integrity`
reported 4,755 passed, 32 skipped, 766 deselected. Affected selection: 481 passed,
8 deselected; scientific selection: 5 passed, 5,548 deselected. Its original three
failures were resolved, not waived. The later CI closeout's hosted-selector local
run (`not slow and not live and not gpu and not external_data`) reported
5,374 passed, 65 skipped, 60 deselected, with 80% on the unchanged seven-module
coverage scope/70% floor. Its scientific selection reported 5 passed, 7 skipped,
5,487 deselected. These selections overlap and must not be added; neither is every
repository test. These are prior producer executions, not publication-stage reruns.

The exact EWP discovery footer is **Ran 1635 tests; OK (skipped=21)**. The accepted
count interpretation is 1,615 successful methods, 20 skipped methods and one skipped
class setup. The class setup skip increases skips without increasing testsRun;
subtracting 21 from 1635 and claiming 1,614 passes is wrong. Earlier private reports
retain that historical reporting error. Both registry closeouts reported 65 PASS,
zero FAIL/ERROR and one declared zero-gate exception. This is not 66 validations.

The three historical-evidence failures protected different contracts. SCI-MD-007
now checks the exact retained manifest/source at `ee12a88ebaa012cd284f66e199d3a1d3cc07953a`
and separately executes the current reducer twice with closure and non-mutation.
Smrke checks inherited source at `SOURCE.base_commit=e786b7846a19da8fae4f02b52b8a2dbbf8b8abee`
while its current scoring entry points still refuse changed frozen dependencies.
Missing historical objects fail explicitly; no current-file fallback is allowed.
Historical hashes, scientific receipts, output exclusivity and tamper tests survive.
See [the merged tests][identitytests] and [candidate authorship guard][authorship].
The historical PV-04 deployment binding was preserved separately from the corrected
local snapshot: merging a research correction does not establish deployment.

Independent-check scope must remain modest. The supplied earlier attachment-check
account verified ten accessible entries of a 65-entry audit manifest, reconstructed
the review diff and ran 48 isolated F13 cases (24 pass/24 fail before; 48 pass after),
not the full PW/native/private work. The owner's later balance-acceptance account
reports 58 payload hashes and aggregate arithmetic covering 27 endpoint rows,
54 timeline rows and 2,616 history records, not a fresh Octave solve or raw-history
replay. No separately identifiable acceptance report/checker was located in the
bounded local attachment search, so those external scopes are **owner-reported**,
not attributed to an invented reviewer or treated as inspected formal approval.
The offline checker included here is a new documentation-stage arithmetic check,
explicitly distinct from both the producer's reductions and that account.

## C. F1–F15 dispositions and consequences

“Confirmed” below always names the claim being confirmed. It does not turn a
Reviewer 2 refutation into agreement with Reviewer 1. Code citations use the merged
PW commit unless a historical pin is stated; the evidence map binds the full
original positions and later review.

| ID | Labelled earlier positions | Current evidenced disposition / consequence |
|---|---|---|
| F1 | R1: Cameron does not reproduce source extraction. R2: figure mismatch reproduced, with a normalization diagnosis | **REFINED.** PW publisher homogeneous-curve RMSE remains 7.102391 EY pp after F13 (7.078051 before). Released-source execution is now complete in sparse Octave, but differs in parameters, horizon and dispersion from PW/paper reconstruction; Fig. 5 reproduction remains unresolved (§F) |
| F2 | R1: increase inventory to resolve the mismatch. R2: investigate concentration/density/output normalization before retuning | **REFINED.** Physical EY remains cup-solute/actual dry dose. Default PW ceiling is 24.467473% of dry dose under its operative geometry; author normalization is conditional on dose-volume identity, not proof of intent (§F) |
| F3 | R1: axial convergence and a small cup/holdup bookkeeping gap. R2: convergence reproduced, holdup explanation refuted | **REFINED.** The PW grid trend survives, but the invariant 0.101550769 pp GS2.1 gap was F13, not uncounted holdup. The later author-scheme endpoint defect is a distinct result (§G), not residual F13 |
| F4 | R1: many gates are simple, estimated from behavior. R2: manual 15/10/10/18/12 classification | **REFINED.** Complete execution and delegated predicates give historical CF15/TR10/SS8/SD21/SC11; mixed-category choices below. Neither timings nor counts measure independent empirical validation |
| F5 | R1/R2: wrong Cameron DOI | **CONFIRMED; corrected and integrated.** DOI is [10.1016/j.matt.2019.12.019][cameronpaper], in merged manifest/card/live provenance |
| F6 | R1: governance/prompting is the principal scientific obstacle. R2: unsupported causal/process opinion | **NOT CHECKED as causality.** No controlled effort/delay comparison was made. Positive trigonelline and empirical results contradict a blanket “all negative” characterization; no process-causality finding is inferred |
| F7 | R1: R0 is too shallow; substitute approximately 19 mm. R2: distinguish density types and source-specific geometries | **REFINED.** R0's assumed 840 kg/m³ bulk basis is unqualified for its unspecified material. Authenticated depth sensitivities change storage/delivery, but no universal physical replacement is identified (§D) |
| F8 | R1: first-order EWP extraction is inferior and 23.9% implausible universally. R2: missing intragrain diffusion is real; those superiority/universal claims do not follow | **REFINED.** Native scalar/indexed release and closure are qualified. Suppression at 180 kg/m³ is not a hard solved-concentration cap; a deliberately coarse step reaches 441 kg/m³. No automatic Cameron port follows |
| F9 | R1: verification exists, no data comparison, excessive mesh cost. R2: data comparisons exist but mechanisms are unidentified | **REFINED.** Thirty native executions, WP02 scores and radial reductions are substantive numerical checks; WP03 converges with the wrong pressure ordering. Mesh size alone does not establish computational burden or physical resolution |
| F10 | R1: finding physics takes most of a reviewer's day. R2: burden/timing claims unmeasured | **REFINED.** Source/config/result navigation is concrete; elapsed reviewer effort was not measured. This record improves navigation without adopting the unmeasured claim |
| F11 | R1: the scoped delivery programme never tests a registered component. R2: refuted by SCI-VAL Wadsworth law plus adapter | **REFUTED as R1 stated; R2 refutation confirmed.** Unchanged registered law, explicit structural adapter and twelve observed permeabilities yield 7 definite failures/4 passes/1 unresolved. Strict SCI-MD-only naming would exclude SCI-VAL, but the review's collection included both |
| F12 | R1: remove hashes because corrections break tests. R2: separate historical identity from live behavior | **REFINED; concrete correction completed.** Frozen producers and receipts remain intact; current reducers/exclusivity and negative cases still execute. HEAD-versus-main authorship checking was subsequently corrected (§B) |
| F13 | R2 new finding: independently interpolated phase/radius/area violate one inventory | **CONFIRMED; repaired and merged.** GS2.1/2.3 gaps 0.101550769/0.152326153 EY pp close by deriving areas from interpolated primitives, not changing EY or C_S0. Separate from §G |
| F14 | R2 new finding: “flexible” predicate tests constant; early peak/mass clock cannot decide H1 | **CONFIRMED; comparator/interpretation corrected and merged.** Actual cubic remains better; surface exchange, intragrain access and mass-coordinate sufficiency remain different hypotheses |
| F15 | Local audit new finding: dry-solids fraction used where density API requires water fraction | **CONFIRMED; corrected and merged.** Ten former conversions were inflated by 25.7–30.8% relative to corrected values; ordering gate still passes. A passing order predicate concealed a units/basis error |

### Cameron repair and figure-reading versions

The repaired [microstructure helper][microstructure] interpolates phase fractions
and radius, then derives geometric area `b_i=3*phi_i/a_i`. Old source, release and
final inventory implied a different volume from the phase-based initial inventory:

```text
EY − EY_solid = 100 V c_s0 [sum_i(b_i a_i/3) − sum_i(phi_i)] / dose.
```

[Before/after records](espresso_programme_review_20261001/review/cameron_before_after.csv)
keep default `c_s0=118` and alternate `118/0.8272` separate. At default N=40/M24,
20 g in/40 g out/5 bar, GS2.1 EY changes 14.965492→14.929997%; GS2.3 changes
14.150135→14.097263%. Complete accounting closes within 3.2e−17 kg in the
producer's 19 corrected cases. This is an interpolation consistency correction,
not an inventory retune, physical validation or output offset. The default ceiling
follows [the operative volume/phase calculation][ceiling], not a universal 29.6%.
Source knots retain the existing primitives. SI Table S2 calls these inferred
geometric areas; source rounding and the fines-table/stated-radius inconsistency
remain source qualifications, not separately measured effective BET evidence.

Reviewer 2 used accepted-manuscript readings; the local audit independently read
final-publisher Fig. 5 (printed p.642/PDF p.13), with visible bars meaning one SD.
Its maximum disagreement with R2 was 0.010560 pp for the homogeneous curve and
0.011602 pp for experimental means. The ±0.03 pp reading allowance is distinct
from measurement spread; occluded bars remain unresolved. The default post-repair
homogeneous-curve RMSE 7.102391 pp and experimental-mean RMSE 6.480780 pp are
**different residuals**; alternate inventory gives 3.839735/3.321602 pp. Primary
PDF identities and the omitted pixel evidence are recorded in the evidence map
and source note. No new digitisation or figure score was performed here.

### Comparator and census boundaries

At the historical 9-bar support, P2 RMSEs are best constant 0.573, empirical
Phi(t) 0.116, flexible cubic 0.096, Cameron-coupled 0.392 and swelling 1.082 g/s.
The [merged predicates][comparators] correctly name the constant and cubic tests;
the cubic comparison stays false. The Cameron branch maps **cup-delivered** solute,
not total solid loss, into pore opening: retained solute was 0.127831537 g at 15 s,
4.6211% of solid loss in the audit recipe. This is not a matched kinetic-mechanism
comparison. A finite-rate depleting reservoir can have an early maximum, so the
0.968 early/peak statistic cannot identify instantaneous surface exchange or rapid
intragrain inventory access. Prior target information remains upstream in Phi(t).

The [historical census](espresso_programme_review_20261001/review/gate_census.csv)
contains 78 defined functions, 52 QUICK functions, 65 registered comparisons and
one zero-gate exception; 13 functions, including the P2 predicate, are QUICK-only.
CF=closed-form/recompute; TR=transcription; SS=solver/model versus solver/model;
SD=solver/model versus measurement; SC=self-consistency. R2's 15/10/10/18/12 becomes
**15/10/8/21/11** because binding measured residuals move
`gate_kappa_t_degeneracy` SS→SD and `gate_kappa_t_composition_diagnostic` SC→SD,
and measured-viscosity ordering moves `gate_g10_foursource_spread` SS→SD.
Their mixed SS+SD/SC+SD/SS+SD content remains visible. Candidate-versus-measurement
is still post-fit when its parameters came from those data. This manual taxonomy
belongs to the audited registrations at the historical pin, not automatically to
any later registry. The [F15 table](espresso_programme_review_20261001/review/f15_conversion.csv)
retains both conversions; gate success did not settle conversion correctness.

## D. EWP native, geometry and conditional-prediction context

The native producer used Foundation OpenFOAM 12 (installation commit
`0f458291f1cd6b7afff839eab96d838d6a9e95c2`), GCC 13.3 / Open MPI 4.1.6;
binary SHA-256 `3de93829850829db53927e5a079a855d1c09922f238a3a330f5d01f32f9eb1fb`.
Source was EWP `f15a417cbf3c7528ac734537bb844cab6dc98287`; its native
wrappers did not import an accidentally partial PW package. Constitutive bridges
separately locked PW `fc61c4670ec7bf801e40bb391aab16048b8da26b`, not audit PW.
These identities are reused, not a new native execution in this publication.

### R0 endpoint and storage

The actual canonical mesh was 131,072 cells (256 axial ×512 radial), dt0.02 s;
H=9.011660896 mm, diameter58 mm, phi=.4, k=1.77e−15 m², 3 s ramp to9 bar,
rho965 kg/m³, mu.000315 Pa·s, dose20 g, soluble fraction.28. See
[config at the native pin][r0config] and the included
[native metrics](espresso_programme_review_20261001/native/30s-and-events.csv).

| Observable | 30-second endpoint | Distinct 40 g beverage event |
|---|---:|---:|
| Time, s | 30 | 29.374480171 |
| Beverage, g | 40.957867483 | 40 |
| EY, % of 20 g dose | 23.938453103 | 23.624029229 |
| TDS, % of beverage | 11.689306389 | 11.812014614 |

Beverage means water plus solute. At30 s cup water=36.170176862 g and
solute=4.787690621 g; retained water/solute=9.190476190/0.192063112 g.
Saturated flow=1.482675972 mL/s, pore capacity=9.523809524 mL. Sharp-front crossing
is4.711696185 s, while the first positive discrete outlet trace is4.74 s because
transport requires saturation at step start ([source][ewpsaturation]). Integrated
water/solute residual maxima were6.80e−16/2.60e−13 kg, not assay uncertainties.
The40 g interpolation bracket is29.36–29.38 s; a4.73e−7 g solute curvature estimate
is diagnostic, not a certified bound. Halving dt changes30 s EY by−0.002688866 pp
and event EY by−0.002600388 pp. Cup-EY refinement differences fall below the existing
0.5% parity comparison, while retained-solute changes2.175%/1.105% on successive
spatial refinements do not. A blanket convergence claim would be misleading.

### Geometry and mechanisms

The audit visually authenticated Perticarini Table 4.1 (printed p.87/PDF p.99;
methods printed p.86):20±.1 g,58.5 mm basket,20 kgf tamp, source depths12.6–14.2 mm.
Mapping equal volume to58 mm gives12.818–14.446 mm. With R0 phi retained, original-k
sensitivities give20.999–25.675 g beverage at30 s; algebraically preserved k/H gives
37.881–38.805 g. All report **NOT_REACHED** for40 g within30 s. Pore capacity grows
to13.547–15.267 mL, so preserving saturated conductance does not preserve wetting
or storage. These are depth sensitivities, not a jointly measured replacement R0.

Roman-Corrochano 2015 Table2 (printed p.113) and the2017 thesis repeat one campaign.
Dry bulk, particle-envelope and skeletal density; interparticle hydraulic porosity,
intraparticle porosity and accessible water storage; dry, consolidated and extracted
states cannot be interchanged. H=dose/(area*rho_bulk) requires the corresponding
bulk definition. Neither Bruno nor Hargarten supplies the missing R0 density.
A single EWP porosity cannot express independently measured hydraulic/storage splits.
No universal19 mm replacement or measured actual R0 material has been established.
Existing [EWP geometry reconciliation][geometry] was found, correcting a scoped
absence claim; the local audit enumerated162 EWP refs, not every future/remote branch.

The [scalar/indexed extraction source][release] uses kg/(bulk m³·s), remaining
inventory per bulk volume, start-of-step source evaluation, saturation suppression
and an inventory/dt cap. It has no intragrain radial state. Batch and flow-through
scalar/indexed cases coincide; a dt5 s diagnostic reaches441 kg/m³ despite180 kg/m³
suppression, conserving5.6 g. Only negative concentrations are clipped in that path;
release suppression is not a global hard upper cap. Gross clipping accounting is
not universally exposed, so a small net residual is not proof of zero corrections.

WP02-004 equal-area-fraction reduction (.25/.75) reproduces native cup solute within
1.59e−11 EY pp. With a4:1 permeability ratio and matched total conductance, flow
fractions are4/7 and3/7, radial velocity≤2.84e−16 m/s. Parallel pressure boundaries
and axially uniform columns explain that behavior; the small0.007248533 EY-pp
native/reduced difference includes transverse solute diffusion, not demonstrated
radial water exchange. Pocket Science assays require a retained-liquid/recovery
operator and do not directly measure solid depletion.

WP03's corrected pressure iteration converged (maximum flow closure error8.36e−13)
but predicted5/9/11-bar endpoint flows0.585354185/0.680973127/0.685942927 g/s,
against decreasing source endpoints1.598666/.739666/.663059 g/s. The source law
`Q=A*k0*Pc/(mu*H) * integral_0^(P/Pc) (1−x)^3/(1−Phi*x) dx`
is increasing inside its declared domain. This is a **converged wrong response**,
not merely the earlier stopping defect. Stress maps constitutively to porosity
and permeability; no displacement equation or mesh motion is solved, and mechanical
porosity is not transport storage. See [complete corrected result][wp03].

### WP02 normalization and target exposure

The native audit reproduced five9-bar and four8-bar source comparisons. Median
absolute hydraulic-flow RMSE=**0.227726511/0.129352713 g/s**; corresponding median
shape RMSE=.083966585/.072456058 and correlations=.989034176/.989158206.
The [scorer][wp02scorer] divides **each prediction and each shot by its own late
mean**, indices900–999; scoring uses indices100–899 of1000 samples. Native time is
source time+3 s, not the source's8 s drip offset. The native observable is965 times
volumetric water flow, not beverage mass derivative. Smoothing, interpolation,
pressure-node correction and adjacent samples induce dependence.

PW's locked source and [upstream provenance][waszprov] retain the measured basket
pressure correction. Source `fit_model_solids.py:24,43,50,59–85` in Zenodo release
18046315/tagfbc33d3 constructs the dissolution sigmoid from the scored9-bar aggregate;
8 and9 bar also enter the static hydraulic fit. No new fitting is not no target
information. Independent raw reconstruction changed the two median absolute RMSEs
to.227726484255/.129352739694 g/s (export-rounding differences), not a new cohort.
See the identity of omitted `private-replay/wp02/REPORT.md` in the evidence map
and the [public source release](https://zenodo.org/records/18046315).

### Twenty-six deliveries: preserve positive and negative results

The included [directory census](espresso_programme_review_20261001/review/directory_census.csv)
points to each existing public result at PW historical pin, with its hash:16
SOURCE_SCORE_RECOMPUTED and10 READ. No historical refitting or inference using current
main substituted for a frozen producer. The independent producer reduction found144
aggregate comparisons agreeing within7.34e−10 in their respective units. Raw
observations/predictions and private score tables remain omitted here.

For mass-weighted within-shot concentration errors,
`R=sqrt(sum(m*e²)/sum(m))`, `B=sum(m*e)/sum(m)`, `A=abs(B)` before averaging.
Shots are equally weighted within conditions, conditions within panels. Incomplete
support preserves intended denominators and null full metrics; nonnegative lower
bounds are not assay uncertainty. CLOCK instead uses vial-solute RMSE in grams.

- [GRUDEVA-CLOCK][clockresult]:13 shots, mean TIME→MASS vial RMSE
  .043075436→.016538323 g (61.6061%;11/13 wins). **All four arms** receive measured
  held-shot beverage masses. The gain concerns a coordinate/shape under supplied
  delivery, not predicted hydraulics or exclusive access to mass. Structural zero
  and missing chemistry records remain distinct.
- [MASS-006][mass6]:C0/C1/C2 balanced R=.652055303/.597587225/.480034143 TDS pp.
  The already-completed target-exposed first-assay projection fixed q1 to its FIT
  mean, retained q2/masses and coefficients, and yielded R=.495218012 pp. It retains
  **91.1733%** of full C2's gain over C0. This was not a new fit or evidence that
  both early assays are necessary; the exact omitted prediction binding is identified
  in the producer report, not silently replaced by a q2-only learned model.
- [MASS-007][mass7]/[008][mass8]:11 eligible of13 shots,98 early assays→22 pools,
  **55 unique suffix observations**. The110 ordered adaptation pairs/550 slots per
  arm reuse these same shots. Zero-shot C2 adequacy fails; one-shot adaptation is
  adequate for9/11 calibration choices, not universally and not110 independent tests.
- [Caffeine][caffeine]:D0→S2 R=.192258152→.125168094 mg/g, a.067090058 mg/g
  improvement below its declared.10 mg/g material threshold; simpler prediction
  was adequate. [Trigonelline][trigonelline]:K0→D0 R=.729502678→.134549535 mg/g,
  improvement.594953144 mg/g/81.556%; positive mass-shape gain survives. Their
  different adequacy/gain budgets must not be merged into one negative conclusion.
- [5-CQA][cqa]:D0 R=.363520937 mg/g, signed bias−.340293651 mg/g; later TDS/share
  and early-assay families also fail their declared budgets. L12 R=.297495166,
  signed bias−.254372362 mg/g. Original FIT/PRED calibration equations and validity
  exclusions differ. Reconstructing those equations preserves the failure; an
  assumed batch shift or unmeasured assay error is not an explanation established
  by these records.
- [SCI-VAL-TAMPED-K][tamped]:the unchanged Wadsworth function plus declared
  consolidated-input adapter gives7 failures/4 passes/1 unresolved across12 observed
  permeabilities. Geometric mean prediction/observation falls39.9511→3.60067 but
  still fails the screen. This tests the law **with its proxy/input adapter**, not
  isolated native-law adequacy or full espresso hydraulics.

None of these results discriminates fast local exchange from rapid intragrain
access. The [existing H1 note identity](espresso_programme_review_20261001/EVIDENCE_MAP.csv)
records the conservative early-maximum counterexample and missing matched observation
map. No new H1 score or successor model family is selected.

## E. C01: absolute observations, closure and model readiness

The completed C01 task selected Colombia Suprema Huila washed Arabica, March2022
prediction shots in native directories01–03, nominal20 g, E65S GL1.7, programmed
86°C/2 mL/s. Those programme settings are not all same-shot achieved inputs.
[Pannusch 2024][pannuschpaper] carries forward [Schmieder 2023][schmiederpaper] methods;
[Mendeley v1][mendeley] explicitly links that lineage, not two independent campaigns.
The fifteen inspected source members matched the retained archive
SHA-256 `bb3542746fbce99aebbcf44c05eec456abebe71f9574d181f1e41f849b15ba49`.
No new raw source version was acquired.

**36 results = six assayed fractions ×three shots ×two analytes.** Support is
F1/F2/F3/F5/F7/F10; onlyF1–F3 are consecutive. Missing chemistry (including other
fraction positions and the unresolved mass slot11) stays missing. The private
observation bundle retains original sample IDs and unmatched full-sample records;
no partial sum is scaled into whole-cup mass.18 preparation tests checked arithmetic,
juxtaposed IDs, missing-term behavior and source integrity, not model validation.

The HPLC workbook
`Experimental_data_validation/HPLC Alcaloids/HPLC_Alcaloids_Validation_2022_03.xlsx`
(SHA-256 `42257832ba03c19bc067121af6eaacdcf378d64060cce1a302c8f555ddeafc06`)
uses caffeine diluted mg/kg=`(area+27.317)/25.628` and trigonelline=`(area−1.9691)/9.4635`.
At `1-3!D15:F34,T10:T27,V10:V27`, dilution is gravimetric:
`d=(water_g+coffee_g)/coffee_g`; undiluted mg/g=diluted mg/kg×d/1000;
**fraction analyte mg=fraction beverage g×analyte mg/g**. The mass source is
`DesignOfExperiments_Validation_03_22.xlsx`, SHA-256
`b7fc864e693ddb40317a4c9493a2fb0c0892b1f1c68f5ce581d48008e21cab57`,
`SampleWeights!A3:L8` and `HPLCWeightsAlcaloids`. This route needs no invented
density. Workbook/MAT agreement is arithmetic consistency, not assay accuracy.

Three caffeine flags are **P1.7/P2.7/P3.7 (all F7)**, above the highest nonzero
calibration standard; they are retained with flags. Source trigonelline hydrochloride,
free-base/purity conventions and analytical uncertainty were not resolved. No
free-trigonelline conversion or fabricated error bars were applied. Technical
injections/shared calibration are not independent shots.

The full-sample loader uses primed IDs `1´/2´/3´` at DoE `A51:L56`, whereas
fractions are unprimed. Source `getExperimentalData_validation.m:37,168,195`
selects those primed mass/assay rows. Full remainders are30 g below their associated
ten-fraction totals at workbook precision. That is unresolved sample/aliquot
bookkeeping, **not demonstrated physical loss or paired independent cup closure**.

The source saved897 scale rows (747 timestamped) and470 keyed machine samples.
The acquisition code leaves the first50 rows per shot without a stored clock;
valid clocks are monotonic but not synchronized to machine, wheel or solver zero.
Machine pressure is between boiler and portafilter, temperature above the puck,
and the flow channel is a machine estimate. `GetMassScale.m:55,60,61,71` fits and
differentiates beverage mass; the plotted density conversion does not redefine the
stored derivative as measured inlet mL/s. PRED inferred fraction times invert that
fit; FIT cumulative mass/scalar-flow times are a different stage. Neither is an
observed wheel-transition clock. These distinctions reuse the completed
[EWP flow-history result][flowhistory] and [fraction-window result][fractionwindow].

Three capabilities remain separate:

| Capability | Current evidence |
|---|---|
| Absolute observed cup-fraction delivery | Reconstructable on the36 observed supports; conditionalF1–F3 subset is useful |
| Operational analyte mass closure | Not supplied: `I_ref_initial−M_cup−M_retained−I_ref_spent−M_other_declared` has incomplete/missing terms; residual stays null, not forced zero |
| Frozen model input/observation bridge | Not qualified: same-material inventory, partition/initial-liquid state, flow/clock/collection mapping and actual storage remain unresolved |

`T_total`, `I_ref`, `Q_production_solid_initial` and model `c_s0` retain the
[SCI-ED-003 meanings][minimum]. Experiment46's reference extraction is not evidence
of March production M0, complete exhaustion, or a shared roast. The candidate
Pannusch species kernel requires concentration/partition, geometry, storage,
boundary flow/temperature and collection windows. Its
[flow argument and conversion][pannuschsolver] remain an explicit input-basis
qualification; a recipe label alone cannot settle them. Cameron's single solute
pool is not a caffeine/trigonelline mapping. See the already-completed
[input-mapping assessment][mapping].

All targets were previously examined; newly recovered metadata do not create a
blind holdout. The bounded next decision remains whether to seek existing-record
clarification about clocks, primed samples, same-material recovery and analytical
conventions. Author questions are open and unsent in the private work. No contact,
new fit, SCI-ED-003 Stage F/D or laboratory programme is authorized by this record.

## F. Released Cameron source execution

Source: [jamiemfoster/Espresso][authorrepo] at
`79ebefb72446eb706084e2392cab64bf0fad93a2`, tree
`cb6f42ce893da256d1d6974e724166044e77af94`. The original six MATLAB files
remained byte-identical. Backend was GNU Octave 8.4.0, executable hash in
[SOURCE_IDENTITIES.json](espresso_programme_review_20261001/balance/SOURCE_IDENTITIES.json).
No MATLAB backend execution was completed.

### Numerical configuration and qualification

The original dense-option N=40 attempt timed out at**1,800.165124 s**, status124,
without returned t/u. Its4.889334 g initial inventory was parameter accounting,
not an extraction result. The sparse study changed only numerical configuration:
exact `sparse(M)`, analytic sparse **dRHS/du**, constant-mass declaration
`MStateDependence='none'`, statistics and headless/export instrumentation. It
continued to call original RHS; no diagonal lumping, regularization, diffusion
removal or initial-state/parameter change. N=40 has**3,240 states/9,478 mass nonzeros**.
This archived study was a NUMERICAL_METHOD_CHANGE; documenting it here is not a
new production solver change.

Installed Octave `ode15s.m:231–261,355–383` dispatched the sparse Mass/Jacobian
and assembled the residual derivative. It did not consume an inverted-mass Jacobian.
The [Jacobian derivation](espresso_programme_review_20261001/JACOBIAN_DERIVATION.md)
and research-only adapter retain both algebraic rows and both particle populations.
For G=K(1−l)s(s−beta*l), derivatives are
`dG/dl=−K*s*(s+beta−2*beta*l)` and
`dG/ds=K*(1−l)*(2*s−beta*l)`.

| Prior executed qualification | Criterion and result |
|---|---|
| Singular DAE M=diag(1,0), RHS=[−x;x+z−1], [1;0], [0,5] | Sparse path,501 outputs,RelTol1e−8/AbsTol1e−10: state error1.854934983e−9≤1e−6; constraint6.661338148e−16≤1e−8;37 installed wrapper calls |
| Complete RHS directional differences |48 checks:4 states×4 directions×3 steps. For each state/direction better of h1e−5/1e−7 must be≤1e−7 scaled error; worst selected8.68103e−9. h1e−3 max3.82528e−5 and h1e−7 max1.01939e−6 do **not** individually pass that limit |
| Surface complex perturbation |8.88178e−16 absolute discrepancy≤1e−12 |
| N=6 dense/sparse,101 common outputs on[0,.1],rtol1e−7/atol1e−9 |Max state difference8.54872e−15≤2e−6; tolerance-scaled1.68327e−7≤20; outlet integral difference2.77590e−17≤1e−7 |
| Mass entries |Entrywise `full(sparse(M_original))==M_original` at N=6/N=40, including M2*M1 and zero algebraic rows |

See [fixture](espresso_programme_review_20261001/sparse/sparse_fixture.json),
[directional differences](espresso_programme_review_20261001/sparse/jacobian_differences.csv)
and [small comparison](espresso_programme_review_20261001/sparse/small_comparison.json).
These criteria were declared before numerical inspection. The N=6 dense/sparse
runs took3.92145/.46502 s and2,870/218 RHS calls with178 accepted/8 rejected steps
each. The extra2,652=34×78 calls are consistent with dense finite differences.
That explains measured small-grid cost; no exact speedup against the incomplete
N=40 attempt is established.

N=40 reference:rtol1e−3/atol1e−6,10,000 requested points[0,10],127 accepted steps,
16.592155 s including export. Tighter:rtol1e−7/atol1e−9,20,001 outputs,724 steps,
61.479600 s. Output callbacks/snapshots are solver-supplied, potentially interpolated
states, not RHS trial times or complete multistep restarts. The following uses each
run's own trapezoid reduction; full precision is in
[endpoints.csv](espresso_programme_review_20261001/sparse/endpoints.csv).

| Run | t_hat | Cup solute g | Solid solute g | Liquid solute g | Boundary-corrected E mg | Author EY % |
|---|---:|---:|---:|---:|---:|---:|
| reference_sparse |1|2.623963521|2.046156456|.217105022|+2.109106|19.19005173|
| reference_sparse |10|4.797007806|.085480423|.001508974|+5.336902|35.08235812|
| tight_sparse |1|2.623875904|2.046150059|.217094916|+2.213228|19.18941095|
| tight_sparse |10|4.796944985|.085507198|.001509996|+5.371927|35.08189868|

### Scales and conditional normalization

The initial inventory is4.889334105803381 g with solute-free liquid. Source
[parameters][parameters] give t_seconds=33.9*t_hat and nominal **reference-density
liquid throughput**40/400 g at t_hat=1/10. The full horizon is339 s, not a40 g
beverage shot. The source does not independently resolve water versus beverage
mass or specify an observed actual dry dose.

Cup solute is `V*c_sat*q*integral(c_exit dt_hat)`; the author's displayed
[normalization][authorey] is `100*alpha*q*beta*integral(c_exit dt_hat)/phi_s`.
It divides cup mass by `V*rho_grounds*phi_s=13.6735614823 g`. Other conditional
identities give19.9829957613 g for `V*rho_grounds/phi_s` and16.5299340937 g for
`V*rho_grounds`. No one of these is an observed dose. Relative to printed
main-text Eq. 25 (printed p.638/PDF p.9), the factor is phi_s^−2=1.46143313;
relative to an intrinsic-particle-density identity it is consistent. SI Table S1
(SI p.3/PDF p.23) instead calls330 kg/m³ **bulk density**. The internal convention
conflict survives; close curve agreement does not settle author intent.

The released a1=80µm,a2=300µm,k=1e−9,Deff_star=1e−6 m²/s differ from the paper/PW
reconstruction. PW omits this nonzero axial dispersion. No genuinely matched
PW/source comparison was completed, and removing dispersion to create one was not
permitted. Source execution refines F1/F2/F3 but is neither F13 repair nor completed
Fig. 5 reproduction. Physical EY remains100*cup_solute/actual_dry_dose when that dose
is known; production EY was not rescaled.

## G. Explained N=40 mass budget

### Verified identity and functional

The [full discrete derivation](espresso_programme_review_20261001/DISCRETE_BALANCE.md)
uses original [RHS stencils][rhs], [mass blocks][massmatrix] and
[checkmass functional][checkmass], one-based spatial indices. Set
h=1/(N−1),epsilon=1−phi_s,V=pi*R0²*L; liquid c_j is scaled by c_sat, grain s by c_s0,
beta=c_sat/c_s0, Q_i=1/(a_i*b0), and b_i is area/b0. Axial trapezoid weights are
w=(h/2,h,…,h,h/2); radial shell volumes are v. Then

```text
M_hat = epsilon sum_j w_j c_j
        + sum_i b_i/(4*pi*beta*Q_i) sum_j w_j vᵀ s_ij
C_hat' = q*c_N; S_j = b1*G1_j + b2*G2_j
(M_hat+C_hat)' = A_adv + A_disp + A_end
A_adv  = q/2 * (c_N-c_(N−1)+c_1+c_2)
A_disp = D/h * (c_N-c_(N−1)-c_2+c_1)
A_end  = h/2 * [epsilon*(c_1'+c_N')-S_1-S_N]
```

The particle block B=A*diag(v) has **1ᵀA=1ᵀ**, hence **1ᵀB=vᵀ**. Internal grain
fluxes telescope; off-diagonal averaging does not lose its shell-volume mass.
Interior liquid release cancels grain loss, but endpoint grains still release
while liquid endpoint rows are algebraic. Trapezoid inventory nevertheless assigns
those liquid endpoints storage weights h/2. Summing the original stencils yields
the nonzero expression above. The reviewer identity is **CONFIRMED for this
functional**, while the proposed blanket particle-averaging explanation is rejected.

Seventeen original-operator state checks (initial,three synthetic,thirteen saved)
give max rate discrepancy1.77688e−14 versus predeclared
5e−11*(1+sum absolute rates); particle identities err≤6e−15/1.61e−15. Boundary
constraints were differentiated analytically using interior RHS derivatives,
not a singular mass inverse or differenced output samples. Saved states were not
projected. Sign, endpoint-weight and unit mutations fail; author inventory versus
reducer agrees within1.365e−12 mg on seven endpoint/bracket states. These are prior
producer checks in [operator results](espresso_programme_review_20261001/balance/operator_results.json)
and [functional equivalence](espresso_programme_review_20261001/balance/functional_equivalence.csv).

### Signed integrated budget

Let F=V*c_sat*10^6 mg. Boundary fluxes are signed under this convention:

```text
F_in_total = F integral[q*c1 − D/h*(−1.5*c1+2*c2−.5*c3)] dt_hat
F_out_disp = F integral[−D/h*(.5*c_(N−2)−2*c_(N−1)+1.5*cN)] dt_hat
E = I0 − M_solid − M_liquid − C_adv − F_out_disp + F_in_total
E_pred = E(0) − F {integral[A_adv+A_disp−h/2*(S1+SN)] dt_hat
                  + epsilon*h/2*Delta(c1+cN)} − F_out_disp + F_in_total
R = E_observed − E_pred
```

Storage uses exact endpoint change; predicted E is not defined from observed E or
its numerical derivative. Core author E omits explicit boundary corrections; the
maximum difference at original endpoints is6.1251e−7 mg. Large inlet advection
410.491763/582.786772 mg in the tighter history nearly cancels inlet dispersion;
net fluxes were calculated, not assumed zero or added twice.

The following are same-run, same-quadrature reductions. Original reference time1
uses its original linear bracket interpolation; tighter output contains1 exactly.
Two diagnostic replays supplied previously unretained boundary-neighbor/surface
states and reproduced **all original moment-history bytes and endpoint states**.
Thus “reference_replay”/“tight_replay” bind the original outputs, not alleged full
original trajectories at every output. Complete moment histories had twelve
columns; diagnostic snapshots alone could not supply the missing terms.

| History / quadrature | t_hat | Observed E mg | Predicted E mg | R mg |
|---|---:|---:|---:|---:|
| reference_replay / trapezoid |1|2.109106053|2.323189546|−.214083492|
| reference_replay / trapezoid |10|5.336902315|5.492895394|−.155993079|
| tight_replay / trapezoid |1|2.213228124|2.240135395|−.026907270|
| tight_replay / trapezoid |10|5.371927113|5.399015865|−.027088751|
| tight_early / Simpson |1|2.207505437|2.207446177|+.000059261|
| tight_early / Simpson |10|5.366247746|5.366325446|−.000077701|

Full unrounded values, initial E=0, all27 endpoint/quadrature rows and separate
fine/coarse inventories are in
[balance_components.csv](espresso_programme_review_20261001/balance/balance_components.csv).
Do not subtract rounded displays to invent another discrepancy.

| Signed contribution to tight_early E, mg (Simpson) | t_hat=1 | t_hat=10 |
|---|---:|---:|
| −F integral A_adv |−455.657602645|−649.879674078|
| −F integral A_disp |+388.601295802|+532.077136009|
| Endpoint release |+74.625972620|+123.206916983|
| Endpoint storage |−5.362219600|−.038053468|
| −F_out_disp+F_in_total |−3.64e−13|−2.30e−12|
| Sum of absolute component magnitudes |924.247090667|1305.201780538|

Large signed terms cancel. Positive-only percentages would hide the accounting.
The initial deficit rate95.345648956129 mg per scaled time, **2.812556016405 mg/s**,
is instantaneous, not a constant loss rate. Predicted deficit grows to.406094 mg
at.339 s,.743411 mg at3.39 s,2.207446 mg at33.9 s and5.366325 mg at339 s. It is
not exclusively an initial-transient effect. The54-row
[timeline](espresso_programme_review_20261001/balance/timeline.csv) uses Simpson;
the2,616-row [history](espresso_programme_review_20261001/balance/balance_history.csv)
is sampled cumulative trapezoid output. They are deliberately labelled differently.

### Output integration, numerical remainder and limits

Original tighter Simpson R≈−.007735/−.007884 mg was small, but predicted E moved
.024703 mg from trapezoid: R alone did not qualify attribution. The third run retained
all20,001 tighter outputs and added early points (logarithmic1e−9..5e−6 plus5e−6
spacing to.02), giving24,361 outputs including0,1,10. Physical parameters, N=40 and
rtol1e−7/atol1e−9 were unchanged; **accepted steps changed724→565**. This is not a
pure quadrature experiment.

Same-new-trajectory sampling followed by between-trajectory comparison decomposes
the old tighter trapezoid R at1/10 into resolved R(+.000059/−.000078 mg), output
effect(−.026992/−.027025 mg) and same-grid trajectory difference(+.000025/+.000014 mg).
For the old reference, output effects are−.084569/−.084639 mg and between-run
effects−.129574/−.071276 mg, with explicit resampling; linear versus PCHIP changes
this by≤.000022 mg. [The decomposition table](espresso_programme_review_20261001/balance/numerical_comparisons.csv)
keeps all terms. Between-run differences include numerical trajectory, output
strategy and resampling; they are not labelled pure time-integration errors.
The original loose run is not retrospectively certified to.01 mg.

The early-resolved attribution meets the fixed**.01 mg reporting target**:
consequential budget sensitivities≈.004110/.003977 mg and R≈+.000059/−.000078 mg.
These are observed diagnostics, not rigorous error bounds or assay uncertainty.
Whole-bed phase-release quadrature remains more sensitive: deliberate decimation
can leave≈.0195 mg residuals, whereas full-grid Simpson phase residuals are below
.000402 mg. Those integrals do not replace endpoint solid inventories or the
endpoint-release contribution.

The three attribution integrations took16.796780/61.285508/53.820682 s, all N=40,
serial,one thread,exit0,within1800 s. No new DAE or N=6 integration was counted.
All three authorized slots were needed for missing-field recovery and temporal
qualification: **no spatial refinement, observed order or continuum extrapolation**.
The source N would refine axial and radial coordinates together. The early-resolved
scaled-state maximum1.0056998365 remains; aggregate extrema do not identify its
state/location or establish positivity/maximum-principle behavior.
[Run statistics](espresso_programme_review_20261001/balance/run_statistics.csv)
retain constraint residuals and overshoot without projection.

An explained diagnostic imbalance is not an exactly conservative original scheme,
experimental solute loss, measured physical EY, author intent, MATLAB equivalence,
Fig. 5 reproduction or an H1 result. No repair is selected here.

## H. Reproduction levels and remaining questions

1. **Immediately checkable offline:** included CSV arithmetic, run/units/quadrature
   joins, decomposition sums and snapshot hashes. Run the supporting checker with
   Python's standard library; its sign/value mutations must fail. This recomputes
   supplied aggregates, not raw trajectories or physics.
2. **Optional external-source re-execution:** pinned MIT author source, installed
   supported Octave, NumPy/SciPy for reduction, fresh output directories and the
   archived sparse adapter. Explicit input hash checks and recipes are included;
   no source solve was rerun to publish this record. A new backend requires its own
   qualification and cannot inherit Octave 8.4 numerical equivalence by assumption.
3. **Omitted private evidence:** full/moment histories, snapshots, native fields and
   logs, original C01 workbooks/MAT/machine rows, raw assays/predictions, PDFs/pixel
   crops, requests and correspondence. Logical identities locate producer material,
   but a hash is not a download link or access grant. This is an **aggregate-only
   evidence snapshot, not a complete trajectory replay package**.

Rights are source-specific: author-code derivatives retain Jamie Foster's MIT notice;
first-party research utilities are separate from Pannusch/Schmieder CC-BY-NC source
records and permissioned private evidence. C01 is preserved here through factual
prose/citations and source identities, without importing its raw or derived row tables
under PW's software license. No author email drafts or contact details are included.

The unresolved scientific questions are narrow: actual Fig. 5 generator/parameters
and dose convention; actual R0 material geometry/storage; C01 synchronized collection,
flow/sample/recovery joins and analytical conventions; matched H1 discrimination;
and Cameron spatial sensitivity. Runtime installation, F13/F14/F15 repairs,
C01 arithmetic reconstruction and N=40 budget attribution are **completed work**,
not reasons to repeat their campaigns. No automatic successor, fit, source-scheme
repair, Stage F/D or author contact is selected by this publication.

[pw304]: https://github.com/trbrewer/puckworks/pull/304
[ewp201]: https://github.com/trbrewer/espresso-whole-pull/pull/201
[cameronpaper]: https://doi.org/10.1016/j.matt.2019.12.019
[pannuschpaper]: https://doi.org/10.1016/j.jfoodeng.2023.111887
[schmiederpaper]: https://doi.org/10.3390/foods12152871
[mendeley]: https://data.mendeley.com/datasets/y2tz67f6ry/1
[identitytests]: https://github.com/trbrewer/puckworks/blob/15479363ab3bcd879364628a1938879f2db8c05c/tests/test_smrke2024_transfer.py#L164
[authorship]: https://github.com/trbrewer/puckworks/blob/15479363ab3bcd879364628a1938879f2db8c05c/tests/test_authorship_identity.py
[microstructure]: https://github.com/trbrewer/puckworks/blob/15479363ab3bcd879364628a1938879f2db8c05c/puckworks/models/cameron2020/extraction_bdf.py#L100
[ceiling]: https://github.com/trbrewer/puckworks/blob/15479363ab3bcd879364628a1938879f2db8c05c/puckworks/models/cameron2020/extraction_bdf.py#L138
[comparators]: https://github.com/trbrewer/puckworks/blob/15479363ab3bcd879364628a1938879f2db8c05c/puckworks/harness.py#L193
[r0config]: https://github.com/trbrewer/espresso-whole-pull/blob/f15a417cbf3c7528ac734537bb844cab6dc98287/config/reference_R0.json#L15
[ewpsaturation]: https://github.com/trbrewer/espresso-whole-pull/blob/f15a417cbf3c7528ac734537bb844cab6dc98287/solver/espressoWholePullFoam/espressoWholePullFoam.C#L2430
[geometry]: https://github.com/trbrewer/espresso-whole-pull/tree/f15a417cbf3c7528ac734537bb844cab6dc98287/docs/analysis/ewp_porosity_permeability_prior_001
[release]: https://github.com/trbrewer/espresso-whole-pull/blob/f15a417cbf3c7528ac734537bb844cab6dc98287/solver/espressoWholePullFoam/espressoWholePullFoam.C#L3213
[wp03]: https://github.com/trbrewer/espresso-whole-pull/blob/f15a417cbf3c7528ac734537bb844cab6dc98287/validation/wp03/WP03_002_CORRECTED_COMPARISON.json
[wp02scorer]: https://github.com/trbrewer/espresso-whole-pull/blob/f15a417cbf3c7528ac734537bb844cab6dc98287/scripts/analyze_wp02.py#L75
[waszprov]: https://github.com/trbrewer/puckworks/blob/713c3c229568bb189c548f4c8a490b69a6319bef/puckworks/data/waszkiewicz2025/PROVENANCE.md#L49
[clockresult]: ../analysis/sci_md_grudeva_clock_001/RESULT.md
[mass6]: ../analysis/sci_md_mass_delivery_006/RESULT.md
[mass7]: ../analysis/sci_md_mass_delivery_007/RESULT.md
[mass8]: ../analysis/sci_md_mass_delivery_008/RESULT.md
[caffeine]: ../analysis/sci_md_caffeine_delivery_001/RESULT.md
[trigonelline]: ../analysis/sci_md_trigonelline_delivery_001/RESULT.md
[cqa]: ../analysis/sci_md_5cqa_delivery_001/RESULT.md
[tamped]: ../analysis/sci_val_tamped_k_001/RESULT.md
[flowhistory]: https://github.com/trbrewer/espresso-whole-pull/blob/73ec476ffe6ac626705ca949e28b32935ddf2992/docs/analysis/sci_md_pannusch_flow_history_001/RESULT.md
[fractionwindow]: https://github.com/trbrewer/espresso-whole-pull/blob/73ec476ffe6ac626705ca949e28b32935ddf2992/docs/analysis/obs_pannusch_fraction_window_001/RESULT.md
[minimum]: https://github.com/trbrewer/espresso-whole-pull/blob/73ec476ffe6ac626705ca949e28b32935ddf2992/docs/analysis/sci_ed_003/MINIMUM_PROGRAMME.md#L7
[mapping]: https://github.com/trbrewer/espresso-whole-pull/blob/73ec476ffe6ac626705ca949e28b32935ddf2992/docs/analysis/xsv_pannusch_ewp_input_mapping_001/RESULT.md
[pannuschsolver]: https://github.com/trbrewer/puckworks/blob/15479363ab3bcd879364628a1938879f2db8c05c/puckworks/models/pannusch2024/solver.py#L95
[authorrepo]: https://github.com/jamiemfoster/Espresso/tree/79ebefb72446eb706084e2392cab64bf0fad93a2
[parameters]: https://github.com/jamiemfoster/Espresso/blob/79ebefb72446eb706084e2392cab64bf0fad93a2/define_parameters.m#L27
[authorey]: https://github.com/jamiemfoster/Espresso/blob/79ebefb72446eb706084e2392cab64bf0fad93a2/make_an_espresso.m#L75
[rhs]: https://github.com/jamiemfoster/Espresso/blob/79ebefb72446eb706084e2392cab64bf0fad93a2/RHS.m#L19
[massmatrix]: https://github.com/jamiemfoster/Espresso/blob/79ebefb72446eb706084e2392cab64bf0fad93a2/build_mass.m#L3
[checkmass]: https://github.com/jamiemfoster/Espresso/blob/79ebefb72446eb706084e2392cab64bf0fad93a2/checkmass.m#L17
