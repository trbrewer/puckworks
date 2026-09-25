# Independent pre-scoring review

Reviewer: independent agent /root/independent_prescore_audit
Task: SCI-MD-GRUDEVA-CLOCK-001
Original freeze SHA-256: `b1e586d2115b03582260a76c476fa5a395ba4ee3a5c78f17c3d5ab737a94f9a6`
Original decision: CHANGES_REQUIRED, retained below as historical review evidence.

Final freeze SHA-256: `6c436b8f5721193a18c879a50c6b58d28f65aeac2b89916b183867c872a50355`

Final decision: **APPROVED_FOR_SCORING** for the frozen retrospective experiment. No blocker remains after the bounded pre-scoring corrections. This approval authorizes the frozen fit-predict/scoring sequence, not a scientific result or production adoption.

The reviewer did not implement the experiment, edit frozen implementation files, execute the upstream notebook, fit a model to real measurements, or compute real comparative scores. Notebook source cells were read as JSON. Raw CSV, thesis methods, frozen protocol, code and tests were inspected directly, rather than relying only on the implementation author's summaries.

## Original findings, resolved before approval

R1 — Failed-fold and numerical-unresolved reporting is incomplete. The initial `score` returns only `per_shot` and `failures` if any prediction is unavailable; `report` attempts to iterate a missing prediction and requires absent aggregate/comparison fields. An independent synthetic fixture containing failed predictions reproduced `TypeError: 'NoneType' object is not iterable`. Numerical qualification and decision stability are separate booleans, while nominal positive increment fields remain exported without the protocol's explicit `NUMERICALLY_UNRESOLVED` disposition. Preserve nominal diagnostics, distinguish unresolved decisions from earned gains, and make the failed-fold report complete without reducing the required 13-shot denominator. Add synthetic regression coverage. No change to source, fitting, thresholds, or comparison definitions is requested.

Minor trace correction: exhausted optimizer attempts do not contain the last evaluated parameter vector/loss or explicit unavailable scipy counters. Preserve these where obtainable and explicitly label unavailable optimizer results; do not invent completed optimizer statistics.

## Scientific findings on the initial freeze

- All nine frozen file hashes, the freeze SHA-256, and the three source hashes match. Original synthetic suite independently passed: 16 tests, including slow tests, in 3.60 seconds. The initial 64-node failure remains disclosed in frozen QA; correcting to 128 nodes occurred before real fits.
- Independent CSV inspection confirms 70 nonempty rows, fourteen five-row blocks, eighteen original column slots, and complete first-sixteen positions. Within the first thirteen blocks there are 26 structural zero-mass vials, 180 eligible positive-mass chemistry values, and the two declared ambiguous positive-mass zero-TDS positions. All checkable regular net masses agree with gross minus tare at the frozen 0.005 g reporting threshold. Rectangular source mapping retains original positions.
- Thesis sections 2.1–2.2 explicitly describe thirteen shots, sixteen consecutive two-second samples, simultaneous pump/wheel start, varying barista-selected grind settings, dilution correction, and no first-drip realignment. Notebook cells 3/4/6/18 iterate the first thirteen source blocks; cells 6/8 establish percent TDS and weight*TDS/100. This supports the ordinal physical-shot grouping within the pinned file. It does not establish universal or cross-file shot IDs.
- The fourteenth block is preserved but lacks authority linking it to the described accepted physical-shot cohort. Blocking that named alternate comparison is defensible and does not manufacture a block on the thirteen-shot experiment. Terminal vials have unqualified time intervals; missing tare/chemistry reinforces the stated terminal exclusions. Existing row window/cohort/missingness fields plus the frozen protocol adequately explain those exclusions without requiring another row-status framework.
- The primary unavailable-chemistry interpretation and bounded literal-zero sensitivity are defensible: recorded zero TDS in positive liquid is unresolved, whereas zero liquid implies zero delivered solute. Known beverage mass advances the mass coordinate even with unavailable chemistry. Structural zeros remain predicted but cannot inflate score denominators. Observed-support totals correctly avoid complete-cup claims.
- The operator integrates mass fraction over beverage mass. Its linear/u-squared/square-root timing assumptions, exact MASS timing invariance, nonnegative bounded delivery, zero-rate limit, and fixed-parameter time endpoint bounds are mathematically consistent. Transformation u=v^8 regularizes the allowed origin behavior; independent direct-u QUADPACK and 256-node refinement qualify predictions. These are numerical checks, not measurement uncertainty.
- Held-shot chemistry and eligibility do not enter training or template construction. Fits use whole-shot exclusion, equal-shot mean vial squared error, fixed bounds/scales/starts/budget, and training-only nested TIME/MASS starts. The independent synthetic leakage/determinism test passed. The arithmetic concentration template uses training positions only and deterministic fallback. Conditioning every candidate on measured beverage masses is fair for the declared prediction question; it does not demonstrate flow prediction.
- Metric definitions, strict paired improvements, 10/13 requirements, adequacy, material gain, and template competitiveness match the frozen protocol. Conservative per-model metric corners cover each monotone decision condition, including paired counts. These owner working budgets are not source error bars, standards, equivalence tests, or physical validation.

## Scope and limitations

Reviewed AGENTS/CLAUDE, onboarding, the relevant minimum-necessary G1 governance and correction rules, external-data guide/policy and Grudeva manifest/card/permission context. Permission is documented, not an SPDX licence; new row-level source and result payloads remain private. Existing registered model behavior and historical post-fit evidence are not upgraded.

This is retrospective, already-exposed source-conditioned grouped prediction. Source qualification involved measurement inspection before the freeze; prospective or sealed-target independence is unavailable. The source itself excludes channelled/clogged attempts and varies grind settings; applicability stays within its accepted source cohort. The two zero interpretations and separate timing sensitivities are bounded checks, not exhaustive joint robustness. Correlated time and cumulative mass can leave mixed parameters unidentified; predictive gains alone establish no mechanism. Numerical precision does not cover source measurement error or optimizer global optimality. Final repository checks, ordinary review, CI, and assessment of the eventual frozen outputs remain separate.

## Bounded delta verification and final approval

R1 is resolved. Failed folds now retain the expected thirteen-shot denominator, produce an explicit unresolved scientific disposition, and remain reportable with failed predictions marked and unavailable aggregates represented as plot gaps. Numerical target or metric-box instability leaves the nominal diagnostics available but all scientific decision axes unresolved. During this same focused audit, the reviewer also identified that the numerical gate checked only eligible chemistry rows; the correction now gates the maximum allowance across every prediction row, including unavailable chemistry and structural zeros, while metric error propagation still uses the declared eligible support.

R2 is resolved. Exception traces retain the last evaluated parameter vector/loss and exact wrapper call count; unavailable scipy counters are explicit. This adds trace information without modifying residuals, bounds, starts, optimizer settings, fit selection or call budget.

The final freeze hash and all nine bound file hashes were independently verified. Source manifest/audit, preflight, README and VizSpec hashes are unchanged from the original freeze. The code/protocol delta is confined to the described reporting, gate-scope and trace corrections, with synthetic regression tests and QA updated. Original freeze, implementation, tests and initial review are preserved privately. No real-source fitting or comparative scoring preceded this approval according to the execution freeze and author's contemporaneous record; the reviewer performed neither.

The final synthetic suite independently passed **20 tests in 6.41 seconds**, including slow recovery/leakage checks, exhausted attempts, deterministic scoring, exclusive output creation, failed-fold reporting, numerical-unresolved reporting, and the excluded-chemistry numerical-gate regression. No test was skipped. The original 16-test passing evidence and initial numerical-test failures remain documented.

APPROVED_FOR_SCORING against the final SHA-256 above. Scientific source/fitting/operator/decision definitions were not retuned. This is completion of one focused independent audit with a bounded pre-scoring correction, not implementation self-review or a new scientific attempt. Final review and CI remain separate.
