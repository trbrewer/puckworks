# Pocket Science → Grudeva regular-window TDS

Task: `SCI-MD-POCKETSCIENCE-GRUDEVA-WINDOW-TDS-001`.
Attribution: Pocket Science Coffee (2024); Grudeva thesis and upstream data/code.
Their permissions remain separate; original data and derived numerical evidence
remain private.

## Disposition

**BLOCKED before fitting; comparative analysis NOT_RUN.** The existing configured
manifest and narrow task locators did not resolve the three pinned Grudeva
originals. This describes availability through the inspected locators, not
nonexistence of the data. The required nominal-dose passage in the authenticated
thesis could not be inspected. A public card's dose statement was not substituted.
The owner subsequently supplied a narrow explicit directory; it was unavailable
in this execution workspace. No neighboring directories were searched and no
additional original files were opened.

The initial bounded qualification used 543.645381 seconds of the 900-second
allowance; the subsequent explicit locator check found no accessible directory.
Scientific computation used zero seconds. No new transfer implementation, target
aggregation, source fit, predictions, scoring, bootstrap or scientific freeze was
completed. This document preserves the requested policy for continuation; it is
**not a completed pre-scoring freeze**. `STATUS.json` records the exact disposition
and safe receipts. The public delta is G0 documentation of a blocked G1 input
qualification; production, registry, predecessor code and artifacts are unchanged.

The one existing artifact needed next is the **Grudeva clock original-source
bundle**, containing the pinned CSV, notebook and thesis PDF. A narrow explicit
private locator is sufficient to resume authentication. No download, broad search,
notebook execution, historical model replay or native EWP run was performed.

## Inspection and authenticated source

The Pocket Science workbook and PR379 private freeze/result and linked artifacts
were authenticated. One unchanged observer pass matched all 60 cup-qualified
observations, identities and original ordering against PR379's full-cohort
`SHOTS.json` and earlier full-cohort records. PR378's 40-row `SHOTS.json` was not
used as full-cohort authority. The original 57-shot membership is unchanged:
37 Sworks and 20 VST, 29 traditional and 28 turbo, in 12 fixed conditions.
Original sectioning exclusions and flush exclusion remain intact.

Grudeva's parser, existing protocol, audit, source card and permission record were
read. Its original CSV, notebook and thesis were **not inspected in this task**.
The earlier audit's 13 qualified blocks and 11 complete-chemistry shots are
historical context, not newly authenticated endpoint membership. No target shots
have been admitted and no new target-membership hash exists.

Both datasets are historically TARGET_EXPOSED and RETROSPECTIVE. Previous used
means and Grudeva clock/MASS analyses preclude blindness. Source-only fitting
would not restore blindness. Unknown sessions, shared calibration, systematic
error and nominal-dose error remain limitations; they did not cause this stop.
P1 blind-TDS remains OPEN.

## Requested observation and fit policy (not executed)

Training uses the unchanged 57 Pocket Science physical shots. The predictor is
measured dose/final beverage mass, converting raw D/E grams to kg; the primary
response is direct filtered numeric raw B, including B54 without substituting
historical derived EY. Raw C is reserved for the source-observation sensitivity.
Derived EY and regional assays are not predictors or substitute targets.

Target endpoints use each complete shot's 16 regular vials in the nominal
0–32-second pump/wheel-activation window. Two whole shots with positive-mass
chemistry gaps are excluded from primary scoring. Unqualified extra blocks and
terminal liquid remain excluded. Recorded net Weight is the mass authority;
gross/tare checks and rectangular identity/order must be retained. Zero-mass
vials contribute zero liquid and solute without inventing TDS or multiplying
zero by NaN. A positive-mass chemistry gap disqualifies the entire endpoint;
its mass must never be removed to shorten the denominator.

For each eligible shot, let B be the sum of all 16 masses in kg, and S the sum
of qualified mass × recorded TDS/100. Then y = 100 S/B. Independently verify
the equivalent gram-weighted TDS mean within 1e-10 percentage points. The
proposed x = 0.0185 kg/B requires the authenticated thesis methods §§2.1–2.2
to establish that nominal dose's applicability to the experimental shots.
This is not individually measured dose; the illustrative S2 configuration
cannot supply authority. No nominal dose has yet been qualified.

The nominal TDS basis is refractometer-equivalent solute per solution mass,
with Grudeva's supplied dilution correction and no density conversion. Its
single recorded channel receives no invented filtered/unfiltered designation.
Whole-cup source and regular-window target observations differ.

Fit P = alpha × x and N = mu independently to the same physical source shots,
with bounds [0,100], using unweighted squared error in absolute TDS percentage
points. Weighted bootstrap fits use alpha = clip(sum(wxy)/sum(wx²),0,100) and
mu = clip(sum(wy)/sum(w),0,100). Reuse only valid source-only fitting and
prediction helpers, not predecessor partitions or target-weight guards.
Require finite inputs/objectives, nonnegative weights, positive total weight
and denominator; verify BVLS at tolerance 1e-14 and raw predictions within
1e-10 percentage points. Active bounds are reported. Raw predictions outside
[0,100] and all extrapolated targets remain scored.

## Requested inference and decisions (not executed)

Primary RMSE gives equal weight to each of the 11 physical target endpoints.
Also report MAE, signed prediction-minus-observation bias, individual errors,
coverage and support. Vial weighting defines an endpoint; vials are not
independent target replicates. There is no target condition-balanced metric.

Use 2,000 paired draws for each resampled analysis, initializing
`numpy.random.SeedSequence(20261027).spawn(2)` identically per analysis for
separate source and target streams. Resample source physical shots within
the 12 fixed conditions at their original sizes. Independently resample whole
target shots. Share both multiplicity vectors across P/N, refit source only,
and score with target weights. Zero individual target weights are valid;
positive total target weight is required. Save attempted vectors and checks.
A failed draw stops that campaign; preserve failed and unattempted counts
and never present successful-only intervals as completed inference.

Delta = RMSE(P) − RMSE(N); gain = 1 − RMSE(P)/RMSE(N). A zero N loss leaves
gain undefined without epsilon. Report percentile 95% intervals for both
RMSEs and paired contrasts. The primary absolute-delta interval determines:

- upper < 0: `P_WINDOW_TRANSFER_ADDED_VALUE_OVER_N`;
- lower > 0: `N_LOWER_WINDOW_TRANSFER_LOSS`;
- otherwise, including zero endpoints: `WINDOW_TRANSFER_COMPARISON_UNRESOLVED`.

Gain grades are worse (<0), small ([0,0.10)), moderate ([0.10,0.25)) and
large (≥0.25). Report the point grade and every CI-intersected grade. Reclassify
unchanged estimates under all nine lower {0.075,0.10,0.125} × upper
{0.1875,0.25,0.3125} reporting boundaries; do not refit or interpret these as
measurement-error assumptions or practical acceptance limits.

Exactly three sensitivities are prescribed: source raw C refitting with the
same 11 target endpoints and its own bootstrap; literal recorded positive-mass
zero TDS with all 13 qualified blocks, complete denominators and its own
bootstrap; and influence diagnostics deleting each source condition with refit
or each target shot while retaining the full-source fit. Deletion ranges are
not confidence intervals. No ALL60-source factorial or target calibration.

Intervals would condition on source conditions and assumed within-condition
source/whole-target-shot exchangeability. They omit unknown target settings,
sessions, order, nominal-dose error, shared calibration/dilution/systematic
error, observer differences and prior selection. They are not simultaneous
intervals, complete-cup transfer, blind validation or new-campaign guarantees.

## Reproduction and continuation

Start from the exact PR379 parent recorded in `STATUS.json`. Resolve private
Pocket Science inputs inside code using the existing affine runner's configured
resolver; authenticate pinned bytes and receipts before use. Supply the one
missing Grudeva bundle through a configured or narrow explicit locator; never
print locators, configuration, directory listings or raw discovery output.
Authenticate all three original SHA256 values, preserve parser semantics and
record the actual thesis passage/location and its scope privately. Stop if
the nominal dose is absent, contradictory or inapplicable.

Only after all required inputs qualify may the scoped implementation and
synthetic checks proceed. Freeze memberships, dose authority, observation,
code/method hashes, source-only policy, seed, decisions and sensitivities before
comparative scoring. The implementation, scientific freeze, target identities,
numerical outputs and new bootstrap records are currently NOT_RUN. Private
blocked receipts include qualification/inspection, source membership,
nominal-dose status, empty score/prediction schemas and campaign accounting.
Public receipts contain no private locators or observation values.

The single subsequent candidate remains
`SCI-MD-WADSWORTH-HELD-COFFEE-PERMEABILITY-001`, requiring qualification of the
existing 21 permeability records' sample/error semantics. It was not executed.
No target calibration or affine rescue follows this blocked transfer.
