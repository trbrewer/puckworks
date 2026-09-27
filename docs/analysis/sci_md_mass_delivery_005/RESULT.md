# SCI-MD-MASS-DELIVERY-005 result

TWO_ASSAY_MASS_INADEQUATE_ON_DECLARED_OBSERVED_WINDOWS.

G1 / NO_GOVERNING_PHYSICS_CHANGE. Reject this fixed first-two-assay, two-parameter family for the declared observed-window decision. No retuning or replacement primary is selected. This is a predictive inadequacy result with qualified numerical computation, not a missing-source or inversion blocker. No arm is adequate across every condition in either panel.

Puckworks [issue #285](https://github.com/trbrewer/puckworks/issues/285), [PR #286](https://github.com/trbrewer/puckworks/pull/286); EWP [issue #191](https://github.com/trbrewer/espresso-whole-pull/issues/191), [PR #192](https://github.com/trbrewer/espresso-whole-pull/pull/192). PRs are OPEN_UNMERGED.

## Authority and support

Evaluated producer commit `2fd6cc46b53cf52e7f0b2798d5ce43d7bfe0869e`, tree `8798d84d007674ceb5434744f183a4200eb6feda`; base `5cc38629482a1eb40e9b8ee5695d5589b7a65c32`. EWP audited consumer `c0c6ea151166746e08b72cf71b03d5f104bd1bdb`, tree `b697492297052c832499f0d0ef5fe08d764b1754`; base `2ea8d05dc91727119dd3163f896d9561127f5e6d`. Later publication commits do not change the evaluated runtime pin.

Live main ancestry was verified locally: 001–004 components were merged at task start. In particular, 004 remains FROZEN_EMPIRICAL_TRANSFER_INADEQUATE; its original score, later adjudication, artifacts and runtime identities remain untouched. Historical OPEN/UNMERGED prose does not override those live merge identities.

The exact accepted six original-file hashes and nine register hashes are in [SOURCE.json](SOURCE.json). The shared Pannusch/Schmieder campaign is counted once. All 42 shots / 14 conditions remain: PRED C01/C02/C05/C06 and FIT C01/C02/C03/C04/C05/C06/C07/C08/C12/C13, three replicates each. The original 001 calibration experiments 9/10/11/14/15 are excluded. Fractions 1 and 2 supply 84 explicit conditioning observations; fraction 2 changes role only in this task. Fractions 3/5/7/10 are the 168 intended future slots.

The primary estimand is error on PREDECLARED, MEASURED-PREFIX, IN-DOMAIN FUTURE ASSAY WINDOWS. Coordinate-only support was committed before conditioning extraction: 48/48 PRED and 113/120 FIT, or 161/168 total. Each arm has this identical fixed mask. Three unavailable measured prefixes and four out-of-domain windows remain as statuses in the full assessment and all 1008 records. These are neither nonexistent assays nor numerical integration failures. Every measured intervening vial advances mass; no missing mass is imputed. The domain remains exactly [0, 0.06350639999999999] kg.

The exact identity set, measured coordinates and per-shot denominators are privately published in `support.json` and `shot_results.json`, hash-bound by [FREEZE.json](FREEZE.json) and [PRIVATE_EVIDENCE_MANIFEST.json](PRIVATE_EVIDENCE_MANIFEST.json). Thirty-six shots have four primary windows, five have three, and one has two. Public condition denominators appear below. No failed arm can remove a declared window.

## Predeclared decisions

| Axis | Meaning | PRED | FIT-transfer | Both panels |
|---|---|---|---|---|
| AXIS_A | Restricted absolute adequacy | FAIL | FAIL | FAIL |
| AXIS_B | Rate adaptation vs fixed MASS | FAIL | FAIL | FAIL |
| AXIS_C | Same-information competitiveness with required adequacy | FAIL | FAIL | FAIL |
| AXIS_D | Two-assay fixed empirical vs first-only empirical | FAIL | FAIL | FAIL |
| AXIS_E | p0 shape vs exponential | PASS | FAIL | FAIL |

A/B/C FAIL independently in both panels: earned rate adaptation is rejected. Axis C includes adequacy and also fails direct competitiveness against fixed/second-only empirical alternatives. A is competitive against exponential alone, but that cannot rescue C. Axis E passes only PRED: improvement 0.705968 pp (39.466%), four condition wins; FIT improvement is 0.077307 pp (4.888%), six wins, below all required material-gain thresholds.

Against fixed MASS, the primary is worse by 0.245851 pp in PRED and 0.726677 pp in FIT; definite wins are 0/4 and 1/10. Absolute-bias deterioration is 0.274370 and 0.876941 pp. Two-assay fixed empirical versus first-only empirical also fails material gain: improvements -0.047773 and +0.026595 pp, wins 0/4 and 4/10. Neither a pooled average nor successful individual conditions changes these decisions.

## Restricted panel metrics

R, signed B and mean |B| are percentage points. Shots are weighted equally within conditions, conditions equally within each panel. Each shot uses measured-window mass weighting. Numerical allowances are carried through comparisons; these tables round only for display.

| Panel | Arm | R | B | mean abs B | All-condition adequacy |
|---|---|---:|---:|---:|---|
| PRED | TWO_ASSAY_MASS | 1.082831 | -0.887394 | 0.940604 | FAIL |
| PRED | TWO_ASSAY_EXPONENTIAL | 1.788799 | -1.646191 | 1.646191 | FAIL |
| PRED | TWO_ASSAY_FIXED_MASS | 0.836980 | -0.666233 | 0.666233 | FAIL |
| PRED | TWO_ASSAY_FIXED_EMPIRICAL | 0.827373 | -0.736379 | 0.736379 | FAIL |
| PRED | SECOND_ASSAY_EMPIRICAL | 0.953257 | -0.888631 | 0.888631 | FAIL |
| PRED | FIRST_ASSAY_EMPIRICAL | 0.779601 | -0.665654 | 0.665654 | FAIL |
| FIT-transfer | TWO_ASSAY_MASS | 1.504431 | 0.023714 | 1.398935 | FAIL |
| FIT-transfer | TWO_ASSAY_EXPONENTIAL | 1.581739 | -0.775852 | 1.424465 | FAIL |
| FIT-transfer | TWO_ASSAY_FIXED_MASS | 0.777754 | 0.079771 | 0.521993 | FAIL |
| FIT-transfer | TWO_ASSAY_FIXED_EMPIRICAL | 0.705651 | 0.037683 | 0.503888 | FAIL |
| FIT-transfer | SECOND_ASSAY_EMPIRICAL | 0.790286 | -0.114994 | 0.695161 | FAIL |
| FIT-transfer | FIRST_ASSAY_EMPIRICAL | 0.732246 | 0.106757 | 0.461025 | FAIL |

## Primary condition metrics and coverage

All states are feasible and qualified: 3/3 per condition per arm. All primary windows have qualified predictions. Full intended denominators are 12 windows and three shots for every condition.

| Condition | Primary / intended windows | R | B | mean abs B | Primary A | Full A |
|---|---:|---:|---:|---:|---|---|
| PRED-C01 | 12/12 | 0.982589 | -0.812664 | 0.812664 | FAIL | FAIL |
| PRED-C02 | 12/12 | 0.959918 | -0.519018 | 0.731858 | FAIL | FAIL |
| PRED-C05 | 12/12 | 0.715579 | -0.606807 | 0.606807 | FAIL | FAIL |
| PRED-C06 | 12/12 | 1.673237 | -1.611085 | 1.611085 | FAIL | FAIL |
| FIT-C01 | 10/12 | 1.328346 | 0.349909 | 1.258551 | FAIL | FAIL |
| FIT-C02 | 12/12 | 2.182870 | 2.119412 | 2.119412 | FAIL | FAIL |
| FIT-C03 | 12/12 | 1.694446 | 1.580730 | 1.580730 | FAIL | FAIL |
| FIT-C04 | 12/12 | 2.537888 | 2.473266 | 2.473266 | FAIL | FAIL |
| FIT-C05 | 10/12 | 2.072214 | -1.872727 | 1.872727 | FAIL | INCOMPLETE |
| FIT-C06 | 9/12 | 1.735350 | -1.573138 | 1.573138 | FAIL | INCOMPLETE |
| FIT-C07 | 12/12 | 0.950324 | -0.894543 | 0.894543 | FAIL | FAIL |
| FIT-C08 | 12/12 | 0.858858 | -0.472144 | 0.743351 | FAIL | FAIL |
| FIT-C12 | 12/12 | 1.290344 | -1.208920 | 1.208920 | FAIL | FAIL |
| FIT-C13 | 12/12 | 0.393674 | -0.264709 | 0.264709 | PASS | PASS |

FIT-C01 explicitly fails: restricted R=1.328346 pp and mean |B|=1.258551 pp on 10 windows across all three shots. On the full suffix, two complete shots alone give mean-|B| lower bound 0.768421 pp using the original denominator three. This proves failure despite the incomplete third shot. Its R lower bound 0.830498 pp alone does not prove R failure. No incomplete signed-error sum supplies an absolute-bias lower bound.

## Full intended suffix

FULL_INTENDED_SUFFIX_STATUS = INADEQUATE_WITH_INCOMPLETE_COVERAGE. PRED has complete coverage and the same decisions as the restricted assessment. FIT retains 120 slots, of which seven lack qualified coordinates/domain. Full panel-balanced FIT metrics are therefore undefined, never replaced by a supported-subset mean. Nonetheless, known complete-shot failures make adequacy A FAIL and dependent C FAIL. Even granting all three incomplete conditions as possible wins cannot meet the eight-condition requirement for B/D/E; they also FAIL. Combined A/B/C/D/E are all FAIL. FIT-C05/C06 individual full adequacy remains incomplete; C01 and other complete failures survive. No full-suffix PASS is claimed.

## Numerical and sensitivity qualification

All 252 states and all 966 supported forecasts qualify. The 42 remaining records (seven windows times six arms) retain source/domain statuses. Zero state failures or outcome-guided retries occurred. The fixed p0=.8327267294693588 and original mass origin were preserved. The computational ceiling k<=10000 kg^-1 is not an empirical physical range.

Primary A spans 0.244500–0.411467 kg/kg and k spans 43.3611–121.1316 kg^-1. These are local concentration-scale/effective-rate estimates, not inventory, diffusivity, permeability or identified physical kinetics. Primary future-TDS sensitivity to fraction-1 TDS is -0.980921 to -0.075567 pp/pp; to fraction-2 TDS it is +0.162192 to +1.734369 pp/pp. Thus later forecasts can amplify second-assay changes even though the local numerical inverse is regular. The A/lambda Jacobian condition number ranges 11.3765–17.4590 in the declared coordinates and units; it is not a unit-invariant measure of physical identifiability.

Primary maximum solute numerical allowance is 9.9607822e-15 kg; maximum relative conditioning-denominator allowance is 1.9619266e-13. Both are below the frozen 1e-9 kg / 1e-6 budgets. All-six-arm ranges, Jacobian/parameter diagnostics and per-input sensitivities appear in [RESULTS.json](RESULTS.json). [Qualification card](QUALIFICATION_CARD.md) describes independent numerical reproduction. Numerical error, export rounding and between-shot variability are separate; no undocumented assay SDs or confidence intervals were invented. No measurement-robustness or real-time-assay feasibility claim follows.

## Estimation and execution counts

84 two-parameter update attempts (42 MASS + 42 exponential), 84 primary scalar solves and 84 tighter qualification solves; 8567 scalar function calls. 168 analytical amplitude updates (42 in each fixed/two-, second-, first-assay arm). This is same-shot local parameter estimation, not zero calibration input. Global curve refits, hyperparameter searches and optimizer calls are all zero. Independent audit reproduction is separately documented, not included as evaluated estimation.

| Numerical call type | Actual calls |
|---|---:|
| adaptive_quadrature_calls | 6172 |
| analytic_exponential_reference_calls | 5481 |
| legacy_adaptive_quadrature_calls | 938 |
| legacy_integral_refinement_and_reference_calls | 938 |
| moment_refinement_256_calls | 658 |
| shape_average_128_calls | 10038 |
| shape_average_256_calls | 1722 |
| shape_average_reference_calls | 10876 |

## Assayed support and detailed diagnostics

| Panel | Observed solute, kg | Primary predicted solute, kg | Sum numerical allowance, kg | Export-rounding allowance, kg | Worst primary shot R, pp | Worst window absolute error, pp |
|---|---:|---:|---:|---:|---:|---:|
| PRED | 0.0146264984 | 0.0122139972 | 8.169e-14 | 2.654e-11 | 1.903444 | 2.379487 |
| FIT-transfer | 0.0332701080 | 0.0333018965 | 2.388e-13 | 6.146e-11 | 2.927031 | 3.585845 |

These sums cover only the declared assayed windows; they are not measured whole-cup totals. [RESULTS.json](RESULTS.json) contains all-arm condition metrics, coverage, feasibility, allowances, fraction/horizon aggregate errors and solute sums. The public projection omits measured coordinates and singleton horizon values to keep actual observations/per-shot results private. The exact original score hash remains in [SCORE_COMPLETION.json](SCORE_COMPLETION.json); this publication projection is not another score.

## Evidence and limits

[PRE_SCORE_REVIEW.json](PRE_SCORE_REVIEW.json) is the independently authored approval for freeze `ae82a73d5336a2cacb78faf358a46fb2a066702bf2c2e9b80d4fb825fc1073cc`. Exactly one exclusive [score attempt](SCORE_RECEIPT.json) completed; the STARTED receipt is immutable and its [completion record](SCORE_COMPLETION.json) proves completion. EXECUTION.json remains the original pre-score snapshot with scoring=NOT_EXECUTED; it is superseded only for execution lifecycle by that completion record. [QA.md](QA.md) separates software/hosted/review statuses. Reproducible prepare/freeze/score/report and synthetic commands are in [README.md](README.md); EWP supplied-JSON consumer commands are in its linked PR. No further real scoring is authorized.

SOURCE_INTERNAL / TARGET_EXPOSED / RETROSPECTIVE_TWO_ASSAY_CONDITIONED_COMPARISON. Previously exposed outcomes did not become blind when this new procedure froze. Source dates/settings and UNKNOWN lot/roast metadata are retained in SOURCE.json; date, recipe and material differences remain confounded. No universal grind-dial map or causal grind claim is made. The grinder-to-cup link remains solute/TDS delivery conditional on supplied measured beverage-mass windows, not recipe-to-hydraulics prediction.

Pannusch/Schmieder, Mendeley 10.17632/y2tz67f6ry.1: source-derived results retain CC-BY-NC-3.0 treatment, separate from first-party software licensing. Raw files, actual observations, states, row predictions, per-shot results and full logs remain private.

```text
DISPOSITION = TWO_ASSAY_MASS_INADEQUATE_ON_DECLARED_OBSERVED_WINDOWS
PHYSICAL_VALIDATION = NOT_ESTABLISHED
GLOBAL_CURVE_REFITS = 0
LOCAL_PARAMETER_ESTIMATION = 84_TWO_PARAMETER_UPDATES_AND_168_AMPLITUDE_UPDATES
NATIVE_EWP_RUNS = 0
PRODUCTION_DEFAULTS_CHANGED = false
PRODUCTION_DEPENDENCY_LOCK_CHANGED = false
FULL_INTENDED_SUFFIX_STATUS = INADEQUATE_WITH_INCOMPLETE_COVERAGE
PRS = OPEN_UNMERGED
MERGE_AUTHORIZED = false
LABORATORY_ACTION_AUTHORIZED = false
NO_SUCCESSOR_AUTHORIZED
```
