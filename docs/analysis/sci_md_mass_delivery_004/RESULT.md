# SCI-MD-MASS-DELIVERY-004 result

**TRANSFER_CLAIM_LIMITED_BY_SOURCE_COORDINATES_AND_FROZEN_MASS_DOMAIN.**
One independently audited scoring pass is complete. ANCHORED_EMPIRICAL remains
primary. All five axes are **NOT_ADJUDICATED_INCOMPLETE_SUPPORT** for the
all-ten-condition claim. The empirical and compact anchored curves pass the
absolute budgets in all seven completely supported conditions, but no all-cohort
adequacy, early-assay value, shape value, competitiveness or material advantage
is established. The source-grind-2.0 and common-setting summaries are descriptive;
they cannot rescue the primary claim. No curve was refitted or selected afterward.

G1 / NO_GOVERNING_PHYSICS_CHANGE. [Puckworks #284](https://github.com/trbrewer/puckworks/pull/284)
and [EWP #190](https://github.com/trbrewer/espresso-whole-pull/pull/190) are
OPEN/UNMERGED; issues #283/#189. Predecessors #278/#280/#282 and #184/#186/#188
were verified MERGED live; their historical handoffs and dispositions are unchanged.

## Coverage and source qualification

Exact cohort: FIT-C01/C02/C03/C04/C05/C06/C07/C08/C12/C13, R1/R2/R3:
30 physical shots, disjoint from the 15 frozen calibration shots at grind 1.7.
All 30 fraction-1 anchors and 150 later TDS/mass observations are source-eligible.
Fraction 1 is never scored. Outcome fractions are exactly 2,3,5,7,10.

Every arm retains 150 intended slots: 143 supported and numerically qualified.
Total records: 750; qualified predictions: 715; unsupported statuses: 35.
All 150 assayed vial masses total **0.880026040 kg**; the 143 supported intervals
cover **0.836030240 kg**. The source-eligible, supported and qualified identity
hashes/mass totals are in COVERAGE.json and RESULTS.json. These are assayed-suffix
masses, not whole-cup measured totals. Twenty-four shots have all five intervals;
six retain explicit incomplete support. No source-invalid TDS assays occurred.

| Source/domain limitation | Intended identities retained |
|---|---|
| Missing measured vial 6 | FIT-E01-R3 fractions 7 and 10: cumulative prefix unavailable |
| Missing measured vial 8 | FIT-E06-R3 fraction 10: cumulative prefix unavailable |
| Beyond frozen 0.06350639999999999 kg domain | Fraction 10 of FIT-E05-R2, FIT-E05-R3, FIT-E06-R1, FIT-E06-R2 |

The missing vials are unassayed. Their source-imputed masses are not used.
Earlier complete measured prefixes remain qualified; later assayed vial mass/TDS
can be valid while cumulative coordinates are unavailable. All ten vial positions
were checked against source mE/mE_cum and workbook net weights, including gaps.
No clipping, extrapolation, nominal-flow mass inference or denominator reduction.
TDS-specific validity is retained; the HPLC spill exclusion does not remove TDS.

Six original files and nine registers match accepted hashes (SOURCE.json).
SOURCE_FIT_DATA labels grant no fitting permission. Dates are retained by
condition, with UNKNOWN coffee lot and roast batch. Grind settings are source
instrument settings; nominal flow labels are metadata, not measured hydraulic
flow. Recipe, date and unresolved material differences prevent a unique grind cause.
SOURCE_INTERNAL; TARGET_EXPOSED; retrospective early-assay-conditioned comparison.
These are existing potentially inspected data, not new/independent/blind validation.

## Complete-condition scores

Cells give mean shot R / mean absolute shot B in TDS percentage points. Within
shots, errors are weighted by measured assayed mass; shots are equally weighted
within condition. Conditions are balanced equally, never pooled fraction replicates.
Signed B and numerical allowances are in RESULTS.json. A dash denotes incomplete
condition support, not an omitted row. All arms have the same interval coverage.

| Condition | Coverage | Anchored empirical | Unanchored empirical | Anchored MASS | Unanchored MASS | Persistence |
|---|---:|---:|---:|---:|---:|---:|
| FIT-C01 | 13/15 | — | — | — | — | — |
| FIT-C02 | 15/15 | 0.701150 / 0.197203 (PASS) | 1.013210 / 0.456917 (FAIL) | 0.836371 / 0.209864 (PASS) | 1.107349 / 0.476608 (FAIL) | 16.243880 / 15.141462 (FAIL) |
| FIT-C03 | 15/15 | 0.800402 / 0.378828 (PASS) | 0.785705 / 0.447108 (PASS) | 0.859407 / 0.357258 (PASS) | 0.843223 / 0.441634 (PASS) | 15.223251 / 14.435397 (FAIL) |
| FIT-C04 | 15/15 | 0.850671 / 0.285423 (PASS) | 1.011644 / 0.253893 (FAIL) | 0.927087 / 0.222623 (PASS) | 1.093474 / 0.315533 (FAIL) | 16.125652 / 15.074826 (FAIL) |
| FIT-C05 | 13/15 | — | — | — | — | — |
| FIT-C06 | 12/15 | — | — | — | — | — |
| FIT-C07 | 15/15 | 0.578578 / 0.249798 (PASS) | 0.894218 / 0.315245 (PASS) | 0.547920 / 0.256444 (PASS) | 0.871370 / 0.306696 (PASS) | 13.343736 / 12.849061 (FAIL) |
| FIT-C08 | 15/15 | 0.455353 / 0.114137 (PASS) | 0.546101 / 0.156456 (PASS) | 0.512562 / 0.191845 (PASS) | 0.564075 / 0.067891 (PASS) | 14.248087 / 13.652312 (FAIL) |
| FIT-C12 | 15/15 | 0.908263 / 0.283301 (PASS) | 1.110263 / 0.499537 (FAIL) | 0.864346 / 0.299635 (PASS) | 1.077919 / 0.521163 (FAIL) | 14.607071 / 14.147712 (FAIL) |
| FIT-C13 | 15/15 | 0.247320 / 0.038981 (PASS) | 0.291587 / 0.053719 (PASS) | 0.289235 / 0.097434 (PASS) | 0.312813 / 0.020910 (PASS) | 15.215037 / 14.579247 (FAIL) |

Budgets are R<=1.00 pp and mean abs B<=0.50 pp in every complete condition,
plus complete declared support. They are working research budgets, not assay
precision or universal standards. Both anchored models pass C02/C03/C04/C07/C08/
C12/C13. Neither has all-ten adequacy. Both unanchored models definitively fail
C02/C04/C12 while passing C03/C07/C08/C13. Persistence fails all seven complete
conditions. These comparator failures are preserved despite other support gaps.

## Separate scientific axes

| Axis | Reporting disposition | Limitation |
|---|---|---|
| A: absolute transfer adequacy | NOT_ADJUDICATED_INCOMPLETE_SUPPORT | C01/C05/C06 incomplete; seven complete conditions pass |
| B: early-assay value | NOT_ADJUDICATED_INCOMPLETE_SUPPORT | Balanced ten-condition R/bias unavailable; definite/possible wins 6/9 |
| C: curve-shape value | NOT_ADJUDICATED_INCOMPLETE_SUPPORT | Balanced ten-condition R/bias unavailable; definite/possible wins 7/10 |
| D: competitiveness against anchored MASS | NOT_ADJUDICATED_INCOMPLETE_SUPPORT | Requires A and complete balanced metrics |
| E: material advantage over anchored MASS | NOT_ADJUDICATED_INCOMPLETE_SUPPORT | Balanced ten-condition R/bias unavailable; definite/possible wins 5/8 |

No superiority follows from competitiveness, and empirical complexity is not
earned by narrower absolute adequacy. E is not adjudicated, not a demonstrated
absence of every possible advantage. No automatic preference or production use.

**Reporting correction:** the frozen scorer labeled B/C/E NUMERICALLY_UNRESOLVED
because missing conditions widened its possible-win counts. Those ranges arise
from incomplete support; zero evaluated condition comparisons overlap numerical
allowances. ADJUDICATION.json preserves the original axes and clarifies the cause.
RESULTS.json remains byte-identical to the original raw scores. The bounded
REPORTING_REVIEW_ADDENDUM.json binds this label-only correction. No code, model,
prediction, metric, threshold, candidate, PASS/FAIL decision or score was changed.
The frozen `report` command returns the original raw aggregates; use the linked
adjudication when interpreting its coarse raw status labels. This is one scoring
pass, not a second scientific attempt.

## Predeclared descriptive summaries

All-ten metrics below use only supported intervals within each shot and remain
**SUPPORTED_SUBSET_ONLY**. They do not substitute for the unavailable full-suffix
balanced comparison, and no primary threshold is awarded from them.

| Arm | Supported slots | Supported-subset balanced R | Mean abs B | Signed B |
|---|---:|---:|---:|---:|
| ANCHORED_EMPIRICAL | 143/150 | 0.878776 | 0.381591 | 0.217905 |
| UNANCHORED_EMPIRICAL | 143/150 | 0.907898 | 0.349214 | 0.202077 |
| ANCHORED_MASS | 143/150 | 0.903988 | 0.355216 | 0.134280 |
| UNANCHORED_MASS | 143/150 | 0.958773 | 0.331341 | 0.156850 |
| ANCHOR_PERSISTENCE | 143/150 | 15.109159 | 14.446767 | 14.446767 |

| Descriptive group | Supported slots | Empirical R / abs B | Anchored MASS R / abs B | Scope |
|---|---:|---:|---:|---|
| grind_1.4 | 68/75 | 1.171087 / 0.549748 | 1.180734 / 0.485310 | Supported subset only |
| grind_2.0 | 75/75 | 0.586465 / 0.213433 | 0.627242 / 0.225121 | Complete descriptive group; absolute budgets pass |
| common_89C_code2 | 30/30 | 0.577792 / 0.161141 | 0.576790 / 0.198535 | Complete descriptive group; absolute budgets pass |
| corners | 113/120 | 0.954022 / 0.436703 | 0.985787 / 0.394386 | Supported subset only |

The grind-1.4 supported-subset errors are substantial; reporting only the common
setting or grind-2.0 would conceal this limitation. Primary maximum complete-shot
RMSE is 3.324708 pp.
Complete condition means and maximum individual-shot errors answer different
questions. Per-grind coverage, all-five-arm group summaries, fraction/horizon
errors and complete unsupported-reason counts are retained in RESULTS.json.

Primary fraction-2/3/5/7/10 balanced absolute errors on supported intervals are
1.166984/0.796881/0.559034/0.830425/0.358566 pp, with 30/30/30/29/24 shots respectively.
Incomplete horizons remain subset diagnostics. No fractions are independent replicates.

## Numerics, amplitudes and rights

All 715 supported predictions meet numerical budgets; maximum solute allowance 5.94511e-15 kg (budget 1e-9).
Maximum anchor denominator relative allowance 8.23528e-12 (budget 1e-6).
Independent incomplete-gamma and 60-digit piecewise-linear checks differ by at
most 1.475e-17 kg. This qualifies the numerical application, not coffee physics.
Thirty measured fraction-1 inputs produce 60 analytical amplitude updates, zero
new base fits and zero optimizer calls. Empirical alpha ranges
0.890072–1.308032; MASS alpha ranges
0.889153–1.290233. Both bases use the identical physical observation and their own integrals.
Analytical error-amplification ranges are in RESULTS.json; these are not confidence
intervals or sensor requirements. Source rounding, documented measurement uncertainty
and between-shot variation remain separate; no assay uncertainty was invented.

On 143 supported assayed intervals, empirical predicted solute is 0.060241733993 kg
versus observed 0.058481214416 kg. Numerical sum allowance is 2.88e-15 kg;
source export rounding allowance is separately 9.15e-11 kg. These are not measured whole-cup totals.

Pannusch/Schmieder source-derived models, states and aggregate evidence retain
CC-BY-NC-3.0, DOI 10.17632/y2tz67f6ry.1, separately from first-party software.
Raw files, actual anchors/states, rows, per-shot outcomes and full logs remain
outside Git, bound by PRIVATE_EVIDENCE_MANIFEST.json. No coffee-corpus exhaustion.

## Reproduction and software status

Evaluation commit `135df5c3b03769c422231672cc12411e84f89d82`, tree `fa7e0b7b8d35efaff5f17a545eb212dd02a3bbea`.
Freeze SHA256 `ff62fd2ba11ba6203a28ede3a380e7b5a51659198484c629fb97013da8c40dec`.
Raw scores SHA256 `a9c93a84e9f8de90864052c4befff59d917e19e76b4bae972e82447683fc663f`.
MASS SHA256 `75aa34648f73883e975b16c2267594a247142e247713f14642641789f5e2182d`.
Empirical SHA256 `659fdb4eec504190e68ece2cfea449db003bce85ea4279ed68feb59b09772c8d`.
Exact original source/runtime/fit identities, coefficients, knots, units and rights
are in BASES.json, SOURCE.json and FREEZE.json. EWP retains the accepted 003
runtime pin, separately binding this evaluation and qualification; no second predictor.
Its examples remain SYNTHETIC_ANCHOR_INPUT, never physical-shot reproductions.

[README.md](README.md) provides exact prepare/freeze/score/report commands.
An existing run rejects another freeze/score. Reproduction of preparation does not
authorize another real score. PRE_SCORE_REVIEW.json, SCORE_RECEIPT.json and
SCORE_COMPLETION.json bind the one approved pass. SOFTWARE_QA.json separates
local tests, hosted CI, source/numerical qualification and PR/merge status.
Initial full-suite selection was interrupted in favor of the ordinary offline lane;
the log remains external. Protocol/implementation commits preceded completion
of broad ordinary QA; focused tests passed before implementation freeze. No
scientific decision changed. EWP initial manifest-related QA failures were repaired
by generated metadata refresh and affected rechecks, without scientific reexecution.

No all-ten research applicability envelope was earned. Narrow supported-source
diagnostics remain conditional on measured fraction-1 TDS/mass and supplied
future mass windows. No universal grinder mapping, recipe-only prediction,
mass/time attainment, real-time controller, identified inventory, independently
validated physics, production adoption or automatic successor follows.

PHYSICAL_VALIDATION = NOT_ESTABLISHED
NEW_BASE_CURVE_FITS = 0
OPTIMIZER_CALLS = 0
NATIVE_EWP_RUNS = 0
PRODUCTION_DEFAULTS_CHANGED = false
PRODUCTION_DEPENDENCY_LOCK_CHANGED = false
MERGE_AUTHORIZED = false
NO_SUCCESSOR_AUTHORIZED
