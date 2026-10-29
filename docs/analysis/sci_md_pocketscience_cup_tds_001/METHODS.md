# SCI-MD-POCKETSCIENCE-CUP-TDS-001

Pocket Science Coffee (2024). G1, offline source-internal comparison; no governing
physics change. SOURCE_INTERNAL / TARGET_EXPOSED / RETROSPECTIVE /
CONDITIONAL_ON_MEASURED_FINAL_BEVERAGE_MASS. Used means and underlying replicates
remain exposed; grouped CV does not create blind data. P1 blind-TDS remains OPEN.

## Frozen observation and cohort

Use the qualified workbook reader and exact original SHA256
`9e9063baea1e8f67d905b1e2d03a61a4227e26ed2964ae118426be09bced01cc`.
Physical identity is sheet plus row. Primary membership is the existing 57
source-retained shots, 37 Sworks and 20 VST, in 12 existing conditions. Preserve
the three sectioning exclusions separately. Conditions are sheet/basket, exact
grinder, screen/paper and dispersion. Explicit source mapping: `Niche Zero` →
traditional; `Superjolly MP64` → turbo. Reject every other grinder label.

Read raw B directly, including B54, as filtered numeric TDS percent; C is the
separate unfiltered observation. D and E are initial dry dose and final beverage
mass in grams; convert to kg at the analysis interface. Reject blanks, nonfinite
values, formulas and percent-formatted primitives. No Excel blank-as-zero.
Nominal TDS basis is refractometer-equivalent solute per solution mass. Historical
Y54 replay remains unchanged. No density conversion. Derived EY = y E/D is only
a diagnostic, never an input. Sessions are unknown. Style and grinder are
confounded; no separate grinder/style, hydraulic, radial or causal effect follows.

## Models and fitting

Set x = measured dose / measured final beverage mass, y = direct TDS in percentage
points. M predicts theta[s] x, C predicts beta[s], N predicts mu. M and C each
fit two scalars; N fits one. C requires fewer measured inputs, not fewer fitted
parameters. Theta is an operational fitted EY percentage, not an extraction
mechanism. Independently minimize the same unweighted physical-shot squared
absolute-TDS error within training data: theta = sum(x y)/sum(x²), beta = mean(y)
within style, mu = pooled mean(y). Clip each coefficient to [0,100] and disclose
active bounds. Check training design rank; no GSA, transformations, interactions,
corrections, target-derived bounds or hyperparameter search.

Leave each of the 12 existing conditions out once, with every replicate together.
Every primary shot gets one prediction from every arm. A fold's held targets
enter scoring only. Cross-check predictions with an independent least-squares
implementation to absolute 1e-10 TDS pp; this verifies arithmetic only.

## Scores, uncertainty and decision

Primary RMSE = sqrt(mean shot squared error). Also report MAE and signed bias
(prediction minus target), paired RMSE difference L_A−L_B (negative favors A),
gain 1−L_A/L_B (positive favors A), and condition-balanced RMSE (mean condition
MSE before square root). Private output includes every prediction, fold fit,
condition error, worst error, coverage and adverse case for M/C, M/N and C/N.

Use 2,000 paired bootstrap draws, numpy default_rng seed 20261026: one global
multiset per draw, sampled within each fixed condition at its original size.
Refit all folds and arms using those multiplicities, and score held observations
with the same multiplicities. Report percentile 95% intervals for differences
and gains, and requested/completed/failed draws. If reference RMSE is zero, gain
is undefined without epsilon. Intervals assume exchangeable shots within fixed
conditions and omit unknown sessions, calibration and shared systematic errors;
they are approximate and not simultaneous across contrasts. Historical assumed
0.01-TDS-pp/0.1-g Monte Carlo errors are not calibrated measurement uncertainty.

Gain grades: worse <0; small [0,.10); moderate [.10,.25); large ≥.25. Report point
grade and all CI-intersected grades. Reclassify unchanged predictions using all
nine lower {.075,.10,.125} × upper {.1875,.25,.3125} boundaries. These conventions
are neither adequacy thresholds nor measurement-error robustness checks.

Select M for conditional research reuse only when both G(M/C) and G(M/N) lower
95% bounds exceed zero. Otherwise retain C as lower-input reference if G(C/N)'s
lower bound exceeds zero. If M/C spans zero, explicitly report unresolved choice
and unestablished incremental scaling value. If only M/N establishes improvement
and M/C is unresolved, report NO_SELECTED_WINNER. If neither alternative
establishes improvement over N, retain N because added value is unestablished,
not because equivalence/adequacy is proved. An entirely negative M/C interval
establishes M's conditional disadvantage on this evaluation. No blind validation,
practical adequacy or production adoption follows.

## Prespecified sensitivities and reproduction

Repeat the fixed comparison and bootstrap separately for direct unfiltered C and
for primary plus each source-rejected shot whose cup primitives independently
qualify. Do not alter primary membership. Delete each condition in turn and
refit the remaining CV pipeline; report point influence ranges, not confidence
intervals. No other variants or search. Freeze methods, membership, exposure and
code hashes before scoring; numerical evidence and source identities stay private.

Use an environment installed with `pip install -e '.[dev,reconstruct]'`:

```bash
python tools/pocketscience_cup_tds.py freeze
python -m pytest -q tests/test_pocketscience_cup_tds.py tests/test_pocketscience2024_assay.py
python tools/pocketscience_cup_tds.py run
```

The runner resolves the source via `PUCKWORKS_EXTERNAL_DATA_ROOT` or owner
`data_sources.json`; evidence is a task subdirectory beside the configured private
inventory manifest. It never prints private paths or values. All new numerical
results stay outside Git; public artifacts contain code, methods and safe hashes
or execution status only. No expanded redistribution grant is recorded.
