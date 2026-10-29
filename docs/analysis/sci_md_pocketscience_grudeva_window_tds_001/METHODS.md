# Pocket Science → Grudeva regular-window TDS

Task: `SCI-MD-POCKETSCIENCE-GRUDEVA-WINDOW-TDS-001`.
Attribution: Pocket Science Coffee (2024); Grudeva thesis and upstream data/code.
Their permissions remain separate. Original data, locators, identities,
coefficients, numerical results, predictions and draws remain private.

## Scope and qualification

This is an exposed retrospective source-only comparison, conditional on measured
collected beverage mass and authenticated nominal target dose. The primary
comparison is P versus an equally source-trained N on absolute pooled-window
TDS. It establishes neither blindness, complete-cup transfer, practical adequacy,
causality nor production readiness. Earlier Pocket Science results remain intact.
P1 blind-TDS remains OPEN.

Scientific parent/base: PR379 `cc6e3d66eb5192e08e0949373548bb3a04ee69fd`;
its Git parent: `2425223a872e104345a787984ee5874671258368`.
PW main is pinned at `21669a427145194e1f4003e3cf1b97dedefe2679`;
read-only EWP at `f44c33dbb9b4fb80143e360e6f4a90f8ac0aa516`.
Grudeva upstream authority is `567ad8f3808eb74fbe3e470eaa333161bf2eac1c`.
No native EWP execution, notebook execution, new acquisition, figure reading,
historical model replay or closed MASS re-scoring is authorized.

Initial configured and explicit locators were unavailable. The owner then
explicitly authorized a local search, which located all three original files
with the pinned SHA256 values. Detailed discovery is private. The initial
blocked packet is preserved; the qualified analysis uses a fresh private bundle.
Qualification stayed within its 15-minute allowance, excluding owner waiting
and required QA. Numerical scientific computation is capped at 30 minutes,
excluding installation and required QA. One implementation/review cycle and at
most one material correction; no post-score policy tuning.

Pocket Science workbook SHA256:
`9e9063baea1e8f67d905b1e2d03a61a4227e26ed2964ae118426be09bced01cc`.
Primary57 membership:
`1b7863192edf7d4f672a71b5409d02004d72fb171da8d2581724427fb924f196`.
PR379 freeze/result are pinned in the runner. Their linked code, input, result
and saved-artifact receipts authenticate historical context without refitting.
One unchanged workbook observer pass across the task matched all60 observations,
identities and original order to PR379's authenticated full-cohort SHOTS.json.
PR378's SHOTS40 is not full-cohort authority. Membership hashing alone does not
protect order: explicit full observation/order equality is also required.

Grudeva originals are authenticated against the existing clock SOURCE.json:
exp13.csv `291cadb1d06a009f758c158c95b020db551c127333e9dec6f6c581eac320130c`;
PlotData.ipynb `bccaa696080166f8b31587c17a7268a7c13ce9dd5d19d4beec349f64e2c70dff`;
thesis `bbe73a303ab0b6838fe727f05d970438c7ba42576a9959f032aa63b88aff84e6`.
The notebook was inspected statically, not executed. Authenticated thesis
§§2.1–2.2, printed pages27–30 (PDF pages28–31), establish the window, recipe
and scope. Printed pages28–29 explicitly link nominal18.5g to the13 experimental
shots. This is not per-shot measured dose and does not use the illustrative S2
configuration. The exact passages/location/scope are retained privately;
the dose-authority receipt SHA256 is pinned in the runner.

## Cohorts and observations

Source: exactly57 physical Pocket Science shots,37 Sworks+20 VST,
29 traditional+28 turbo,12 original conditions. Preserve original ordering,
sectioning exclusions, grinder/style mapping and condition tuples. Ten flushes
remain excluded. No new LOCO fitting: each arm fits once to the full source.
Source x is measured dose/final beverage mass; raw D/E grams convert to kg.
Primary y is direct filtered numeric raw B, including B54. Raw C is reserved
for the source-observation sensitivity. No derived EY, historical Y54 or
regional-assay predictors/targets. Preparation N means paper, not model N.

Target: the first13 source-qualified physical blocks, each with16 regular
vials, in original rectangular order. Two whole shots have positive-mass
chemistry gaps and are excluded from the primary11. Their precise identities
and gap provenance are frozen privately. The unqualified extra block and
terminal vials remain excluded. The nominal0–32s window begins with simultaneous
pump/wheel activation; no first-drip realignment or full-cup extrapolation.
The unchanged parser reproduces208 regular slots,26 structural-zero vials,
180 positive-mass chemistry observations and two unavailable positive-mass
chemistry observations. No independent compaction of mass and chemistry columns.

Recorded Weight is mass authority; preserve gross/tare checks. For each eligible
shot, B=sum16 recorded net masses in kg and S=sum positive-mass vial
mass_kg×recorded_TDS_percent/100. Then y=100S/B and x=0.0185/B. Require finite
nonnegative vial masses and positive total B. Zero-mass vials contribute zero
liquid/solute without inventing TDS or computing0×NaN. A positive-mass chemistry
gap disqualifies the whole endpoint; never shorten its denominator.
Independently verify y=sum(m_g×TDS_percent)/sum(m_g), explicitly handling
structural zeros, within absolute1e-10 TDSpp.

Both nominal bases are refractometer-equivalent solute per solution mass.
Grudeva includes the supplied dilution correction; no density conversion or
invented filtered/unfiltered channel label. Freeze source/target x ranges and
every target extrapolation before fitting; retain every qualified target.
Vial weighting defines each endpoint, while shots receive equal primary weight.

## Frozen arms and arithmetic checks

P=alpha×x and N=mu each independently fit one scalar on identical source
physical-shot squared TDS error, bounds[0,100]. Point weights are one.
Weighted fits use alpha=clip(sum(wxy)/sum(wx²),0,100) and
mu=clip(sum(wy)/sum(w),0,100). Reuse the explicit P/N source-only fitter and
prediction/oracle helpers, without changing predecessor globals. Prediction
accepts coefficients and target x only; target y never enters fitting.
No target means, offsets, dose adjustments, affine rescue or calibration.

Require finite inputs/objectives, nonnegative weights, positive total training
weight and P denominator. Independently verify BVLS bounded least squares,
tol1e-14, and source/target predictions within absolute1e-10 TDSpp for point,
bootstrap and deletion fits. This tolerance concerns arithmetic, not measurement
precision or independent human review. Active bounds are reported, not automatic
failures. Predict raw values and score domain excursions outside[0,100] unchanged.
No nesting assertion, GSA campaign or additional model family.

## Loss, paired intervals and decision

Primary loss is RMSE across11 physical target endpoints. Also report MAE,
signed prediction-minus-observation bias, individual errors, adverse/worst cases,
coverage, support, coefficients and predictions privately. No target
condition-balanced metric or pooled-liquid pseudo-shot.

Delta=RMSE(P)−RMSE(N); gain=1−RMSE(P)/RMSE(N). If N loss is zero, gain is
undefined without epsilon, while absolute contrasts remain valid.
Each analysis uses2000 paired draws. Initialize NumPy SeedSequence(20261027),
spawn two independent source/target streams, identically for each analysis.
Resample source shots within12 fixed conditions at original sizes; independently
resample whole target shots at target cohort size. Share both multiplicity
vectors across P/N, refit source only on every draw, predict all original target
rows, and score with target multiplicities. Individual target zero weights are
valid; positive total target weight is required. Save both vectors and all draw
scores, contrasts, fit checks, active bounds and domain flags.

Report percentile95% CIs for each RMSE and paired delta/gain, plus requested,
completed, failed, unattempted and undefined counts. Stop at a failed draw and
retain its vectors; no successful-only interval substitutes for a completed
required campaign. Any failed necessary inference is INCOMPLETE.
Primary absolute-delta CI determines:

- upper<0: `P_WINDOW_TRANSFER_ADDED_VALUE_OVER_N`;
- lower>0: `N_LOWER_WINDOW_TRANSFER_LOSS`;
- otherwise, including zero endpoints: `WINDOW_TRANSFER_COMPARISON_UNRESOLVED`.

Zero is no improvement, not an adequacy, equivalence or noninferiority margin.
Gain grades: worse<0; small[0,0.10); moderate[0.10,0.25); large≥0.25. Report the
point and every CI-intersected grade. Reclassify unchanged estimates under all
nine lower{0.075,0.10,0.125}×upper{0.1875,0.25,0.3125} combinations. These are
reporting boundaries, not measurement robustness or practical acceptance.

## Exactly three sensitivities and limitations

1. Refit the same57 source shots on raw C, evaluate the same11 recorded-channel
   target endpoints, and run its own paired bootstrap. Only source observation
   changes; Grudeva is not called unfiltered.
2. Refit filtered source and include all13 qualified target blocks, interpreting
   the two recorded positive-mass zeros literally. Retain all16 masses per
   denominator and use its own13-shot bootstrap. This is an alternative
   observation assumption, not13 primary chemistry-qualified targets.
3. Delete each of12 source conditions, refit and score all11 primary targets.
   Delete each of11 target shots, retain the full-source fit and score10.
   Report ranges, ties and reversals as influence diagnostics, not CIs.

Report exactly which interval conclusion changes; no favorable observer
selection, ALL60-source factorial, reverse transfer or additional endpoint.
Both datasets are TARGET_EXPOSED/RETROSPECTIVE. Previous used means and
clock/MASS analyses preclude blindness; procedural separation does not restore
it. Intervals assume source within-condition and target whole-shot
exchangeability. They omit unknown settings/sessions/order, nominal-dose error,
shared calibration/dilution/systematic error, observer differences and prior
selection. They are not simultaneous or new-campaign validation intervals.
Source whole cups and target windows differ, confounded with campaign effects.

## Reproduction and handoff

Use the qualified private input bundle authenticated by its ARTIFACTS.json,
including SOURCE_SHOTS, original Grudeva records, LOCATORS, qualification and
nominal-dose receipts. A reproduction copies only the frozen private inputs to
a fresh external directory, retaining authenticated original locators. The
runner resolves paths inside code and authenticates bytes rather than filenames.
The initial once-only workbook inspection receipt is reused and verified against
PR379; no second original observer pass or historical campaign is required.
Never print private paths/configuration or raw discovery. With a private
WINDOW_EVIDENCE locator configured by the owner:

```sh
python tools/pocketscience_grudeva_window_tds.py freeze --output "$WINDOW_EVIDENCE"
python tools/pocketscience_grudeva_window_tds.py run --output "$WINDOW_EVIDENCE"
```

`freeze` records source/target membership, support, dose authority, code/method
hashes, policy, seed, comparisons, decisions and sensitivities before scoring.
`run` rechecks all frozen hashes and refuses an existing attempt. CLI output is
safe status/hashes only. Private RESULT.md≤750 words/2 pages and SUMMARY.md≤120
words accompany complete JSON/CSVs, predictions, draws and artifact hashes.
Source/identity/basis/dose drift, leakage, arithmetic failure, invalid inference,
exhausted budget or an unfixed material defect stop with precise evidence.

Public output is first-party code, synthetic tests, methods and safe status/hash
receipts only. Preserve predecessor artifacts/defaults and corrected pytest
configuration. Draft PR380 remains stacked on PR379 while unmerged; no merge or
auto-merge. The single next candidate is
SCI-MD-WADSWORTH-HELD-COFFEE-PERMEABILITY-001: qualify sample/error semantics of
existing21 records before any held-coffee comparison. Do not execute it here;
reassess priority if genuinely unexposed existing data become executable.
