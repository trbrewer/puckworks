# SCI-MD-POCKETSCIENCE-CROSS-BASKET-TDS-001

Pocket Science Coffee (2024). G1 / NO_GOVERNING_PHYSICS_CHANGE. One retrospective,
source-internal Sworks-to-VST transfer, conditional on measured final beverage mass.
Primary P/N; secondary M/P, M/C, C/N. Scientific parent and branch base PR375:
`9f8c6c7cf894872908f3ea212c69209db13c602a`; PR374 ancestor:
`2f93c216f02700e28801418a3069684fff0ba9ea`; PW main:
`21669a427145194e1f4003e3cf1b97dedefe2679`; read-only EWP:
`f44c33dbb9b4fb80143e360e6f4a90f8ac0aa516`. Stack on PR375 while unmerged.

## Source, observation and split freeze

Dataset `pocketscience2024/workbook_assay_reconstruction`. Resolve originals and
private predecessors through existing owner configuration. Basenames and symlinks
are not authority. Authenticate workbook SHA256
`9e9063baea1e8f67d905b1e2d03a61a4227e26ed2964ae118426be09bced01cc`, 57-shot membership
`1b7863192edf7d4f672a71b5409d02004d72fb171da8d2581724427fb924f196`, PR375 FREEZE.json
`cdad2b189075198368efdcd5b46953df4ef0d38a20a662ff4e24ebb160c595e5`, and RESULT.json
`fdf422e40b9ccd7598c3d99be10a211a6a41b342c89943a9a87232845811d868`.
Check predecessor code/input receipts, all 60 cup-qualified rows and order with
the unchanged observer. Authenticate saved bootstrap artifacts without rerunning
the LOCO campaign; reproduce primary point predictions/scores once to absolute
1e-10, against full-precision saved JSON. Never reuse their coefficients for transfer.

Freeze exact sheet/row identities, original ordering, disjointness, one globally
unique condition map, split hashes, source/method/code hashes, and x support by style
before transfer fitting. Primary source: 37 Sworks shots / 8 conditions; target:
20 VST shots / 4 conditions. Total 57 shots / 12 conditions / one campaign. Ten
flush measurements excluded; readings, summaries and bootstrap copies add no shots.
All 60 sensitivity: 40 Sworks -> the same 20 VST; source sectioning rejects at
Sworks rows 7, 9, 23 remain cup-qualified and retain their provenance.

x = measured dose_kg / measured final beverage_kg; raw D/E grams convert to kg.
y = raw filtered numeric TDS percentage points, column B including B54. Raw C
is a separate unfiltered sensitivity, independently fitted and scored. Nominal
basis: refractometer-equivalent solute per solution mass, no density conversion.
Derived EY, regional assays and historical Y54 are not predictors; Y54 is unchanged.
Niche Zero -> traditional; Superjolly MP64 -> turbo. Both styles must be in source.
Report source/target x ranges and overlap before scoring; retain/flag extrapolation.

Both sides: SOURCE_INTERNAL / TARGET_EXPOSED / RETROSPECTIVE /
CONDITIONAL_ON_MEASURED_FINAL_BEVERAGE_MASS. Prior means, selection and LOCO exposed
these targets. Procedural exclusion does not restore blindness. Sworks has brass
and teflon dispersion, VST only teflon; style is confounded with grinder. This tests
observed distributions, not an isolated basket intervention or unseen campaign.
Record actual original/private inspections. Sessions and shared calibration
uncertainty remain UNKNOWN. No new acquisition, figure reading or corpus audit.

## Frozen fits and arithmetic checks

P=alpha*x; N=mu; M=theta[style]*x; C=beta[style]. Independently minimize unweighted
physical-shot squared error in absolute TDS pp on exactly the same Sworks shots,
coefficient bounds [0,100]. P/N have one coefficient each, M/C two each; M/P tests
the extra style coefficient, not matched-complexity mechanism evidence. These
are operational coefficients, not measured extraction properties.
P uses clip(sum(w*x*y)/sum(w*x*x),0,100); N the bounded weighted source mean;
M/C the corresponding style-separated objective. Point weights are all one.
Explicit source-only fitting inputs and separate target prediction inputs; no
target offsets, recalibration, tuning, model selection, interactions or search.
The transfer fitter never invokes cross_predict/joint_predict.

Require finite inputs, complete coverage and full training rank; report active
bounds. Independently verify bounded least-squares predictions with scipy BVLS
to 1e-10 TDS pp. For point/bootstrap/source-deletion fits require
SSE_train(M) <= SSE_train(P) + 128*machine_epsilon*max(1,sum(w*y*y),SSE_train(P)).
Target deletions retain the original source fit. These checks establish arithmetic,
not measurement accuracy. No GSA or native EWP execution is needed.

## Scoring, inference and decision

Primary loss: sqrt(mean squared error across physical VST shots), TDS pp. Also
report MAE, signed bias (prediction minus observation), condition-balanced RMSE,
condition errors, adverse cases, coefficients, coverage and predictions privately.
Delta(A/B)=L_A-L_B, negative favors A; gain=1-L_A/L_B, positive favors A.
Zero reference RMSE makes gain undefined, without epsilon; keep absolute differences.

Each of primary, unfiltered and all-60 uses its own 2,000 paired draws, numpy
default_rng seed 20261026. Within every fixed condition resample physical shots
at its original size. One common global multiplicity vector per draw/all arms;
source multiplicities and source y fit; target multiplicities and target y score.
Refit every draw. Percentile 95% intervals for differences and gains; report requested,
completed, failed, undefined and active-bound counts. Any failed draw blocks a
completed inferential decision; never discard it and claim a full campaign.

Primary paired absolute P-minus-N difference CI: upper <0 gives
P_TRANSFER_ADDED_VALUE_OVER_N; lower >0 gives N_LOWER_TRANSFER_LOSS; otherwise
(including zero endpoint) TRANSFER_COMPARISON_UNRESOLVED. No secondary result
replaces this decision; favorable P/N does not establish P best among four arms.
Zero is a no-improvement reference, not adequacy. Unresolved is neither equivalence
nor noninferiority. No blind validation, causal mechanism or production readiness.

Intervals condition on fixed 8 source/4 target conditions, previously selected
family and exchangeability within conditions. They include source-fit and target
sampling variation, omit unknown session dependence, shared systematic measurement
and previous selection uncertainty, and are not simultaneous or new-campaign evidence.
Gain grades: worse <0; small [0,.10); moderate [.10,.25); large >=.25. Report point
and every CI-intersected grade, plus all nine unchanged-result reclassifications:
lower {.075,.10,.125} x upper {.1875,.25,.3125}. These stress descriptive boundaries,
not measurement robustness or practical adequacy. Never tune boundaries.

## Only prespecified sensitivities and completion

Unfiltered source C -> target C, same 37->20 split, own bootstrap. All 60 qualified
shots, filtered 40->20, own bootstrap. Delete each of 8 source conditions and refit
against all targets; delete each of 4 target conditions and retain the original
source fit. Report point ranges and ranking sign reversals as influence diagnostics,
not CIs. Keep the primary decision separate; state exactly what sensitivities change.
No reverse-transfer, matched-teflon, cross-style or other additional analysis.

One author implementation/review cycle; at most one material correction. Numerical
cross-checks are not independent human review. Scientific computation <=30 minutes,
excluding installation and required repository QA. Stop on unavailable authenticated
inputs, drift, failed predecessor reproduction, rank failure, leakage, invalid paired
inference, budget exhaustion or unfixed material bug. Preserve NOT_RUN/INCOMPLETE
and the precise blocker. Never overwrite predecessor or current frozen evidence.

## Reproduce

Install `pip install -e '.[dev,reconstruct]'`, then:

```bash
python tools/pocketscience_cross_basket_tds.py freeze
python -m pytest -q tests/test_pocketscience_cross_basket_tds.py tests/test_pocketscience_pooled_scaling.py tests/test_pocketscience_cup_tds.py
python tools/pocketscience_cross_basket_tds.py run
```

Default output is a fresh task directory beside the configured private inventory;
`--output` chooses a fresh external directory. Freeze writes private support before
fitting. Public deliverables: code, synthetic tests, methods, reproduction, safe
hashes/status. Originals, locators, identities, coefficients, results, predictions,
aggregates and draws remain private. RESULT.md <=800 words target, summary <=120;
complete JSON/CSVs, freeze and ARTIFACTS.json hashes. Leave PR draft, unmerged,
auto-merge off; distinguish actual local and hosted QA. P1 blind-TDS=OPEN.
Only next candidate if completed: SCI-MD-POCKETSCIENCE-CROSS-STYLE-TDS-001,
traditional -> turbo, frozen P/N within qualified source. Do not execute here;
reassess priority if genuinely unexposed existing data become executable.
