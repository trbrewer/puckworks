# SCI-MD-POCKETSCIENCE-POOLED-SCALING-001

Pocket Science Coffee (2024). G1 / NO_GOVERNING_PHYSICS_CHANGE. Scientific parent
and stacked dependency: PR374, `2f93c216f02700e28801418a3069684fff0ba9ea`.
PW main remains `21669a427145194e1f4003e3cf1b97dedefe2679`; read-only EWP is
`f44c33dbb9b4fb80143e360e6f4a90f8ac0aa516`. Preserve predecessor artifacts/code.

SOURCE_INTERNAL / TARGET_EXPOSED / RETROSPECTIVE /
CONDITIONAL_ON_MEASURED_FINAL_BEVERAGE_MASS. Folds are procedural holdouts, not
blind data. Used means and underlying shots remain exposed. P1 blind-TDS=OPEN.

## Source and observation freeze

Resolve source and predecessor evidence using the predecessor configuration
resolver, then authenticate hashes; an owner-facing symlink/basename is not source
authority. Workbook SHA256:
`9e9063baea1e8f67d905b1e2d03a61a4227e26ed2964ae118426be09bced01cc`;
primary membership:
`1b7863192edf7d4f672a71b5409d02004d72fb171da8d2581724427fb924f196`;
parent numerical result:
`1b548e74f24e7e576c6bf1b831109ae7fce9d6bf27575d7d73986a2f0b3253d5`;
parent freeze:
`48bfd9e5de9659486e754fad72860b3f77cedb5324901ae3097ab6e49749d5f6`.
Verify the original with the unchanged observer and compare every observed shot,
in original order, against the hash-bound parent SHOTS.json. Reuse that exact order.

Primary: 57 physical shots (37 Sworks, 20 VST), 12 conditions. Identity is sheet
plus row; ten flush measurements, repeated readings and bootstrap copies are not
additional physical shots. Raw B, including B54, is filtered numeric TDS pp;
raw C is the unfiltered sensitivity. D/E grams become dose/beverage kg. Historical
Y54 remains unchanged. Nominal basis is refractometer-equivalent solute per solution
mass; no density conversion. Derived EY is a diagnostic, never a predictor.
Exact mapping: Niche Zero → traditional; Superjolly MP64 → turbo. Existing condition
combines sheet/basket, grinder, screen/paper and dispersion. Sessions unknown;
style/grinder confounded. One bounded source/receipt check, no corpus audit.

## Equations, fitting and numerical checks

For x=measured dose/measured final beverage mass and y=direct TDS pp:
P=alpha*x and N=mu each fit one scalar; M=theta[style]*x and C=beta[style] each
fit two. P/N and M/C have matched freedom; M/P tests the added coefficient.
Alpha/theta are operational fitted coefficients, not measured extraction parameters.
All independently minimize the same unweighted physical-shot squared TDS error on
the same training observations, with coefficient bounds [0,100]. Preserve the
predecessor M/C/N fitting exactly. P uses clip(sum(x*y)/sum(x*x),0,100), or
clip(sum(w*x*y)/sum(w*x*x),0,100) for bootstrap multiplicities. No copied parameters,
interactions, shrinkage, hyperparameter search or additional models.

Use the existing 12 leave-one-condition-out folds. Every replicate/copy of a held
condition stays outside its fit; each shot receives exactly one prediction per arm.
Check training rank and disclose active bounds. Independently verify P predictions
against scipy.optimize.lsq_linear with bounds [0,100], method=bvls, tol=1e-14,
to absolute 1e-10 TDS pp. For every point/bootstrap/deletion fold require minimized
training SSE(M) <= SSE(P) + 128*machine_epsilon*max(1,sum_train(w*y²),SSE(P)); this
training-only roundoff allowance is numerical, not a scientific margin. Held-condition
ranking may differ. No GSA. These checks establish arithmetic, not measurement accuracy.

## Scores and paired intervals

Primary RMSE=sqrt(mean physical-shot squared error), TDS pp. Report MAE, signed
bias (prediction minus observation), and unchanged condition-balanced RMSE.
New contrasts are M/P (primary) and P/N (supporting); retain M/C, M/N and C/N as
parent context. Difference L_A−L_B is negative when A wins; gain 1−L_A/L_B is
positive when A wins. Zero reference loss means undefined gain, without epsilon.
Private artifacts include complete predictions, coefficients, coverage, condition
errors, adverse/worst cases, draws and multiplicities.

Use 2,000 draws, numpy default_rng seed 20261026, exact predecessor shot/group
ordering and bootstrap helper. One global multiplicity vector per draw samples
shots within every fixed condition at original size. Refit all arms/all folds and
score with those same multiplicities. Report percentile 95% CIs and requested,
completed, failed draws. Any failed draw makes the decision INCOMPLETE; do not issue
an unconditional reuse verdict. Reproduce all parent point predictions/scores and
all parent bootstrap contrast draws against full-precision artifacts to 1e-10
(TDS pp for absolute values; absolute numerical tolerance for dimensionless gains).
No rounded chat number is a regression target. Preserve parent artifacts.

Intervals assume exchangeable shots within these fixed conditions; they omit unknown
session dependence, calibration and shared systematic error and are not simultaneous.

## Grades, decision and fixed sensitivities

Gain grades: worse <0; small [0,.10); moderate [.10,.25); large >=.25. Report point
and all CI-intersected grades. Reclassify unchanged results under all nine lower
{.075,.10,.125} × upper {.1875,.25,.3125} pairs. These are descriptive conventions,
not adequacy margins or sensor-error robustness checks.

If lower CI G(M/P)>0: STRATIFICATION_EARNS_CONDITIONAL_PREDICTIVE_INCREMENT; retain M.
If upper CI G(M/P)<0 and lower CI G(P/N)>0: POOLED_SCALING_CONDITIONALLY_BETTER;
select P. If M/P spans zero: M/P_UNRESOLVED; if P/N improves, P is a supported
parsimonious alternative with no established superiority between M and P.
Otherwise retain the historical M qualification and report an unresolved comparison.
No equivalence, noninferiority, unnecessary-stratification, causal style/grinder,
practical adequacy, blind validation or production-adoption claim follows.

Separate sensitivities: direct unfiltered C on the primary cohort (own bootstrap);
all 60 already cup-qualified shots including source sectioning rejects (own
bootstrap); delete each primary condition and refit remaining CV, reporting point
influence ranges, not CIs. No further variants. A pooled formula establishes no
transfer to unseen grinders, baskets, coffees or campaigns. Do not execute the
candidate Sworks-to-VST basket-transfer task here.

## Reproduction and publication

Install `pip install -e '.[dev,reconstruct]'`. Commands:

```bash
python tools/pocketscience_pooled_scaling.py freeze
python -m pytest -q tests/test_pocketscience_pooled_scaling.py tests/test_pocketscience_cup_tds.py
python tools/pocketscience_pooled_scaling.py run
```

The new private task directory sits beside the configured inventory manifest;
`--output` may select a fresh external evidence directory. Never overwrite a freeze
or result. Source/membership/method/code hashes freeze before P is fitted. Stop
on receipt/observation drift, failed reproduction or invalid inference. Keep all
numerical outputs/identifiers/paths private; publish code, methods and safe hashes
or status only. Expanded redistribution permission remains absent. No native EWP
runs, production changes or new data. One author implementation/review cycle and
at most one material correction; scientific computation capped at 30 minutes.
