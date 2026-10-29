# SCI-MD-POCKETSCIENCE-CROSS-STYLE-TDS-001

Pocket Science Coffee (2024). G1 / NO_GOVERNING_PHYSICS_CHANGE, exposed retrospective
comparison under the owner's bounded one-cycle authorization. Scientific parent and
branch base PR376: `e21a98db63a1912a0f8baa2ef1c7cdc562293c18`; PR375 ancestor:
`9f8c6c7cf894872908f3ea212c69209db13c602a`; PR374 ancestor:
`2f93c216f02700e28801418a3069684fff0ba9ea`; PW main:
`21669a427145194e1f4003e3cf1b97dedefe2679`; read-only EWP:
`f44c33dbb9b4fb80143e360e6f4a90f8ac0aa516`. Stack on PR376 while unmerged.

## Source, observation and split

Use only `pocketscience2024/workbook_assay_reconstruction`. Resolve the workbook
and predecessor bundles inside code through the owner's configured resolver;
`--predecessor` permits one explicit PR376 locator if necessary. Never search
unrelated directories, echo configuration/locators or trust a basename. Authenticate:

| Artifact | SHA256 |
|---|---|
| Workbook | `9e9063baea1e8f67d905b1e2d03a61a4227e26ed2964ae118426be09bced01cc` |
| Primary membership | `1b7863192edf7d4f672a71b5409d02004d72fb171da8d2581724427fb924f196` |
| PR376 FREEZE.json | `22a50d10197d1fda389210fdc0fd672906e7b2a65134d8a7dc934e3429476f30` |
| PR376 RESULT.json | `ef32f88905be021395d5bd87b8f3afe2a4e7bd964ef6712d7380295894a7d317` |
| Historical basket SPLIT.json | `fcf4e6f2f57df234b283d651d19c192097451d531c9f87d1480d13ece2077c68` |

One source pass with the unchanged qualified observer compares all 60 cup-qualified
rows, exact observations, identities and original order with authenticated
PR374–376 SHOTS.json. Preserve 57-shot membership and source sectioning exclusions
Sworks rows 7, 9, 23. Ten distinct flush measurements remain excluded. Authenticate
predecessor code/input/artifact receipts and saved bootstrap intervals/multiplicities;
never rerun historical bootstrap campaigns. Allow one PR376 primary point reproduction
against full-precision predictions/scores to 1e-10 pp, never rounded chat values.

Primary training is every retained traditional shot; evaluation is every retained
turbo shot, both baskets represented, six conditions per side, 57 shots in total.
Calculate actual per-style counts from authenticated rows; no guessed counts.
Separately freeze the complete 60-shot partition and confirm 30 traditional/30 turbo.
Assign each of the three added rows by its actual style; either side may change.
Freeze identities, order, disjointness, complete coverage and one global condition
mapping, plus new style-split hashes. Never reuse the historical basket partition.
Private SUPPORT.json precedes fitting and reports x ranges, overlap, extrapolation
counts and missing training support overall, by basket and by comparable preparation
(basket, screen/paper, dispersion). Flag every target; retain all qualified targets.

x=measured dose_kg/measured final beverage_kg; raw D/E grams convert to kg.
y=direct filtered numeric TDS percentage points from B, including B54. C is the
separate unfiltered observation. Nominal basis: refractometer-equivalent solute per
solution mass; no density conversion. Derived EY, regional assays and historical
Y54 are not predictors or substitute targets; historical treatment remains unchanged.
Exact mapping: Niche Zero→traditional; Superjolly MP64→turbo.

BOTH sides: SOURCE_INTERNAL / TARGET_EXPOSED / RETROSPECTIVE /
CONDITIONAL_ON_MEASURED_FINAL_BEVERAGE_MASS. Used means expose their underlying shots.
Current training exclusion does not restore blindness. Style, grinder, recipe and
duration are confounded. The claim concerns conditional predictor reuse in this
observed campaign and direction across the observed brew-ratio change, not causal
style/grinder effects. Actual original/private inspections and limits are recorded;
sessions, shared calibration and systematic measurement uncertainty remain UNKNOWN.
No new acquisition, figures, experiments, native EWP runs or corpus audit.

## Frozen P/N-only fitting

P(x)=alpha*x; N(x)=mu. Independently fit one scalar each to the same traditional
physical shots, minimizing the same unweighted squared error in absolute TDS pp,
coefficient bounds [0,100]. Point fits are clip(sum(x*y)/sum(x*x),0,100) and
clip(mean(y),0,100); weighted fits use sum(w*x*y)/sum(w*x*x) and sum(w*y)/sum(w).
Inputs to fit_source are source-only x/y/weights. Prediction takes only coefficients
and evaluation x. No intercept for P, offsets, copied coefficients, EY fitting,
shrinkage, target calibration, hyperparameter search or target-informed tuning.

M/C are not fitted: turbo coefficients are unavailable from traditional-only data.
Preserve predecessor both-style/rank guards and globals; no pseudoinverse, zero fill
or generic basket-fitter refactor. P/N are not nested; no M/P assertion is inherited.
Check finite inputs/objectives/predictions, positive total training weight, positive
P denominator, active bounds and complete coverage. Verify both bounded solutions
using independent SciPy BVLS on training data and training/target predictions to
absolute 1e-10 TDS pp, for point, bootstrap and source-condition-deletion fits. This
is an arithmetic tolerance, not measurement precision. No GSA campaign is needed.

## Scoring, inference and decision

Primary loss is physical-shot turbo RMSE. Also report MAE, signed prediction-minus-
observation bias, condition-balanced RMSE, per-condition and descriptive per-basket
errors, adverse cases, worst errors, coverage and predictions privately. These do
not select alternate winners. Delta=RMSE(P)−RMSE(N), negative favors P;
gain=1−RMSE(P)/RMSE(N), positive favors P. If N loss is zero, gain is undefined;
retain absolute differences and add no epsilon.

Each of primary filtered, primary unfiltered and all-60 filtered uses its own 2,000
paired draws, numpy default_rng seed 20261026. Within each of 12 fixed conditions,
resample physical shots at the original condition size. Save one common global
multiplicity vector per draw. Refit only traditional x/y using source weights;
predict every turbo row; score only turbo y using target weights. Repeated readings,
means and resampled copies are not additional physical identities. Report percentile
95% delta/gain CIs, requested/completed/failed/not-run/undefined counts and active
bounds. A failed draw stops the campaign with INCOMPLETE and preserves multiplicities;
no CI from successful-only draws. Undefined relative gains leave absolute contrasts
intact; a relative CI requires every completed gain defined.

Decision from the primary paired absolute delta CI:

- upper bound <0: P_CROSS_STYLE_ADDED_VALUE_OVER_N;
- lower bound >0: N_LOWER_CROSS_STYLE_LOSS;
- otherwise, including a zero endpoint: CROSS_STYLE_COMPARISON_UNRESOLVED.

Zero is the no-improvement reference. No practical adequacy, equivalence or
noninferiority margin. An unfavorable/unresolved result limits this additional
reuse claim; completed basket/LOCO results remain unchanged.

Intervals condition on six source/six target conditions, exchangeability within
conditions and the previously selected family. They include source-fit and target-
sampling variation, omit unknown session dependence, shared systematic measurement
error and prior model-selection uncertainty, and are neither simultaneous intervals
nor new-campaign validation. Numerical verification is not independent human review.

Gain grades: worse <0, small [0,.10), moderate [.10,.25), large >=.25. Report point
and every CI-intersected grade. Reclassify unchanged results under all nine lower
{.075,.10,.125} × upper {.1875,.25,.3125} combinations. This ±25% check concerns
reporting boundaries, not sensor-error robustness or practical acceptance; no refits.

## Only three sensitivities and bounded execution

A: same primary split, fit traditional C and evaluate turbo C, own paired bootstrap.
B: separately frozen all-60 split, fit/evaluate filtered B, own paired bootstrap;
retain original exclusion provenance and disclose additions on each side.
C: delete each of six training conditions, refit remaining source, evaluate all
primary targets; delete each of six target conditions, retain the full primary
source fit, score remaining targets. Report point ranges, ties and sign reversals
as influence diagnostics, not CIs. Keep primary decision separate and identify
exactly which conclusion changes. No reverse transfer, dispersion, basket-subset
fitting, target-calibrated or other additional analyses.

Freeze source, membership, split, support, code, methods, bounds, seed, comparisons,
decision and sensitivities before any new transfer score. One implementation/review
cycle, at most one material correction. Scientific computation <=30 minutes, including
metadata/source authentication and excluding installation/required QA. Stop on unavailable
authenticated inputs, drift, unresolved identities, invalid fitting, leakage, failed
necessary reproduction, invalid inference, cap exhaustion or an unfixed material bug.
Preserve precise BLOCKED/NOT_RUN/INCOMPLETE evidence; never overwrite predecessors.

## Reproduction and publication

Install `pip install -e '.[dev,reconstruct]'`. From the isolated PR376-based branch:

```bash
python tools/pocketscience_cross_style_tds.py inspect
python -m pytest -q tests/test_pocketscience_cross_style_tds.py tests/test_pocketscience_cross_basket_tds.py tests/test_pocketscience_pooled_scaling.py tests/test_pocketscience_cup_tds.py
python tools/pocketscience_cross_style_tds.py freeze
python tools/pocketscience_cross_style_tds.py run
```

`inspect` opens the original once and saves private source/split/support receipts.
`freeze` checks receipts and binds final scientific code/methods before fitting.
`run` refuses a second attempt. Default output is a fresh task directory beside
the configured predecessor inventory; `--output` selects a fresh external directory.
Use the same options for all stages. An explicit `--predecessor` is a locator only;
the pinned PR376 hashes remain mandatory. CLI output is safe hashes/status only.

Public: code, synthetic tests, methods, reproduction and safe status/hashes.
Private: locators, identities, coefficients, numerical results, predictions,
condition aggregates and saved draws; RESULT.md <=2 pages/target <=750 words,
SUMMARY.md <=120 words, complete RESULT.json, SCORES.csv, CONTRASTS.csv, prediction
CSVs, inspection/source/split/code/method freeze and ARTIFACTS.json. Distinguish local
and hosted checks. Draft PR explicitly depends on PR376; leave unmerged and auto-merge
off. P1 blind-TDS=OPEN. Only next candidate on completion:
SCI-MD-POCKETSCIENCE-CROSS-DISPERSION-TDS-001 (existing frozen P/M/C/N family,
brass→teflon within 37 Sworks shots, both styles). Do not execute; reassess priority
if genuinely unexposed existing data become executable. If blocked, name the single
existing artifact required next.
