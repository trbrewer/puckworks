# SCI-MD-MASS-DELIVERY-002 result

**Recipe conditioning did not earn its additional complexity.** The primary MTF family is inadequate under the frozen all-four-condition contract and has slightly worse balanced RMSE than frozen M0. SETTING_AWARE_EMPIRICAL also fails absolute adequacy; it is not established as preferable. Working research software, source-qualified execution and the single audited scoring pass are complete. No post-score fitting or software/model adjustment occurred.

G1 / NO_GOVERNING_PHYSICS_CHANGE. Puckworks [issue #279](https://github.com/trbrewer/puckworks/issues/279), [PR #280](https://github.com/trbrewer/puckworks/pull/280); EWP [issue #185](https://github.com/trbrewer/espresso-whole-pull/issues/185), [PR #186](https://github.com/trbrewer/espresso-whole-pull/pull/186). Both task PRs remain OPEN/UNMERGED for owner disposition.

## Four-condition primary comparison

Cells show mean shot R / mean absolute shot B in TDS percentage points, followed by adequacy. Every model has 12/12 physical shots and 72/72 eligible intervals supported. Mass weighting is within each shot, then equal shot and condition weighting; these are not pooled fraction-level RMSEs.

| Condition | M0 | MT | MF | MTF (primary) | SETTING_AWARE_EMPIRICAL |
|---|---|---|---|---|---|
| PRED-C01 | 1.356431 / 0.534279 FAIL | 1.306770 / 0.515730 FAIL | 1.344773 / 0.529563 FAIL | 1.295798 / 0.511070 FAIL | 1.241255 / 0.513331 FAIL |
| PRED-C02 | 0.894086 / 0.189383 PASS | 0.940394 / 0.240510 PASS | 0.890037 / 0.177624 PASS | 0.935481 / 0.228570 PASS | 0.892596 / 0.177307 PASS |
| PRED-C05 | 0.772350 / 0.171814 PASS | 0.788508 / 0.188244 PASS | 0.932751 / 0.285847 PASS | 0.950758 / 0.302265 PASS | 1.066530 / 0.242885 FAIL |
| PRED-C06 | 1.080891 / 0.190768 FAIL | 1.095653 / 0.206470 FAIL | 0.958784 / 0.074983 PASS | 0.970717 / 0.080008 PASS | 1.012994 / 0.104060 FAIL |
| Balanced | 1.025939 / 0.271561 | 1.032831 / 0.287738 | 1.031586 / 0.267004 | 1.038188 / 0.280478 | 1.053344 / 0.259396 |

MTF passes C02/C05/C06 and fails C01 on both R=1.295798 pp and mean abs(B)=0.511070 pp. MT passes two conditions; MF passes three. These remain secondary ablations and do not replace MTF. Empirical passes C02 only. M0 passes C02/C05, exactly preserving the predecessor.

## Separate scientific axes

| Axis | MTF decision | Evidence |
|---|---|---|
| A: absolute adequacy | FAIL | C01 exceeds both 1.00 pp R and 0.50 pp bias budgets |
| B: material gain over M0 | FAIL | R is 0.012249 pp (1.1939%) worse; only 2/4 condition R improve; bias deterioration 0.008918 pp |
| C: empirical competitiveness | FAIL | Both relative 0.10 pp margins pass, but mandatory absolute adequacy fails |
| D: material superiority over empirical | FAIL | R improvement 0.015155 pp (1.4388%), only 2/4 condition R improve; bias deterioration 0.021083 pp |

Disposition: `TESTED_CONDITIONING_FAMILY_INADEQUATE`. `CONDITIONING_EARNED` is not satisfied. The empirical model has lower balanced absolute bias but higher balanced RMSE and fails three conditions, so an adequate empirical alternative was not established here. Neither candidate earns production adoption. Margins are working decisions, not statistical equivalence, population inference, causal effects or mechanism identification.

## Added software and verified source contracts

The additive Puckworks API provides explicit M0/MT/MF/MTF/SETTING_AWARE_EMPIRICAL selection, constant nominal temperature/source-code inputs, exact-kernel interval solute and average TDS, conditional stopping-mass queries, explicit unsupported reasons and strict model serialization. The source adapter provides bounded FIT-only fitting, training selection, freeze and once-only audited scoring. EWP checks the explicit producer commit/tree plus all runtime module/model hashes, loading wrapper and reused kernel in an isolated namespace. Synthetic nonzero-slope examples are offline; fitted predictions use the actual fitted slopes. See README.md for commands.

The six inherited raw-source hashes, nine qualified registers, shot/assay identities and full measured mass prefixes were verified through existing configuration/reconstruction. FIT experiments 9/10/11/14/15: 15 physical shots and 90 valid TDS assays at source grind 1.7 and dose 20 g. Primary March C01/C02/C05/C06: 12 shots and 72 valid TDS assays. No other grind or experiment 46 was fitted; related Schmieder/Pannusch records were not doubled as independent cohorts. Every intervening vial advances mass. Missing chemistry remains missing; TDS-valid records survive HPLC-specific spill exclusions. Source dates, UNKNOWN lot identity and unresolved potentially different March roast batch remain in source evidence. Assayed-support totals are not measured whole-cup totals.

Both hash-verified ExpSheet designs, the common source DE1 context, qualified program/register joins and common nominal 60/code collection-design convention support a shared source-design meaning. FIT uses the labelled flow/temperature design columns; March extends them to start/end settings, equal for the primary cases. Preprocessing stores scale-derived run.flow separately. The new input is only a dimensionless nominal source-flow-setting code; no measured flow, derivative, density conversion or hydraulic boundary enters it. Temperature is a programmed setpoint internally in kelvin, not local puck temperature. Historical physical flow-conversion and ramp-clock ambiguities remain unresolved and are not reopened.

## Training-only selection, domain and conditioning

Three fixed within-setting replicate folds hold R1/R2/R3 from all five settings. Shared fold domains and equally spaced knots depend only on training records. Common supported CV intervals are 29/30/30, 89/90 overall; all 15 held physical shots and original denominators remain visible. One R1-held tail interval is outside that fold mass domain. Partial-support CV is a development diagnostic, not an adequacy or unseen-setting validation claim.

| Empirical K | lambda | Balanced CV R (pp) | Selection status |
|---:|---:|---:|---|
| 5 | 0 | 0.454908 | ADMISSIBLE |
| 5 | 0.001 | 1.471311 | ADMISSIBLE |
| 5 | 0.1 | 3.430752 | ADMISSIBLE |
| 5 | 10 | 3.513380 | ADMISSIBLE |
| 9 | 0 | not scored as candidate | EXCLUDED_OR_FAILED |
| 9 | 0.001 | 1.441521 | ADMISSIBLE |
| 9 | 0.1 | 3.417899 | ADMISSIBLE |
| 9 | 10 | 3.513241 | ADMISSIBLE |

Selected **K=5, lambda=0**, with 25 profile coefficients, no monotonicity. K=9/lambda=0 is excluded because a required training-site observation design is rank-deficient; no arbitrary nonunique curve is treated as identified. All site/fold data and augmented ranks, singular values and conditioning diagnostics are in TRAINING_SELECTION.json. Compact CV diagnostic R: MT 0.670078, MF 0.575753, MTF 0.577779 pp. All families were fixed before target scoring; no target family selection occurred.

MTF coefficients (c_ref,k_ref,p,aT,aF,dT,dF): `[0.277544594707011, 66.1285558455733, 0.8525853093024881, 0.024509201620888897, -0.10683453083762316, 0.002824203860763293, -0.05311310744844232]`. Local final Jacobians are full rank, with scale-dependent conditioning diagnostics retained; this does not establish parameter identification. The fitted temperature effects are small and the software reports them as fitted.

The final mass interval is [0,0.0635064] kg, unchanged from 001. The recipe hull is |xT|+|xF|<=1. Their product is a modeling assumption, not evidence of complete joint observational coverage.

| FIT condition | Largest measured mass endpoint (kg) | Borrowed/model-supported region above own extent (kg) |
|---|---:|---|
| FIT-C09 | 0.0564434 | 0.0564434 to 0.0635064 |
| FIT-C10 | 0.0564322 | 0.0564322 to 0.0635064 |
| FIT-C11 | 0.0635064 | none |
| FIT-C14 | 0.0571946 | 0.0571946 to 0.0635064 |
| FIT-C15 | 0.0569211 | 0.0569211 to 0.0635064 |

C03/C04/C07/C08 are `NOT_ADJUDICATED_VARIABLE_SETTING_INPUT`; all 72 ramp assay-coordinate records remain explicit exclusions per candidate. No ramp duration, averaged setting, pseudo-steady prediction or new ramp score was invented. Predecessor ramp findings remain historical and cannot alter this four-condition decision.

## Execution, numerics, review and QA

Exactly 192 real nonlinear starts completed; 13,207 actual residual evaluations including numerical Jacobians, maximum 131/start, zero failures; hard ceilings 500 starts and 2,000 calls/start. Exactly 124 bounded linear solves. Original attempt traces, termination reasons, boundary hits and selected objectives are retained privately. A pre-freeze source-identity metadata addition changed no coefficients or predictions and required no refit; original metadata artifacts are preserved. No extra post-score work occurred.

Primary/refined integration and independent quadrature qualified every supported interval. Maximum allowance is 1.391119e-14 kg against 1e-9 kg. Empirical integrals were independently split at knots. Allowances propagate into condition/balanced metrics and comparison gates; no threshold is numerically unresolved. The reviewer additionally checked 480 compact cases against independent gamma integrals (maximum error 2.857e-12 kg) and 120 empirical cases (8.674e-19 kg). These are numerical qualification, never physical validation.

The independent reviewer approved freeze `e8333b85943bc3ab54db88adb8b631cd863911a9e626a9ba20c006b5c7dbc7c6` before the single March scoring invocation. All 720 frozen prediction records reproduced exactly. M0 condition and balanced R/B/abs(B) replay differences are exactly zero (tolerance 1e-9 pp). PRE_SCORE_REVIEW.json, FREEZE.json and score receipts bind that evidence. Implementation author did not approve the audit. No March chemistry entered this task’s fitting/selection; task choice was informed by exposed predecessor results, so March is not newly blind.

- Source: QUALIFIED for the declared nominal-code/mass/TDS contract; variable-setting use not adjudicated.
- Numerical: QUALIFIED; no unresolved threshold.
- Scientific: TESTED_CONDITIONING_FAMILY_INADEQUATE; all MTF A/B/C/D axes FAIL.
- Software/local QA: 77 focused producer tests and seven consumer tests pass; registry 65 PASS plus one acknowledged exception; lint and EWP source/static/historical/change/boundary/shell/JSON checks pass. Full-suite initial environment/manifest failures and their passing affected reruns are explicitly retained in SOFTWARE_QA.json.
- Review: independent exact-freeze pre-score audit APPROVED. Final PR-head review/owner disposition remain separate.
- Hosted CI: resolve from live exact-head PR checks; this scientific result does not assert their completion.

Exact runtime producer: `cec97741e72b126f04f05b73691d9223bbdb148f`, tree `1b30d6d6152baedc28fab42419a2c33d61b8694b`. EWP reviewed runtime consumer: `db02beaf12976497d9f9714d36d38142f7a37ad1`, tree `5f701e8fa8dd75b2118e7d0aeb366566f3cc438d`. Later result/current-state commits do not change those scientific runtime identities. EWP HANDOFF.json records every model/kernel hash. Both predecessor PRs #278/#184 are live-verified MERGED, with squash trees identical to their historical PR heads; their artifacts were not rewritten.

## Rights and limits

Models, source summaries and tables retain Pannusch/Schmieder attribution, [Mendeley Data DOI 10.17632/y2tz67f6ry.1](https://doi.org/10.17632/y2tz67f6ry.1), and CC-BY-NC-3.0 treatment, distinct from first-party software licensing. Raw files, measurement/prediction rows, full optimizer logs and per-shot results remain private and are hash-bound by PRIVATE_EVIDENCE_MANIFEST.json. This is SOURCE_INTERNAL, TARGET_EXPOSED, RETROSPECTIVE_MODEL_DEVELOPMENT_COMPARISON. No causal coefficient, mechanism, inventory, whole-cup truth, universal coffee/grinder transfer, pressure/flow/time or mass-attainment claim.

```text
PHYSICAL_VALIDATION = NOT_ESTABLISHED
NATIVE_EWP_RUNS = 0
PRODUCTION_DEFAULTS_CHANGED = false
PRODUCTION_DEPENDENCY_LOCK_CHANGED = false
NO_SUCCESSOR_AUTHORIZED
```
