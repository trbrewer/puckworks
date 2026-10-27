# SCI-MD-WADSWORTH-MEASURED-SURFACE-PERMEABILITY-001

Owner-authorized G1 retrospective representation comparison. Replace mean radius
with tabulated connected specific surface area in a matched three-coefficient
empirical model. S3/E3 is primary; S3/W3 and S3/N qualify preference. This is not
adding surface area alongside radius, a causal effect, independent validation of
LB physics, permission for measurement acquisition, or production use.

One implementation/review cycle; at most one material pre-score correction.
Qualification plus narrow inherited-test repair <=20 minutes; scientific
computation <=30 minutes excluding installation and required repository QA.
No new experiments, raw acquisition, figures, native solvers, extra families,
parameter rescue, post-score tuning or separate historical bootstrap campaigns.

## Authority and actual inspection

PW main `21669a427145194e1f4003e3cf1b97dedefe2679`; base/scientific parent PR381
`7c04a644c7b74be53ffb1cf611ebfb7ab06c5fd2`; its Git parent PR380
`097e5c7f0bdc1bef38d56938374f936003d55a39`; PR380 Git parent
`d41af1d08cda65864fdbdf5c6e1814cc027c5ef1`; read-only EWP
`f44c33dbb9b4fb80143e360e6f4a90f8ac0aa516`.

Read the pinned full CSV, provenance, parent implementation/tests/launcher/
METHODS/STATUS, native permeability formula, historical collapse gate, permission
record and inherited assay comparison. The known private parent bundle was
authenticated against its manifest and the pinned FREEZE/RESULT hashes; no broad
directory search or locator/configuration disclosure. Preserve that bundle and
all parent scientific files byte-for-byte. PR381 historical QA stays failed.

Wadsworth et al., *Royal Society Open Science* 13,252031 (2026),
[DOI 10.1098/rsos.252031](https://doi.org/10.1098/rsos.252031),
[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
Original [methods §§3.3–3.5](https://strathprints.strath.ac.uk/95930/1/Wadsworth-etal-RSOS-2026-A-model-for-the-permeability-of-coffee-pucks-validated.pdf)
were inspected as text, without reading figures or acquiring raw observations.
Connected porosity/surface area derive from segmented XCT geometry; permeability
derives from LB simulation on that geometry. Preparations are untamped. Three
simulated directions do not constitute three preparations. Reported directional
spread is not calibrated Gaussian SD/SEM or independent replication; k_err is
never a fit weight, perturbation input or pseudo-replicate, nor divided by sqrt(3).
Attribution and bounded existing permissions remain unchanged; new calculations
are private derived outputs, not a broader rights clearance.

## Qualification and repair

Authenticate before parsing: source SHA256
`3b0139fe02108d3dfcd1441d9e4062e86d9b7e1a8505141a7beefd9366ebf20f`,
Git blob `37b4136bfa1a84df159f41c01245000288db4ebf`, 2315 bytes, 23 CRLF endings.
Use the unchanged parent reader for R/phi/k/k_err. Independently parse
`s_p_connected_per_m` from the same bytes, uniquely join (coffee,G), and preserve
parent observations/order. Require 21 finite positive connected-area values;
excluded Guayacan G2 must have a blank field. No total area, polydispersivity,
radius-derived estimate or target-derived transform. Guayacan G1 connected area
is 33588.43 m^-1, not total area 40384.06 m^-1.

There are 22 samples, 21 endpoints (Guayacan10/Tumba11), two coffees and zero
espresso shots. No imputation. R is mean radius in metres, phi is dimensionless
connected porosity, s_p is m^-1, k and reported k_err are m². Parent positivity,
finiteness, 0<phi<1 and nonnegative-error checks remain. TDS/EY NOT_APPLICABLE;
no density conversion. Compare all63 observation rows in authenticated parent
predictions with these unchanged R/phi/k/k_err values.

Parent ordered identity SHA256:
`f72c57505fab4b7bf42876970c89207b36f3f1975e0b79081b09ca10563a8821`.
Parent annotated-fold SHA256:
`4db17f4379b600c6ccca735ec4f96fc48f2f490240ad0b07c155eb1dd8e2a8fe`.
Parent FREEZE SHA256:
`1f2ccc1c4ce94f0d1654d113b322a936a924664f12c108978d056d4da417d624`.
Parent RESULT SHA256:
`7a724f317f638e303e69bbd403ebf742efc98ee18baa8292e17c47dc5b7c4467`.
Known parent ARTIFACTS manifest SHA256, retained from the preceding session:
`4d81a65e5020868cef1b65102ef4c7c6f810f29e5ef097a356b047a229981599`.
Bind that digest before trusting any manifest entry; authenticate all26 entries.
Check old annotated folds separately, then exact source/evaluation lists.
Create new augmented-observation and annotated-fold hashes; changed metadata
must not be forced to equal the old fold hash.

The only predecessor edit is the owner's assay-test exception: recursively
check exact field/key order, types, tuple lengths and None structure, then compare
each numeric leaf using scalar pytest.approx with its original default
tolerances. Require 15 numeric leaves per basket, 30 total. Preserve existing
depletion/conservation assertions. The two affected cases must pass before
freeze. No pytest downgrade, assay/model edit or broader test relaxation.

## Exposure, folds and frozen arms

Both folds SOURCE_INTERNAL / TARGET_EXPOSED / RETROSPECTIVE. S3 conditions on
tabulated connected surface area/porosity; W3/E3 on measured mean radius and
connected porosity; N has no morphology predictor. Prior target/summary use and
representation selection after PR381 preclude blindness.

Train Guayacan10 -> predict Tumba11, then train Tumba11 -> predict Guayacan10.
Exactly one OOF prediction per endpoint/arm. R0=1e-3 m, s0=1e4 m^-1,
k0=1e-10 m², r=R/R0, z=ln(k/k0),
o=ln[2 R0²/(9 k0)]+2 ln(r)-ln(1-phi).

* S3: z_hat=sIntercept+sSlope ln(s_p/s0)+sPhi ln(phi).
* E3: z_hat=e0+eR ln(r)+ePhi ln(phi).
* W3: z_hat=o+c-2 a r+b ln(phi).
* N: training mean z, equivalent to training geometric-mean k.

S3/E3/W3 independently fit three unrestricted coefficients; N fits one. Identical
source records, nonnegative weights and log-SSE objective; independent fits in
every fold/draw/deletion. No target-based preprocessing, offsets, means, priors,
bounds, hyperparameters or imported all-data constants. G/coffee identify roles
only. S3 is empirical, not physical parameter identification. Preserve W3 a<0
and b<=0 fits and frequencies; no fixed-b rescue. Parent sign frequencies are
not Sobol ST and cannot justify fixing/refuting b. Any future necessary GSA is
training-only; ST<0.01 supports fixing, not refutation. No GSA deliverable here.

## Numerical rules and parent reproduction

Task-local four-arm evaluator, S3 fitter, summaries, preference, deletion and
support reporting. Never mutate parent ARMS/PAIRS. Use immutable parent fit for
W3/E3/N and its score/contrast/interval/grade/checked_k primitives. Diagnostics
are keyed by training coffee and arm, never positional.

Float64 weighted training-only centering/scaling; retain exact inverse map.
Unit weights for points/deletions; integer multiplicities for bootstrap.
Require positive total weight, finite positive feature scales, finite objectives,
full rank with singular_value>eps*max(active weighted design shape)*largest
singular_value. Save singular values, thresholds, condition numbers, centers,
scales, coefficients and SSE. Local rank is not physical identifiability.
Independent SVD and QR+solve predictions agree on source/target within
1e-9*max(1,abs(z_hat)); inverse-map predictions use the same tolerance.
S3 and E3 SSE <= N SSE+1e-12*max(1,N SSE); no W3 nesting requirement.
Use direct log predictions and checked exp(ln(k0)+z); no clipping or exclusions.
Retain raw extrapolations; S3 support is s_p/phi, W3/E3 support R/phi, N has no
morphology feature. Marginal containment does not establish joint support.

In the one new campaign, check retained-arm point predictions before interpreting
S3 losses. Each new draw is compared inline with the corresponding authenticated
parent draw: exact multiplicities and role lists; absolute log-prediction error
<=1e-10; every derived score error <=1e-10*max(unit,abs(parent_score)), where unit
is1 for log metrics and k0 for m² metrics. No standalone parent fits/campaign.
Retained-arm comparisons are reproduction/context; do not reopen PR381 decisions.

## Metrics, uncertainty and decisions

L=sqrt(0.5 MSE_Guayacan(z_hat-z)+0.5 MSE_Tumba(z_hat-z)); not pooled21 RMSE or
mean of directional RMSEs. Also save directional log RMSE/MAE/bias and absolute
permeability RMSE/MAE/bias with the same equal-coffee aggregation, per-record
errors, coverage, worst cases and source/target feature ranges.

Exactly2000 paired draws: SeedSequence(20261027), two spawned default_rng streams
in Guayacan/Tumba order. Each coffee uses rng.integers(0,n,size=n) then
bincount(minlength=n), n=10/11. Its ONE vector is reused in its training and
opposite-fold evaluation role across all four arms. Refit each arm. Zero
individual weights valid; positive total required. Save weights, predictions,
scores, diagnostics, contrasts and reproduction receipts. Stop on first required
failure, saving vectors/reason; no retry, reseed, pseudoinverse or successful-only
CI. Report requested/completed/failed/unattempted/undefined counts.

Percentile95% CIs, method='linear', 2.5/97.5, for every metric/direction and new
contrast S3/E3 (primary), S3/W3 (key), S3/N (naive). Delta=L_A-L_B; gain=1-L_A/L_B.
Zero reference loss makes gain undefined without epsilon; no gain CI if any
required gain is undefined, retain absolute comparison and count undefineds.
These are conditional within-coffee selected-record sampling intervals with
uncalibrated coverage. Measurement/coffee-population CIs NOT_ESTIMABLE. Exclude
correlated predictor/response geometry errors, segmentation effects, physical
replication, directional uncertainty, shared systematics and prior model/
representation selection. Two coffees do not establish a coffee population.

Primary delta CI upper<0: S3_LOWER_CONDITIONAL_LOG_LOSS_THAN_E3; lower>0:
E3_LOWER_CONDITIONAL_LOG_LOSS_THAN_S3; otherwise, including zero endpoints:
SURFACE_RADIUS_COMPARISON_UNRESOLVED. S3_CONDITIONAL_PREFERENCE requires upper<0
against EACH of E3/W3/N and point loss no higher than EACH in BOTH directions.
If a comparator has resolved lower aggregate loss, SURFACE_REPRESENTATION_NOT_SELECTED
and identify it. Otherwise SURFACE_REPRESENTATION_PREFERENCE_UNRESOLVED with
direction dependence explicit. Incomplete inference: INCOMPLETE, no selection.
An S3/E3 win alone does not establish superiority to W3/N. No practical adequacy,
equivalence, causality, native-law, wet-puck, espresso, blindness or production claim.

Grades: worse<0; small[0,.10); moderate[.10,.25); large>=.25. Report point and
every grade intersecting the closed CI. Reclassify unchanged values under all
nine {.075,.10,.125} x {.1875,.25,.3125} boundaries. They are descriptive, not
measurement allowances/acceptance margins. Zero is directional, not adequacy.

## Bounded diagnostics and outputs

A: absolute-unit losses from identical fits/draws, no objective refit.
B: delete each21 eligible physical record from BOTH roles.
C: delete each G1–11 from BOTH coffees, retaining actual G2 missingness.
B/C refit all arms and retain all remaining endpoints; report delta/gain ranges,
exact zero ties and point-ranking reversals for each new contrast/direction/unit.
Influence ranges are not CIs. Complete main campaign:16264 fit instances;
synthetic tests are separate. No extra bootstrap, perturbation, family or policy.

Private pre-score FREEZE binds inputs/parent manifest, order/memberships, new
observations/folds, features/equations, code/tests/repair, methods, numerical
policy, metrics/seed/decisions/diagnostics. New output directory outside Git and
parent bundle; never silently overwrite a scored run. Stop on missing/hash-drift
authority, observation/join/unit drift, leakage, reproduction/rank/arithmetic/
nonfinite failure, invalid inference, exhausted budget or unfixed material defect.
Preserve BLOCKED/INCOMPLETE/NOT_RUN and completed evidence. Post-score QA failure
stays explicit even if inference completed.

Focused synthetic tests before freeze; required repository QA once, with focused
follow-up only for concrete failure. Existing discovery suffices. Report local
and hosted status separately. Numerical checks are not independent human review.
Only five new task files plus narrow assay-test repair; old defaults/gates and
scientific predecessors/EWP untouched. Public: code/tests/methods/safe status and
hashes. Private: RESULT.md <=750 words/~two pages, SUMMARY.md <=120 words,
RESULT.json, SCORES.csv, CONTRASTS.csv, PREDICTIONS.csv, FOLDS.json,
FEATURE_RECEIPT.json, MULTIPLICITIES.csv, DRAWS.jsonl, DIAGNOSTICS.json,
FREEZE.json and ARTIFACTS.json SHA256 manifest.

Draft PR stacks on sci-md-wadsworth-held-coffee-permeability-001; unmerged,
auto-merge disabled. P1 blind-TDS=OPEN. Exactly one provisional next candidate,
NOT_RUN: SCI-MD-TRIGONELLINE-RECIPE-INCREMENT-001. Fresh bounded selection review
must freeze matched-capacity recipe family/control, independent tuning policy,
actual held-fold mass support, refitting/uncertainty contract and credible budget
for canonical45 shots/15 designs. No completed mass-shape replay or silent reuse
of its old executor/selected-lambda validation claim. Reassess if genuinely
unexposed existing data become executable.
