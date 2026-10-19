# Retained MASS evidence: decisions and sensitivity

**The compact anchored MASS model does not establish an advantage over the
already adequate ANCHORED_EMPIRICAL benchmark.** Its baseline RMSE advantage is
0.006481 pp and changes sign under the declared deletions; its absolute-bias
penalty remains positive. The three-coefficient parameterization is smaller,
but both models consume the same early assay and supplied future mass windows.
No independently justified operational use or practical margin was found in the
original protocols, model cards, decision records or EWP consumer contracts.
Practical value remains unestablished; neither equivalence nor uselessness follows.

All three historical metric/decision reductions and direct fraction-to-shot checks
reproduce exactly. New work covers 36 primary and six temperature paired whole-shot
deletions, plus their four baselines: **46 scenarios**, with no fits, optimizer
calls, replacement predictions, historical scoring invocations or simulations.
This is source-internal, target-exposed, retrospective research. The shared
Pannusch/Schmieder lineage and reused shots do not create independent evidence.

| Case | Historical contractual result reproduced | New finding on original support | Supported next decision |
|---|---|---|---|
| MASS-003, first milestone | A/B/C/D = FAIL/FAIL/PASS/FAIL; both E tests FAIL; ANCHORED_EMPIRICAL adequate | Gains over unanchored MASS, persistence and anchored setting empirical stay positive; gain over anchored empirical changes sign. Bias penalties against all three non-persistence references persist. | Retain the adequate empirical benchmark; compact-model advantage and practical adoption are unestablished. |
| MASS-001 | Primary adequacy limited to C02/C05; no declared competitiveness/material gain; temperature MASS PASS | Primary TIME/empirical gains positive in every deletion; 0.10 pp TIME gain relation sensitive; C01 RMSE failure persists. Temperature C03 RMSE relation sensitive. | Retain descriptive timing/temperature benefit and original failure limits; no broad adequacy claim. |
| MASS-002 | A/B/C/D all FAIL; TESTED_CONDITIONING_FAMILY_INADEQUATE | Primary MTF RMSE remains worse than M0 in all deletions, slightly better than setting empirical; C01 RMSE failure persists. | Retain the negative result for this frozen nominal-conditioning family; MT/MF remain ablations. |

[Declaration](PROTOCOL.md) · [Input identities](INPUT_MANIFEST.json) ·
[Full-precision public aggregates](RESULTS.json) ·
[Comparison CSV](aggregate_comparisons.csv) · [Execution and limitations](HANDOFF.md).
Policy interpretation uses the accepted `DECISION_RESOLUTION_POLICY/v1-proposed`
(#335 owner acceptance/merge), without changing any historical requirement.

## What the finite deletion family resolves

Positive gain means reference R minus candidate R, in TDS percentage points.
Each shot R uses scored-interval mass weights; shots are equally averaged within
conditions, then conditions equally. Mean A is mean absolute **shot** bias, not
absolute balanced signed bias. Each deletion removes the same trajectory from
all arms, retains all conditions, and recalculates numerical allowances with its
actual two/three-shot condition weights. The ranges below exclude baseline;
the JSON separately retains baseline, deletion-only numerical envelopes and
baseline-plus-deletion numerical envelopes. Numerics do not change any reported
sign or requirement-relation count.

| Case / candidate | Reference | Baseline gain | Deletion-only gain range | Positive numerical lower endpoints |
|---|---|---:|---:|---:|
| 003 ANCHORED_MASS | UNANCHORED_MASS | 0.141427 | 0.113127 to 0.177135 | 12/12 |
| 003 ANCHORED_MASS | ANCHOR_PERSISTENCE | 13.149142 | 12.990176 to 13.266265 | 12/12 |
| 003 ANCHORED_MASS | ANCHORED_EMPIRICAL | 0.006481 | −0.001248 to 0.016037 | 10/12 |
| 003 ANCHORED_MASS | ANCHORED_SETTING_EMPIRICAL | 0.132371 | 0.111537 to 0.159479 | 12/12 |
| 001 MASS | TIME | 0.093795 | 0.061063 to 0.117440 | 12/12 |
| 001 MASS | BOUNDARY_AWARE_EMPIRICAL | 0.006941 | 0.001910 to 0.012858 | 12/12 |
| 001 MASS, timing sensitivity | TIME_u2 | 0.006688 | −0.020862 to 0.037345 | 8/12 |
| 001 MASS, timing sensitivity | TIME_sqrt | 0.244274 | 0.209341 to 0.272229 | 12/12 |
| 002 MTF | M0 | −0.012249 | −0.015092 to −0.007298 | 0/12 |
| 002 MTF | SETTING_AWARE_EMPIRICAL | 0.015155 | 0.003295 to 0.028025 | 12/12 |

These are named finite sensitivities, not confidence intervals, reliability
estimates, population claims, equivalence tests or replacement historical verdicts.
The 001/002 primary support has six fractions/72 intervals; 003 has five suffix
fractions/60 intervals and twelve separate fraction-1 inputs. Their aggregate
error levels must not be ranked directly across cases.

## MASS-003: error, bias and complexity

Historical balanced R/B/A for ANCHORED_MASS are
0.770456/−0.441874/0.441874 pp; ANCHORED_EMPIRICAL has
0.776937/−0.381108/0.381108 pp. The latter's original positive all-condition
adequacy is preserved. Its individual R and A requirement relations also satisfy
the original limits throughout the deletion family; this is a stability statement,
not a new reduced-cohort adequacy verdict.

The detailed C01 diagnostic is private. Its original anchored-MASS A exceeds
0.50 pp; that relation violates in ten deletions and satisfies in two. All four
anchored-MASS condition RMSE relations satisfy throughout. Against unanchored MASS,
the >=0.10 pp gain and >=3/4 condition-win relations satisfy throughout, while
the 20% affine and <=0.10 pp bias-deterioration requirements violate throughout.
The absolute-bias penalty is 0.304947 pp at baseline and 0.287381–0.323399 pp
under deletion. Signed balanced B changes from +0.029919 to −0.441874 pp;
that signed change is distinct from the absolute-shot-bias penalty.

Against persistence every original material-gain component satisfies in every
deletion. Against anchored setting empirical, the >=0.10 pp and condition-win
components satisfy throughout, while 20% and bias-deterioration components violate
throughout (bias penalty 0.221010–0.292942 pp). Against anchored empirical, both
0.10 pp competitiveness margins satisfy, but all three RMSE material-gain/count
components violate throughout. Its bias penalty remains 0.043344–0.074596 pp.
Candidate adequacy remains a separate requirement in D. C01 sensitivity cannot
repair stable failures of B or E; persistence success does not establish an
advantage over the adequate empirical alternative.

The decomposition uses **per-shot** V=R²−B². Squared-error components are averaged
in pp²; RMSE contributions divide each shot's components by R_reference+R_candidate
before the original hierarchical averaging. Neither squared balanced R nor
squared balanced B substitutes for these calculations.

| Reference | Mean ΔB² (pp²) | Mean ΔV (pp²) | Bias contribution to R gain (pp) | Residual-variation contribution (pp) | Net R gain (pp) |
|---|---:|---:|---:|---:|---:|
| UNANCHORED_MASS | −0.177162 | 0.475488 | −0.108935 | 0.250362 | 0.141427 |
| ANCHOR_PERSISTENCE | 177.988046 | 15.587716 | 12.092286 | 1.056855 | 13.149142 |
| ANCHORED_EMPIRICAL | −0.053656 | 0.065650 | −0.034237 | 0.040718 | 0.006481 |
| ANCHORED_SETTING_EMPIRICAL | −0.149290 | 0.367360 | −0.087366 | 0.219737 | 0.132371 |

Against each non-persistence reference the bias contribution is adverse and the
centered-residual contribution favorable at baseline and every deletion,
including their numerical endpoints. Both contributions are favorable against
persistence. Opposing terms remain visible even when larger than the net gain;
no percentages of the net are used. V describes variation of residuals over
measured fractions; it is not assay variance, irreducible noise, continuous-curve
shape error or a causal explanation of the bias. Direct fractions independently
verify V. No negative-roundoff correction or unresolved contribution bound arose.
Independently widened contribution intervals are separate from tighter direct
net-gain bounds and are not required to sum endpoint by endpoint.

MASS uses three frozen coefficients (amplitude, mass rate, exponent), transformed
Gauss–Legendre quadrature and retained refinement/independent integration checks.
The boundary-aware empirical base uses nine fitted ordinates and exact integrated
piecewise-linear segments. Both receive one analytical anchor amplitude update;
neither is newly fitted here. Both require the same first-vial mass/TDS assay and
measured future mass windows. Setting empirical additionally needs constant nominal
recipe inputs and its frozen 25-ordinate setting profiles. Persistence shares the
anchor and windows but has no decaying curve and performs badly. Fewer coefficients
alone do not establish lower operational cost, faster evaluation, better calibration
or controller value. No timing benchmark or practical cost-benefit threshold is
invented from these results.

## MASS-001: timing, temperature and incomplete flow

MASS primary R/B/A remain 1.025939/0.271408/0.271561 pp. C01 RMSE violates its
limit in every deletion. C01 bias satisfies in two and violates in ten; C06 RMSE
satisfies in one and violates in eleven. C02/C05 R and A relations satisfy throughout.
Against TIME the absolute 0.10 pp gain relation satisfies in five deletions and
violates in seven; the 20% and condition-win components violate throughout.
Against boundary-aware empirical the small positive R gain and reduced A persist,
but absolute/20%/condition-win components violate throughout. The empirical arm
retains its original adequacy failure; descriptive competitiveness margins alone
do not satisfy the historical adequacy-plus-competitiveness axis.

TIME_u2 gain changes sign. TIME_sqrt has a larger, stable positive gain, but its
20% relation satisfies in five deletions and condition-win relation in only one.
These retain their original timing-sensitivity roles, without creating additional
primary requirements or selecting a replacement timing convention. The historical
2,000-draw paired hierarchical bootstrap is authenticated and reused as descriptive
context in RESULTS.json; it was not rerun.

The historical positive MASS temperature result remains PASS (R=0.840938,
A=0.218678 pp). Across six separate temperature deletions, MASS gains remain
positive against TIME (0.090366–0.168208), TIME_u2 (0.022905–0.100328), TIME_sqrt
(0.186134–0.276251) and empirical (0.008260–0.022753 pp), including numerical lower
endpoints. C03's RMSE relation violates in two of six deletions; both bias relations
and C04 RMSE satisfy throughout. No primary three-of-four count is imposed on
this two-condition panel, and no new panel verdict replaces the original PASS.

Flow retains 35/36 supported assays per arm and the unsupported C07 fraction-10
interval. Full C07/full flow metrics remain unavailable. Every C08 arm retains
its adverse historical adequacy result, and every original flow-panel adequacy
status remains FAIL alongside incomplete support. No flow deletion or full-flow
comparison was fabricated. Export-rounding flow diagnostics explicitly cover
only the supported subsets.

## MASS-002: nominal conditioning

Primary MTF R/B/A remain 1.038188/0.268557/0.280478 pp, versus M0
1.025939/0.271408/0.271561. All C01 RMSE relations violate across deletion;
its bias relation satisfies in two and violates in ten. The originally satisfactory
MTF C05 and C06 RMSE relations become adverse in one and two deletions respectively.
MT/MF metrics and sensitivities remain reported as ablations, without invented
incremental pairs or promotion based on their results.

MTF is worse than M0 in every deletion, including numerical endpoints. Its small
baseline A deterioration changes sign (−0.001967 to +0.014392 pp), while remaining
inside the original 0.10 pp margin. Against setting empirical its positive R gain
and positive A penalty persist; the 0.10 pp absolute and 20% gain requirements
violate throughout. The condition-win relation satisfies in one deletion and
violates in eleven. All competitiveness RMSE/bias margins satisfy in both pairs,
but this cannot replace mandatory A. CONDITIONING_EARNED still means A/B/C;
D is separate. Stored historical helper diagnostics retain their roles.

Ramps remain NOT_ADJUDICATED_VARIABLE_SETTING_INPUT. The model consumes programmed
temperature and a source-specific nominal flow-setting code, not measured local
puck temperature or hydraulic flow. No causal recipe interpretation is earned.

## Supported uncertainty and unresolved inputs

Numerical integration allowances and their actual nested reduction/contrast
propagation are executed for every declared scenario. The supplied allowances
are numerical qualifications, not certified total predictive uncertainty.
Arithmetic reconciliation is separate: original metrics/decisions and direct
shot metrics agree exactly; decomposition differences are ordinary floating
arithmetic within the declared 512-ulp reconciliation convention. No scientific
threshold was relaxed. Historical source-export mass/TDS/derived-solute
consistency checks reproduce; their summed kg allowance is not converted to
an assay SD, mass distribution or general RMSE uncertainty.

A separate export-only diagnostic interprets documented eight-decimal TDS output
as rounding. Conditional on fixed masses and frozen parameters, observation-only
allowances are 5e-9 pp for 001/002 and unanchored 003. With retained anchor
amplification and its allowance, anchored-MASS balanced export allowances are
6.720e-9 pp for R and 6.630e-9 pp for B/A; persistence is 1e-8 pp. These are
additional conditional source-rounding calculations, not original decision
allowances or an instrument precision claim. Full joint mass/source/calibration
propagation was **not executed**: no justified primitive-error magnitudes or
joint dependence model are established by these records.

Observed variability is executed from the original TDS rows: three physical
shots per condition/fraction, at their actual differing mass windows. The public
JSON supplies whole-panel summaries; private records retain the detailed cells.
Between-shot spread cannot identify analytical repeatability. Missing components
remain explicit: analytical repeatability, calibration/recovery, mass measurement,
shared systematic error, training/model selection and source/campaign transfer.
No distribution, independence assumption, confidence coverage or universal noise
floor is supplied for them.

The retained mapping verifies qhat_i=q_anchor*g_i. At fixed masses/parameters,
anchor-only additive error changes prediction by g_i*delta; shared additive
calibration error in anchor and later observation changes residual by
(g_i−1)*delta. The original sub-unity amplification factors are reused, not
recomputed as a new prediction family. They do not explain the observed bias
penalty. The documented mass-basis TDS input contract supplies no joint assay/
mass calibration model; correlated gravimetric effects are therefore unresolved.

For primitive vial masses, b0_i=sum(m_j,j<i), b1_i=b0_i+m_i and
w_i=m_i/sum(m_scored). With q_anchor and parameters held fixed,
alpha=q_anchor*m_1/I(0,m_1), so
alpha'=q_anchor*(I(0,m_1)−m_1*q0(m_1))/I(0,m_1)².
An anchor-mass perturbation changes normalization and shifts every suffix
endpoint; fixed later widths and normalized weights do not change. For later
vial j, the integral derivative is
q0(b1_i)*1(j<=i)−q0(b0_i)*1(j<i). A scored vial additionally changes its own
width and all suffix weight normalizations:
∂w_i/∂m_j=(1(i=j)*W−m_i*1(j scored))/W².
An unassayed vial shifts downstream endpoints without becoming a scored mass or
observation. Shared scale error transforms the entire primitive vector jointly;
weights remain unchanged but fixed mass-rate models and anchor normalization
need not. Synthetic checks exercise each map. No independently jittered derived
coordinates, weights, widths or new scored predictions were produced.

## Execution ceiling and owner decision

All declared core components, the optional direct fraction verification,
observation variability, numerical propagation, conditional TDS export-rounding
calculation and retained anchor check executed. Mass-coordinate dependency was
assessed analytically. Full input/measurement/training/transfer uncertainty is
not propagated and is not zero. This completes the available retained-evidence
reductions; it does **not** label the full uncertainty-bearing R-02 analysis
complete. The exact unexecuted component is joint primitive mass/assay/calibration
propagation, requiring justified magnitudes/dependence or an admissible error
model; workbook reconstruction or historical fit logs do not supply that missing
information. No additional data collection is commissioned.

The concrete owner decision is to retain the original three-case contractual
results, credit their stable descriptive gains, and decline to claim earned
compact-anchor or nominal-conditioning complexity on this evidence. The adequate
ANCHORED_EMPIRICAL benchmark remains available as a conditional research reference;
no production adoption or successor is authorized.

PHYSICAL_VALIDATION=NOT_ESTABLISHED. Claims are conditional fraction-delivery
predictions at supplied measured mass windows. Attained beverage mass, time,
pressure/flow, whole-cup closure, soluble inventory, real-time assay, controller
performance and production suitability remain outside the supported claim.

Source-derived artifacts: Pannusch and related Schmieder measurements,
[Mendeley Data 10.17632/y2tz67f6ry.1](https://doi.org/10.17632/y2tz67f6ry.1),
[CC-BY-NC-3.0](https://creativecommons.org/licenses/by-nc/3.0/).
These rights are separate from first-party software licensing. Raw observations,
anchors/states, individual metrics, all deletion vectors, C01 details, private
locators and full logs remain outside Git. Public projection was designed jointly
with already public aggregates to exclude reconstructive three-shot summaries.
