# SCI-MD-MASS-DELIVERY-001 result

**Primary adequacy is limited to PRED-C02 and PRED-C05.** MASS and the boundary-aware empirical model both fail the all-four-condition absolute-TDS requirement. The reusable research software is implemented and executed; broad predictive adequacy, declared practical competitiveness, and material superiority are not established. No post-score fitting or model repair occurred.

G1 / NO_GOVERNING_PHYSICS_CHANGE. SOURCE_INTERNAL; TARGET_EXPOSED. Owner issues: Puckworks #277 and EWP #183. Both resulting PRs remain open/unmerged.

## Primary campaign result

| Candidate | Balanced R (TDS pp) | Mean abs B (pp) | Conditions adequate |
|---|---:|---:|---:|
| MASS | 1.025939 | 0.271561 | 2/4 |
| TIME | 1.119735 | 0.918691 | 1/4 |
| BOUNDARY_AWARE_EMPIRICAL | 1.032881 | 0.276947 | 2/4 |
| TIME_u2 | 1.032628 | 0.808554 | 2/4 |
| TIME_sqrt | 1.270214 | 1.036421 | 1/4 |

Equal shot weight within conditions and equal condition weight; not pooled-row RMSE. Working budgets (R <=1.00 pp; mean abs B <=0.50 pp) are task decisions, not measurement uncertainties or published espresso standards.

MASS is only 0.006941 pp (0.672%) lower in R than the empirical baseline and improves only one of four conditions. Its bias metric is 0.005386 pp lower. Both comparative 0.10 pp margins pass, but primary adequacy fails, so **declared practical competitiveness fails**. No material gain versus the baseline. Against primary TIME, R decreases 0.093795 pp (8.377%), with only one condition improved; the absolute, relative and condition-count gain tests all fail. Bias improves 0.647130 pp. Beating TIME on an aggregate alone earns no empirical-superiority claim.

## Every condition, including stress cases

Cells show mean shot R / mean absolute shot B, TDS percentage points, followed by adequacy. TIME depends on the declared within-interval timing assumption.

| Condition | MASS | TIME linear | Empirical | TIME u² | TIME sqrt(u) |
|---|---|---|---|---|---|
| PRED-C01 | 1.3564 / 0.5343 FAIL | 1.3324 / 1.0277 FAIL | 1.3529 / 0.5594 FAIL | 1.1590 / 0.8725 FAIL | 1.5399 / 1.1921 FAIL |
| PRED-C02 | 0.8941 / 0.1894 PASS | 0.7066 / 0.5165 FAIL | 0.8889 / 0.1660 PASS | 0.6537 / 0.4342 PASS | 0.7805 / 0.5972 FAIL |
| PRED-C03 | 0.9803 / 0.3055 PASS | 0.8475 / 0.6902 FAIL | 1.0149 / 0.2859 FAIL | 0.7388 / 0.5698 FAIL | 0.9981 / 0.8143 FAIL |
| PRED-C04 | 0.7016 / 0.1318 PASS | 1.0896 / 0.9571 FAIL | 0.6963 / 0.1602 PASS | 1.0694 / 0.8939 FAIL | 1.1468 / 1.0169 FAIL |
| PRED-C05 | 0.7723 / 0.1718 PASS | 0.5525 / 0.4154 PASS | 0.7702 / 0.1878 PASS | 0.5916 / 0.3799 PASS | 0.6732 / 0.4621 PASS |
| PRED-C06 | 1.0809 / 0.1908 FAIL | 1.8875 / 1.7151 FAIL | 1.1196 / 0.1945 FAIL | 1.7262 / 1.5476 FAIL | 2.0872 / 1.8943 FAIL |
| PRED-C07 | UNSUPPORTED (one interval) | UNSUPPORTED (one interval) | UNSUPPORTED (one interval) | UNSUPPORTED (one interval) | UNSUPPORTED (one interval) |
| PRED-C08 | 1.5063 / 0.5848 FAIL | 2.2019 / 1.7263 FAIL | 1.4617 / 0.6233 FAIL | 2.0939 / 1.6265 FAIL | 2.3141 / 1.8280 FAIL |

Temperature ramps C03/C04: MASS R=0.840938, abs B=0.218678 pp, both pass; empirical R=0.855580, abs B=0.223015, only C04 passes. TIME linear R=0.968559, abs B=0.823669; TIME u² 0.904070/0.731847; TIME sqrt(u) 1.072446/0.915628; none passes both temperature conditions.

Flow ramps C07/C08: no full two-condition aggregate is reported because PRED-E07-R1 fraction 10 extends to 0.0717189 kg beyond the training maximum. All models retain that case as unsupported. C08 fails for every model. C07 other shots and supported-only diagnostics for the affected shot remain in the private complete shot report; no reduced denominator earns a pass. Ramp success cannot rescue primary failure.

## Source and fitted artifact

Primary FIT: experiments 9,10,11,14,15, source grind 1.7; five conditions, 15 physical shots, 90 valid TDS assays. Other grinds (30 shots) and experiment 46 excluded. Primary March: C01/C02/C05/C06, 12 shots/72 assays. Secondary: C03/C04 temperature ramps and C07/C08 flow ramps, six shots/36 assays each. Zero TDS spill exclusions: the declared source spills affect HPLC, not TDS. No required measured mass prefix is missing or source-imputed in these cohorts.

All ten FIT vials and eleven March collected vials advance source cumulative mass; assayed fraction IDs are 1,2,3,5,7,10. Six assays per shot leave intervening gaps, plus the later eleventh vial. Measured workbook net masses cross-check the exact shot mE arrays; source mE_cum is reused. Source fraction-derived solute mg agrees within propagated 8-decimal export rounding. Observations are mass-basis TDS and measured collected mass; clocks remain source-fitted and programs remain machine instructions. No telemetry join or flow history is invented.

`SCI-MD-MASS-DELIVERY-001/MASS/v1`, schema `mass-delivery/1`: c0=0.2827944898059652 kg/kg, kb=68.0383392716077 kg^-1, p=0.8327267294693588. Supported mass domain [0,0.0635064] kg. TIME has additional source-clock support [0,58.31531651059772] s. All model identities, units and coefficients are in `models/*.json`; empirical baseline selected nine equally spaced knots and lambda=0 using training-only LOCO. Three fold-held intervals outside their fold-specific mass domains remain visible in selection diagnostics; no later campaign information sets knots or lambda. Selection errors are not unbiased final scores.

Exact implementation/model producer: `d59cec8ab8314e2697837c6752d296d20f4dc370`, tree `1645ad55cf08d18938088d19ec8d7efcffa15ef1`. EWP handoff binds this revision and MASS artifact SHA-256 `75aa34648f73883e975b16c2267594a247142e247713f14642641789f5e2182d`; subsequent documentation commits do not redefine that producer. The original Grudeva producer/handoff were verified merged (#276/#182); historical code, coefficients, evidence and scores are unchanged.

## Numerical, software and review axes

- SOURCE_CONTRACT: qualified for declared mass-basis observations; one later stress interval outside training domain.
- SOFTWARE_AND_QA: working SI predictor, source adapter, fit/predict/score CLI, serialization, synthetic example and thin EWP consumer. Focused producer tests: 38 passed; consumer tests: five passed. Full-suite/CI results are tracked separately in SOFTWARE_QA.json and the live PR checks.
- NUMERICAL_QUALIFICATION: supported final intervals qualified; maximum integration allowance below 9.46e-14 kg versus 1e-9 kg target. Allowances propagated to metrics and decisions; no scored threshold is numerically unresolved. All expected cases retained.
- PRIMARY_PREDICTIVE_ADEQUACY: MASS and empirical pass C02/C05 only; primary TIME passes C05 only. Sensitivities remain separate.
- COMPETITIVENESS_VS_BOUNDARY_AWARE_BASELINE: FAIL under the predeclared conjunction because MASS is not adequate across all primary conditions; comparative error margins alone pass.
- MASS_VS_TIME: no material gain under the frozen primary criteria.
- RAMP_STRESS_RESULTS: MASS passes both temperature ramps; flow-ramp complete comparison blocked at C07 support and C08 fails.
- REVIEW_AND_CI: independent exact-freeze pre-score audit approved; ordinary final review and hosted CI have their own actual-head status. No author self-approval.

Exactly 192 nonlinear starts, 8,089 actual residual calls including numerical Jacobians, zero failed starts, maximum 109 calls/start. Caps: 500 starts and 2,000 actual calls/start. No native build/run. The independent audit prompted pre-score fixes to source-register integrity checks, numerical-decision propagation, and constant/near-zero quadrature summation. The final numerical fix changed frozen predictions by at most 3.56e-17 kg using unchanged coefficients; no extra fits occurred. Superseded evidence is preserved. The revised prediction bundle froze before one scoring pass; all code/source/artifact hashes were checked.

Independent audit: 38 producer tests, five consumer tests, 420 analytical/near-zero cases and all 720 intended records checked. There are 715 supported records across five treatments and five explicit unsupported entries for the same physical interval. `PRE_SCORE_REVIEW.json`, `FREEZE.json`, score receipts and `PRIVATE_EVIDENCE_MANIFEST.json` bind the retained evidence. Full per-shot R/B, interval-solute RMSE, signed/absolute assayed-total errors, maximum running assayed residual, coverage and numerical allowances exist in private scores.json and ALL_SHOT_RESULTS.md; no restricted row-level artifact is redistributed.

Paired 2,000-replicate hierarchical bootstrap preserves condition/shot/fraction grouping. Descriptive 95% MASS-minus-empirical R interval: [-0.030793,0.015697] pp; MASS-minus-TIME [-0.570274,0.224568] pp. Four conditions do not support strong population, superiority or equivalence claims. Complete intervals in RESULTS.json.

## Use and limits

See [README.md](README.md) for runnable synthetic, fitted-model and source-evaluation commands. The fitted component is usable for conditional research predictions, with the documented condition failures. It is not generally qualified for the declared primary absolute observable. EWP loads the exact producer kernel/model and requests synthetic intervals and a 0.04 kg stop; it does not duplicate the kernel or change the production lock.

Source-derived coefficients and aggregate tables retain Pannusch/Schmieder attribution and CC-BY-NC-3.0 treatment, not MIT. Raw MAT/workbooks, chemistry rows, prediction rows, full optimizer traces and the complete shot report remain external.

PHYSICAL_VALIDATION remains NOT_ESTABLISHED. This direct observational regression does not resolve c_s0-to-inventory mapping, EWP absolute closure, initial/residual puck inventory, whole-pull hydraulics, pressure-to-flow prediction, or disentangle coffee/roast/campaign causes. Coefficient universality is not established. Assayed-support totals are not measured complete-cup totals; modeled gap integrals remain predictions. Production defaults and dependencies/puckworks.lock.json are unchanged. No laboratory work, automatic merge or successor.
